"""夸克网盘 API 客户端。

API Base: https://drive-pc.quark.cn
认证: Cookie

注意: 离线下载 API 需加密请求体，网页端不可用。
BT 下载只能通过夸克客户端。
"""
import requests
from .credentials import get

class QuarkAPI:
    def __init__(self, cookie: str = None):
        self.cookie = cookie or get("QUARK_COOKIE")
        if not self.cookie:
            raise ValueError("QUARK_COOKIE not found. Run extract_credentials.py first.")
        self.base_url = get("QUARK_API_BASE", "https://drive-pc.quark.cn")
        self.session = requests.Session()
        self.session.headers["Cookie"] = self.cookie

    def list_files(self, dir_id: str = "0", page: int = 1, size: int = 50) -> dict:
        """列出网盘文件。"""
        resp = self.session.get(f"{self.base_url}/1/clouddrive/file/sort", params={
            "dir_id": dir_id,
            "page": page,
            "size": size,
            "sort": "file_name",
            "order": "asc",
        })
        return resp.json()

    def list_tasks(self, page: int = 1, size: int = 50) -> dict:
        """列出离线下载任务（含 BT 任务和 magnet 链接）。"""
        resp = self.session.get(f"{self.base_url}/1/clouddrive/task/list", params={
            "page": page,
            "size": size,
            "type": "offline",
        })
        return resp.json()

    def get_task_detail(self, task_id: str) -> dict:
        """获取任务详情。"""
        resp = self.session.get(f"{self.base_url}/1/clouddrive/task", params={
            "task_id": task_id,
        })
        return resp.json()
