from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Union, Callable
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
import logging

logger = logging.getLogger(__name__)


@dataclass
class URLParameters:
    """URL參數配置"""
    base_url: str
    search_params: Dict[str, str] = field(default_factory=dict)
    filter_params: Dict[str, str] = field(default_factory=dict)
    type_param_key: Optional[str] = None
    type_param_format: Optional[Union[str, Callable]] = None
    page_param_key: Optional[str] = None
    page_param_format: Optional[Union[str, Callable]] = None
    extra_params: Dict[str, str] = field(default_factory=dict)
    show_first_page_param: bool = False


class URLBuilder(ABC):
    """URL構建器的抽象基類"""

    @abstractmethod
    def build_url(self,
                  article_type: Optional[str] = None,
                  page: Optional[int] = None) -> str:
        """構建完整的URL"""
        pass


class BaseURLBuilder(URLBuilder):
    """通用的URL構建器"""

    def __init__(self, url_config: URLParameters):
        self.config = url_config
        self.logger = logging.getLogger(self.__class__.__name__)

    def _merge_params(self, *param_dicts) -> Dict[str, str]:
        """合併多個參數字典，過濾掉None值"""
        merged = {}
        for d in param_dicts:
            if d:
                # 過濾掉值為None的項
                filtered = {k: v for k, v in d.items() if v is not None}
                merged.update(filtered)
        return merged

    def _format_type_param(self, article_type: Optional[str]
                           ) -> Dict[str, str]:
        """
        格式化文章類型參數
        Returns:
            Dict[str, str]: 格式化後的參數字典，如果無法格式化則返回空字典
        """
        try:
            # 如果沒有文章類型或參數鍵，返回空字典
            if not article_type or not self.config.type_param_key:
                return {}

            # 根據配置決定如何格式化值
            if callable(self.config.type_param_format):
                # 如果是函數，調用它
                value = self.config.type_param_format(article_type)
            elif self.config.type_param_format:
                # 如果是字串模板，使用format方法
                value = self.config.type_param_format.format(type=article_type)
            else:
                value = article_type

            return {self.config.type_param_key: value}

        except Exception as e:
            self.logger.warning(
                f"格式化文章類型參數時出錯 (type={article_type}): {str(e)}"
            )
            return {}

    def _format_page_param(self, page: Optional[int]) -> Dict[str, str]:
        """
        格式化分頁參數。

        Args:
            page: 頁碼，如果為None則返回空字典

        Returns:
            Dict[str, str]: 格式化後的參數字典
                - 如果頁碼為None，返回空字典
                - 如果是第一頁且設定不顯示第一頁參數，返回空字典
                - 如果格式化出錯，返回空字典

        Examples:
            >>> builder._format_page_param(1)
            {'page': '1'}
            >>> builder._format_page_param(0)  # show_first_page_param=False
            {}
        """
        if any([
            page is None,
            not self.config.page_param_key,
            page == 0 and not self.config.show_first_page_param
        ]):
            return {}
        try:
            # 確保 page_param_key 不為 None (雖然前面已經檢查過了)
            if not self.config.page_param_key:
                return {}

            if callable(self.config.page_param_format):
                value = str(self.config.page_param_format(page))
            elif self.config.page_param_format:
                value = str(self.config.page_param_format.format(page=page))
            else:
                value = str(page)

            return {self.config.page_param_key: value}

        except Exception as e:
            self.logger.warning(
                f"格式化分頁參數時出錯 (page={page}): {str(e)}"
            )
            return {}

    def build_url(self,
                  article_type: Optional[str] = None,
                  page: Optional[int] = None) -> str:
        """
        構建完整的URL
        即使參數格式化失敗也會返回基礎URL
        """
        try:
            # 解析基礎URL
            parsed_url = urlparse(self.config.base_url)
            # 獲取現有的查詢參數
            existing_params = parse_qs(parsed_url.query)

            # 合併所有參數
            all_params = self._merge_params(
                existing_params,                        # URL中原有的參數
                self.config.search_params,              # 搜尋參數
                self.config.filter_params,              # 過濾參數
                self._format_type_param(article_type),  # 文章類型參數
                self._format_page_param(page),          # 分頁參數
                self.config.extra_params                # 額外參數
            )

            # 重建URL
            return urlunparse((
                parsed_url.scheme,                      # http/https
                parsed_url.netloc,                      # 域名
                parsed_url.path,                        # 路徑
                parsed_url.params,                      # 參數
                urlencode(all_params, doseq=True),      # 查詢字串
                parsed_url.fragment                     # 錨點
            ))

        except Exception as e:
            self.logger.error(f"構建URL時出錯: {str(e)}")
            return self.config.base_url  # 返回基礎URL作為後備
