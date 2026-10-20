import http.client
from urllib.parse import urlencode

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 4280
TARGET_PATH = "/lab_cases/S019/index.php"


def post_content(content: str):
    if TARGET_HOST != "127.0.0.1" or TARGET_PORT != 4280:
        raise SystemExit("目标必须固定为 127.0.0.1:4280")

    body = urlencode({"content": content}).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html",
    }

    conn = http.client.HTTPConnection(TARGET_HOST, TARGET_PORT, timeout=10)
    try:
        conn.request("POST", TARGET_PATH, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read().decode("utf-8", "replace")
        return resp.status, resp.getheader("Content-Type"), data
    finally:
        conn.close()


def show(label: str, content: str):
    status, ctype, data = post_content(content)
    print(f"[{label}] status={status} content-type={ctype}")

    marker = '<div class="preview">'
    idx = data.find(marker)
    if idx == -1:
        print("未找到预览区片段")
    else:
        print(data[idx:idx + 400])

    print("响应体包含原始输入:", content in data)
    print("-" * 60)


def main():
    normal = "普通预览内容 S019-NORMAL"
    payload = "<img src=x onerror=alert('S019-XSS')>"

    show("普通对照", normal)
    show("测试输入", payload)

    print("人工浏览器步骤：打开 http://127.0.0.1:4280/lab_cases/S019/index.php")
    print("1) 普通输入提交，预览区应只显示文本；")
    print("2) 测试输入提交，人工确认是否弹出 S019-XSS；")
    print("HTTP 响应体出现 payload 不等于 JavaScript 执行。")


if __name__ == "__main__":
    main()
