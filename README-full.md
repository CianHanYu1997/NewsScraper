# Think Tank Scraper Framework

用於爬取各大智庫文章的爬蟲框架，採用模組化設計，支援多個智庫網站的文章爬取。

## 目錄結構

```
├── models/                # 數據模型定義
│   ├── article_type.py    # 文章類型定義
│   └── article.py         # 通用文章結構
├── scrapers/              # 爬蟲實現
│   ├── base.py            # 爬蟲基類
│   └── news/        # 各新聞專用爬蟲
│       └── tvbs_scraper.py
├── strategies/            # 爬蟲策略
│   ├── filter.py          # 篩選策略
│   └── page_load.py       # 頁面加載策略
├── url_builders/          # URL構建器
│   ├── base.py            # URL構建基類
│   └── news_url.py        # 新聞URL構建器
├── utils/                 # 工具函數
│   └── logging_config.py  # 日誌配置
└── manager/               # 爬蟲管理
    └── scraper_manager.py # 爬蟲管理器
```

## 核心功能

### 1. 數據模型 (models/)

```python
@dataclass
class Article:
    think_tank_name: str    # 智庫名稱
    article_type: str       # 文章類型
    publish_date: datetime  # 發布日期
    title: str             # 標題
    url: str               # 文章URL
```

### 2. 爬蟲基礎架構 (scrapers/base.py)

#### ThinkTankScraper 基類

爬蟲基類提供了一個通用的爬取框架,實現了以下核心功能:

**1. 瀏覽器配置與管理**

```python
def __init__(self,
    headless: bool = True,
    page_load_strategy: Optional[PageLoadStrategy] = None,
    url_builder: Optional[BaseURLBuilder] = None,
    filter_strategy: Optional[FilterStrategy] = None)
```

**2. 策略整合**

- 頁面加載策略(PageLoadStrategy):
  - 支援滾動加載(ScrollLoadStrategy)
  - 支援分頁加載(PaginationLoadStrategy)
  - 支援滾動點擊加載(ScrollPaginationLoadStrategy)
- URL 構建策略(URLBuilder)
- 內容過濾策略(FilterStrategy)

**3. 抽象方法定義**
必須由子類實現的核心方法:

```python
@abstractmethod
def get_article_type_enum(self) -> Type[BaseArticleType]           # 文章類型定義
def get_default_load_count(self) -> int                            # 預設加載次數
def get_name(self) -> str                                          # 智庫名稱
def get_base_url(self) -> str                                      # 基礎URL
def get_article_elements_locator(self) -> tuple                    # 文章元素定位器
def parse_article(self, element: WebElement) -> Optional[Article]  # 文章解析
```

**4. 文章爬取流程(fetch_articles)**

```python
def fetch_articles(self, article_type: str, load_count: Optional[int] = None)
```

完整的文章爬取流程包含:

- 文章類型驗證
- WebDriver 初始化
- 頁面加載與等待
- 元素定位與解析
- 動態內容加載(根據加載策略)
- 去重處理
- 錯誤處理和日誌記錄

**5. 輔助功能**

- URL 生成(`get_url`)
- 文章類型驗證(`validate_article_type`)
- 與頁面互動篩選特定選項(`apply_filter`)

#### 實現新爬蟲

要實現特定智庫的爬蟲,需要:

1. 繼承 ThinkTankScraper
2. 實現所有抽象方法
3. 根據需要配置相應策略

基本範例:

```python
class NewThinkTankScraper(ThinkTankScraper):
    def __init__(self):
        super().__init__(
            page_load_strategy=ScrollLoadStrategy(),  # 選擇加載策略
            url_builder=CustomURLBuilder(),           # 自定義URL構建器
            filter_strategy=CustomFilterStrategy()    # 自定義過濾策略
        )

    def get_article_type_enum(self):
        return NewThinkTankType

    def get_name(self):
        return "新智庫名稱"

    # ... 實現其他抽象方法
```

### 3. 策略模式 (strategies/)

提供兩種主要策略：

- **頁面加載策略**: 處理不同網站的內容加載機制
- **篩選策略**: 處理頁面上的文章類型篩選

### 4. URL 構建 (url_builders/)

提供靈活的 URL 構建機制：

- 支援基礎 URL 配置
- 支援查詢參數
- 支援分頁參數
- 支援文章類型參數

### 5. 爬蟲管理 (manager/scraper_manager.py)

ScraperManager 提供統一的爬蟲管理介面:

**1. 爬蟲註冊和管理**

```python
def register_scraper(self, scraper: ThinkTankScraper)
```

- 維護爬蟲註冊表
- 支援動態添加新爬蟲
- 通過名稱識別和存取爬蟲

**2. 爬蟲資訊查詢**

```python
def list_scrapers(self) -> Dict[str, List[str]]
def get_supported_types(self, scraper_name: str) -> List[str]
```

- 列出所有可用爬蟲
- 查詢支援的文章類型
- 驗證爬蟲和文章類型的有效性

**3. 爬蟲執行控制**

```python
def scrape_all(self, article_types: Optional[Dict] = None,
               load_counts: Optional[Dict] = None)
def scrape_selected(self, names: List[str],
                   article_types: Optional[Dict] = None,
                   load_counts: Optional[Dict] = None)
```

- 支援批量或選擇性執行爬蟲
- 自動處理爬蟲異常
- 支援自定義爬取參數
- 提供彈性的文章類型選擇

**4. 錯誤處理和日誌**

- 獨立的爬蟲錯誤隔離
- 詳細的日誌記錄
- 爬取狀態追踪
- 異常情況警告

## 使用方法

### 1. 基礎配置與初始化

```python
from manager.scraper_manager import ScraperManager
from scrapers.think_tank.cfr_scraper import CFRScraper
from scrapers.think_tank.brookings_scraper import BrookingsScraper

# 初始化爬蟲管理器
manager = ScraperManager()

# 註冊爬蟲
manager.register_scraper(CFRScraper())
manager.register_scraper(BrookingsScraper())
```

### 2. 查看可用爬蟲

```python
# 列出所有註冊的爬蟲及其支持的文章類型
scrapers_info = manager.list_scrapers()
print("可用的爬蟲及其支持的文章類型：")
for name, types in scrapers_info.items():
    print(f"{name}: {', '.join(types)}")

# 獲取特定爬蟲支持的文章類型
supported_types = manager.get_supported_types("外交關係協會")
print(f"外交關係協會支持的文章類型: {supported_types}")
```

### 3. 執行爬蟲

#### 方法一：執行所有註冊的爬蟲

```python
# 執行所有爬蟲，使用預設設置
all_articles = manager.scrape_all()

# 指定特定爬蟲的文章類型
article_types = {
    "外交關係協會": ["Report", "Article"],
    "布魯金斯研究所": "Policy Brief"
}
# 指定加載次數
load_counts = {
    "外交關係協會": 5,
    "布魯金斯研究所": 10
}
articles = manager.scrape_all(
    article_types=article_types,
    load_counts=load_counts
)
```

#### 方法二：執行選定的爬蟲

```python
# 只執行指定的爬蟲
selected_articles = manager.scrape_selected(
    names=["布魯金斯研究所"],
    article_types={"布魯金斯研究所": ["Report"]},
    load_counts={"布魯金斯研究所": 15}
)
```

### 4. 保存結果

```python
from utils.file_handler import save_to_csv

# 保存爬取結果到CSV文件
save_to_csv(articles, 'output.csv')
```

### 參數說明

#### scrape_all() 和 scrape_selected() 方法

- `article_types`: (可選) Dictionary

  ```python
  {
      "智庫名稱": "文章類型" 或 ["文章類型1", "文章類型2"],
      # 例如:
      "外交關係協會": ["Report", "Article"],
      "布魯金斯研究所": "Policy Brief"
  }
  ```

  - 如果不指定，將爬取所有支持的文章類型
  - 可以為每個爬蟲指定單個類型或類型列表

- `load_counts`: (可選) Dictionary

  ```python
  {
      "智庫名稱": 加載次數(整數),
      # 例如:
      "外交關係協會": 5,
      "布魯金斯研究所": 10
  }
  ```

  - 如果不指定，將使用每個爬蟲的預設加載次數

- `names`: (僅用於 scrape_selected) List[str]
  - 要執行的爬蟲名稱列表
  ```python
  names=["外交關係協會", "布魯金斯研究所"]
  ```

### 錯誤處理

- 管理器會自動處理每個爬蟲的錯誤，確保一個爬蟲的失敗不會影響其他爬蟲的執行
- 所有錯誤和警告都會被記錄到日誌中
- 無效的文章類型會被跳過並記錄警告
- 找不到的爬蟲名稱會被跳過並記錄警告

### 執行建議

1. 建議先使用 `list_scrapers()` 檢查可用的爬蟲和文章類型
2. 對於大量數據爬取，建議適當控制 `load_counts` 值
3. 使用日誌跟踪爬取進度和可能的問題
4. 考慮使用 try-except 包裝爬蟲執行代碼，以處理可能的異常

## 配置

### 日誌配置

```python
setup_logging(
    level=logging.DEBUG,
    log_file='scraper.log',
    log_dir='logs'
)
```

## 輸出格式

CSV 輸出包含以下欄位：

- 智庫名稱
- 文章類型
- 發布日期
- 標題
- 連結

## 依賴項目

- Python 3.7+
- Selenium
- Pandas
- Python-dataclass

## 注意事項

1. 請確保已安裝相應版本的 ChromeDriver
2. 部分網站可能需要配置代理
3. 建議設置適當的延遲以避免被封鎖
