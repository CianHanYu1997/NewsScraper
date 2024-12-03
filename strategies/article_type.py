from abc import ABC, abstractmethod


class ArticleTypeStrategy(ABC):
    """文章類型策略的抽象基類"""

    @abstractmethod
    def get_article_type_url(self, base_url: str, article_type: str) -> str:
        """獲取特定類型文章的URL"""
        pass


class FilterBasedTypeStrategy(ArticleTypeStrategy):
    """基於頁面篩選的文章類型策略"""

    def __init__(self, filter_locator: tuple):
        """
        Args:
            filter_locator: 篩選器的定位元組
        """
        self.filter_locator = filter_locator

    def get_article_type_url(self, base_url: str, article_type: str) -> str:
        return base_url
