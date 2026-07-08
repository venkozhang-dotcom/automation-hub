"""阿里云盘 API 客户端。

API Base: https://api.aliyundrive.com
认证: Bearer Token (从 refresh_token 自动刷新)

注意:
- 单分片上传 ≤1GB
- OSS PUT 不加额外 header（加了会 SignatureDoesNotMatch）
- 存在多个 drive，上传时需指定正确 drive_id
"""
import requests
import os
from .credentials import get

class AlipanAPI:
    def __init__(self, refresh_token: str = None, drive_id: str = None):
        self.refresh_token = refresh_token or get("ALIPAN_REFRESH_TOKEN")
        if not self.refresh_token:
            raise ValueError("ALIPAN_REFRESH_TOKEN not found.")
        self.drive_id = drive_id or get("ALIPAN_DRIVE_ID")
        self.base_url = get("ALIPAN_API_BASE", "https://api.aliyundrive.com")
        self.access_token = None
        self._refresh_access_token()

    def _refresh_access_token(self) -> None:
        """用 refresh_token 刷新 access_token。"""
        resp = requests.post(f"{self.base_url}/v2/account/token", json={
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        })
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"Token refresh failed: {data}")
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        self.drive_id = data.get("default_drive_id", self.drive_id)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    def list_files(self, folder_id: str = "root") -> dict:
        """列出文件夹内容。"""
        resp = requests.post(f"{self.base_url}/v2/file/list", 
            headers=self._headers(),
            json={
                "drive_id": self.drive_id,
                "parent_file_id": folder_id,
                "limit": 100,
            }
        )
        return resp.json()

    def search_folder(self, name: str) -> str:
        """查找文件夹，返回 file_id。"""
        resp = requests.post(f"{self.base_url}/v2/file/list",
            headers=self._headers(),
            json={
                "drive_id": self.drive_id,
                "parent_file_id": "root",
                "limit": 100,
            }
        )
        for item in resp.json().get("items", []):
            if item.get("name") == name and item.get("type") == "folder":
                return item["file_id"]
        return None

    def create_folder(self, name: str, parent_id: str = "root") -> str:
        """创建文件夹，返回 file_id。"""
        resp = requests.post(f"{self.base_url}/v2/file/create",
            headers=self._headers(),
            json={
                "drive_id": self.drive_id,
                "parent_file_id": parent_id,
                "name": name,
                "type": "folder",
                "check_name_mode": "refuse",
            }
        )
        return resp.json().get("file_id")

    def upload_file(self, file_path: str, parent_folder_id: str,
                    part_size: int = 1024*1024*1024) -> str:
        """上传文件（分片），返回 file_id。

        Args:
            file_path: 本地文件路径
            parent_folder_id: 目标文件夹 ID
            part_size: 单分片大小，默认 1GB（最大值）
        """
        import math
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        part_count = math.ceil(file_size / part_size)

        # 1. 创建上传
        resp = requests.post(f"{self.base_url}/v2/file/create",
            headers=self._headers(),
            json={
                "drive_id": self.drive_id,
                "parent_file_id": parent_folder_id,
                "name": file_name,
                "type": "file",
                "check_name_mode": "auto_rename",
                "part_info_list": [
                    {"part_number": i + 1} for i in range(part_count)
                ],
            }
        )
        data = resp.json()
        file_id = data["file_id"]
        upload_id = data["upload_id"]
        part_urls = [p["upload_url"] for p in data["part_info_list"]]

        # 2. 分片上传到 OSS（不加额外 header）
        with open(file_path, "rb") as f:
            for i in range(part_count):
                chunk = f.read(part_size)
                resp = requests.put(part_urls[i], data=chunk)
                if resp.status_code != 200:
                    raise RuntimeError(f"Part {i+1}/{part_count} upload failed: {resp.status_code}")
                print(f"  Part {i+1}/{part_count} uploaded ({len(chunk)//1024//1024}MB)")

        # 3. 完成上传
        resp = requests.post(f"{self.base_url}/v2/file/complete",
            headers=self._headers(),
            json={
                "drive_id": self.drive_id,
                "file_id": file_id,
                "upload_id": upload_id,
            }
        )
        print(f"Upload complete: {file_name} → file_id={file_id}")
        return file_id
