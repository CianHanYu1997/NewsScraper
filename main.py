# import pandas as pd
# import os
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


# def save_to_csv(articles: List[NewsURLs], filename: str) -> None:
#     # 將 Article 對象轉換為字典列表
#     articles_dict = [{
#         '智庫名稱': article.think_tank_name,
#         '文章類型': article.article_type,
#         '發布日期': article.publish_date,
#         '標題': article.title,
#         '連結': article.url
#     } for article in articles]

#     # 創建 DataFrame 並保存
#     df = pd.DataFrame(articles_dict)
#     df.to_csv(filename, index=False, encoding='utf-8-sig')  # utf-8-sig 支持中文
#     print(f'已保存 {len(articles)} 筆資料到 {filename}')


# def save_articles_separately(
#         articles: List[NewsURLs],
#         output_dir: str = "output") -> None:
#     """
#     將不同智庫的文章分別儲存成獨立的 CSV 檔案

#     Args:
#         articles: Article 物件列表
#         output_dir: 輸出目錄路徑
#     """
#     # 確保輸出目錄存在
#     os.makedirs(output_dir, exist_ok=True)

#     # 依據智庫名稱分組
#     articles_by_thinktank: Dict[str, List[NewsURLs]] = {}
#     for article in articles:
#         if article.think_tank_name not in articles_by_thinktank:
#             articles_by_thinktank[article.think_tank_name] = []
#         articles_by_thinktank[article.think_tank_name].append(article)

#     # 分別儲存每個智庫的資料
#     for think_tank_name, think_tank_articles in articles_by_thinktank.items():
#         filename = os.path.join(output_dir, f"{think_tank_name}.csv")
#         save_to_csv(think_tank_articles, filename)


# def save_articles_combined(
#         articles: List[NewsURLs],
#         filename: str = "all_thinktank_articles.csv") -> None:
#     """
#     將所有智庫的文章合併儲存成單一 CSV 檔案

#     Args:
#         articles: Article 物件列表
#         filename: 輸出檔案名稱
#     """
#     save_to_csv(articles, filename)


def main():
    # 初始化Redis客戶端
    redis_client = RedisClient(host='localhost', port=6379)

    # 初始化管理器
    manager = ScraperManager()
    # 註冊爬蟲
    manager.register_scraper(SETNScraper())
    # manager.register_scraper(BrookingsScraper())
    # manager.register_scraper(AEIScraper())
    # manager.register_scraper(RANDScraper())
    # manager.register_scraper(AmericanProgressScraper())
    # manager.register_scraper(HeritageScraper())

    # 列出所有爬蟲及其支持的類型
    # scrapers_info = manager.list_scrapers()

    # print("可用的爬蟲及其支持的文章類型：")
    # for name, types in scrapers_info.items():
    #     print(f"{name}: {', '.join(types)}")

    # # 執行全部爬蟲
    # articles = manager.scrape_all()
    # # 方法一：分別儲存
    # save_articles_separately(articles, "output_files")

    # # 方法二：合併儲存
    # save_articles_combined(articles, "所有智庫文章.csv")

    # 只執行選定的爬蟲
    # articles = manager.scrape_selected(
    #     names=["布魯金斯研究所"],
    # )
    # print(len(articles))
    # save_to_csv(articles, '布魯金斯研究所.csv')

    urls = manager.scrape_selected(
        names=["三立新聞"],
    )
    print(len(urls))
    # redis_client.clear_all()
    stats = redis_client.add_urls(urls)
    print(f"添加URL統計: {stats}")

    # 獲取待處理的url
    # while url := redis_client.get_pending_url():
    #     print(f"處理需爬蟲網站:{url}")
    #     break

    # 獲取統計信息
    stats = redis_client.get_stats()
    print(f"爬蟲統計: {stats}")

    # save_to_csv(articles, '美國企業研究所.csv')

    # articles = manager.scrape_selected(
    #     names=["蘭德"],
    # )
    # print(len(articles))
    # save_to_csv(articles, '蘭德.csv')

    # articles = manager.scrape_selected(
    #     names=["美國進步中心"],
    # )
    # print(len(articles))
    # save_to_csv(articles, '美國進步中心.csv')

    # articles = manager.scrape_selected(
    #     names=["美國傳統基金會"],
    # )
    # print(len(articles))
    # save_to_csv(articles, '美國傳統基金會.csv')


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

    main()
