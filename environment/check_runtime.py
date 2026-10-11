#!/usr/bin/env python3
"""Check PHP syntax and source hashes in the running local DVWA container.

Writes environment/runtime_check.json. The report contains file hashes and
exit codes only; it never records Compose configuration or environment values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from build_lab_cases import OUTPUT_ROOT, REPO_ROOT, resolve_commit, wanted_files


DVWA_ROOT = REPO_ROOT / "third_party" / "DVWA"
REPORT_PATH = REPO_ROOT / "environment" / "runtime_check.json"
CONTAINER_ROOT = "/var/www/html/lab_cases"
SHA256_PATTERN = re.compile(rb"^([0-9a-f]{64})  ")


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def dvwa_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=DVWA_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=20,
    )
    commit = result.stdout.decode("ascii", errors="replace").strip()
    if result.returncode or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("could not identify the local DVWA commit")
    return commit


def run_command(arguments: list[str]) -> tuple[int | None, bytes]:
    """Return exit code and stdout; intentionally discard diagnostic stderr."""
    try:
        result = subprocess.run(
            arguments,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=30,
        )
        return result.returncode, result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None, b""


def running_container() -> str:
    command = [
        "docker",
        "compose",
        "--env-file",
        str(REPO_ROOT / "local" / "lab.env"),
        "-f",
        str(DVWA_ROOT / "compose.yml"),
        "-f",
        str(REPO_ROOT / "environment" / "compose.lab.yml"),
        "ps",
        "-q",
        "dvwa",
    ]
    code, output = run_command(command)
    container = output.decode("ascii", errors="replace").strip()
    if code != 0 or not re.fullmatch(r"[0-9a-f]{12,64}", container):
        raise RuntimeError("DVWA Compose application container is unavailable")
    return container


def unexpected_runtime_files(expected: set[Path]) -> list[str]:
    if not OUTPUT_ROOT.is_dir() or OUTPUT_ROOT.is_symlink():
        return ["runtime directory missing or a symlink"]
    unexpected = []
    for item in OUTPUT_ROOT.rglob("*"):
        relative = item.relative_to(OUTPUT_ROOT)
        if item.is_symlink() or (item.is_file() and relative not in expected):
            unexpected.append(relative.as_posix())
    return sorted(unexpected)


def check_file(container: str, relative: Path, source: bytes) -> dict[str, object]:
    local_path = OUTPUT_ROOT / relative
    container_path = f"{CONTAINER_ROOT}/{relative.as_posix()}"
    source_hash = sha256(source)
    local_hash = sha256(local_path.read_bytes()) if local_path.is_file() else None

    lint_code, _ = run_command(["docker", "exec", container, "php", "-l", container_path])
    hash_code, hash_output = run_command(
        ["docker", "exec", container, "sha256sum", container_path]
    )
    match = SHA256_PATTERN.match(hash_output)
    container_hash = match.group(1).decode("ascii") if hash_code == 0 and match else None

    source_matches_local = local_hash == source_hash
    container_matches_local = local_hash is not None and container_hash == local_hash
    passed = source_matches_local and lint_code == 0 and container_matches_local
    return {
        "path": relative.as_posix(),
        "source_sha256": source_hash,
        "local_sha256": local_hash,
        "container_sha256": container_hash,
        "source_matches_local": source_matches_local,
        "container_matches_local": container_matches_local,
        "php_lint_exit_code": lint_code,
        "sha256sum_exit_code": hash_code,
        "passed": passed,
    }


def write_report(report: dict[str, object]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=".runtime-check-", dir=REPORT_PATH.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as temporary_file:
            json.dump(report, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
        os.replace(temporary_name, REPORT_PATH)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a-ref", default="origin/a/criteria-and-sql01")
    parser.add_argument("--c-ref", default="origin/c/samples")
    args = parser.parse_args()

    try:
        a_commit = resolve_commit(args.a_ref)
        c_commit = resolve_commit(args.c_ref)
        sources = wanted_files(a_commit, c_commit)
        if len(sources) != 23 or any(path.suffix != ".php" for path in sources):
            raise RuntimeError("expected exactly 23 PHP runtime files")
        dvwa_revision = dvwa_commit()
        container = running_container()
        unexpected = unexpected_runtime_files(set(sources))
        results = [
            check_file(container, relative, source)
            for relative, source in sorted(sources.items())
        ]
        passed = sum(item["passed"] is True for item in results)
        report = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
                "+00:00", "Z"
            ),
            "a_source": {"ref": args.a_ref, "commit": a_commit},
            "c_source": {"ref": args.c_ref, "commit": c_commit},
            "dvwa_commit": dvwa_revision,
            "summary": {
                "total": len(results),
                "passed": passed,
                "failed": len(results) - passed,
                "unexpected_runtime_files": unexpected,
            },
            "files": results,
        }
        write_report(report)
        print(f"Runtime check: {passed}/{len(results)} PHP files passed.")
        print(f"Report: {REPORT_PATH}")
        return 0 if passed == len(results) and not unexpected else 1
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"check_runtime: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
