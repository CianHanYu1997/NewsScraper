from abc import ABC, abstractmethod
from typing import Optional, List
import time
import logging

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

from strategies.page_load import (
    PageLoadStrategy, ScrollLoadStrategy, PaginationLoadStrategy,
    ScrollPaginationLoadStrategy)
from url_buliders.base import BaseURLBuilder

logger = logging.getLogger(__name__)


class NewsScraper(ABC):
    """智庫爬蟲基類"""

    def __init__(
        self,
        headless: bool = True,
        page_load_strategy: Optional[PageLoadStrategy] = None,
        url_builder: Optional[BaseURLBuilder] = None,
    ):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')

        # 調用配置方法
        self._configure_options()

        self.driver = None
        self.wait = None
        self.page_load_strategy = page_load_strategy
        self.url_builder = url_builder

    def start_driver(self):
        """初始化 WebDriver"""
        try:
            if self.driver is None:
                # 添加請求頭
                self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')  # noqa
                # 使用驅動實例開啟會話
                self.driver = webdriver.Chrome(options=self.options)
                self.wait = WebDriverWait(
                    self.driver, timeout=10, poll_frequency=2)  # 設置輪詢時間為2秒
        except Exception as e:
            raise Exception(f"Driver 初始化失敗: {str(e)}")

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

    def _configure_options(self):
        """配置 Chrome 選項的鉤子方法，子類可以重寫此方法來添加特定配置"""
        pass

    @abstractmethod
    def get_default_load_count(self) -> int:
        """返回此智庫建議的預設加載次數"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """返回智庫名稱"""
        pass

    @abstractmethod
    def get_base_url(self) -> str:
        """返回智庫網站的基礎URL"""
        pass

    @abstractmethod
    def get_url_elements_locator(self) -> tuple:
        """返回url元素的定位器"""
        pass

    @abstractmethod
    def extract_url(self, element: WebElement) -> Optional[str]:
        """提取單筆url"""
        pass

    def get_url(
            self,
            url_type: Optional[str] = None,
            page: Optional[int] = None
    ) -> str:
        """獲取目標URL"""
        if self.url_builder:
            return self.url_builder.build_url(page=page)
        return self.get_base_url()  # 如果沒有URL構建器，返回基礎URL

    def fetch_urls(
            self,
            load_count: Optional[int] = None
    ) -> List[str]:
        """
        獲取報導url
        Args:
            load_count: 加載次數（可選），如果不指定則使用 get_default_load_count 的值
        """
        default_count = self.get_default_load_count()
        max_loads = load_count if load_count is not None else default_count
        all_urls: List[str] = []
        current_load = 0  # 當前加載次數計數器

        try:
            self.start_driver()

            # 1. 確保 driver 已經初始化
            if self.driver is None:
                raise Exception("WebDriver 未正確初始化")

            # 2. 找到爬取網址
            initial_url = self.get_url(page=current_load)
            logger.info(f'當前網址:{initial_url}')
            self.driver.get(initial_url)

            while (max_loads == -1 or current_load+1 <= max_loads):
                logger.info(
                    f"爬取 {self.get_name()} - 載入頁數 {current_load + 1}")

                # 3. 等待指定元素出現
                try:
                    url_elements = self.wait.until(
                        EC.presence_of_all_elements_located(
                            self.get_url_elements_locator()
                        )
                    )
                    logger.info(f'總共找到:{len(url_elements)}筆相關元素')

                except TimeoutException:
                    logger.info(f"等待元素超時，已到達最後一頁，共載入 {current_load + 1} 頁")
                    break

                except Exception as e:
                    logger.error(f"頁面載入發生意外錯誤: {e}")
                    break

                # 設置標誌，用於追蹤是否找到新報導
                new_urls_found = False
                for element in url_elements:
                    try:
                        # 提取單個報導元素
                        url = self.extract_url(element)
                        if url and url not in all_urls:
                            all_urls.append(url)
                            # 設置標誌為True，表示找到了新報導
                            new_urls_found = True
                    except Exception as e:
                        logger.error(f"網站爬取失敗: {e}")
                        continue

                if not new_urls_found:
                    logger.info("沒有找到新報導, 停止爬取該網頁...")
                    break

                logger.info(f'目前找到的內容:{all_urls}')

                # 判斷頁面加載策略類型
                if self.page_load_strategy:
                    # 滾動頁面
                    if isinstance(self.page_load_strategy, ScrollLoadStrategy):
                        logger.info("滾動加載策略...")
                        if not self.page_load_strategy.load_more_content(
                                self.driver, self.wait):
                            logger.info("滾動到底部，沒有更多內容可加載...")

                    # 分頁頁面
                    elif isinstance(self.page_load_strategy, PaginationLoadStrategy):  # noqa:E501
                        current_load += 1
                        new_url = self.get_url(page=current_load+1)
                        self.driver.get(new_url)
                        logger.info(f'準備爬取:{new_url}')
                        time.sleep(3)  # 給頁面一點時間讀取

                    # 滾動點擊show more頁面
                    elif isinstance(self.page_load_strategy, ScrollPaginationLoadStrategy):  # noqa:E501
                        logger.info("滾動點擊show more加載策略...")
                        if not self.page_load_strategy.load_more_content(
                                self.driver, self.wait):
                            logger.info("滾動到底部，沒有更多內容可加載...")

                    else:
                        logger.warning("未知的頁面加載策略類型")
                        break
                else:
                    logger.info("沒有設置頁面加載策略，僅爬取單頁")
                    break

        except Exception as e:
            logger.error(f"錯誤| 爬取 {self.get_name()} 中發生錯誤: {str(e)}")

        finally:
            self.close_driver()

        return all_urls
