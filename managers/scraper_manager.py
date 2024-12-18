from typing import List, Optional, Dict
from scrapers.base import NewsSeleniumFetcher
import logging
import asyncio

logger = logging.getLogger(__name__)


class ScraperManager:
    def __init__(
        self,
    ):
        self.scrapers: Dict[str, NewsSeleniumFetcher] = {}

    def register_scraper(self, scraper: NewsSeleniumFetcher):
        """註冊爬蟲"""
        self.scrapers[scraper.get_name()] = scraper

    async def scrape_all(
            self,
            load_counts: Optional[Dict[str, int]] = None
    ) -> List[str]:
        """
        執行所有註冊的爬蟲
        Args:
            load_counts: 各爬蟲的加載次數字典 {爬蟲名稱: 加載次數}
        """
        load_counts = load_counts or {}
        tasks = []
        # 創建每個爬蟲任務
        for name, scraper in self.scrapers.items():
            logger.info(f"開始爬取 {name}")
            load_count = load_counts.get(name)
            # 調用異步函數不執行, 返回協程對象
            tasks.append(scraper.fetch_urls(load_count=load_count))

        # 使用gather，並行執行多個協程(任務)
        # return_exceptions=True 表示如果某個任務出錯，不會影響其他任務的執行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_urls: List[str] = []
        for name, result in zip(self.scrapers.keys(), results):
            if isinstance(result, Exception):
                logger.error(f'爬取 {name} 時發生錯誤: {str(result)}')
            all_urls.extend(result)  # type: ignore

        return all_urls

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
