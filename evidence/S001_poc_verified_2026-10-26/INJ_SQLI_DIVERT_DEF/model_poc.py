#!/usr/bin/env python3
import html as htmlmod
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"
EXPECTED_NORMAL = {("1", "Alice")}
EXPECTED_TEST_KEYS = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}


class BlockRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url,
            code,
            f"blocked redirect to {newurl}",
            headers,
            fp,
        )


OPENER = urllib.request.build_opener(BlockRedirect())


def fetch(name):
    query = urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(BASE + "?" + query, method="GET")
    with OPENER.open(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def parse_records(body):
    records = []
    for m in re.finditer(r"<p>\s*ID\s*([^：<]+)：\s*(.*?)\s*</p>", body, re.S):
        rid = htmlmod.unescape(m.group(1)).strip()
        rname = htmlmod.unescape(m.group(2)).strip()
        records.append((rid, rname))
    return records


def main():
    try:
        status_normal, body_normal = fetch("Alice")
        normal = parse_records(body_normal)

        status_test, body_test = fetch("' OR '1'='1")
        test = parse_records(body_test)
    except Exception as exc:
        print(f"请求失败或重定向被拒绝：{exc}", file=sys.stderr)
        print("请检查入口、common/db_connect.php、MariaDB、lab_people 数据和网络。", file=sys.stderr)
        return 2

    print("普通响应状态:", status_normal)
    print("普通记录:", normal)
    print("测试响应状态:", status_test)
    print("测试记录:", test)

    ok_normal = set(normal) == EXPECTED_NORMAL
    ok_test = EXPECTED_TEST_KEYS.issubset(set(test)) and set(test) != set(normal)

    if ok_normal and ok_test:
        print("成功：普通请求仅返回 Alice；测试输入返回包含 Bob、Carol 的额外记录。")
        print("数据库预期：数据未被修改；观察者应在浏览器/响应正文看到普通仅 ID 1：Alice，测试出现 ID 2：Bob 和 ID 3：Carol。")
        return 0

    print("未能判定：普通或测试记录不符合预期。", file=sys.stderr)
    print("请检查连接、表数据、HTML 结构、重定向拦截或 SQL 模式。", file=sys.stderr)
    print("普通预期:", EXPECTED_NORMAL, file=sys.stderr)
    print("测试预期至少包含:", EXPECTED_TEST_KEYS, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
