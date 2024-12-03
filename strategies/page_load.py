import logging
import random
from abc import ABC, abstractmethod
from typing import Optional
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException)
import time

logger = logging.getLogger(__name__)


class PageLoadStrategy(ABC):
    """頁面加載策略的抽象基類"""

    @abstractmethod
    def load_more_content(
            self, driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
        """加載更多內容
        Returns:
            bool: 是否成功加載更多內容
        """
        pass


class ScrollLoadStrategy(PageLoadStrategy):
    """滾動加載策略"""

    def __init__(
            self,
            scroll_pause_time: float = 2.0):
        # 設置每次滾動後等待的時間，讓新內容有時間加載
        self.scroll_pause_time = scroll_pause_time

    def load_more_content(
            self, driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
        # 獲取當前頁面高度
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        same_high_count = 0

        # 設置最大嘗試次數，防止異常情況
        max_attempts = 100
        attempts = 1

        while attempts < max_attempts:
            # 1. 滾動到頁面底部
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # 2. 等待新內容加載
            time.sleep(self.scroll_pause_time)

            # 3. 計算新的頁面高度
            new_height = driver.execute_script(
                "return document.body.scrollHeight")

            # 4. 如果高度沒變，表示沒有新內容了
            if new_height == last_height:
                same_high_count += 1
                # 如果連續三次高度沒有變化，認為已到達底部
                if same_high_count >= 1:
                    return False
            else:
                same_high_count = 0

            # 5. 更新高度並繼續下一次滾動
            last_height = new_height
            attempts += 1

        return True


class PaginationLoadStrategy(PageLoadStrategy):
    """翻頁加載策略"""

    def __init__(self, next_button_locator: tuple):
        self.next_button_locator = next_button_locator

    def load_more_content(self, driver: webdriver.Chrome,
                          wait: WebDriverWait) -> bool:
        try:
            time.sleep(5)  # 等待2秒

            next_button = wait.until(
                EC.element_to_be_clickable(self.next_button_locator))
            # # 2. 等到按鈕出現
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", next_button)

            driver.execute_script("arguments[0].click();", next_button)
            # next_button.click()

            time.sleep(2)  # 給頁面一點時間讀取
            return True
        except Exception as e:
            logger.info(f"翻頁失敗: {e}")
            return False


class ScrollPaginationLoadStrategy(PageLoadStrategy):
    """滾動搭配翻頁加載策略，能處理Show More 按鈕"""

    def __init__(
            self,
            next_button_locator: tuple,
            max_result_locator: Optional[tuple] = None,
            max_result: int = 20):
        self.next_button_locator = next_button_locator
        self.max_result_locator = max_result_locator
        self.max_result = max_result

    def random_sleep(self):
        """生成自然的隨機延遲"""
        # 基礎延遲
        base_delay = 2
        # 隨機偏移量（-30% 到 +30%）
        random_offset = random.uniform(-0.3, 0.3) * base_delay
        delay = base_delay + random_offset
        time.sleep(max(0.5, delay))  # 確保至少休眠0.5秒

    def load_more_content(
            self,
            driver: webdriver.Chrome,
            wait: WebDriverWait) -> bool:
        try:
            scroll_attempts = 0
            while True:
                # 1. 獲取當前頁面高度
                last_height = driver.execute_script(
                    "return document.body.scrollHeight")

                # 2. 滾動到頁面底部
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                self.random_sleep()  # 給滾動一個短暫的緩衝時間

                try:
                    # 3. 尋找 Show More
                    show_more_button = wait.until(
                        EC.element_to_be_clickable(self.next_button_locator))

                    # 4. 處理最大筆數選項（如果有設定）
                    if self.max_result_locator and scroll_attempts == 0:
                        try:
                            max_result_select = wait.until(
                                EC.element_to_be_clickable(
                                    self.max_result_locator))
                            select = Select(max_result_select)
                            select.select_by_value(str(self.max_result))
                            max_result_select.click()
                            self.random_sleep()  # 給一點時間讓選項生效
                        except TimeoutException:
                            logger.info("未找到最大筆數選擇器，將繼續使用Show More按鈕加載")

                    # 5. 滾動到按鈕位置並點擊
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", show_more_button)
                    time.sleep(2)  # 給頁面一些時間來響應滾動

                    # 嘗試點擊按鈕，如果按鈕變為不可點擊或消失則結束
                    try:
                        show_more_button.click()
                    except (ElementClickInterceptedException,
                            StaleElementReferenceException):
                        driver.execute_script(
                            "arguments[0].click();", show_more_button)

                    self.random_sleep()

                    # 6. 檢查頁面是否有新內容加載
                    new_height = driver.execute_script(
                        "return document.body.scrollHeight")
                    if new_height == last_height:
                        logger.info("頁面高度未變化，已到達底部")
                        return False
                    scroll_attempts += 1

                    logger.info(f"目前已進入第 {scroll_attempts+1} 頁")

                except TimeoutException:
                    logger.info("已達頁面底部: 等待按鈕超時")
                    return True

        except Exception:
            logger.info("未找到Show More按鈕")
            return False
