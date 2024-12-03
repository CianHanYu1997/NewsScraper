import logging

from datetime import datetime
from typing import Optional, Type
from selenium.webdriver.common.by import By

from scrapers.base import ThinkTankScraper
from models.article import Article
from models.article_type import (
    BaseArticleType, CFRThinkTankType)
from strategies.page_load import ScrollLoadStrategy
from strategies.filter import NoFilterStrategy
from url_buliders.thinl_tnak_url import CFRURLBuilder


logger = logging.getLogger(__name__)


class CFRScraper(ThinkTankScraper):
    def __init__(self):
        # 1. 創建滾動加載策略
        scroll_strategy = ScrollLoadStrategy(
            scroll_pause_time=5.0, max_scroll_attempts=10)

        # 2. 創建 URL 生成策略
        url_builder = CFRURLBuilder()

        # 3. 初始化父類
        super().__init__(
            page_load_strategy=scroll_strategy,
            url_builder=url_builder,
            filter_strategy=NoFilterStrategy
        )

    def get_name(self) -> str:
        return "外交關係協會"

    def get_base_url(self) -> str:
        return "https://www.cfr.org/asia/china/"

    def get_default_load_count(self) -> int:
        # 對於滾動加載的網站，預設滾動次數
        return 10

    def get_article_type_enum(self) -> Type[BaseArticleType]:
        return CFRThinkTankType

    def get_article_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, ".card-article-large__container")  # noqa:E501

    def _format_date(self, date_str):
        try:
            # 解析原始日期字符串
            date_obj = datetime.strptime(date_str.strip(), '%B %d, %Y')
            # 轉換成需要的格式
            return date_obj.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"日期格式化失敗: {e}")
            return date_str

    def parse_article(self, element) -> Optional[Article]:
        try:
            # 先檢查是否為 None
            if self._current_article_type is None:
                raise ValueError("Article type沒有進行設置")
            return Article(
                think_tank_name=self.get_name(),
                article_type=CFRThinkTankType.get_display_name(
                    self._current_article_type),
                publish_date=self._format_date(
                    element.find_element(
                        By.CSS_SELECTOR, ".card-article-large__date").text),
                title=element.find_element(
                    By.CSS_SELECTOR, ".card-article-large__title").text,
                url=element.find_element(
                    By.CSS_SELECTOR, ".card-article-large__link")
                .get_attribute("href")
            )
        except Exception as e:
            logger.error(f"解析文章失敗: {e}")
            return None
