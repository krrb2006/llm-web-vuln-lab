"""Lightweight AST-ish taint analysis for PHP / JS / TS / Python.

Not a full parser: the source is tokenized (comments removed, strings and
brackets respected), split into statements, then a small fixpoint data-flow pass
follows user-controlled values through assignments into dangerous sinks. Each
finding carries the **propagation path** (source -> variables -> sink), which is
what makes it reviewable instead of a bare regex hit.

Sanitizers are modelled per sink class (html / sql / shell / path / url), so
"escaped for HTML then concatenated into SQL" is still reported, while
"intval() before a query" is not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- sources ----

SOURCE_PATTERNS = (
    r"\$_(?:GET|POST|REQUEST|COOKIE|FILES|SERVER)\s*\[",
    r"\$argv\b",
    r"(?:req|request)\.(?:query|body|params|args|form|json|values|headers|GET|POST)\b",
    r"\blocation\.(?:search|hash|href)\b",
    r"\bdocument\.(?:URL|referrer|location)\b",
    r"\bparams\.get\s*\(",
    r"\bgetParameter\s*\(",
)
SOURCE_RE = re.compile("|".join(SOURCE_PATTERNS), re.IGNORECASE)

# ------------------------------------------------------------- sanitizers ----

SANITIZERS: dict[str, tuple[str, str]] = {
    "htmlspecialchars": ("html", "HTML 转义"),
    "htmlentities": ("html", "HTML 转义"),
    "strip_tags": ("html", "标签剥离（弱）"),
    "esc_html": ("html", "HTML 转义"),
    "dompurify.sanitize": ("html", "DOM 清洗"),
    "encodeuricomponent": ("html", "URL 编码（非 HTML 上下文）"),
    "mysqli_real_escape_string": ("sql", "SQL 转义"),
    "real_escape_string": ("sql", "SQL 转义"),
    "pg_escape_string": ("sql", "SQL 转义"),
    "pg_escape_literal": ("sql", "SQL 转义"),
    "esc_sql": ("sql", "SQL 转义"),
    "intval": ("sql", "整数化"),
    "floatval": ("sql", "浮点化"),
    "escapeshellarg": ("shell", "Shell 参数转义"),
    "escapeshellcmd": ("shell", "Shell 命令转义"),
    "shlex.quote": ("shell", "Shell 参数转义"),
    "basename": ("path", "路径基名"),
    "realpath": ("path", "路径规范化"),
    "os.path.basename": ("path", "路径基名"),
    "urlencode": ("url", "URL 编码"),
    "parse_url": ("url", "URL 解析"),
    "urlparse": ("url", "URL 解析"),
    "bleach.clean": ("html", "HTML 清洗"),
}
SANITIZER_RE = re.compile(
    "|".join(sorted((re.escape(key) for key in SANITIZERS), key=len, reverse=True)),
    re.IGNORECASE,
)
CAST_RE = re.compile(r"\(\s*(?:int|integer|float|double|bool)\s*\)", re.IGNORECASE)

# ------------------------------------------------------------------ sinks ----

SINKS: list[dict] = [
    {
        "key": "sql",
        "category": "SQL Injection",
        "severity": "high",
        "title": "用户输入进入 SQL 查询",
        "sanitizer": "sql",
        "pattern": r"(?:->query|->prepare|->exec|->raw|mysqli_query|mysqli_multi_query|mysql_query|pg_query|"
                   r"db\.query|connection\.query|cursor\.execute|sequelize\.query|knex\.raw|execute)\s*\(",
        "remediation": "使用参数化查询（预处理 + 绑定参数）；拼接字符串即使用转义也仍然有风险。",
    },
    {
        "key": "xss_html",
        "category": "Cross-site Scripting",
        "severity": "high",
        "title": "未转义地输出用户输入",
        "sanitizer": "html",
        "pattern": r"(?:\becho\b|\bprint\b|\bprintf\b|<\?=)",
        "remediation": "按输出上下文转义（htmlspecialchars + ENT_QUOTES），或使用自动转义的模板引擎。",
    },
    {
        "key": "xss_dom",
        "category": "Cross-site Scripting",
        "severity": "high",
        "title": "DOM 直接写入可控数据",
        "sanitizer": "html",
        "pattern": r"(?:innerHTML|outerHTML|insertAdjacentHTML|document\.write)\s*(?:=|\()",
        "remediation": "改用 textContent / createTextNode，或先做 HTML 转义或白名单清洗。",
    },
    {
        "key": "cmd",
        "category": "Command Injection",
        "severity": "critical",
        "title": "用户输入进入系统命令",
        "sanitizer": "shell",
        "pattern": r"(?:\bsystem\b|\bexec\b|shell_exec|passthru|\bpopen\b|proc_open|child_process\.exec|"
                   r"subprocess\.(?:run|call|Popen|check_output)|os\.system|commands\.getoutput)\s*\(",
        "remediation": "避免拼接命令；必须执行时使用参数数组并做严格白名单校验。",
    },
    {
        "key": "path",
        "category": "Path Traversal / LFI",
        "severity": "high",
        "title": "用户输入控制文件路径",
        "sanitizer": "path",
        "pattern": r"(?:\binclude\b|\binclude_once\b|\brequire\b|\brequire_once\b|file_get_contents|readfile|\bfopen\b|"
                   r"\breadFile\b|sendFile|\bopen\b)\s*\(",
        "remediation": "对路径做白名单或基于 basename 的规范化校验，拒绝 .. 与绝对路径。",
    },
    {
        "key": "eval",
        "category": "Code Injection",
        "severity": "critical",
        "title": "动态执行用户输入",
        "sanitizer": None,
        "pattern": r"(?:\beval\b|new\s+Function|create_function)\s*\(",
        "remediation": "移除动态执行，改为显式分支或映射表。",
    },
    {
        "key": "deser",
        "category": "Insecure Deserialization",
        "severity": "high",
        "title": "反序列化不可信数据",
        "sanitizer": None,
        "pattern": r"(?:unserialize|pickle\.loads|yaml\.load)\s*\(",
        "remediation": "改用 JSON + 严格 schema 校验；不要反序列化用户可控数据。",
    },
    {
        "key": "ssrf",
        "category": "Server-side Request Forgery",
        "severity": "high",
        "title": "用户输入控制服务端请求地址",
        "sanitizer": "url",
        "pattern": r"(?:curl_exec|requests\.(?:get|post)|httpx\.(?:get|post)|urlopen|\bfetch\b|axios\.(?:get|post))\s*\(",
        "remediation": "对目标地址做协议与域名白名单，禁止访问内网与云元数据地址。",
    },
]

for _sink in SINKS:
    _sink["compiled"] = re.compile(_sink["pattern"], re.IGNORECASE)


@dataclass(slots=True)
class FlowStep:
    line: int
    code: str
    note: str

    def as_dict(self) -> dict:
        return {"line": self.line, "code": self.code, "note": self.note}


@dataclass(slots=True)
class DataFlowFinding:
    category: str
    severity: str
    title: str
    file_path: str
    line: int
    snippet: str
    explanation: str
    remediation: str
    confidence: int
    flow: list[FlowStep] = field(default_factory=list)
    source: str = "dataflow"


# ------------------------------------------------------------- tokenizing ----

def strip_comments(text: str) -> str:
    """Replace comments with spaces; keep strings and newlines so lines align."""
    out: list[str] = []
    index = 0
    length = len(text)
    quote: str | None = None
    while index < length:
        char = text[index]
        nxt = text[index + 1] if index + 1 < length else ""
        if quote:
            out.append(char)
            if char == "\\" and index + 1 < length:
                out.append(nxt)
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "'\"`":
            quote = char
            out.append(char)
            index += 1
            continue
        if char == "/" and nxt == "/":
            while index < length and text[index] != "\n":
                out.append(" ")
                index += 1
            continue
        if char == "#":
            while index < length and text[index] != "\n":
                out.append(" ")
                index += 1
            continue
        if char == "/" and nxt == "*":
            out.append("  ")
            index += 2
            while index < length and not (text[index] == "*" and index + 1 < length and text[index + 1] == "/"):
                out.append("\n" if text[index] == "\n" else " ")
                index += 1
            out.append("  ")
            index += 2
            continue
        out.append(char)
        index += 1
    return "".join(out)


def split_statements(clean: str, language: str = "") -> list[tuple[int, str]]:
    """Split into (line, code) statements; line is the first non-space line."""
    statements: list[tuple[int, str]] = []
    depth = 0
    start = 0
    line = 1
    start_line = 1
    quote: str | None = None
    python = language.lower() in {"python", "py"}
    index = 0
    length = len(clean)

    def flush(end_index: int, newline_terminator: bool = False) -> None:
        nonlocal start, start_line
        chunk = clean[start:end_index + 1]
        next_start_line = line + 1 if newline_terminator else line
        if not chunk.strip():
            start = end_index + 1
            start_line = next_start_line
            return
        leading = len(chunk) - len(chunk.lstrip())
        effective = start_line + chunk[:leading].count("\n")
        statements.append((effective, chunk.strip()))
        start = end_index + 1
        start_line = next_start_line

    while index < length:
        char = clean[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
            if char == "}" and depth == 0 and not python:
                flush(index)
        elif char == ";" and depth == 0:
            flush(index)
        elif char == "\n" and python and depth == 0:
            flush(index, newline_terminator=True)
        if char == "\n":
            line += 1
        index += 1
    if clean[start:].strip():
        flush(length - 1)
    return statements


ASSIGN_RE = re.compile(
    r"(?:^|[;{}\s])(?:const|let|var|my|our|public|private|protected|static)?\s*"
    r"(?P<var>\$?[A-Za-z_][\w$]*)\s*(?P<op>\.=|\+=|=)(?!=)\s*(?P<rhs>.+)$",
    re.DOTALL,
)
IDENT_RE = re.compile(r"\$?[A-Za-z_][\w$]*")
KEYWORDS = {
    "const", "let", "var", "function", "return", "new", "if", "else", "for", "while",
    "echo", "print", "printf", "include", "require", "require_once", "include_once",
    "true", "false", "null", "this", "self", "await", "async", "def", "class",
}


def _identifiers(text: str) -> set[str]:
    names = set()
    for match in IDENT_RE.finditer(text):
        name = match.group(0)
        if name.lower() in KEYWORDS:
            continue
        names.add(name)
    return names


def _sanitizer_hint(text: str) -> tuple[str, str] | None:
    if CAST_RE.search(text):
        return ("sql", "强制类型转换")
    match = SANITIZER_RE.search(text)
    if match:
        return SANITIZERS[match.group(0).lower()]
    return None


def _statement_var(statement: str) -> str | None:
    match = ASSIGN_RE.match(" ".join(statement.split()))
    return match.group("var") if match else None


PHP_OPEN_RE = re.compile(r"<\?php", re.IGNORECASE)
PHP_ECHO_RE = re.compile(r"<\?=")


def normalize_markup(text: str) -> str:
    """把 PHP 标签换成等长空白（<?= 换成 echo），保持行号不变。"""
    text = PHP_OPEN_RE.sub(lambda match: " " * len(match.group(0)), text)
    text = PHP_ECHO_RE.sub("echo", text)
    return text.replace("?>", "  ")


def analyze_text(text: str, relpath: str, language: str) -> list[DataFlowFinding]:
    clean = strip_comments(normalize_markup(text))
    if not clean.strip():
        return []
    statements = split_statements(clean, language)

    # var -> (line, code, origin_var, has_source, sanitizer)
    assignments: dict[str, tuple[int, str, str | None, bool, tuple[str, str] | None]] = {}
    for line, code in statements:
        flat = " ".join(code.split())
        match = ASSIGN_RE.match(flat)
        if not match:
            continue
        var = match.group("var")
        rhs = match.group("rhs")
        has_source = bool(SOURCE_RE.search(rhs))
        origin = None
        if not has_source:
            candidates = [name for name in _identifiers(rhs) if name != var and name in assignments]
            origin = candidates[0] if candidates else None
        assignments[var] = (line, flat, origin, has_source, _sanitizer_hint(rhs))

    tainted: dict[str, bool] = {name: data[3] for name, data in assignments.items()}
    for _ in range(6):
        changed = False
        for name, (line, code, origin, has_source, sanitizer) in assignments.items():
            if tainted.get(name):
                continue
            if any(tainted.get(other) for other in _identifiers(code) if other != name):
                tainted[name] = True
                changed = True
        if not changed:
            break

    def chain_for(var: str) -> list[FlowStep]:
        steps: list[FlowStep] = []
        current = var
        seen: set[str] = set()
        while current and current in assignments and current not in seen and len(seen) < 12:
            seen.add(current)
            line, code, origin, has_source, sanitizer = assignments[current]
            note = "污染源赋值" if has_source else f"变量 {current} 继承污染"
            if sanitizer:
                note = f"{note}（经过 {sanitizer[1]}）"
            steps.append(FlowStep(line=line, code=code[:220], note=note))
            current = (origin or "").strip()
        steps.reverse()
        return steps

    findings: list[DataFlowFinding] = []
    seen_keys: set[tuple[str, int]] = set()

    for line, code in statements:
        flat = " ".join(code.split())
        lhs = _statement_var(flat)
        body = flat[len(lhs):] if lhs else flat
        for sink in SINKS:
            if not sink["compiled"].search(flat):
                continue
            touched = [name for name in _identifiers(body) if tainted.get(name)]
            direct = bool(SOURCE_RE.search(body))
            if not touched and not direct:
                continue
            key = (sink["key"], line)
            if key in seen_keys:
                continue

            suppressed = False
            sanitizer_note = ""
            hint = _sanitizer_hint(body)
            if hint and sink["sanitizer"] and hint[0] == sink["sanitizer"]:
                suppressed = True
            elif hint and sink["sanitizer"] and hint[0] != sink["sanitizer"]:
                sanitizer_note = f"使用了 {hint[1]}，但它不能防护 {sink['category']}"
            if not suppressed and touched:
                var_hint = assignments.get(touched[0], (0, "", None, False, None))[4]
                if var_hint and sink["sanitizer"] and var_hint[0] == sink["sanitizer"]:
                    suppressed = True
            if suppressed:
                continue

            flow: list[FlowStep] = []
            for name in touched[:2]:
                flow.extend(chain_for(name))
            if direct and not touched:
                flow.insert(0, FlowStep(line=line, code=flat[:220], note="请求数据直接进入危险操作"))
            flow.append(FlowStep(line=line, code=flat[:220], note=f"危险操作：{sink['title']}"))

            unique: list[FlowStep] = []
            seen_steps: set[tuple[int, str]] = set()
            for step in flow:
                marker = (step.line, step.code)
                if marker in seen_steps:
                    continue
                seen_steps.add(marker)
                unique.append(step)

            confidence = 80 if len(unique) >= 3 else 68
            if sanitizer_note:
                confidence -= 18
            explanation = "数据流：" + " → ".join(step.note for step in unique)
            if sanitizer_note:
                explanation += f"；注意：{sanitizer_note}。"

            findings.append(
                DataFlowFinding(
                    category=sink["category"],
                    severity=sink["severity"],
                    title=sink["title"],
                    file_path=relpath,
                    line=line,
                    snippet="\n".join(step.code for step in unique)[:1500],
                    explanation=explanation,
                    remediation=sink["remediation"],
                    confidence=max(40, min(95, confidence)),
                    flow=unique,
                )
            )
            seen_keys.add(key)
            break

    return findings


def analyze_files(files, language_of) -> list[DataFlowFinding]:
    findings: list[DataFlowFinding] = []
    for item in files:
        try:
            text = item.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text:
            continue
        findings.extend(analyze_text(text, item.relpath, language_of(item)))
    return findings
