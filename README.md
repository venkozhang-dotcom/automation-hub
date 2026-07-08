# Automation Hub

通用自动化工具库，配合 TRAE Work 云端沙箱环境使用。

## 结构

```
automation-hub/
├── lib/                 # 核心库模块
│   ├── credentials.py   # 凭证加载（从 ~/.config/automation-hub/.env 或环境变量）
│   ├── chrome_cdp.py    # Chrome DevTools Protocol 客户端
│   ├── quark_api.py     # 夸克网盘 API
│   ├── alipan_api.py    # 阿里云盘 API
│   └── utils.py         # 通用工具
├── scripts/             # 可执行脚本
│   ├── extract_credentials.py   # 从 Chrome 提取 Cookie/Token
│   ├── download_movie.py        # 电影下载流水线
│   ├── upload_alipan.py         # 上传到阿里云盘
│   └── refresh_alipan_token.py  # 刷新阿里云盘 Token
├── config/              # 配置模板
│   └── cloud-sandbox.json       # 自定义云端沙箱环境配置
└── docs/                # 文档
    └── api-notes.md             # API 调研笔记
```

## 快速开始

### 本地使用

```bash
# 1. 加载凭证
source ~/.config/automation-hub/env.sh

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行脚本
python scripts/extract_credentials.py
```

### 云端使用

在 TRAE Work 中选择 `Automation Hub` 云端环境，凭证自动注入环境变量。

## 凭证管理

| 凭证 | 存储位置 | 加载方式 |
|------|---------|---------|
| 本地 | `~/.config/automation-hub/.env` (chmod 600) | `source env.sh` 或 Python `credentials.py` |
| 云端 | TRAE Work 敏感变量 (KMS 加密) | 自动注入 `os.environ` |

## 凭证有效期

| 凭证 | 有效期 | 更新方式 |
|------|--------|---------|
| 夸克 Cookie | 7-30 天 | 重新登录 pan.quark.cn |
| 阿里云盘 access_token | ~2 小时 | 脚本自动用 refresh_token 刷新 |
| 阿里云盘 refresh_token | ~30 天 | 重新登录 alipan.com |
