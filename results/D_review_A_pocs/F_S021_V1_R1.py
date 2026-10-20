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
    submit_url = urllib.parse.urljoin(base_url, "submit.php")
    req = urllib.request.Request(submit_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    opener = urllib.request.build_opener(NoRedirect)
    try:
        resp = opener.open(req, timeout=10)
        status = resp.status
        location = resp.headers.get("Location")
        resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        location = exc.headers.get("Location")
        exc.read()
    if not location:
        raise RuntimeError(f"POST submit.php 未返回 Location，HTTP {status}")
    preview_url = urllib.parse.urljoin(base_url, location)
    return status, preview_url

def get_preview(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:4280/",
        help="submit.php 所在目录 URL，需以 / 结尾",
    )
    parser.add_argument("mode", choices=["normal", "test"])
    args = parser.parse_args()
    base_url = args.base_url
    if not base_url.endswith("/"):
        base_url += "/"
    if args.mode == "normal":
        title = "S021 normal"
        body = "S021 normal body - no script"
        expected = "人工浏览器确认：不应弹出提示框"
    else:
        title = "S021 test"
        body = "<script>alert('S021-XSS')</script>"
        expected = "人工浏览器确认：应弹出 alert('S021-XSS')"
    post_status, preview_url = post_draft(base_url, title, body)
    get_status, html = get_preview(preview_url)
    print(f"POST HTTP {post_status}")
    print(f"preview_url: {preview_url}")
    print(f"GET preview HTTP {get_status}")
    print(f"响应体是否包含本次提交的 body 字符串: {body in html}")
    print(expected)
    print("注意：响应体包含字符串不等同于 JavaScript 执行。")
    print("请用浏览器打开 preview_url 进行人工确认。")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
