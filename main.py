# import pandas as pd
# import os
import asyncio
# from typing import List, Dict
from managers.scraper_manager import ScraperManager
from scrapers.first_layer.setn_crawler import SETNScraper
# from scrapers.think_tank.brookings_scraper import BrookingsScraper
# from scrapers.think_tank.aei_scraper import AEIScraper
# from scrapers.think_tank.rand_scraper import RANDScraper
# from scrapers.think_tank.americanprogress_scraper import AmericanProgressScraper  # noqa
# from scrapers.think_tank.heritage_scraper import HeritageScraper
# from models.article import NewsURLs
# from .models.article_type import CFRThinkTankType  # type:ignore
from utils.logging_config import setup_logging
from utils.redis_client import RedisClient
import logging


logging.getLogger('selenium').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.WARNING)


async def main():
    # 初始化Redis客戶端
    redis_client = RedisClient(host='localhost', port=6379)

    # 初始化管理器
    manager = ScraperManager()
    # 註冊爬蟲
    manager.register_scraper(SETNScraper())

    urls = await manager.scrape_selected(
        names=["三立新聞"],
    )
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


if __name__ == "__main__":
    # 基本配置
    setup_logging()

    # 自定義配置
    setup_logging(
        level=logging.DEBUG,           # 控制台日誌等級
        log_file='scraper.log',    # 指定日誌文件名
        log_dir='logs',        # 自定義日誌目錄
        file_level=logging.DEBUG      # 文件日誌等級
    )

    # main()

    asyncio.run(main())
