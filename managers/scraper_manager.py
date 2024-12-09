from typing import List, Optional, Dict, Union
from scrapers.base import NewsScraper
import logging

logger = logging.getLogger(__name__)


class ScraperManager:
    def __init__(
        self,
    ):
        self.scrapers: Dict[str, NewsScraper] = {}

    def register_scraper(self, scraper: NewsScraper):
        """註冊爬蟲"""
        self.scrapers[scraper.get_name()] = scraper

    def scrape_all(
            self,
            article_types: Optional[Dict[str, Union[str, List[str]]]] = None,
            load_counts: Optional[Dict[str, int]] = None) -> List[str]:
        """
        執行所有註冊的爬蟲
        Args:
            article_types: 字典，鍵為爬蟲名稱，值為要爬取的文章類型或列表，None為爬取全部文章類型
            load_counts: 字典，鍵為爬蟲名稱，值為加載次數
        """
        article_types = article_types or {}
        load_counts = load_counts or {}
        all_articles = []

        for name, scraper in self.scrapers.items():
            logger.info(f"開始爬取 {name}")
            try:
                # 獲取要爬取的類型列表
                types_to_scrape = article_types.get(name)
                # 確保類型是列表形式
                if isinstance(types_to_scrape, str):
                    types_to_scrape = [types_to_scrape]
                elif types_to_scrape is None:
                    types_to_scrape = self.get_supported_types(name)  # 預設使用全部

                load_count = load_counts.get(name)
                supported_types = self.get_supported_types(name)

                # 對每個類型執行爬蟲
                for article_type in types_to_scrape:
                    # 驗證文章類型
                    if article_type and article_type not in supported_types:
                        logger.warning(
                            f"爬蟲 {name} 不支持文章類型 {article_type}，跳過此類型"
                        )
                        continue

                    logger.info(f"爬取 {name} 的 {article_type} 類型文章")
                    articles = scraper.fetch_articles(
                        article_type=article_type,
                        load_count=load_count
                    )
                    all_articles.extend(articles)

            except Exception as e:
                logger.error(f"爬取 {name} 時發生錯誤: {str(e)}")
                continue

        return all_articles

    async def scrape_selected(
            self,
            names: List[str],
            load_count: Optional[int] = None
    ) -> List[str]:
        """
        執行選定的爬蟲
        Args:
            names: 要執行的爬蟲名稱列表
            load_counts: 加載次數
        """
        for name in names:
            if name not in self.scrapers:
                logger.warning(f"找不到爬蟲: {name}")
                continue

            logger.info(f"開始爬取 {name}")
            try:
                scraper = self.scrapers[name]
                urls = await scraper.fetch_urls(load_count)

            except Exception as e:
                logger.error(f"爬取 {name} 時發生錯誤: {str(e)}")
                continue

        return urls
