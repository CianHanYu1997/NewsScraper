from celery_scraper.celery import app
from utils.redis_client import RedisClient
from managers.scraper_manager import ScraperManager
from scrapers.first_layer.setn_crawler import SETNScraper
from scrapers.first_layer.cna_crawler import CNAScraper
import asyncio


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@app.task
def scrape_all():
    # 使用 asyncio 創建新的事件循環
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _do_scrape():
        # 在這個函數內部創建和管理所有異步資源
        # 建立Redis客戶端
        redis_client = RedisClient()
        try:
            # 初始化管理器
            manager = ScraperManager()
            manager.register_scraper(SETNScraper())
            manager.register_scraper(CNAScraper())

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
    try:
        return loop.run_until_complete(_do_scrape())

    finally:
        try:
            # 清理所有懸掛的任務
            pending = asyncio.all_tasks(loop)
            loop.run_until_complete(asyncio.gather(
                *pending, return_exceptions=True))
        finally:
            # 關閉事件循環
            loop.close()


@app.task
def daily_report():
    print("生成每日報告")
    return "報告已生成"
