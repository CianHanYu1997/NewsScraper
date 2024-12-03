# Think Tank Scraper Framework

用於爬取各大智庫文章的爬蟲框架，採用模組化設計。

## 安裝需求

- Python 3.7+
- Selenium
- Pandas
- Python-dataclass
- ChromeDriver

## 核心功能

### 1. 基礎架構

```
├── models/              # 數據模型
├── scrapers/           # 爬蟲實現
├── strategies/         # 爬蟲策略
├── url_builders/       # URL構建
└── manager/           # 爬蟲管理
```

### 2. 主要元件

- **ThinkTankScraper**: 爬蟲基類，提供通用爬取框架
- **ScraperManager**: 統一管理介面，處理爬蟲註冊與執行
- **Article**: 標準化文章數據結構

## 快速開始

```python
# 初始化
from manager.scraper_manager import ScraperManager
manager = ScraperManager()
manager.register_scraper(CFRScraper())

# 執行爬蟲
articles = manager.scrape_all(
    article_types={"外交關係協會": ["Report", "Article"]},
    load_counts={"外交關係協會": 5}
)

# 保存結果
from utils.file_handler import save_to_csv
save_to_csv(articles, 'output.csv')
```

## 輸出格式

CSV 包含：智庫名稱、文章類型、發布日期、標題、連結

## 注意事項

1. 設置適當延遲避免被封鎖
2. 部分網站可能需要代理
3. 確保 ChromeDriver 版本相容
