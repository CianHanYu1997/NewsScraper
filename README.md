# News Scraper Framework

一個基於異步設計的新聞爬蟲框架，整合 Redis 緩存與定時任務功能。目前僅支援 URL 爬取，HTTP 內容解析尚在開發中。

## 開發狀態

- ✅ 第一層爬蟲：URL 收集（已完成）
- 🚧 第二層爬蟲：內容解析（開發中）
## 特色

- 異步爬蟲設計 (使用 `asyncio`)
- 定時任務排程 (Celery)
- Redis 緩存管理
- 代理池支援
- 模組化設計
- 多重新聞來源支援
- 靈活的頁面載入策略

## 系統需求

### 基礎環境
- Python 3.7+
- Redis Server
- Chrome/Chromium
- ChromeDriver

### Python 套件
```
selenium
beautifulsoup4
celery
redis
eventlet    # Windows 環境下 Celery 需要
httpx
fake-useragent
```

## 專案結構

```
├── scrapers/               # 爬蟲實現
│   ├── first_layer/        # 第一層爬蟲 (URL收集)
│   ├── second_layer/       # 第二層爬蟲 (內容解析)
│   └── base.py             # 爬蟲基礎類
├── managers/               # 管理模組
├── models/                 # 數據模型
├── strategies/             # 爬蟲策略
│   └── page_load.py        # 頁面載入策略
├── utils/                  # 工具類
│   ├── redis_client.py     # Redis操作
│   └── proxy_operations.py # 代理池操作
├── celery_scraper/         # Celery任務
└── config/                 # 配置文件
```
## 核心組件

### 1. 爬蟲基礎架構 (Base Scrapers)

框架提供兩種基礎爬蟲類型：

#### NewsSeleniumFetcher (Selenium基礎爬蟲)
- 處理動態加載內容的網站
- 支援多種頁面載入策略
- 異步操作設計
- 主要功能：
  - URL採集
  - 頁面導航
  - 動態內容處理

關鍵方法：
```python
class NewsSeleniumFetcher(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """返回新聞網站名稱"""
        pass

    @abstractmethod
    def get_base_url(self) -> str:
        """返回新聞網站的基礎URL"""
        pass

    @abstractmethod
    def get_url_elements_locator(self) -> tuple:
        """返回URL元素的定位器"""
        pass

    async def fetch_urls(self, load_count: Optional[int] = None) -> List[str]:
        """獲取新聞URL列表"""
        pass
```

#### NewsHTTPFetcher (HTTP基礎爬蟲)
- 處理靜態內容的網站
- 支援代理池整合
- 異步HTTP請求
- 主要功能：
  - 內容解析
  - 元數據提取
  - 新聞資訊結構化

### 2. 爬蟲管理器 (ScraperManager)
- 統一管理多個爬蟲實例
- 支援異步爬取
- 錯誤處理與日誌記錄

### 3. Redis 客戶端
- URL 去重
- 任務狀態追蹤
- 統計資訊儲存

### 4. 代理池管理
- 支援代理伺服器使用
- 代理自動切換
- 代理可用性驗證

### 5. 定時任務
- 使用 Celery 進行任務排程
- 定期執行爬蟲任務

## 頁面載入策略

支援三種頁面載入策略：

1. ScrollLoadStrategy：滾動加載
2. PaginationLoadStrategy：分頁加載
3. ScrollPaginationLoadStrategy：混合加載策略

```python
from strategies.page_load import ScrollLoadStrategy
scraper = NewsSeleniumFetcher(
    page_load_strategy=ScrollLoadStrategy(scroll_pause_time=2.0)
)
```

## 快速開始

### 1. 環境準備

確保已安裝所有必要的套件：
```bash
pip install -r requirements.txt
```

### 2. 啟動服務

```bash
# 啟動 Redis 服務
redis-server

# Windows 環境下啟動 Celery Worker
celery -A celery_scraper worker -l info -P eventlet

# 啟動 Celery Beat (定時任務)
celery -A celery_scraper beat -l info
```

### 3. 基本使用

```python
import asyncio
from managers.scraper_manager import ScraperManager
from scrapers.first_layer.setn_crawler import SETNScraper
from utils.redis_client import RedisClient

async def main():
    # 初始化 Redis 客戶端
    redis_client = RedisClient()
    
    # 初始化管理器
    manager = ScraperManager()
    
    # 註冊爬蟲
    manager.register_scraper(SETNScraper())
    
    # 執行爬蟲並獲取結果
    urls = await manager.scrape_all()
    stats = await redis_client.add_urls(urls)
    print(f"爬蟲統計: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Redis 配置

```python
redis_config = {
    'host': 'localhost',
    'port': 6379,
    'db_crawler': 0  # 爬蟲數據庫
}
```

## Windows 環境注意事項

1. Windows 環境下必須使用 eventlet 作為 Celery 的執行池
2. 需要安裝 eventlet：`pip install eventlet`
3. 啟動 Celery 時需指定 eventlet：`-P eventlet`

## 一般注意事項

1. 確保 Redis 服務已啟動
2. 適當設置爬蟲間隔，避免對目標網站造成負擔
3. 確保 ChromeDriver 版本與 Chrome 瀏覽器版本相符
4. 注意記憶體使用，特別是在大量爬取時
