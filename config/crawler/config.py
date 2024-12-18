
from pydantic import BaseModel


class HttpxFetcherConfig(BaseModel):
    """基礎爬蟲配置"""
    retry_times: int = 3                # 重試次數
    retry_delay: float = 1.0            # 
    timeout: float = 10.0               # 請求時間超過此秒數，中斷請求
    use_proxy: bool = True              # 是否使用代理池
    random_delay_range: tuple = (1, 3)  # 隨機延遲
