import logging
from typing import Optional
from selenium.webdriver.common.by import By

from scrapers.base import NewsSeleniumFetcher
from strategies.page_load import ScrollLoadStrategy, ScrollType

logger = logging.getLogger(__name__)


class ETtodayScraper(NewsSeleniumFetcher):
    def __init__(self):
        # 1. 創建滾動加載策略
        page_load_strategy = ScrollLoadStrategy(
            scroll_type=ScrollType.SMOOTH,
            smooth_scroll_distance=2500)

        # 2. 初始化父類
        super().__init__(
            page_load_strategy=page_load_strategy
        )

    def get_name(self) -> str:
        return "ettoday"

    def get_base_url(self) -> str:
        return "https://www.ettoday.net/news/news-list.htm"

    def get_default_load_count(self) -> int:
        return -1

    def get_url_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, ".part_list_2 a")

    def extract_url(self, element) -> Optional[str]:
        try:
            url = element.get_attribute("href")
            return url

        except Exception as e:
            logger.error(f"提取網址失敗: {e}")
            return None
