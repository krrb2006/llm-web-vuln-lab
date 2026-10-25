#!/usr/bin/env python3
"""Run local normal and controlled comparisons for the four ADV cases."""

from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar


BASE = "http://127.0.0.1:4280/lab_cases/advanced"


def request(path: str, data: dict | None = None, opener=None) -> tuple[int, str]:
    body = None
    headers = {}
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(BASE + path, data=body, headers=headers)
    client = opener or urllib.request.build_opener()
    with client.open(req, timeout=10) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def lint(compose: list[str]) -> None:
    paths = [
        "advanced/SECOND_SQLI_01/vulnerable/save_profile.php",
        "advanced/SECOND_SQLI_01/vulnerable/lookup_profile.php",
        "advanced/SECOND_SQLI_01/fixed/save_profile.php",
        "advanced/SECOND_SQLI_01/fixed/lookup_profile.php",
        "advanced/IDOR_01/vulnerable/invoice.php",
        "advanced/IDOR_01/fixed/invoice.php",
    ]
    for path in paths:
        result = subprocess.run(compose + ["exec", "-T", "dvwa", "php", "-l", f"/var/www/html/lab_cases/{path}"], capture_output=True, text=True, check=False)
        if result.returncode:
            raise RuntimeError(f"php -l failed for {path}: {result.stdout}{result.stderr}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose", nargs="+", required=True)
    args = parser.parse_args()
    lint(args.compose)

    status, saved = request("/SECOND_SQLI_01/vulnerable/save_profile.php", {"nickname": "normal-adv"})
    if status != 200 or "saved" not in saved:
        raise RuntimeError("normal profile write failed")
    status, saved = request("/SECOND_SQLI_01/vulnerable/save_profile.php", {"nickname": "' OR 1=1 #"})
    if status != 200 or "saved" not in saved:
        raise RuntimeError("controlled profile write failed")
    vulnerable_status, vulnerable = request("/SECOND_SQLI_01/vulnerable/lookup_profile.php?id=4")
    fixed_status, fixed = request("/SECOND_SQLI_01/fixed/lookup_profile.php?id=4")
    if vulnerable_status != 200 or fixed_status != 200 or len(vulnerable) <= len(fixed):
        raise RuntimeError("second-order SQLi contrast was not observed")

    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    request("/IDOR_01/set_user.php?user_id=101", opener=opener)
    own_v_status, own_v = request("/IDOR_01/vulnerable/invoice.php?id=1001", opener=opener)
    other_v_status, other_v = request("/IDOR_01/vulnerable/invoice.php?id=1002", opener=opener)
    own_f_status, own_f = request("/IDOR_01/fixed/invoice.php?id=1001", opener=opener)
    other_f_status, other_f = request("/IDOR_01/fixed/invoice.php?id=1002", opener=opener)
    if not all(s == 200 for s in (own_v_status, other_v_status, own_f_status, other_f_status)):
        raise RuntimeError("IDOR endpoint returned a non-200 response")
    if json.loads(own_v).get("owner_id") != 101 or json.loads(own_f).get("owner_id") != 101:
        raise RuntimeError("own invoice comparison failed")
    if json.loads(other_v).get("owner_id") != 202 or other_f.strip() != "":
        raise RuntimeError("IDOR contrast was not observed")
    print(json.dumps({"second_order_sqli": "vulnerable_contrast_observed", "idor": "ownership_enforced_in_fixed"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
