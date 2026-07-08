#!/usr/bin/env python3
"""刷新阿里云盘 access_token。

用法:
    python scripts/refresh_alipan_token.py

输出新的 access_token，可用于调试。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.alipan_api import AlipanAPI

def main():
    print("=== 阿里云盘 Token 刷新 ===\n")
    api = AlipanAPI()
    print(f"✅ access_token: {api.access_token[:80]}...")
    print(f"   refresh_token: {api.refresh_token[:80]}...")
    print(f"   drive_id: {api.drive_id}")

if __name__ == "__main__":
    main()
