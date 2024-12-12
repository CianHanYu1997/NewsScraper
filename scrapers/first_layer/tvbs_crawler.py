import logging
from typing import Optional
from selenium.webdriver.common.by import By

from scrapers.base import NewsScraper
from strategies.page_load import ScrollLoadStrategy, ScrollType


logger = logging.getLogger(__name__)


class TVBSScraper(NewsScraper):
    def __init__(self):
        # 1. 創建滾動加載策略
        page_load_strategy = ScrollLoadStrategy(
            scroll_type=ScrollType.DIRECT
        )

        # 2. 初始化父類
        super().__init__(
            page_load_strategy=page_load_strategy
        )

    def get_name(self) -> str:
        return "TVBS"

    def get_base_url(self) -> str:
        return "https://news.tvbs.com.tw/realtime"

    def get_default_load_count(self) -> int:
        return -1

    def get_url_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, ".news_list .list li")

    def extract_url(self, element) -> Optional[str]:
        try:
            url = element.find_elements(
                By.CSS_SELECTOR, "a")[0].get_attribute("href")
            return url

        except Exception as e:
            logger.error(f"提取網址失敗: {e}")
            return None
