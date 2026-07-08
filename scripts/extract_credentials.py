#!/usr/bin/env python3
"""从 Chrome CDP 调试端口提取夸克 Cookie 和阿里云盘 Token。

用法:
    python scripts/extract_credentials.py

前提: Chrome 以 --remote-debugging-port=9222 启动，
且已登录 pan.quark.cn 和 alipan.com。
"""
import sys
import os
import json

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.chrome_cdp import find_tab, evaluate
from lib.credentials import ENV_FILE

def extract_quark_cookie() -> str:
    """从夸克网盘标签页提取 Cookie。"""
    tab = find_tab("pan.quark.cn")
    if not tab:
        print("❌ 未找到夸克网盘标签页，请先在 Chrome 中打开 pan.quark.cn")
        return None
    result = evaluate(tab["webSocketDebuggerUrl"], "document.cookie")
    cookie = result.get("result", {}).get("result", {}).get("value", "")
    if cookie:
        print(f"✅ 夸克 Cookie 提取成功 ({len(cookie)} chars)")
    return cookie

def extract_alipan_tokens() -> dict:
    """从阿里云盘标签页提取 Token。"""
    tab = find_tab("alipan.com")
    if not tab:
        print("❌ 未找到阿里云盘标签页，请先在 Chrome 中打开 alipan.com")
        return None

    # 提取 localStorage 中的 token
    result = evaluate(tab["webSocketDebuggerUrl"],
        "JSON.stringify({token: localStorage.getItem('token')})")
    value = result.get("result", {}).get("result", {}).get("value", "")

    if not value:
        print("❌ 阿里云盘 Token 提取失败")
        return None

    token_data = json.loads(value)
    token_str = token_data.get("token", "{}")
    token_obj = json.loads(token_str)

    tokens = {
        "access_token": token_obj.get("access_token", ""),
        "refresh_token": token_obj.get("refresh_token", ""),
        "default_drive_id": token_obj.get("default_drive_id", ""),
        "user_id": token_obj.get("user_id", ""),
        "nick_name": token_obj.get("nick_name", ""),
        "expire_time": token_obj.get("expire_time", ""),
    }

    print(f"✅ 阿里云盘 Token 提取成功")
    print(f"   refresh_token: {tokens['refresh_token'][:16]}...")
    print(f"   drive_id: {tokens['default_drive_id']}")
    print(f"   expire_time: {tokens['expire_time']}")
    return tokens

def update_env_file(quark_cookie: str, alipan_tokens: dict) -> None:
    """更新本地 .env 文件。"""
    import shutil
    from pathlib import Path

    if ENV_FILE.exists():
        shutil.copy2(ENV_FILE, str(ENV_FILE) + ".bak")
        print(f"   备份: {ENV_FILE}.bak")

    lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    # 更新或添加凭证行
    updates = {
        "QUARK_COOKIE": quark_cookie,
        "ALIPAN_REFRESH_TOKEN": alipan_tokens["refresh_token"],
        "ALIPAN_DRIVE_ID": alipan_tokens["default_drive_id"],
        "ALIPAN_USER_ID": alipan_tokens["user_id"],
    }

    for key, value in updates.items():
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f'{key}="{value}"\n'
                found = True
                break
        if not found:
            lines.append(f'{key}="{value}"\n')

    with open(ENV_FILE, "w") as f:
        f.writelines(lines)

    os.chmod(ENV_FILE, 0o600)
    print(f"✅ 本地 .env 已更新: {ENV_FILE}")
    print("⚠️  云端敏感变量需要手动在 TRAE Work 设置中更新")

def main():
    print("=== 凭证提取工具 ===\n")

    quark_cookie = extract_quark_cookie()
    alipan_tokens = extract_alipan_tokens()

    if quark_cookie and alipan_tokens:
        print("\n=== 更新本地凭证 ===")
        update_env_file(quark_cookie, alipan_tokens)
        print("\n✅ 完成！本地凭证已更新。")
        print("如需更新云端沙箱环境，请手动在 TRAE Work 设置中修改敏感变量。")
    else:
        print("\n❌ 部分凭证提取失败，请确保 Chrome 已登录相关网站。")
        sys.exit(1)

if __name__ == "__main__":
    main()
