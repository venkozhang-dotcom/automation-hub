"""通用工具函数。"""
import os
import time
from pathlib import Path

def ensure_dir(path: str) -> str:
    """确保目录存在。"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def monitor_download(path: str, interval: float = 2.0, stable_seconds: float = 10.0) -> bool:
    """监控文件下载，大小稳定后返回 True。

    Args:
        path: 文件路径
        interval: 轮询间隔（秒）
        stable_seconds: 大小无变化多少秒后视为下载完成
    """
    last_size = -1
    stable_since = 0

    while True:
        if not os.path.exists(path):
            time.sleep(interval)
            continue

        current_size = os.path.getsize(path)
        if current_size == last_size:
            if time.time() - stable_since >= stable_seconds:
                print(f"Download complete: {path} ({current_size // 1024 // 1024}MB)")
                return True
        else:
            last_size = current_size
            stable_since = time.time()
            print(f"Downloading: {current_size // 1024 // 1024}MB")

        time.sleep(interval)

def format_size(bytes: int) -> str:
    """格式化文件大小。"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}PB"
