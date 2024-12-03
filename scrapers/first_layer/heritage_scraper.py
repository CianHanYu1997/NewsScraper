import logging

from datetime import datetime
from typing import Optional, Type
from selenium.webdriver.common.by import By

from scrapers.base import ThinkTankScraper
from models.article import Article
from models.article_type import (
    BaseArticleType, HeritageThinkTankType)
from strategies.page_load import PaginationLoadStrategy
from strategies.filter import NoFilterStrategy
from url_buliders.thinl_tnak_url import HeritageURLBuilder


logger = logging.getLogger(__name__)


class HeritageScraper(ThinkTankScraper):
    def __init__(self):
        # 1. 創建滾動加載策略
        # 實際上我並沒有點擊按鈕，而是直接用url跳轉
        pagination_strategy = PaginationLoadStrategy(
            next_button_locator=(By.LINK_TEXT, "Next"))

        # 2. 創建 URL 生成策略
        url_builder = HeritageURLBuilder()

        # 3. 初始化父類
        super().__init__(
            page_load_strategy=pagination_strategy,
            url_builder=url_builder,
            filter_strategy=NoFilterStrategy
        )

    def _configure_options(self):
        """重寫配置方法，添加禁用 JavaScript 的設定"""
        # 垃圾網站，一堆問題
        self.options.add_experimental_option(
            "prefs",
            {"profile.managed_default_content_settings.javascript": 2}
        )

    def get_name(self) -> str:
        return "美國傳統基金會"

    def get_base_url(self) -> str:
        return "https://www.heritage.org/china"

    def get_default_load_count(self) -> int:
        return -1

    def get_article_type_enum(self) -> Type[BaseArticleType]:
        return HeritageThinkTankType

    def get_article_elements_locator(self) -> tuple:
        return (By.CSS_SELECTOR, ".views-row")

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
        try:
            # 先檢查是否為 None
            if self._current_article_type is None:
                raise ValueError("Article type沒有進行設置")
            article = Article(
                think_tank_name=self.get_name(),
                article_type=HeritageThinkTankType.get_display_name(
                    self._current_article_type),
                publish_date=self._format_date(
                    element.find_element(
                        By.CSS_SELECTOR, ".result-card__date span").text),
                title=element.find_element(
                    By.CSS_SELECTOR, ".result-card__title").text,
                url=element.find_element(
                    By.CSS_SELECTOR, ".result-card__title")
                .get_attribute("href")
            )
            return article

        except Exception as e:
            logger.error(f"解析文章失敗: {e}")
            return None
