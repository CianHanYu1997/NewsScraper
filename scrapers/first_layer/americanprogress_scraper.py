import logging
from datetime import datetime
from typing import Optional, Type
from selenium.webdriver.common.by import By

from scrapers.base import ThinkTankScraper
from models.article import Article
from models.article_type import (
    BaseArticleType, AmericanProgressThinkTankType)
from strategies.page_load import ScrollPaginationLoadStrategy
from strategies.filter import NoFilterStrategy
from url_buliders.thinl_tnak_url import AmericanProgressURLBuilder
from utils.logging_config import get_logger

logger = get_logger(__name__)


class AmericanProgressScraper(ThinkTankScraper):
    """美國進步中心爬蟲"""

    def __init__(
        self,
        headless: bool = True,
    ):
        # 使用翻頁策略，定位下一頁按鈕
        page_load_strategy = ScrollPaginationLoadStrategy(
            next_button_locator=(
                By.CSS_SELECTOR, ".stream1-more .button1"),
        )
        # 使用URL構建器
        url_builder = AmericanProgressURLBuilder()

        # 不進行頁面點擊篩選
        filter_strategy = NoFilterStrategy()

        super().__init__(
            page_load_strategy=page_load_strategy,
            url_builder=url_builder,
            filter_strategy=filter_strategy
        )

    def get_article_type_enum(self) -> Type[BaseArticleType]:
        """返回美國進步中心的文章類型枚舉"""
        return AmericanProgressThinkTankType

    def get_default_load_count(self) -> int:
        """返回預設加載頁數"""
        return -1

    def get_name(self) -> str:
        """返回智庫名稱"""
        return "美國進步中心"

    def get_base_url(self) -> str:
        """返回基礎URL"""
        return "https://www.americanprogress.org/"

    def get_article_elements_locator(self) -> tuple:
        """返回文章元素的定位器"""
        return (
            By.XPATH,
            "//article[contains(@class, 'card2') and "
            "contains(@class, '-v2') and "
            "contains(@class, '-sep')]//span[contains(text(), "
            f"'{self._current_article_type}')]/ancestor::article"
        )

    def _format_date(self, date_str):
        try:
            # 解析原始日期字符串
            date_obj = datetime.strptime(date_str.strip(), '%b %d, %Y')
            # 轉換成需要的格式
            return date_obj.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"日期格式化失敗: {e}")
            return date_str

    def parse_article(self, element) -> Optional[Article]:
        """解析單個文章元素

        Args:
            element: WebElement 文章元素

        Returns:
            Article: 解析後的文章對象，如果解析失敗返回None
        """
        try:
            # 先檢查是否為 None
            if self._current_article_type is None:
                raise ValueError("Article type沒有進行設置")

            return Article(
                think_tank_name=self.get_name(),
                article_type=self._current_article_type,  # 從元素中獲取文章類型
                publish_date=self._format_date(
                    element.find_element
                    (By.CSS_SELECTOR, ".card2-meta time").text),
                title=element.find_element(
                    By.CSS_SELECTOR, "a.card2-link").text,
                url=element.find_element(
                    By.CSS_SELECTOR, "a.card2-link")
                .get_attribute("href")
            )
        except Exception as e:
            logging.error(f"解析文章失敗: {e}")
            return None
