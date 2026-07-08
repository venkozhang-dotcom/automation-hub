"""Chrome DevTools Protocol 客户端。

通过 localhost:9222 调试端口控制 Chrome 浏览器。
用于 Cookie 提取、localStorage 读取、页面导航等。
"""
import json
import urllib.request
import socket
import os
from typing import Optional
from urllib.parse import urlparse

CDP_HOST = "localhost"
CDP_PORT = 9222

def get_tabs() -> list:
    """获取所有 Chrome 标签页。"""
    resp = urllib.request.urlopen(f"http://{CDP_HOST}:{CDP_PORT}/json/list")
    return json.loads(resp.read())

def find_tab(url_fragment: str) -> Optional[dict]:
    """通过 URL 片段查找标签页。"""
    for tab in get_tabs():
        if tab.get("type") == "page" and url_fragment in tab.get("url", ""):
            return tab
    return None

def evaluate(ws_url: str, expression: str) -> dict:
    """通过 CDP WebSocket 执行 JS 表达式。"""
    parsed = urlparse(ws_url)
    host_port = parsed.netloc
    path = parsed.path

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host_port.split(":")[0], int(host_port.split(":")[1])))

    # WebSocket 握手
    key = "dGhlIHNhbXBsZSBub25jZQ=="
    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host_port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(handshake.encode())

    response = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(4096)

    # 发送 evaluate 请求
    msg = json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": expression, "returnByValue": True}
    })

    payload = msg.encode()
    frame = bytearray()
    frame.append(0x81)

    mask_key = os.urandom(4)
    length = len(payload)
    if length < 126:
        frame.append(0x80 | length)
    elif length < 65536:
        frame.append(0x80 | 126)
        frame.extend(length.to_bytes(2, 'big'))
    else:
        frame.append(0x80 | 127)
        frame.extend(length.to_bytes(8, 'big'))

    frame.extend(mask_key)
    masked = bytearray(payload)
    for i in range(len(masked)):
        masked[i] ^= mask_key[i % 4]
    frame.extend(masked)

    sock.sendall(bytes(frame))

    # 读取响应
    data = b""
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        data += chunk
        if len(data) >= 2:
            idx = 0
            b1 = data[idx]; idx += 1
            b2 = data[idx]; idx += 1
            masked = (b2 & 0x80) != 0
            length = b2 & 0x7F
            if length == 126:
                length = int.from_bytes(data[idx:idx+2], 'big'); idx += 2
            elif length == 127:
                length = int.from_bytes(data[idx:idx+8], 'big'); idx += 8
            if masked:
                mask = data[idx:idx+4]; idx += 4
            if len(data) >= idx + length:
                payload_data = data[idx:idx+length]
                if masked:
                    payload_data = bytearray(payload_data)
                    for i in range(len(payload_data)):
                        payload_data[i] ^= mask[i % 4]
                    payload_data = bytes(payload_data)
                sock.close()
                return json.loads(payload_data.decode())

    sock.close()
    return {}

def get_cookie(domain: str) -> str:
    """从指定域名标签页提取 Cookie。"""
    tab = find_tab(domain)
    if not tab:
        raise RuntimeError(f"Chrome tab not found for: {domain}")
    result = evaluate(tab["webSocketDebuggerUrl"], "document.cookie")
    return result.get("result", {}).get("result", {}).get("value", "")

def get_localstorage(domain: str, key: str) -> str:
    """从指定域名标签页提取 localStorage 值。"""
    tab = find_tab(domain)
    if not tab:
        raise RuntimeError(f"Chrome tab not found for: {domain}")
    result = evaluate(tab["webSocketDebuggerUrl"], f"localStorage.getItem('{key}')")
    return result.get("result", {}).get("result", {}).get("value", "")
