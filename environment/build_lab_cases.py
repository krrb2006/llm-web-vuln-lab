#!/usr/bin/env python3
"""Build the PHP-only local lab tree from pinned A and C Git revisions.

Run from anywhere with ``python environment/build_lab_cases.py``. The output
is ``local/lab_cases`` under this repository and is ignored by Git. Only the
listed PHP files are copied; sample cards and internal truth notes never enter
the web document root.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = REPO_ROOT / "local" / "lab_cases"
BOOTSTRAP = b"<?php\nrequire_once __DIR__ . '/../common/db_connect.php';\n"


def git_bytes(*arguments: str) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(arguments)} failed: {detail}")
    return result.stdout


def resolve_commit(ref: str) -> str:
    if not ref or ref.startswith("-"):
        raise ValueError(f"invalid Git ref: {ref!r}")
    commit = git_bytes("rev-parse", "--verify", f"{ref}^{{commit}}").decode("ascii").strip()
    if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
        raise RuntimeError(f"could not resolve {ref!r} to a full commit hash")
    return commit


def source_file(commit: str, relative_path: str) -> bytes:
    return git_bytes("cat-file", "blob", f"{commit}:{relative_path}")


def wanted_files(a_commit: str, c_commit: str, d_commit: str | None = None) -> dict[Path, bytes]:
    files: dict[Path, bytes] = {}

    for number in range(1, 9):
        sample_id = f"S{number:03d}"
        files[Path(sample_id) / "index.php"] = source_file(
            a_commit, f"dataset/raw/{sample_id}/index.php"
        )
    for sample_id in ("S007", "S008"):
        files[Path(sample_id) / "repository.php"] = source_file(
            a_commit, f"dataset/raw/{sample_id}/repository.php"
        )
    files[Path("common") / "db_connect.php"] = source_file(
        a_commit, "dataset/raw/common/db_connect.php"
    )

    for number in range(9, 17):
        sample_id = f"S{number:03d}"
        files[Path(sample_id) / "index.php"] = source_file(
            c_commit, f"dataset/raw/{sample_id}/index.php"
        )
    for number in range(9, 13):
        files[Path(f"S{number:03d}") / "bootstrap.php"] = BOOTSTRAP

    if d_commit is not None:
        for number in range(17, 25):
            sample_id = f"S{number:03d}"
            prefix = f"dataset/raw/{sample_id}/"
            paths = git_bytes("ls-tree", "-r", "--name-only", d_commit, "--", prefix)
            php_paths = [
                path for path in paths.decode("utf-8").splitlines()
                if path.startswith(prefix) and path.endswith(".php")
            ]
            if not php_paths:
                raise RuntimeError(f"no PHP files found for {sample_id} in D commit {d_commit}")
            for path in php_paths:
                relative_path = Path(path).relative_to("dataset/raw")
                files[relative_path] = source_file(d_commit, path)

    return files


def check_output_directory(expected_paths: set[Path]) -> None:
    if OUTPUT_ROOT.is_symlink():
        raise RuntimeError(f"refusing to write through symlink: {OUTPUT_ROOT}")
    if not OUTPUT_ROOT.exists():
        return
    for existing in OUTPUT_ROOT.rglob("*"):
        if existing.is_symlink():
            raise RuntimeError(f"refusing to use symlink in runtime tree: {existing}")
        if existing.is_file() and existing.relative_to(OUTPUT_ROOT) not in expected_paths:
            raise RuntimeError(
                f"unexpected file in runtime tree (left untouched): {existing}"
            )


def write_and_verify(relative_path: Path, content: bytes) -> tuple[str, bool]:
    destination = OUTPUT_ROOT / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected_sha256 = hashlib.sha256(content).hexdigest()

    if destination.is_file() and destination.read_bytes() == content:
        changed = False
    else:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".lab-case-", dir=destination.parent
        )
        try:
            with os.fdopen(descriptor, "wb") as temporary_file:
                temporary_file.write(content)
            os.replace(temporary_name, destination)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
        changed = True

    actual_sha256 = hashlib.sha256(destination.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError(f"SHA-256 mismatch after copying {relative_path}")
    return actual_sha256, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--a-ref", default="origin/a/criteria-and-sql01", help="Git ref containing S001-S008"
    )
    parser.add_argument(
        "--c-ref", default="origin/c/samples", help="Git ref containing S009-S016"
    )
    parser.add_argument(
        "--d-ref", help="Git ref containing S017-S024; omit while those files are not committed"
    )
    args = parser.parse_args()

    try:
        a_commit = resolve_commit(args.a_ref)
        c_commit = resolve_commit(args.c_ref)
        d_commit = resolve_commit(args.d_ref) if args.d_ref else None
        files = wanted_files(a_commit, c_commit, d_commit)
        check_output_directory(set(files))
        changed_count = 0
        print(f"A source: {args.a_ref} ({a_commit})")
        print(f"C source: {args.c_ref} ({c_commit})")
        if d_commit is not None:
            print(f"D source: {args.d_ref} ({d_commit})")
        print(f"Runtime directory: {OUTPUT_ROOT}")
        for relative_path, content in sorted(files.items()):
            digest, changed = write_and_verify(relative_path, content)
            changed_count += changed
            print(f"{digest}  {relative_path.as_posix()}")
        print(f"Verified {len(files)} PHP files; wrote {changed_count}.")
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"build_lab_cases: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
