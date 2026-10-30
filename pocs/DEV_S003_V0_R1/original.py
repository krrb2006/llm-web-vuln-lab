#!/usr/bin/env python3
# S003 本地教学验证脚本：仅访问 127.0.0.1:4280，不修改数据库。
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S003/index.php"
TIMEOUT = 5

def fetch(payload: str) -> str:
    query = urllib.parse.urlencode({"id": payload})
    url = f"{BASE}?{query}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read()
    return body.decode("utf-8", errors="replace")

def main() -> None:
    cases = [
        ("normal", "1"),
        ("test", "1 OR 1=1"),
    ]

    results = {}
    for name, payload in cases:
        print(f"[{name}] id={payload!r}")
        try:
            body = fetch(payload)
        except Exception as exc:
            print(f"  请求失败: {exc}")
            print("  检查：服务是否监听 127.0.0.1:4280；页面路径是否正确。")
            return
        results[name] = body
        print(f"  正文长度: {len(body)}")
        print(f"  包含 Alice: {'Alice' in body}")
        print(f"  包含 Bob: {'Bob' in body}")
        print(f"  包含 Carol: {'Carol' in body}")
        print(f"  包含“查询失败”: {'查询失败' in body}")

    normal = results.get("normal", "")
    test = results.get("test", "")

    normal_ok = ("Alice" in normal) and ("Bob" not in normal) and ("Carol" not in normal)
    test_changed = ("Alice" in test) and ("Bob" in test) and ("Carol" in test)

    print("\n比较结果（仅作运行观察，不以 HTTP 200 为成功条件）：")
    print(f"  普通输入符合预期记录范围: {normal_ok}")
    print(f"  测试输入出现记录范围变化: {test_changed}")
    if not normal_ok:
        print("  请检查 lab_people 是否预置 1 Alice、2 Bob、3 Carol，以及数据库连接是否正常。")
    if not test_changed:
        print("  若普通输入正常但测试未变化，请检查实际代码是否已改为预处理/整数转换，或请求是否被拦截。")

if __name__ == "__main__":
    main()
