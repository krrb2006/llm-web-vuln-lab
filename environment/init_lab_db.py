#!/usr/bin/env python3
"""Start the local MariaDB service and seed the isolated teaching database.

The generated password stays in local/lab.env (ignored by Git). This script
only changes teaching_lab; it does not reset DVWA's own database or volume.
"""

from __future__ import annotations

import argparse
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV = ROOT / "local" / "lab.env"
DVWA_COMPOSE = ROOT / "third_party" / "DVWA" / "compose.yml"
LAB_COMPOSE = ROOT / "environment" / "compose.lab.yml"
PASSWORD_PATTERN = re.compile(r"[0-9a-f]{48}\Z")


def load_or_create_password() -> str:
    LOCAL_ENV.parent.mkdir(parents=True, exist_ok=True)
    if LOCAL_ENV.exists():
        lines = LOCAL_ENV.read_text(encoding="utf-8").splitlines()
        values = [line.partition("=")[2] for line in lines if line.startswith("LAB_DB_PASSWORD=")]
        if len(values) != 1 or not PASSWORD_PATTERN.fullmatch(values[0]):
            raise RuntimeError(f"Invalid LAB_DB_PASSWORD in {LOCAL_ENV}")
        return values[0]

    password = secrets.token_hex(24)
    with LOCAL_ENV.open("x", encoding="utf-8", newline="\n") as file:
        file.write(f"LAB_DB_PASSWORD={password}\n")
    if sys.platform != "win32":
        LOCAL_ENV.chmod(0o600)
    return password


def compose_command() -> list[str]:
    if not DVWA_COMPOSE.is_file():
        raise RuntimeError(f"Official DVWA Compose file is missing: {DVWA_COMPOSE}")
    return [
        "docker", "compose", "--env-file", str(LOCAL_ENV),
        "-f", str(DVWA_COMPOSE), "-f", str(LAB_COMPOSE),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset-data", action="store_true",
        help="delete rows only from teaching_lab.lab_people before seeding three fictitious rows",
    )
    args = parser.parse_args()

    password = load_or_create_password()
    compose = compose_command()
    subprocess.run(compose + ["up", "-d", "db"], cwd=ROOT, check=True)

    reset_sql = "DELETE FROM teaching_lab.lab_people;\n" if args.reset_data else ""
    sql = f"""
CREATE DATABASE IF NOT EXISTS teaching_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS teaching_lab.lab_people (
    id INT PRIMARY KEY,
    name VARCHAR(80) NOT NULL
) CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'lab_user'@'%' IDENTIFIED BY '{password}';
ALTER USER 'lab_user'@'%' IDENTIFIED BY '{password}';
GRANT SELECT ON teaching_lab.lab_people TO 'lab_user'@'%';
{reset_sql}INSERT INTO teaching_lab.lab_people (id, name) VALUES
    (1, 'Alice'), (2, 'Bob'), (3, 'Carol')
    ON DUPLICATE KEY UPDATE name = VALUES(name);
SELECT COUNT(*) FROM teaching_lab.lab_people;
"""
    command = compose + [
        "exec", "-T", "db", "sh", "-c",
        'exec mariadb -uroot -p"$MYSQL_ROOT_PASSWORD" --batch --skip-column-names',
    ]
    for attempt in range(1, 31):
        result = subprocess.run(command, input=sql, text=True, capture_output=True, cwd=ROOT)
        if result.returncode == 0:
            counts = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            if not counts or counts[-1] != "3":
                raise RuntimeError(
                    "lab_people does not contain exactly three rows; "
                    "inspect the teaching data or rerun with --reset-data"
                )
            print("teaching_lab.lab_people ready: 1 Alice, 2 Bob, 3 Carol")
            print("Local credentials stored in ignored local/lab.env")
            return 0
        if attempt == 30:
            raise RuntimeError(result.stderr.strip() or "MariaDB initialization failed")
        time.sleep(1)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
