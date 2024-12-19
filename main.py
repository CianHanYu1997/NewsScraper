import asyncio
from managers.scraper_manager import ScraperManager
from scrapers.first_layer.setn_crawler import SETNScraper
from scrapers.first_layer.cna_crawler import CNAScraper
from scrapers.first_layer.mnews_crawler import MNEWSScraper
from scrapers.first_layer.itn_crawler import ITNScraper
from scrapers.first_layer.tvbs_crawler import TVBSScraper
from scrapers.first_layer.ettoday_crawler import ETtodayScraper
from scrapers.second_layer.setn_second_crawler import SetnHTTPFetcher
from utils.logging_config import setup_logging
from utils.redis_client import RedisClient
from celery_scraper.scraper_tasks import scrape_all
import logging


logging.getLogger('selenium').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.INFO)


async def first_main():
    # 初始化Redis客戶端
    redis_client = RedisClient(host='localhost', port=6379)

    # 初始化管理器
    manager = ScraperManager()
    # 註冊爬蟲
    manager.register_scraper(SETNScraper())
    manager.register_scraper(CNAScraper())
    manager.register_scraper(MNEWSScraper())
    manager.register_scraper(ITNScraper())
    manager.register_scraper(TVBSScraper())
    manager.register_scraper(ETtodayScraper())

    urls = await manager.scrape_selected(
        names=["鏡新聞"],
    )
    # urls = await manager.scrape_all()
    print(urls)
    print(len(urls))
    # 獲取統計信息
    stats = await redis_client.add_urls(urls)
    print(f"添加URL統計: {stats}")

    # 獲取待處理的url
    while url := await redis_client.get_pending_url():
        print(f"處理需爬蟲網站:{url}")
        break

    # 獲取統計信息
    stats = await redis_client.get_stats()
    print(f"爬蟲統計: {stats}")


async def second_main():
    manager = ScraperManager()
    manager.register_scraper(SETNScraper())
    # urls = await manager.scrape_all()
    urls = ['https://www.setn.com/News.aspx?NewsID=1581720']
    for url in urls:
        async with SetnHTTPFetcher() as fetcher:
            news = await fetcher.fetch(url)
            print(f"媒體: {news.media_name}")
            print(f"記者: {news.author}")
            print(f"地區: {news.coverage}")
            print(f"分類: {news.category}")
            print(f"標題: {news.title}")
            print(f"發布日期: {news.publish_date}")
            print(f"關鍵字: {', '.join(news.keywords)}")
            print(f"內容摘要: {news.description[:100]}...")
            print(f"url: {news.url}")

if __name__ == "__main__":
    # 基本配置
    setup_logging()

    # 自定義配置
    setup_logging(
        level=logging.INFO,           # 控制台日誌等級
        log_file='scraper.log',    # 指定日誌文件名
        log_dir='logs',        # 自定義日誌目錄
        file_level=logging.INFO      # 文件日誌等級
    )
    asyncio.run(second_main())
    # result = scrape_all.delay()
    # print(result.get())
