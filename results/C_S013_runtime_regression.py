"""Run safe PHP lint and ordinary q=hello regression for S013 packages.

The four files are extracted from the line-numbered packets into a host
temporary directory, copied to the already configured D container, linted with
that container's PHP, and served through PHP's built-in server. No generated
POC or attack payload is sent.
"""
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from C_S013_verify import ATTACKS, MANIFEST, digest, extract_php, file_hash


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "C_S013_runtime_regression.json"
CONTAINER_DIR = "/tmp/s013_c_audit_runtime"
PORT = 18080


def run(args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False, timeout=45)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}")
    return result


def docker_exec(container: str, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return run(["docker", "exec", container, *args], check=check)


def container_name() -> str:
    result = run(["docker", "ps", "--filter", "name=dvwa-dvwa-1", "--format", "{{.Names}}"], check=True)
    name = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    if not name:
        raise RuntimeError("D DVWA container is not running")
    return name


def php_version(container: str) -> str:
    return docker_exec(container, "php", "-v", check=True).stdout.splitlines()[0]


def request_inside(container: str, path: str) -> dict:
    # The PHP one-liner makes an HTTP request inside the same container. The
    # q=hello value is ordinary business input, not a POC.
    client = (
        "$u=$argv[1];"
        "$c=stream_context_create(['http'=>['ignore_errors'=>true]]);"
        "$b=@file_get_contents($u,false,$c);"
        "$h=$http_response_header??[];"
        "$s=0; foreach($h as $x){if(preg_match('/^HTTP\\/[^ ]+ ([0-9]+)/',$x,$m)){$s=(int)$m[1];}};"
        "echo json_encode(['status'=>$s,'body_b64'=>base64_encode($b===false?'':$b),'headers'=>$h],JSON_UNESCAPED_SLASHES);"
    )
    result = docker_exec(container, "php", "-r", client, f"http://127.0.0.1:{PORT}/{path}?q=hello")
    if result.returncode:
        raise RuntimeError(f"ordinary HTTP request failed for {path}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def main() -> int:
    container = container_name()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    original_packet = ROOT / MANIFEST["source_path"]
    result: dict = {
        "kind": "s013_injection_php_lint_and_normal_business_regression",
        "started_at_utc": started,
        "container": container,
        "php_version": php_version(container),
        "ordinary_input": "q=hello",
        "poc_executed": False,
        "packages": {},
    }
    host_temp = Path(tempfile.mkdtemp(prefix="s013_runtime_"))
    try:
        docker_exec(container, "sh", "-c", f"rm -rf {CONTAINER_DIR} && mkdir -p {CONTAINER_DIR}", check=True)
        for attack, entry in MANIFEST["attacks"].items():
            raw = extract_php(ROOT / entry["packet_path"])
            host_file = host_temp / f"{attack}.php"
            host_file.write_bytes(raw)
            destination = f"{CONTAINER_DIR}/{attack}.php"
            run(["docker", "cp", str(host_file), f"{container}:{destination}"], check=True)
            lint = docker_exec(container, "php", "-l", destination)
            result["packages"][attack] = {
                "packet_path": entry["packet_path"],
                "extracted_php_sha256": digest(raw),
                "container_file": destination,
                "php_lint": {
                    "status": "pass" if lint.returncode == 0 else "fail",
                    "returncode": lint.returncode,
                    "stdout": lint.stdout.strip(),
                    "stderr": lint.stderr.strip(),
                },
            }

        server = docker_exec(
            container,
            "sh",
            "-c",
            f"php -S 127.0.0.1:{PORT} -t {CONTAINER_DIR} >/tmp/s013_c_audit_php_server.log 2>&1 & echo $!",
            check=True,
        )
        pid = server.stdout.strip().splitlines()[-1]
        time.sleep(1)
        try:
            for attack in MANIFEST["attacks"]:
                observed = request_inside(container, f"{attack}.php")
                body = base64.b64decode(observed.get("body_b64", ""))
                text = body.decode("utf-8", errors="replace")
                result["packages"][attack]["normal_http"] = {
                    "status": "pass" if (
                        observed.get("status") == 200
                        and "<p>搜索词：hello</p>" in text
                        and "Fatal error" not in text
                    ) else "fail",
                    "http_status": observed.get("status"),
                    "response_sha256": hashlib.sha256(body).hexdigest(),
                    "response_contains_expected_business_text": "<p>搜索词：hello</p>" in text,
                    "php_fatal_error_visible": "Fatal error" in text,
                    "response_headers": observed.get("headers", []),
                }
        finally:
            docker_exec(container, "kill", pid)
    finally:
        docker_exec(container, "sh", "-c", f"rm -rf {CONTAINER_DIR}")
        shutil.rmtree(host_temp, ignore_errors=True)
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result["all_php_lint_passed"] = all(p["php_lint"]["status"] == "pass" for p in result["packages"].values())
    result["all_normal_http_passed"] = all(p["normal_http"]["status"] == "pass" for p in result["packages"].values())
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUT)
    print("php_lint", result["all_php_lint_passed"], "normal_http", result["all_normal_http_passed"])
    for attack, package in result["packages"].items():
        print(attack, package["php_lint"]["status"], package["normal_http"]["status"], package["normal_http"]["http_status"])
    return 0 if result["all_php_lint_passed"] and result["all_normal_http_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
