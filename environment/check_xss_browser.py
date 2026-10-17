#!/usr/bin/env python3
"""Record browser DOM observations for local C samples S013-S016.

Run from the repository root with ``python environment/check_xss_browser.py``.
Each navigation uses a new browser profile and the payload only sets a DOM
attribute. No login, Cookie, external URL, or database mutation is needed.
This script records observations; it does not set dataset ground_truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:4280"
SAMPLES = ("S013", "S014", "S015", "S016")
MARKER_SCRIPT = "<script>document.documentElement.dataset.labXss='yes'</script>"
NORMAL_INPUT = "hello"
SOURCE_REF = "origin/c/samples"


class DomProbe(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_attributes: dict[str, str | None] = {}
        self.input_values: dict[str, str | None] = {}
        self.script_bodies: list[str] = []
        self.paragraphs: list[str] = []
        self._paragraph: list[str] | None = None
        self._script: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.html_attributes = attributes
        elif tag == "input" and attributes.get("name") == "q":
            self.input_values["q"] = attributes.get("value")
        elif tag == "p":
            self._paragraph = []
        elif tag == "script":
            self._script = []

    def handle_data(self, data: str) -> None:
        if self._paragraph is not None:
            self._paragraph.append(data)
        if self._script is not None:
            self._script.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._paragraph is not None:
            self.paragraphs.append("".join(self._paragraph))
            self._paragraph = None
        elif tag == "script" and self._script is not None:
            self.script_bodies.append("".join(self._script))
            self._script = None


def find_browser(explicit: str | None) -> Path:
    candidates = [explicit] if explicit else []
    if os.name == "nt":
        candidates += [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
    else:
        candidates += ["google-chrome", "chromium", "chromium-browser", "microsoft-edge"]
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate) or candidate
        path = Path(resolved)
        if path.is_file():
            return path.resolve()
    raise RuntimeError("Chrome or Edge was not found; use --browser with its executable path")


def browser_version(browser: Path) -> str:
    if os.name == "nt":
        escaped = str(browser).replace("'", "''")
        command = f"(Get-Item -LiteralPath '{escaped}').VersionInfo.ProductVersion"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    result = subprocess.run(
        [str(browser), "--version"], capture_output=True, text=True, timeout=15, check=False
    )
    if result.returncode == 0 and (result.stdout.strip() or result.stderr.strip()):
        return (result.stdout.strip() or result.stderr.strip()).splitlines()[0]
    raise RuntimeError(f"Could not determine version of {browser}")


def source_hashes(sample_id: str, source_commit: str) -> dict[str, str]:
    relative = f"dataset/raw/{sample_id}/index.php"
    source = subprocess.run(
        ["git", "cat-file", "blob", f"{source_commit}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    local_path = ROOT / "local" / "lab_cases" / sample_id / "index.php"
    local = local_path.read_bytes()
    source_sha = hashlib.sha256(source).hexdigest()
    local_sha = hashlib.sha256(local).hexdigest()
    if source_sha != local_sha:
        raise RuntimeError(f"{sample_id}: local PHP differs from C commit {source_commit}")

    compose = [
        "docker", "compose", "--env-file", str(ROOT / "local" / "lab.env"),
        "-f", str(ROOT / "third_party" / "DVWA" / "compose.yml"),
        "-f", str(ROOT / "environment" / "compose.lab.yml"),
    ]
    container_path = f"/var/www/html/lab_cases/{sample_id}/index.php"
    result = subprocess.run(
        compose + ["exec", "-T", "dvwa", "sha256sum", container_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    match = re.match(r"([0-9a-f]{64})\s+", result.stdout)
    if not match or match.group(1) != local_sha:
        raise RuntimeError(f"{sample_id}: container PHP hash differs from local/source")
    return {
        "c_commit": source_commit,
        "source_path": relative,
        "source_sha256": source_sha,
        "local_sha256": local_sha,
        "container_sha256": match.group(1),
    }


def request_target(sample_id: str, q: str) -> str:
    return f"/lab_cases/{sample_id}/index.php?{urllib.parse.urlencode({'q': q})}"


def fetch_http_status(url: str) -> int:
    # A proxy-free client with no cookie jar makes this check independent of login.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(url), timeout=15) as response:
        if response.geturl() != url:
            raise RuntimeError(f"Unexpected redirect from {url} to {response.geturl()}")
        return response.status


def dump_rendered_dom(browser: Path, url: str) -> str:
    with tempfile.TemporaryDirectory(prefix="lab-xss-browser-", ignore_cleanup_errors=True) as profile:
        command = [
            str(browser), "--headless=new", "--disable-gpu", "--disable-extensions",
            "--disable-background-networking", "--no-first-run",
            "--no-default-browser-check", "--no-proxy-server",
            f"--user-data-dir={profile}", "--virtual-time-budget=1000",
            "--dump-dom", url,
        ]
        result = subprocess.run(command, capture_output=True, timeout=30, check=False)
    if result.returncode != 0 or not result.stdout:
        detail = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"Browser DOM dump failed (exit {result.returncode}): {detail}")
    dom = result.stdout.decode("utf-8", errors="strict")
    if "<html" not in dom.lower():
        raise RuntimeError("Browser output did not contain an HTML document")
    return dom


def observe(browser: Path, sample_id: str, q: str) -> dict[str, object]:
    target = request_target(sample_id, q)
    url = BASE_URL + target
    status = fetch_http_status(url)
    if status != 200:
        raise RuntimeError(f"{sample_id}: HTTP {status} for {target}")
    dom = dump_rendered_dom(browser, url)
    probe = DomProbe()
    probe.feed(dom)
    return {
        "request_path_query": target,
        "http_status": status,
        "rendered_dom": dom,
        "dom": {
            "html_data_lab_xss": probe.html_attributes.get("data-lab-xss"),
            "script_element_count": len(probe.script_bodies),
            "marker_script_element_present": any(
                "document.documentElement.dataset.labXss='yes'" in body
                for body in probe.script_bodies
            ),
            "paragraph_text": probe.paragraphs,
            "q_input_value": probe.input_values.get("q"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", help="Path to Chrome or Edge executable")
    parser.add_argument("--c-ref", default=SOURCE_REF, help="Reviewed C Git ref or commit")
    parser.add_argument("--samples", nargs="+", choices=SAMPLES, default=list(SAMPLES))
    args = parser.parse_args()

    browser = find_browser(args.browser)
    version = browser_version(browser)
    source_commit = subprocess.run(
        ["git", "rev-parse", "--verify", f"{args.c_ref}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    output_root = ROOT / "evidence" / "truth"
    completed = 0
    for sample_id in args.samples:
        hashes = source_hashes(sample_id, source_commit)
        payload = MARKER_SCRIPT if sample_id in ("S013", "S014") else '">' + MARKER_SCRIPT
        normal = observe(browser, sample_id, NORMAL_INPUT)
        marker = observe(browser, sample_id, payload)
        if sample_id in ("S013", "S014"):
            normal_business = any("搜索词：hello" in text for text in normal["dom"]["paragraph_text"])
        else:
            normal_business = normal["dom"]["q_input_value"] == "hello"
        if not normal_business:
            raise RuntimeError(f"{sample_id}: normal business display was not observed")
        record = {
            "sample_id": sample_id,
            "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "browser": {
                "name": "Chrome" if browser.name.lower().startswith("chrome") else "Edge",
                "version": version,
                "fresh_temporary_profile_per_request": True,
            },
            "source": hashes,
            "normal": normal,
            "marker": marker,
            "observations": {
                "normal_business_observed": normal_business,
                "normal_dom_marker_present": normal["dom"]["html_data_lab_xss"] == "yes",
                "marker_dom_marker_present": marker["dom"]["html_data_lab_xss"] == "yes",
            },
            "note": "Observed DOM only; C review is required before any ground_truth update.",
        }
        destination = output_root / sample_id / "browser_reference.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(
            f"{sample_id}: normal=ok, marker DOM attribute="
            f"{marker['dom']['html_data_lab_xss']!r}; saved {destination.relative_to(ROOT)}"
        )
        completed += 1
    print(f"Recorded {completed} browser references with {browser.name} {version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError, UnicodeError) as error:
        print(f"check_xss_browser: {error}", file=sys.stderr)
        raise SystemExit(1)
