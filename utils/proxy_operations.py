import httpx
from typing import List, Dict
from fake_useragent import UserAgent


class ProxyOperations:
    def __init__(self):
        self.ua = UserAgent()
        self.client = httpx.AsyncClient()

    async def get_proxy(self, https: bool = False) -> Dict:
        """
        隨機獲取一個代理資訊

        Args:
            https (bool):
                - True: 只返回支持 HTTPS 的代理
                - False: 返回所有代理（默認）
        Returns:
            - proxy: 代理服務器的地址和端口(例如：'203.95.198.150:8080')
            - anonymous: 代理的匿名程度
            - https: 是否支持 HTTPS(boolean)
            - region: 代理服務器的地理位置
            - check_count: 檢查次數
            - fail_count: 失敗次數
            - last_status: 最後一次檢查狀態(boolean)
            - last_time: 最後一次檢查時間
            - source: 代理來源
        """
        response = await self.client.get(
            f"http://127.0.0.1:5010/get/{'?type=https' if https else ''}")
        return response.json()

    async def get_all_proxy(self, https: bool = False) -> List[Dict]:
        """
        獲取所有代理服務的資訊

        Args:
            https (bool):
                - True: 只返回支持 HTTPS 的代理
                - False: 返回所有代理（默認）
        """
        response = await self.client.get(
            f"http://127.0.0.1:5010/all/{'?type=https' if https else ''}")
        return response.json()

    async def get_proxy_count(self) -> Dict:
        """
        查看代理數量

        Returns:
            - count: 代理數輛
            - http_type: 不同協議類型的代理數量
                - http: HTTP代理數量
                - https: HTTPS代理數量
            - source: 不同來源的代理數量
                - freeProxy03: 來源03的代理數量
                - freeProxy11: 來源11的代理數量

        """
        response = await self.client.get("http://127.0.0.1:5010/count/")
        return response.json()

    async def pop_proxy(self, https: bool = False) -> Dict:
        """
        隨機獲取並刪除一個代理資訊

        Args:
            https (bool):
                - True: 只返回支持 HTTPS 的代理
                - False: 返回所有代理（默認）
        """
        response = await self.client.get(
            f"http://127.0.0.1:5010/pop/{'?type=https' if https else ''}")
        return response.json()

    async def delete_proxy(self, proxy: str):
        """
        刪除代理

        Args:
            proxy (str): 代理ip
        """
        response = await self.client.get(
            "http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
        return response

    async def close(self):
        """
        Cleanup method to properly close the async client
        """
        await self.client.aclose()

    # 上下文管理器
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# # 使用範例
# async def main():
#     async with ProxyOperations() as proxy_ops:
#         result = await proxy_ops.get_proxy(https=True)
#         proxy = result.get('proxy')
#         print(result)
#         print(type(result))
#         print("Current User-Agent:", proxy_ops.ua.random)
#         await proxy_ops.delete_proxy(proxy)

# asyncio.run(main())
