import logging
import json
import time
from redis import Redis
from typing import Set, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# TODO: 改為異步操作


class RedisClient:
    """Redis客戶端，管理所有數據庫操作"""
    KEYS = {
        'all': 'urls:all',              # hash 類型: URL 及其添加時間
        'pending': 'urls:pending',      # set 類型: 待處理的URLs佇列
        'failed': 'urls:failed',        # hash 類型: 失敗的URLs及其錯誤信息
        'completed': 'urls:completed',  # set 類型: 已完成處理的URLs
        'html': 'html:pending',         # hash 類型: 儲存HTML內容
        'stats': 'stats:crawler',       # hash 類型: 爬蟲統計信息
    }

    def __init__(self, host: str = '127.0.0.1', port: int = 6379):
        # 創建Redis連接
        self.redis: Redis = Redis(
            host=host,
            port=port,
            decode_responses=True,  # 將bytes解碼為str
        )

    def _initialize_redis(self):
        """初始化Redis數據庫"""
        # 檢查並初始化統計計數器
        if not self.redis.exists(self.KEYS['stats']):
            initial_stats = {
                'total_urls': 0,
                'success_count': 0,
                'failure_count': 0,
                'last_update': datetime.now().isoformat()
            }
            # 將整個initial_stats保存到 Redis中
            self.redis.hset(self.KEYS['stats'], mapping=initial_stats)

    def add_urls(self, urls: Set[str]) -> Dict[str, int]:
        """批量添加新URLs到Redis數據庫中的集合(urls:pending, urls:all)"""
        stats = {
            'total': len(urls),  # 輸入的URL總數
            'new': 0,            # 新增的URL數量
            'duplicate': 0       # 重複的URL數量
        }

        current_time = str(time.time())

        # 使用pipeline 減少與Redis通信次數，並保證操作的原子性
        with self.redis.pipeline() as pipe:
            for url in urls:
                # 檢查URL是否已存在
                if not self.redis.hexists(self.KEYS['all'], url):
                    # 新URL，添加到 all（帶時間戳）和 pending
                    pipe.hset(self.KEYS['all'], url, current_time)
                    pipe.sadd(self.KEYS['pending'], url)
                    stats['new'] += 1
                else:
                    stats['duplicate'] += 1

            # 更新統計信息
            if stats['new'] > 0:  # 只有當有新URL時才更新統計
                pipe.hincrby(self.KEYS['stats'], 'total_urls', stats['new'])
                pipe.hset(self.KEYS['stats'], 'last_update',
                          datetime.now().isoformat())

            pipe.execute()  # 執行所有命令

        return stats

    def get_pending_url(self) -> Optional[str]:
        """獲取一個待處理的URL"""
        # spop 返回值為 str, list, None
        result = self.redis.spop(self.KEYS['pending'])
        return str(result) if result is not None else None

    def mark_url_completedd(self, url: str, html_content: Optional[str]
                            ) -> bool:
        """標記URL為已完成"""
        try:
            with self.redis.pipeline() as pipe:
                # 從pending中刪除
                pipe.srem(self.KEYS['pending'], url)

                # 將URL添加到completed集合
                pipe.sadd(self.KEYS['completed'], url)

                # 保存網頁內容
                if html_content:
                    pipe.hset(self.KEYS['html'], url, html_content)

                # 更新統計資料
                pipe.hincrby(self.KEYS['stats'], 'success_count', 1)  # 增加成功數量
                pipe.hset(self.KEYS['stats'], 'last_update',
                          datetime.now().isoformat())

                # 執行所有操作
                pipe.execute()
            return True
        except Exception as e:
            logger.error(f"標記URL為已完成時出現錯誤: {str(e)}")
            return False

    def mark_url_failed(self, url: str, error_msg: str) -> bool:
        """標記URL為失敗"""
        try:
            # Reids只能存字符串, 不能直接存python字典, 因此轉成json格式
            failed_info = json.dumps({
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'retries': 0
            })

            with self.redis.pipeline() as pipe:
                pipe.hset(self.KEYS['failed'], url, failed_info)
                pipe.hincrby(self.KEYS['stats'], 'failure_count', 1)
                pipe.execute()
            return True
        except Exception as e:
            logger.error(f"標記URL為失敗時出現錯誤: {str(e)}")
            return False

    def get_stats(self) -> Dict[Any, Any]:
        """獲取爬蟲統計信息"""
        return self.redis.hgetall(self.KEYS['stats'])  # type: ignore

    def cleanup_old_urls(self, days: int = 7):
        """清理指定天數前添加的URLs"""
        cutoff_time = int(time.time()) - (days * 86400)

        # 獲取所有URL及其時間戳
        all_urls: Dict[str, str] = self.redis.hgetall(
            self.KEYS['all'])  # type: ignore

        # 找出需要刪除的URLs
        urls_to_delete = [
            url for url, timestamp in all_urls.items()
            if int(timestamp) < cutoff_time
        ]

        if urls_to_delete:
            with self.redis.pipeline() as pipe:
                # 從 all 中刪除舊的URLs
                pipe.hdel(self.KEYS['all'], *urls_to_delete)

                # 同時從其他集合中也清理掉這些URL
                for url in urls_to_delete:
                    pipe.srem(self.KEYS['pending'], url)
                    pipe.srem(self.KEYS['completed'], url)
                    pipe.hdel(self.KEYS['failed'], url)
                    pipe.hdel(self.KEYS['html'], url)

                pipe.execute()

            logger.info(f"已清理 {len(urls_to_delete)} 個舊的URLs")
