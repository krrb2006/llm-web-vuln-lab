#!/usr/bin/env python3
"""Build isolated runtime copies for the four advanced bonus cases.

The source blueprints remain unchanged. Runtime copies use the lab bootstrap,
add the documented $conn compatibility alias, and expose a local-only session
setter for the IDOR comparison.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "local" / "lab_cases" / "advanced"
SOURCE = ROOT / "experiments" / "advanced_cases"
REQUIRE = "require __DIR__ . '/../../../../dataset/raw/common/db_connect.php';"
RUNTIME_REQUIRE = "require __DIR__ . '/../../../common/db_connect.php';\n$conn = $db;"


def write_verified(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    fd, tmp = tempfile.mkstemp(prefix=".advanced-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"SHA-256 mismatch after writing {path}")
    return digest


def main() -> int:
    expected = []
    for case in ("SECOND_SQLI_01", "IDOR_01"):
        for variant in ("vulnerable", "fixed"):
            for source in sorted((SOURCE / case / variant).glob("*.php")):
                text = source.read_text(encoding="utf-8")
                if REQUIRE not in text:
                    raise RuntimeError(f"unexpected database include in {source}")
                runtime = text.replace(REQUIRE, RUNTIME_REQUIRE)
                destination = OUTPUT / case / variant / source.name
                digest = write_verified(destination, runtime.encode("utf-8"))
                expected.append((destination.relative_to(ROOT).as_posix(), digest))

    session_setter = """<?php
declare(strict_types=1);
// Local-only test harness; not part of the application authorization model.
session_start();
$_SESSION['user_id'] = (int)($_GET['user_id'] ?? 0);
header('Content-Type: text/plain; charset=utf-8');
echo 'session_user=' . (int)$_SESSION['user_id'];
"""
    setter = OUTPUT / "IDOR_01" / "set_user.php"
    expected.append((setter.relative_to(ROOT).as_posix(), write_verified(setter, session_setter.encode("utf-8"))))
    print("advanced runtime ready")
    for path, digest in expected:
        print(f"{digest}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
