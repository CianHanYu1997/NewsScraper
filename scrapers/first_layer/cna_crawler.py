import logging
from typing import Optional
from selenium.webdriver.common.by import By

from scrapers.base import NewsSeleniumFetcher
from strategies.page_load import ScrollPaginationLoadStrategy


logger = logging.getLogger(__name__)


class CNAScraper(NewsSeleniumFetcher):
    def __init__(self):
        # 1. 使用翻頁策略，定位下一頁按鈕
        page_load_strategy = ScrollPaginationLoadStrategy(
            next_button_locator=(
                By.CSS_SELECTOR, "#SiteContent_uiViewMoreBtn"),
        )

        # 2. 初始化父類
        super().__init__(
            page_load_strategy=page_load_strategy
        )

    def get_name(self) -> str:
        return "中央社"

    def get_base_url(self) -> str:
        return "https://www.cna.com.tw/list/aall.aspx"

    def get_default_load_count(self) -> int:
        return -1

    def get_url_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, "#jsMainList a")

    def extract_url(self, element) -> Optional[str]:
        try:
            url = element.get_attribute("href")
            return url

        except Exception as e:
            logger.error(f"提取網址失敗: {e}")
            return None
