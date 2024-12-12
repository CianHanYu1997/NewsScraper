import logging
from typing import Optional
from selenium.webdriver.common.by import By

from scrapers.base import NewsScraper
from strategies.page_load import ScrollPaginationLoadStrategy


logger = logging.getLogger(__name__)


class MNEWSScraper(NewsScraper):
    def __init__(self):
        # 1. 使用翻頁策略，定位下一頁按鈕
        page_load_strategy = ScrollPaginationLoadStrategy(
            next_button_locator=(
                By.CSS_SELECTOR,
                ".load-more.g-button-load-more.button-load-more"),
            load_page=15
        )

        # 2. 初始化父類
        super().__init__(
            page_load_strategy=page_load_strategy
        )

    def get_name(self) -> str:
        return "鏡新聞"

    def get_base_url(self) -> str:
        return "https://www.mnews.tw/"

    def get_default_load_count(self) -> int:
        return -1

    def get_url_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, ".card")

    def extract_url(self, element) -> Optional[str]:
        try:
            url = element.find_element(
                By.CSS_SELECTOR, "a").get_attribute("href")
            return url

        except Exception as e:
            logger.error(f"提取網址失敗: {e}")
            return None
