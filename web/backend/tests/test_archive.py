"""Archive extraction safety tests."""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from app.config import get_settings
from app.services.archive import ArchiveError, extract

settings = get_settings()


def _make_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return path


class ArchiveSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_zip_slip_members_are_ignored(self):
        archive = _make_zip(
            self.root / "evil.zip",
            {
                "../../../evil.php": b"<?php echo 'pwn';",
                "/abs/evil.php": b"<?php echo 'pwn';",
                "src/index.php": b"<?php echo $_GET['q'];",
            },
        )
        workdir = self.root / "work"
        workdir.mkdir()
        files = extract(archive, workdir, "evil.zip")
        relpaths = {item.relpath for item in files}
        self.assertEqual(relpaths, {"src/index.php"})
        self.assertFalse((self.root.parent / "evil.php").exists())

    def test_non_source_files_are_filtered(self):
        archive = _make_zip(
            self.root / "mixed.zip",
            {"a.php": b"<?php", "b.exe": b"MZ", "c.png": b"\x89PNG", "node_modules/x.js": b"1"},
        )
        workdir = self.root / "work"
        workdir.mkdir()
        relpaths = {item.relpath for item in extract(archive, workdir, "mixed.zip")}
        self.assertEqual(relpaths, {"a.php"})

    def test_empty_archive_is_rejected(self):
        archive = _make_zip(self.root / "empty.zip", {"readme.md": b"hello"})
        workdir = self.root / "work"
        workdir.mkdir()
        with self.assertRaises(ArchiveError):
            extract(archive, workdir, "empty.zip")

    def test_oversized_single_file_is_rejected(self):
        original = settings.max_file_kb
        settings.max_file_kb = 1
        try:
            archive = _make_zip(self.root / "big.zip", {"big.php": b"a" * 4096})
            workdir = self.root / "work"
            workdir.mkdir()
            with self.assertRaises(ArchiveError):
                extract(archive, workdir, "big.zip")
        finally:
            settings.max_file_kb = original


if __name__ == "__main__":
    unittest.main()
