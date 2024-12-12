import logging
import random
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException)
import time

logger = logging.getLogger(__name__)


class PageLoadStrategy(ABC):
    """頁面加載策略的抽象基類"""

    @abstractmethod
    async def load_more_content(
            self, driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
        """加載更多內容
        Returns:
            bool: 是否成功加載更多內容
        """
        pass


class ScrollType(Enum):
    SMOOTH = "smooth"
    DIRECT = "direct"
    BOTH = "both"


class ScrollLoadStrategy(PageLoadStrategy):
    """滾動加載策略"""

    def __init__(
            self,
            scroll_type: ScrollType = ScrollType.DIRECT,
            smooth_scroll_distance: int = 3000,
            scroll_pause_time: float = 2.0):
        # 設置每次滾動後等待的時間，讓新內容有時間加載
        self.scroll_type = scroll_type
        self.smooth_scroll_distance = smooth_scroll_distance
        self.scroll_pause_time = scroll_pause_time

    async def load_more_content(
            self, driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
        # 獲取當前頁面高度
        last_height = await asyncio.to_thread(
            lambda: driver.execute_script("return document.body.scrollHeight")
        )

        same_high_count = 0

        # 設置最大嘗試次數，防止異常情況
        max_attempts = 100
        attempts = 1

        while attempts < max_attempts:
            # 根據滾動類型執行相應的滾動操作
            if self.scroll_type == ScrollType.SMOOTH:
                await self._smooth_scroll(driver, self.smooth_scroll_distance)
            elif self.scroll_type == ScrollType.DIRECT:
                await self._scroll_to_bottom(driver)
            else:  # ScrollType.BOTH
                await self._smooth_scroll(driver, self.smooth_scroll_distance)
                await asyncio.sleep(0.5)  # 短暫停頓
                await self._scroll_to_bottom(driver)

            # 等待新內容加載
            await asyncio.sleep(self.scroll_pause_time)

            # 計算新的頁面高度
            new_height = await asyncio.to_thread(
                lambda: driver.execute_script(
                    "return document.body.scrollHeight")
            )

            # 檢查是否到達底部
            if new_height == last_height:
                same_high_count += 1
                if same_high_count >= 1:
                    return False
            else:
                same_high_count = 0

            last_height = new_height
            attempts += 1

        return True

    async def _smooth_scroll(self, driver: webdriver.Chrome, distance: int):
        """平滑滾動指定距離"""
        await asyncio.to_thread(
            lambda: driver.execute_script("""
                window.scrollBy({
                    top: arguments[0],
                    behavior: 'smooth'
                });
            """, distance)
        )

    async def _scroll_to_bottom(self, driver: webdriver.Chrome):
        """直接滾動到底部"""
        await asyncio.to_thread(
            lambda: driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
        )


class PaginationLoadStrategy(PageLoadStrategy):
    """翻頁加載策略"""

    def __init__(self, next_button_locator: tuple):
        self.next_button_locator = next_button_locator

    async def load_more_content(self, driver: webdriver.Chrome,
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
            load_page: int = 100,
            max_result_locator: Optional[tuple] = None,
            max_result: int = 20):
        self.next_button_locator = next_button_locator
        self.load_page = load_page
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

    async def load_more_content(
            self,
            driver: webdriver.Chrome,
            wait: WebDriverWait,
            max_retries: int = 3) -> bool:
        try:
            scroll_attempts = 1
            # 設置最大嘗試次數，防止異常情況
            max_attempts = 100
            while scroll_attempts < min(self.load_page, max_attempts):
                # 1. 獲取當前頁面高度
                last_height = await asyncio.to_thread(
                    lambda: driver.execute_script(
                        "return document.body.scrollHeight")
                )

                # 2. 滾動到頁面底部
                await asyncio.to_thread(
                    lambda: driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                )
                await self._async_random_sleep()  # 給滾動一個短暫的緩衝時間

                try:
                    # 3. 尋找 Show More
                    show_more_button = await asyncio.to_thread(
                        lambda: wait.until(
                            EC.element_to_be_clickable(
                                self.next_button_locator)
                        )
                    )

                    # # 4. 處理最大筆數選項（如果有設定）
                    # if self.max_result_locator and scroll_attempts == 0:
                    #     try:
                    #         max_result_select = wait.until(
                    #             EC.element_to_be_clickable(
                    #                 self.max_result_locator))
                    #         select = Select(max_result_select)
                    #         select.select_by_value(str(self.max_result))
                    #         max_result_select.click()
                    #         self.random_sleep()  # 給一點時間讓選項生效
                    #     except TimeoutException:
                    #         logger.info("未找到最大筆數選擇器，將繼續使用Show More按鈕加載")

                    # 5. 滾動到按鈕位置並點擊
                    await asyncio.to_thread(
                        lambda: driver.execute_script(
                            "arguments[0].scrollIntoView(true);",
                            show_more_button
                        )
                    )
                    await asyncio.sleep(2)  # 給頁面一些時間來響應滾動

                    # 使用重試機制處理按鈕點擊
                    success = await self._retry_click_button(
                        driver,
                        show_more_button,
                        max_retries
                    )
                    if not success:
                        logger.warning("無法點擊Show More按鈕")
                        return False

                    await self._async_random_sleep()

                    # 6. 檢查頁面是否有新內容加載
                    new_height = await asyncio.to_thread(
                        lambda: driver.execute_script(
                            "return document.body.scrollHeight"
                        )
                    )
                    if new_height == last_height:
                        logger.info("頁面高度未變化，已到達底部")
                        return False

                    scroll_attempts += 1
                    logger.info(f"目前已進入第 {scroll_attempts} 頁")

                except TimeoutException:
                    logger.info("已達頁面底部: 等待按鈕超時")
                    return True
            return False
        except Exception:
            logger.info("未找到Show More按鈕")
            return False

    async def _async_random_sleep(
            self,
            min_time: float = 1,
            max_time: float = 3):
        """異步隨機休眠"""
        sleep_time = random.uniform(min_time, max_time)
        await asyncio.sleep(sleep_time)

    async def _retry_click_button(
        self,
        driver,
        button: WebElement,
        max_retries: int
    ) -> bool:
        """重試按鈕點擊的輔助方法"""
        for attempt in range(max_retries):
            try:
                # 方法1: 使用 Selenium 的普通點擊方法
                await asyncio.to_thread(lambda: button.click())
                return True
            # 捕獲兩種特定的點擊異常：
            # - ElementClickInterceptedException: 元素被其他元素遮擋
            # - StaleElementReferenceException: 元素已經過期（頁面更新了）
            except (ElementClickInterceptedException,
                    StaleElementReferenceException):
                try:
                    # 方法2: 使用 JavaScript 來點擊
                    await asyncio.to_thread(
                        lambda: driver.execute_script(
                            "arguments[0].click();",
                            button
                        )
                    )
                    return True
                # 如果連 JavaScript 點擊也失敗
                except Exception:
                    if attempt == max_retries - 1:
                        return False
                    await asyncio.sleep(1)  # 重試前等待
                    continue
        return False
