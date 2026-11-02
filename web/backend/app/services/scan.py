"""Deterministic pre-scan rules.

Two-part detection: a *sink* (dangerous operation) plus a *source* (request /
DOM controlled data) either on the same statement, in a small window around it,
or through a variable that was assigned from a source a few lines earlier.

Rules only flag *candidates*; confirmation is optional (user's own LLM key) and
final judgement stays with the human reviewer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# 请求 / DOM 可控数据
PHP_TAINT = r"\$_(?:GET|POST|REQUEST|COOKIE|FILES|SERVER)\s*\["
JS_SERVER_TAINT = r"(?:request|req)\.(?:args|form|values|json|query|body|params|headers)"
DOM_TAINT = r"(?:location\.(?:search|hash|href)|document\.(?:URL|referrer|location)|params\.get\()"
TAINT = rf"(?:{PHP_TAINT}|{JS_SERVER_TAINT}|{DOM_TAINT})"

# 变量赋值来源：$x = ...$_GET... / const x = ...req.query...
ASSIGN_PHP = re.compile(rf"\$(\w+)\s*=\s*[^;]*{TAINT}", re.IGNORECASE)
ASSIGN_JS = re.compile(rf"(?:const|let|var)\s+(\w+)\s*=\s*[^;]*{TAINT}", re.IGNORECASE)


@dataclass(slots=True)
class Rule:
    key: str
    category: str
    severity: str
    title: str
    sink: str
    remediation: str
    source: str | None = None
    requires: str | None = None
    window: int = 3
    languages: tuple[str, ...] = ()


@dataclass(slots=True)
class Candidate:
    rule: Rule
    file_path: str
    line: int
    snippet: str
    language: str = ""


RULES: list[Rule] = [
    Rule(
        key="sqli",
        category="SQL Injection",
        severity="high",
        title="用户输入进入 SQL 查询",
        sink=r"(?:->query|->prepare|mysqli_query|mysql_query|pg_query|->exec|->raw|execute)\s*\(",
        source=TAINT,
        requires=r"\b(?:select|insert|update|delete|where|order\s+by)\b",
        window=4,
        remediation="改用参数化查询（预处理 + 绑定参数）；不要把用户输入拼进 SQL 字符串，也不要只靠转义。",
    ),
    Rule(
        key="xss_echo",
        category="Cross-site Scripting",
        severity="high",
        title="未转义地输出用户输入",
        sink=r"(?:echo|print|printf|<%=|response\.write|document\.write)\b",
        source=TAINT,
        window=2,
        remediation="按输出上下文转义（PHP 用 htmlspecialchars 且带 ENT_QUOTES），或使用模板引擎的自动转义。",
    ),
    Rule(
        key="xss_dom",
        category="Cross-site Scripting",
        severity="high",
        title="DOM 直接写入可控数据",
        sink=r"(?:innerHTML|outerHTML|insertAdjacentHTML|document\.write)\s*(?:=|\()",
        source=DOM_TAINT,
        window=3,
        remediation="改用 textContent / createTextNode，或先做 HTML 转义与白名单清洗。",
    ),
    Rule(
        key="cmd_injection",
        category="Command Injection",
        severity="critical",
        title="用户输入进入系统命令",
        sink=r"(?:system|exec|shell_exec|passthru|popen|proc_open|child_process\.exec|subprocess\.(?:run|call|Popen))\s*\(",
        source=TAINT,
        window=1,
        remediation="避免拼接命令；必须执行时使用参数数组并做严格白名单校验。",
    ),
    Rule(
        key="file_read",
        category="Path Traversal / LFI",
        severity="high",
        title="用户输入控制文件路径",
        sink=r"(?:include|include_once|require|require_once|file_get_contents|readfile|fopen|readFile)\s*\(?",
        source=TAINT,
        window=0,
        remediation="对路径做白名单或规范化校验，拒绝 .. 与绝对路径，改用固定映射表。",
    ),
    Rule(
        key="code_eval",
        category="Code Injection",
        severity="critical",
        title="动态执行用户输入",
        sink=r"(?:eval|assert|create_function|new\s+Function)\s*\(",
        source=TAINT,
        window=2,
        remediation="移除动态执行，改为显式分支或映射表。",
    ),
    Rule(
        key="deserialization",
        category="Insecure Deserialization",
        severity="high",
        title="反序列化不可信数据",
        sink=r"(?:unserialize|pickle\.loads|yaml\.load)\s*\(",
        source=TAINT,
        window=2,
        remediation="改用 JSON + 严格 schema 校验；不要反序列化用户可控数据。",
    ),
    Rule(
        key="ssrf",
        category="Server-side Request Forgery",
        severity="high",
        title="用户输入控制服务端请求地址",
        sink=r"(?:curl_exec|requests\.(?:get|post)|httpx\.(?:get|post)|urlopen|fetch)\s*\(",
        source=TAINT,
        window=1,
        remediation="对目标地址做协议与域名白名单，禁止访问内网和云元数据地址。",
    ),
    Rule(
        key="hardcoded_secret",
        category="Sensitive Data Exposure",
        severity="medium",
        title="疑似硬编码密钥",
        sink=r"(?:api[_-]?key|secret|token|passwd|password)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']",
        window=0,
        remediation="把密钥移到环境变量或密钥管理服务，并轮换已泄露的密钥。",
    ),
    Rule(
        key="weak_hash",
        category="Weak Cryptography",
        severity="low",
        title="使用弱哈希处理口令",
        sink=r"(?:md5|sha1)\s*\(",
        requires=r"(?:pass|pwd|secret)",
        window=1,
        remediation="改用 bcrypt / argon2 等带盐慢哈希。",
    ),
    Rule(
        key="tls_verify_off",
        category="Transport Security",
        severity="medium",
        title="关闭了 TLS 证书校验",
        sink=r"(?:verify\s*=\s*False|rejectUnauthorized\s*:\s*false|CURLOPT_SSL_VERIFYPEER\s*,\s*(?:false|0))",
        window=0,
        remediation="恢复证书校验，配置可信 CA，而不是关闭校验。",
    ),
    Rule(
        key="debug_exposure",
        category="Configuration",
        severity="low",
        title="调试输出暴露请求内容",
        sink=r"(?:var_dump|print_r|console\.log)\s*\(",
        source=TAINT,
        window=1,
        remediation="移除调试输出，改用结构化日志并脱敏。",
    ),
]


def _tainted_variables(lines: list[str]) -> list[set[str]]:
    """For every line index, the set of variables already assigned from taint."""
    result: list[set[str]] = []
    current: set[str] = set()
    for line in lines:
        match = ASSIGN_PHP.search(line) or ASSIGN_JS.search(line)
        if match:
            current = current | {match.group(1)}
        result.append(current)
    return result


def _mentions(variables: set[str], text: str) -> bool:
    for name in variables:
        if re.search(rf"(?:\$|\b){re.escape(name)}\b", text):
            return True
    return False


def scan_text(text: str, relpath: str, language: str) -> list[Candidate]:
    lines = text.splitlines()
    tainted = _tainted_variables(lines)
    found: list[Candidate] = []
    for rule in RULES:
        if rule.languages and language not in rule.languages:
            continue
        sink = re.compile(rule.sink, re.IGNORECASE)
        source = re.compile(rule.source or TAINT, re.IGNORECASE)
        requires = re.compile(rule.requires, re.IGNORECASE) if rule.requires else None
        for index, line in enumerate(lines):
            if not sink.search(line):
                continue
            start = max(0, index - rule.window)
            end = min(len(lines), index + rule.window + 1)
            window = "\n".join(lines[start:end])
            if requires and not requires.search(window):
                continue
            if rule.source is not None:
                if not (source.search(window) or _mentions(tainted[index], window)):
                    continue
            found.append(
                Candidate(
                    rule=rule,
                    file_path=relpath,
                    line=index + 1,
                    snippet="\n".join(lines[max(0, index - 3): min(len(lines), index + 4)]),
                    language=language,
                )
            )
            break
    return found


def scan_files(files, language_of) -> list[Candidate]:
    candidates: list[Candidate] = []
    for item in files:
        try:
            text = Path(item.path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text:
            continue
        candidates.extend(scan_text(text, item.relpath, language_of(item)))
    return candidates
