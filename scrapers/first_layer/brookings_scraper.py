import logging
import re
from datetime import datetime
from typing import Optional, Type
from selenium.webdriver.common.by import By

from scrapers.base import ThinkTankScraper
from models.article import Article
from models.article_type import (
    BaseArticleType, BrookingsThinkTankType)
from strategies.page_load import ScrollPaginationLoadStrategy
from strategies.filter import SingleClickFilterStrategy
from url_buliders.thinl_tnak_url import BrookingsURLBuilder
from utils.logging_config import get_logger

logger = get_logger(__name__)


class BrookingsScraper(ThinkTankScraper):
    """布魯金斯研究所爬蟲"""

    def __init__(
        self,
        headless: bool = True,
    ):
        # 使用翻頁策略，定位下一頁按鈕
        page_load_strategy = ScrollPaginationLoadStrategy(
            next_button_locator=(
                By.CSS_SELECTOR, ".btn-outline-alt"),
            max_result_locator=(By.ID, "results-limiter"),
            max_result=40
        )
        # 使用URL構建器
        url_builder = BrookingsURLBuilder()

        # 進行頁面篩選`，內容為當前的article_type
        filter_strategy = SingleClickFilterStrategy(
            base_selector='input.form-checkbox')

        super().__init__(
            page_load_strategy=page_load_strategy,
            url_builder=url_builder,
            filter_strategy=filter_strategy
        )

    def get_article_type_enum(self) -> Type[BaseArticleType]:
        """返回布魯金斯研究所的文章類型枚舉"""
        return BrookingsThinkTankType

    def get_default_load_count(self) -> int:
        """返回預設加載頁數"""
        return 3

    def get_name(self) -> str:
        """返回智庫名稱"""
        return "布魯金斯研究所"

    def get_base_url(self) -> str:
        """返回基礎URL"""
        return "https://www.brookings.edu/research-commentary/"

    def get_article_elements_locator(self) -> tuple:
        """返回文章元素的定位器"""
        return (By.CSS_SELECTOR, ".ais-InfiniteHits-item")

    def _format_date(self, date_str):
        """
        將日期字符串轉換為標準格式 (YYYY-MM-DD)
        特殊格式如 Fall 2006 或 1996, No. 2 會轉換為該年的1月1日

        Args:
            date_str: 輸入的日期字符串
        Returns:
            格式化後的日期字符串，如果無法解析則返回原始字符串
        """
        try:
            date_str = date_str.strip()

            # 處理 "Fall 2006" 格式
            season_match = re.search(
                r'(Spring|Summer|Fall|Winter)\s+(\d{4})', date_str)
            if season_match:
                year = season_match.group(2)
                return f"{year}-01-01"

            # 處理 "1996, No. 2" 格式
            no_match = re.search(r'(\d{4}),\s*No\.\s*\d+', date_str)
            if no_match:
                year = no_match.group(1)
                return f"{year}-01-01"

            # 處理帶有星期的格式
            if "," in date_str and any(day in date_str for day in [
                    "Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"]):
                date_str = date_str.split(",", 1)[1].strip()

            # 一般日期格式列表
            formats = [
                ('%B %d, %Y', '%Y-%m-%d'),      # March 15, 2022 -> 2022-03-15
                ('%b %d, %Y', '%Y-%m-%d'),      # Mar 15, 2022 -> 2022-03-15
                ('%B %Y', '%Y-%m-%d'),          # March 2022 -> 2022-03-01
                ('%b %Y', '%Y-%m-%d'),          # Mar 2022 -> 2022-03-01
                ('%Y-%m-%d', '%Y-%m-%d'),       # 2022-03-15 -> 2022-03-15
                ('%Y/%m/%d', '%Y-%m-%d'),       # 2022/03/15 -> 2022-03-15
                ('%B, %Y', '%Y-%m-%d'),         # March, 2022 -> 2022-03-15
            ]

            # 嘗試每種格式
            for input_fmt, output_fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, input_fmt)
                    return date_obj.strftime(output_fmt)
                except ValueError:
                    continue

            # 如果無法識別格式，記錄警告並返回原始字符串
            logging.warning(f"無法識別的日期格式: {date_str}")
            return date_str

        except Exception as e:
            logging.error(f"日期格式化失敗: {e}")
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
                    element.find_element(By.CSS_SELECTOR, ".date").text),
                title=element.find_element(
                    By.CSS_SELECTOR, ".sr-only").text,
                url=element.find_element(
                    By.CSS_SELECTOR, ".overlay-link")
                .get_attribute("href")
            )
        except Exception as e:
            logging.error(f"解析文章失敗: {e}")
            return None
