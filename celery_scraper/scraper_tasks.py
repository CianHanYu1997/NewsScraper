from celery_scraper.celery import app
from utils.redis_client import RedisClient
from managers.scraper_manager import ScraperManager
from scrapers.first_layer.setn_crawler import SETNScraper
from scrapers.first_layer.cna_crawler import CNAScraper
from scrapers.first_layer.mnews_crawler import MNEWSScraper
from scrapers.first_layer.itn_crawler import ITNScraper
from scrapers.first_layer.tvbs_crawler import TVBSScraper
from scrapers.first_layer.ettoday_crawler import ETtodayScraper
import asyncio


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@app.task
def scrape_all():
    async def _do_scrape():
        # 在這個函數內部創建和管理所有異步資源
        # 建立Redis客戶端
        redis_client = RedisClient()
        try:
            # 初始化管理器
            manager = ScraperManager()
            # 註冊爬蟲
            manager.register_scraper(SETNScraper())
            manager.register_scraper(CNAScraper())
            manager.register_scraper(MNEWSScraper())
            manager.register_scraper(ITNScraper())
            manager.register_scraper(TVBSScraper())
            manager.register_scraper(ETtodayScraper())

            # 執行爬蟲: 運行直到一個 Future 實例完成
            urls = await manager.scrape_all()
            stats = await redis_client.add_urls(urls)

            return {
                'urls_count': len(urls),
                'stats': stats
            }
        finally:
            # 確保 Redis 連接被關閉
            await redis_client.close()
        # 使用 asyncio 創建新的事件循環

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_do_scrape())

    finally:
        try:
            # 安全機制: 確保程式能正確地關閉
            # 清理所有懸掛的任務, all_tasks() 返回所有還在運行中的任務
            pending = asyncio.all_tasks(loop)
            # gather 等待任務完成, return_exceptions=True 表示任務出錯也不會中斷其他任務
            loop.run_until_complete(asyncio.gather(
                *pending, return_exceptions=True))
        finally:
            # 關閉事件循環
            loop.close()


@app.task
def daily_report():
    print("生成每日報告")
    return "報告已生成"
