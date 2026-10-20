#!/usr/bin/env python3
import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_draft(base_url, title, body):
    data = urllib.parse.urlencode({"title": title, "body": body}).encode("utf-8")
    req = urllib.request.Request(urllib.parse.urljoin(base_url, "submit.php"), data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        resp = urllib.request.build_opener(NoRedirect).open(req, timeout=10)
        status, location = resp.status, resp.headers.get("Location")
        resp.read()
    except urllib.error.HTTPError as exc:
        status, location = exc.code, exc.headers.get("Location")
        exc.read()
    if not location:
        raise RuntimeError(f"POST submit.php 未返回 Location，HTTP {status}")
    return status, urllib.parse.urljoin(base_url, location)


def get_preview(url):
    with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:4280/")
    parser.add_argument("mode", choices=["normal", "test"])
    args = parser.parse_args()
    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    if args.mode == "normal":
        title, body = "S021 normal", "S021 normal body - no script"
        expected = "人工浏览器确认：不应弹出提示框"
    else:
        title, body = "S021 test", "<script>alert('S021-XSS')</script>"
        expected = "人工浏览器确认：应弹出 alert('S021-XSS')"
    post_status, preview_url = post_draft(base_url, title, body)
    get_status, html = get_preview(preview_url)
    print(f"POST HTTP {post_status}")
    print(f"preview_url: {preview_url}")
    print(f"GET preview HTTP {get_status}")
    print(f"响应体是否包含本次提交的 body 字符串: {body in html}")
    print(expected)
    print("注意：响应体包含字符串不等同于 JavaScript 执行。")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
