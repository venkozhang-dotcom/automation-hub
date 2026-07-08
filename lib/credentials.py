"""凭证加载模块。

本地: 从 ~/.config/automation-hub/.env 读取
云端: 从 os.environ 读取（TRAE Work 敏感变量自动注入）
"""
import os
from pathlib import Path

ENV_FILE = Path.home() / ".config" / "automation-hub" / ".env"

def _load_from_file() -> dict:
    """从 .env 文件加载凭证。"""
    creds = {}
    if not ENV_FILE.exists():
        return creds
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            creds[key.strip()] = value
    return creds

def load_credentials() -> dict:
    """加载凭证，优先环境变量（云端），其次文件（本地）。"""
    creds = _load_from_file()
    # 环境变量覆盖文件值（云端优先）
    for key in list(creds.keys()):
        env_val = os.environ.get(key)
        if env_val:
            creds[key] = env_val
    # 补充只在环境变量中的凭证
    for key in ["QUARK_COOKIE", "ALIPAN_REFRESH_TOKEN", "ALIPAN_DRIVE_ID",
                 "ALIPAN_USER_ID", "ALIPAN_API_BASE", "QUARK_API_BASE",
                 "ALIPAN_TARGET_FOLDER_NAME", "DOWNLOAD_DIR"]:
        if key not in creds and os.environ.get(key):
            creds[key] = os.environ[key]
    return creds

def get(key: str, default: str = "") -> str:
    """获取单个凭证值。"""
    return load_credentials().get(key, default)

def ensure_env() -> None:
    """将凭证加载到 os.environ（供读取环境变量的脚本使用）。"""
    for key, value in load_credentials().items():
        os.environ.setdefault(key, value)
