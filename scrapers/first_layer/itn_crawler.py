import logging
from typing import Optional
from selenium.webdriver.common.by import By

from scrapers.base import NewsScraper
from strategies.page_load import ScrollLoadStrategy, ScrollType


logger = logging.getLogger(__name__)


class ITNScraper(NewsScraper):
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
        return "自由時報"

    def get_base_url(self) -> str:
        return "https://news.ltn.com.tw/list/breakingnews"

    def get_default_load_count(self) -> int:
        return -1

    def get_url_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, ".tit")

    def extract_url(self, element) -> Optional[str]:
        try:
            url = element.get_attribute("href")
            return url

        except Exception as e:
            logger.error(f"提取網址失敗: {e}")
            return None
