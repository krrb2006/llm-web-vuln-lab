"""Safe archive extraction: no code execution, no path traversal, hard limits."""

from __future__ import annotations

import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from ..config import get_settings

settings = get_settings()

# Only source files we can reason about statically.
ALLOWED_SUFFIXES = {
    ".php", ".phtml", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
    ".py", ".java", ".go", ".rb", ".jsp", ".asp", ".aspx", ".sh",
    ".html", ".htm", ".vue", ".svelte", ".kt", ".cs", ".sql",
}

SKIP_DIRS = {
    ".git", ".github", "node_modules", "vendor", "dist", "build", "out",
    "__pycache__", ".venv", "venv", "env", "target", "bin", "obj",
    ".idea", ".vscode", "coverage", ".next", ".nuxt", "Pods",
}

LANGUAGE_BY_SUFFIX = {
    ".php": "PHP", ".phtml": "PHP", ".js": "JavaScript", ".jsx": "JavaScript",
    ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".py": "Python", ".java": "Java", ".go": "Go", ".rb": "Ruby", ".jsp": "Java",
    ".asp": "Classic ASP", ".aspx": "ASP.NET", ".sh": "Shell", ".html": "HTML",
    ".htm": "HTML", ".vue": "Vue", ".svelte": "Svelte", ".kt": "Kotlin",
    ".cs": "C#", ".sql": "SQL",
}


@dataclass(slots=True)
class ExtractedFile:
    path: Path
    relpath: str
    suffix: str


class ArchiveError(ValueError):
    """Raised when the upload is rejected by the extraction policy."""


def _within(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _is_skipped(relpath: str) -> bool:
    return any(part in SKIP_DIRS for part in Path(relpath).parts)


def _check_member_size(size: int) -> None:
    if size > settings.max_file_kb * 1024:
        raise ArchiveError(f"压缩包内有单个文件超过 {settings.max_file_kb} KiB 限制")


def _extract_zip(archive: Path, target: Path) -> list[str]:
    names: list[str] = []
    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        if len(members) > settings.max_files * 4:
            raise ArchiveError(f"压缩包内条目过多（{len(members)}），超过 {settings.max_files * 4} 限制")
        for info in members:
            if info.is_dir():
                continue
            relpath = info.filename.replace("\\", "/")
            if relpath.startswith("/") or ".." in Path(relpath).parts or _is_skipped(relpath):
                continue
            suffix = Path(relpath).suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                continue
            _check_member_size(info.file_size)
            destination = target / relpath
            if not _within(target, destination):
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, destination.open("wb") as sink:
                shutil.copyfileobj(source, sink, length=1024 * 256)
            names.append(relpath)
    return names


def _extract_tar(archive: Path, target: Path) -> list[str]:
    names: list[str] = []
    with tarfile.open(archive, "r:*") as tf:
        for member in tf.getmembers():
            if not member.isfile() or member.issym() or member.islnk():
                continue
            relpath = member.name.replace("\\", "/")
            if relpath.startswith("/") or ".." in Path(relpath).parts or _is_skipped(relpath):
                continue
            suffix = Path(relpath).suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                continue
            _check_member_size(member.size)
            destination = target / relpath
            if not _within(target, destination):
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = tf.extractfile(member)
            if source is None:
                continue
            with source, destination.open("wb") as sink:
                shutil.copyfileobj(source, sink, length=1024 * 256)
            names.append(relpath)
    return names


def _extract_single_file(archive: Path, target: Path, original_name: str) -> list[str]:
    if Path(original_name).suffix.lower() not in ALLOWED_SUFFIXES:
        raise ArchiveError("只接受压缩包，或受支持的源码文件")
    destination = target / Path(original_name).name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfileobj(archive.open("rb"), destination.open("wb"))
    return [destination.name]


def extract(archive: Path, workdir: Path, original_name: str) -> list[ExtractedFile]:
    """Extract supported source files under ``workdir/src`` and return them."""
    target = workdir / "src"
    target.mkdir(parents=True, exist_ok=True)
    lowered = original_name.lower()

    if lowered.endswith(".zip"):
        names = _extract_zip(archive, target)
    elif lowered.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")):
        names = _extract_tar(archive, target)
    else:
        names = _extract_single_file(archive, target, original_name)

    files: list[ExtractedFile] = []
    for relpath in names:
        path = target / relpath
        if not path.is_file():
            continue
        if path.stat().st_size > settings.max_file_kb * 1024:
            continue
        files.append(ExtractedFile(path=path, relpath=relpath, suffix=path.suffix.lower()))
        if len(files) >= settings.max_files:
            break

    if not files:
        raise ArchiveError("没有找到可分析的源码文件（支持 PHP/JS/TS/Python/Java/Go 等常见源码）")
    return files


def language_counts(files: list[ExtractedFile]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in files:
        language = LANGUAGE_BY_SUFFIX.get(item.suffix, "Other")
        counts[language] = counts.get(language, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))
