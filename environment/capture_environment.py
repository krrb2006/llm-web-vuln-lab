#!/usr/bin/env python3
"""Capture reproducible, redacted facts about the running local lab."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DVWA = ROOT / "third_party" / "DVWA"
COMPOSE = [
    "docker", "compose", "--env-file", str(ROOT / "local" / "lab.env"),
    "-f", str(DVWA / "compose.yml"),
    "-f", str(ROOT / "environment" / "compose.lab.yml"),
]
PRIVATE_KEY = re.compile(r"PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY", re.IGNORECASE)


def run(*command: str) -> str:
    return subprocess.run(
        list(command), cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True, timeout=30,
    ).stdout.strip()


def sanitize(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: "<redacted>" if PRIVATE_KEY.search(key) else sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return value.replace(str(ROOT), "<repo>").replace(str(ROOT).replace("\\", "/"), "<repo>")
    return value


def main() -> int:
    out = ROOT / "environment"
    runtime = json.loads((out / "runtime_check.json").read_text(encoding="utf-8"))
    config = json.loads(run(*COMPOSE, "config", "--format", "json"))
    redacted = sanitize(config)
    config_text = json.dumps(redacted, ensure_ascii=False, indent=2) + "\n"
    if "LAB_DB_PASSWORD=" in config_text or "p@ssw0rd" in config_text:
        raise RuntimeError("Compose redaction failed")
    (out / "compose_effective.redacted.json").write_text(config_text, encoding="utf-8")
    (out / "services.txt").write_text(run(*COMPOSE, "ps") + "\n", encoding="utf-8")

    official_low = DVWA / "vulnerabilities" / "sqli" / "source" / "low.php"
    low_local = hashlib.sha256(official_low.read_bytes()).hexdigest()
    low_container = run(*COMPOSE, "exec", "-T", "dvwa", "sha256sum", "/var/www/html/vulnerabilities/sqli/source/low.php").split()[0]
    if low_local != low_container:
        raise RuntimeError("Official DVWA low.php differs between checkout and running container")

    with urllib.request.urlopen("http://127.0.0.1:4280/login.php", timeout=10) as response:
        login_status = response.status
    browser_record = ROOT / "evidence" / "truth" / "S013" / "browser_reference.json"
    browser = json.loads(browser_record.read_text(encoding="utf-8"))["browser"] if browser_record.exists() else None

    facts = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "team_repo_base_commit": run("git", "rev-parse", "main"),
        "a_source_commit": runtime["a_source"]["commit"],
        "c_source_commit": runtime["c_source"]["commit"],
        "dvwa_checkout_commit": run("git", "-C", str(DVWA), "rev-parse", "HEAD"),
        "dvwa_image": config["services"]["dvwa"]["image"],
        "mariadb_image": config["services"]["db"]["image"],
        "dvwa_image_id": run("docker", "image", "inspect", config["services"]["dvwa"]["image"], "--format", "{{.Id}}"),
        "mariadb_image_id": run("docker", "image", "inspect", config["services"]["db"]["image"], "--format", "{{.Id}}"),
        "docker_server_version": run("docker", "version", "--format", "{{.Server.Version}}"),
        "docker_compose_version": run("docker", "compose", "version", "--short"),
        "php_version_in_dvwa": run(*COMPOSE, "exec", "-T", "dvwa", "php", "-r", "echo PHP_VERSION;"),
        "mariadb_server_version": run(*COMPOSE, "exec", "-T", "db", "sh", "-c", 'mariadb -uroot -p"$MYSQL_ROOT_PASSWORD" --batch --skip-column-names -e "SELECT VERSION()"'),
        "browser_used_for_xss_reference": browser,
        "host_binding": "127.0.0.1:4280",
        "dvwa_login_http_status": login_status,
        "official_low_php_local_sha256": low_local,
        "official_low_php_container_sha256": low_container,
        "runtime_php_checks": runtime["summary"],
    }
    lines = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in facts.items()]
    (out / "version.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Captured redacted Compose config, services, and version facts.")
    print(f"DVWA login HTTP {login_status}; official low.php hashes match: {low_local == low_container}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
