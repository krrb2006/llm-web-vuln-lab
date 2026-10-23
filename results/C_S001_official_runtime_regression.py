#!/usr/bin/env python3
"""Run only PHP lint and name=Alice ordinary requests in a disposable container."""
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ghcr.io/digininja/dvwa@sha256:1af2cedda7617e4d22937e61c98bbf71d8b74b98e46f5e41dd6aa0a5183311b0"
ATTACKS = ("ignore_task", "force_safe_verdict", "request_hidden_rules", "divert_output")
def sha(value):
    return hashlib.sha256(value).hexdigest()
def run(args, env=None):
    return subprocess.run(args, capture_output=True, text=True, env=env)
def main():
    env_file = Path(os.environ["C_AUDIT_LAB_ENV"])
    password = next(line.split("=", 1)[1].strip() for line in env_file.read_text(encoding="utf-8").splitlines()
                    if line.startswith("LAB_DB_PASSWORD="))
    env = os.environ.copy()
    env["DB_PASSWORD"] = password
    evidence = {"runtime_image": IMAGE, "php_version": None, "ordinary_input": "name=Alice",
                "poc_executed": False, "source_data_modified": False, "packages": {}}
    with tempfile.TemporaryDirectory(prefix="c_s001_official_") as tmp:
        root = Path(tmp)
        (root / "cases/common").mkdir(parents=True)
        (root / "cases/common/db_connect.php").write_bytes((ROOT / "dataset/raw/common/db_connect.php").read_bytes())
        for attack in ATTACKS:
            src = ROOT / f"experiments/prompt_injection/official_packets/S001/{attack}/code_input.txt"
            rows = []
            for line in src.read_text(encoding="utf-8").splitlines():
                m = re.match(r"F01:(\d{4}) \|(?: ?)(.*)$", line)
                if m: rows.append(m.group(2))
            if len(rows) != 24:
                raise RuntimeError(f"{attack}: expected 24 source lines, found {len(rows)}")
            dest = root / f"cases/{attack}/index.php"
            dest.parent.mkdir()
            dest.write_text("\n".join(rows) + "\n", encoding="utf-8")
            evidence["packages"][attack] = {"extracted_php_sha256": sha(dest.read_bytes())}
        mount = str(root.resolve()) + ":/audit:ro"
        ver = run(["docker", "run", "--rm", "--pull", "never", "-v", mount, IMAGE, "php", "-v"])
        evidence["php_version"] = ver.stdout.splitlines()[0] if ver.returncode == 0 else None
        for attack in ATTACKS:
            path = f"/audit/cases/{attack}/index.php"
            lint = run(["docker", "run", "--rm", "--pull", "never", "-v", mount, IMAGE, "php", "-l", path])
            evidence["packages"][attack]["php_lint"] = {
                "returncode": lint.returncode, "stdout": lint.stdout.strip(), "stderr": lint.stderr.strip()}
        started = run(["docker", "run", "--rm", "-d", "--pull", "never", "--network", "dvwa_dvwa",
                       "-p", "127.0.0.1:18081:18081", "-v", mount,
                       "-e", "DB_HOST=db", "-e", "DB_PORT=3306", "-e", "DB_NAME=teaching_lab",
                       "-e", "DB_USER=lab_user", "-e", "DB_PASSWORD",
                       IMAGE, "php", "-S", "0.0.0.0:18081", "-t", "/audit/cases"], env=env)
        if started.returncode != 0:
            evidence["startup_error"] = started.stderr.strip()
        else:
            cid = started.stdout.strip()
            try:
                for attack in ATTACKS:
                    url = f"http://127.0.0.1:18081/{attack}/index.php?name=Alice"
                    response = None
                    error = None
                    for _ in range(12):
                        try:
                            with urllib.request.urlopen(url, timeout=4) as h:
                                response = (h.status, h.read())
                            break
                        except Exception as exc:
                            error = str(exc)
                            time.sleep(1)
                    if response is None:
                        evidence["packages"][attack]["normal_http"] = {"status": "unavailable", "error": error}
                    else:
                        status, body = response
                        text = body.decode("utf-8", errors="replace")
                        evidence["packages"][attack]["normal_http"] = {
                            "http_status": status, "response_sha256": sha(body),
                            "contains_alice": "ID 1：Alice" in text,
                            "contains_bob": "Bob" in text, "contains_carol": "Carol" in text,
                            "php_fatal_visible": "Fatal error" in text,
                            "status": "pass" if status == 200 and "ID 1：Alice" in text
                                      and "Bob" not in text and "Carol" not in text and "Fatal error" not in text
                                      else "fail",
                            "response_utf8": text}
            finally:
                run(["docker", "stop", cid])
    out = ROOT / "results/C_S001_official_runtime_regression.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
if __name__ == "__main__":
    main()
