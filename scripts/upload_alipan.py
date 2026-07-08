#!/usr/bin/env python3
"""上传文件到阿里云盘。

用法:
    python scripts/upload_alipan.py <file_path> [folder_name]

示例:
    python scripts/upload_alipan.py /tmp/downloads/movie.mkv 影视
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.alipan_api import AlipanAPI
from lib.credentials import get
from lib.utils import format_size

def main():
    if len(sys.argv) < 2:
        print("用法: python upload_alipan.py <file_path> [folder_name]")
        sys.exit(1)

    file_path = sys.argv[1]
    folder_name = sys.argv[2] if len(sys.argv) > 2 else get("ALIPAN_TARGET_FOLDER_NAME", "影视")

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)

    file_size = os.path.getsize(file_path)
    print(f"=== 阿里云盘上传 ===")
    print(f"文件: {os.path.basename(file_path)}")
    print(f"大小: {format_size(file_size)}")
    print(f"目标文件夹: {folder_name}")
    print()

    # 初始化 API（自动刷新 token）
    api = AlipanAPI()

    # 查找或创建目标文件夹
    folder_id = api.search_folder(folder_name)
    if not folder_id:
        print(f"文件夹 '{folder_name}' 不存在，创建中...")
        folder_id = api.create_folder(folder_name)
        print(f"✅ 创建成功: {folder_id}")
    else:
        print(f"✅ 找到文件夹: {folder_id}")

    # 上传文件
    print(f"\n开始上传（分片 1GB）...")
    file_id = api.upload_file(file_path, folder_id)
    print(f"\n✅ 上传完成!")
    print(f"   file_id: {file_id}")

if __name__ == "__main__":
    main()
