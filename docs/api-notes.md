# API 调研笔记

## 夸克网盘 API

| 项目 | 内容 |
|---|---|
| API Base | `https://drive-pc.quark.cn` |
| 认证方式 | Cookie |
| 文件列表 | `GET /1/clouddrive/file/sort` — 可用 |
| Task list | `GET /1/clouddrive/task/list` — 可用，返回 BT 任务和 magnet 链接 |
| 离线下载 | `POST /1/clouddrive/offline/task/submit` — 需加密请求体，返回 `decrypt_fail` |
| **结论** | 网页端 API 不支持离线下载，BT 下载只能通过夸克客户端 |

## 阿里云盘 API

| 项目 | 内容 |
|---|---|
| API Base | `https://api.aliyundrive.com` |
| 认证方式 | Bearer Token |
| Token 刷新 | `POST /v2/account/token` |
| 文件上传 | `POST /v2/file/create` → OSS PUT → `POST /v2/file/complete` |
| 多 Drive 问题 | default_drive_id 与用户原始文件夹所在 drive 可能不同 |
| 上传限制 | 单分片 ≤1GB；OSS PUT 不加额外 header |
| access_token 有效期 | ~2 小时 |
| refresh_token 有效期 | ~30 天 |

## Chrome CDP 自动化

| 项目 | 内容 |
|---|---|
| 调试端口 | localhost:9222 |
| 启动方式 | `--remote-debugging-port=9222 --user-data-dir=<独立profile>` |
| 获取标签页 | `GET http://localhost:9222/json/list` |
| 执行 JS | WebSocket → `Runtime.evaluate` |
| 已验证操作 | Cookie 提取、localStorage 读取、页面导航 |
