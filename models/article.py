from pydantic import BaseModel
from typing import List
from datetime import datetime


class News(BaseModel):
    """通用新聞數據結構"""
    media_name: str
    journal_name: str
    coverage: str
    publish_date: datetime
    category: str
    title: str
    description: str
    keywords: List[str]
    url: str


# 不使用，只返回urls列表
# class NewsURLs(BaseModel):
#     """新聞網址"""
#     media_name: str
#     title: str
#     url: str
