"""Data-flow analyzer tests (run with: python -m unittest discover -s tests)."""

from __future__ import annotations

import unittest

from app.services.dataflow import analyze_text, split_statements, strip_comments

PHP_VULN = """<?php
$name = $_GET['name'];
$sql = "SELECT id FROM users WHERE name = '" . $name . "'";
$rows = $db->query($sql);
"""

PHP_SAFE = """<?php
$id = intval($_GET['id']);
$rows = $db->query("SELECT id FROM t WHERE id = " . $id);
$name = htmlspecialchars($_GET['name']);
echo "<p>" . $name . "</p>";
"""

JS_DOM = """const q = new URLSearchParams(location.search).get('q');
const el = document.getElementById('out');
el.innerHTML = '<b>' + q + '</b>';
"""

PY_CMD = """import subprocess
from flask import request

def ping():
    host = request.args.get('host', '127.0.0.1')
    return subprocess.run('ping -c 1 ' + host, shell=True)
"""


class TokenizerTests(unittest.TestCase):
    def test_comments_are_removed_but_lines_kept(self):
        source = "<?php\n// 注释 $_GET['x']\n$a = 1; /* 多行\n注释 */\n$b = 2;\n"
        clean = strip_comments(source)
        self.assertEqual(clean.count("\n"), source.count("\n"))
        self.assertNotIn("注释", clean)

    def test_strings_with_semicolons_do_not_split_statements(self):
        statements = split_statements('$a = "a;b"; $b = 2;', "PHP")
        self.assertEqual(len(statements), 2)
        self.assertIn('$a = "a;b"', statements[0][1])

    def test_python_splits_on_newlines(self):
        statements = split_statements("a = 1\nb = 2\n", "Python")
        self.assertEqual(len(statements), 2)


class DataFlowTests(unittest.TestCase):
    def test_php_sql_injection_has_three_step_flow(self):
        findings = analyze_text(PHP_VULN, "login.php", "PHP")
        categories = [item.category for item in findings]
        self.assertIn("SQL Injection", categories)
        finding = next(item for item in findings if item.category == "SQL Injection")
        self.assertGreaterEqual(len(finding.flow), 3)
        self.assertEqual(finding.flow[0].line, 2)          # 污染源赋值
        self.assertEqual(finding.flow[-1].line, 4)         # 危险操作
        self.assertIn("query", finding.flow[-1].code)
        self.assertEqual(finding.source, "dataflow")

    def test_sanitized_php_produces_no_findings(self):
        self.assertEqual(analyze_text(PHP_SAFE, "safe.php", "PHP"), [])

    def test_dom_xss_is_detected_in_js(self):
        findings = analyze_text(JS_DOM, "app.js", "JavaScript")
        self.assertTrue(any(item.category == "Cross-site Scripting" for item in findings))
        finding = next(item for item in findings if item.category == "Cross-site Scripting")
        self.assertIn("innerHTML", finding.flow[-1].code)

    def test_python_command_injection(self):
        findings = analyze_text(PY_CMD, "admin.py", "Python")
        self.assertTrue(any(item.category == "Command Injection" for item in findings))

    def test_untainted_sink_is_not_reported(self):
        source = "<?php\n$rows = $db->query('SELECT id FROM users WHERE id = 1');\n"
        self.assertEqual(analyze_text(source, "static.php", "PHP"), [])


if __name__ == "__main__":
    unittest.main()
