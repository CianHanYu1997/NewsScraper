import json
import logging
from typing import Dict
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base import NewsHTTPFetcher
from models.article import News

logger = logging.getLogger(__name__)


class SetnHTTPFetcher(NewsHTTPFetcher):
    """三立新聞網 HTTP 爬蟲實作"""

    def parse_metadata(self, soup: BeautifulSoup) -> Dict:
        """解析所有需要的 meta 資料"""
        metadata: Dict[str, str] = {}

        try:
            meta_tags = soup.find_all('meta', attrs={'name': True})
            if not meta_tags:
                return metadata

            # 需要找的meta標籤名稱
            target_names = ['keywords', 'Description', 'Title', 'section']

            for meta_tag in meta_tags:
                name = meta_tag.get('name')
                if name in target_names:
                    metadata[name] = meta_tag.get('content', '')

        except Exception as e:
            logger.error(f"無法解析 meta 資料 : {e}")

        return metadata

    def parse_json_ld(self, soup: BeautifulSoup) -> Dict:
        """解析 JSON-LD 數據"""
        json_ld = {}

        try:
            scripts = soup.find_all('script', type='application/ld+json')

            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'NewsArticle':  # noqa
                        json_ld.update(data)
                except json.JSONDecodeError:
                    logger.warning(f"無法解析 JSON-LD: {script.string}")
                    continue

        except Exception as e:
            logger.error(f"無法解析 JSON-LD : {e}")

        return json_ld

    def parse_html(self, soup: BeautifulSoup) -> dict:
        """從 HTML 結構中解析新聞資訊"""
        html_data = {}

        try:
            # 找到時間區塊
            time_div = soup.find('div', class_='newsPage newsTime printdiv')
            if time_div:
                time_tag = time_div.find('time')
                if time_tag:
                    html_data['publish_date'] = time_tag.text.strip()  # type:ignore # noqa

            # 找到新聞內容區塊
            news_div = soup.find('div', id='ckuse', class_='newsCon')
            if news_div:
                # 解析日期
                time_tag = news_div.find('time', class_='pageDate')  # type:ignore # noqa
                if time_tag and 'publish_date' not in html_data:
                    html_data['publish_date'] = time_tag.text.strip()  # type:ignore # noqa

                # 解析記者和地區資訊
                reporter_text = news_div.find('p')
                if reporter_text:
                    text = reporter_text.text.strip()  # type:ignore

                    # 解析記者名字
                    if '記者' in text:
                        reporter = text.split('／')[0].replace('記者', '').strip()
                        html_data['author'] = reporter
                    elif '報導' in text and 'author' not in html_data:
                        reporter = text.split('／')[1].replace('報導', '').strip()
                        html_data['author'] = reporter

                    # 解析地區
                    if '／' in text:
                        coverage = text.split('／')[1].replace('報導', '').strip()
                        html_data['coverage'] = coverage

        except Exception as e:
            logger.info(f"無法解析 HTML : {e}")

        return html_data

    def transform_to_news(self, json_ld: dict, metadata: dict, html_data: dict, url: str) -> News:  # noqa
        """將解析的數據轉換為 News 物件"""
        # 提取資料
        title = (json_ld.get('headline') or
                 metadata.get('Title', ''))

        author = (json_ld.get('author', {}).get('name') or
                  html_data.get('author', ''))

        raw_publish_date = (json_ld.get('datePublished') or
                            html_data.get('publish_date', ''))

        category = (json_ld.get('articleSection') or
                    metadata.get('section') or
                    self._get_category(title))

        description = (json_ld.get('description',) or
                       metadata.get('Description', ''))

        coverage = (
            (
                self._get_tw_coverage(description)
                if category not in ['國際', '兩岸(大陸)']
                else self._get_intl_coverage(description)
            )
            or html_data.get('coverage', '')
        )

        raw_keywords = (json_ld.get('keywords') or
                        metadata.get('keywords'))

        # 處理發布日期和關鍵字格式
        publish_date = self._parse_date(raw_publish_date)
        keywords = self._parse_keywords(raw_keywords)

        return News(
            media_name='三立新聞網',
            title=title,
            author=author,
            coverage=coverage,
            publish_date=publish_date,
            category=category,
            description=description,
            keywords=keywords,
            url=url
        )

    def _get_category(self, title: str) -> str:
        """從標題提取報導類別"""
        categories = ['健康']
        for category in categories:
            if category in title:
                return category
        return '未分類'

    def _parse_date(self, date_str: str) -> datetime:  # type: ignore
        try:
            # 處理 ISO 格式 (2024-12-18T19:15:00+00:00)
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

            # 處理包含 '/' 的格式 (2024/12/18 19:22)
            elif '/' in date_str:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M')

            # 處理包含 '-' 的格式 (2024-12-19 21:38)
            elif '-' in date_str:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M')

        except ValueError as e:
            logger.error(f"無法解析日期 {date_str}: {e}")
            return datetime.now()

    def _parse_keywords(self, raw_keywords: str | list | None) -> list:
        """處理關鍵字，將字串或列表轉換成統一的列表格式"""
        if not raw_keywords:
            return []

        if isinstance(raw_keywords, list):
            return raw_keywords

        if isinstance(raw_keywords, str):
            return [k.strip() for k in raw_keywords.split(',') if k.strip()]

        return []
