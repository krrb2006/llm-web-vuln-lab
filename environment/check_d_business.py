#!/usr/bin/env python3
"""Record ordinary business-flow HTTP observations for local D samples.

Only the loopback teaching site is contacted. Stored fixtures are fictitious,
sample-scoped, and removed after observation. These records are not truth labels.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:4280"
STORED = ("S017", "S018", "S021", "S022")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str | None] = []
        self.inputs: dict[str, str | None] = {}
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a":
            self.links.append(attributes.get("href"))
        if tag == "input" and attributes.get("name"):
            self.inputs[attributes["name"]] = attributes.get("value")

    def handle_data(self, data):
        self.text.append(data)


def fetch(sample: str, endpoint: str, *, method: str = "GET", fields: dict[str, str] | None = None) -> dict:
    path = f"/lab_cases/{sample}/{endpoint}"
    data = urllib.parse.urlencode(fields).encode("utf-8") if fields is not None else None
    request = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"User-Agent": "D-business-check/1.0"},
    )
    try:
        response = OPENER.open(request, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read()
        status = response.status
        location = response.headers.get("Location")
        content_type = response.headers.get("Content-Type", "")
    decoded = body.decode("utf-8", errors="replace")
    parser = PageParser()
    parser.feed(decoded)
    return {
        "method": method,
        "path": path,
        "form_fields": fields,
        "status": status,
        "location": location,
        "content_type": content_type,
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "response_body_utf8": decoded,
        "parsed_links": parser.links,
        "parsed_inputs": parser.inputs,
        "parsed_text": " ".join(part.strip() for part in parser.text if part.strip()),
        "php_fatal_error_visible": "Fatal error" in decoded,
    }


def fetch_url(sample: str, endpoint: str, parameters: dict[str, str]) -> dict:
    path = endpoint + "?" + urllib.parse.urlencode(parameters)
    result = fetch(sample, path)
    result["query_parameters"] = parameters
    return result


def reset_sample(sample: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "environment" / "init_lab_db.py"), "--reset-sample", sample],
        cwd=ROOT, capture_output=True, text=True, timeout=90, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"{sample}: database sample reset failed: {result.stderr.strip()}")


def require(check: bool, message: str) -> None:
    if not check:
        raise RuntimeError(message)


def report(sample: str, observations: list[dict], *, notes: list[str]) -> None:
    for item in observations:
        require(not item["php_fatal_error_visible"], f"{sample}: visible PHP fatal error")
    runtime = json.loads((ROOT / "environment" / "runtime_check.json").read_text(encoding="utf-8"))
    content = {
        "kind": "ordinary_business_http_observation",
        "review_status": "pending_independent_review",
        "ground_truth": None,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "base_url": BASE,
        "sample_id": sample,
        "d_source_commit": runtime["d_source"]["commit"],
        "runtime_check": {"passed": runtime["summary"]["passed"], "total": runtime["summary"]["total"]},
        "notes": notes,
        "requests": observations,
    }
    destination = ROOT / "evidence" / "truth" / sample / "business_http.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{sample}: {len(observations)} normal-flow requests recorded")


def check_guestbook(sample: str) -> None:
    reset_sample(sample)
    greeting = f"Hello from {sample} teaching lab"
    empty = fetch(sample, "index.php")
    posted = fetch(sample, "index.php", method="POST", fields={"body": greeting})
    after = fetch(sample, "index.php")
    require(empty["status"] == 200 and greeting not in empty["parsed_text"], f"{sample}: empty board")
    require(posted["status"] == 303 and posted["location"] == "index.php", f"{sample}: POST redirect")
    require(after["status"] == 200 and greeting in after["parsed_text"], f"{sample}: stored readback")
    report(sample, [empty, posted, after], notes=["Sample rows reset before this flow and again after all flows."])


def check_preview_form(sample: str) -> None:
    greeting = f"Hello from {sample} teaching lab"
    empty = fetch(sample, "index.php")
    posted = fetch(sample, "index.php", method="POST", fields={"content": greeting})
    require(empty["status"] == 200 and "内容预览" in empty["parsed_text"], f"{sample}: form GET")
    require(posted["status"] == 200 and greeting in posted["parsed_text"], f"{sample}: POST preview")
    require(posted["parsed_text"].count(greeting) == 2, f"{sample}: form and preview both shown")
    report(sample, [empty, posted], notes=["The ordinary preview appears in both textarea and preview region."])


def check_draft(sample: str) -> None:
    reset_sample(sample)
    title = f"Teaching draft {sample}"
    body = f"Hello from {sample} teaching lab"
    form = fetch(sample, "submit.php")
    posted = fetch(sample, "submit.php", method="POST", fields={"title": title, "body": body})
    location = posted["location"] or ""
    require(form["status"] == 200 and "提交草稿" in form["parsed_text"], f"{sample}: form GET")
    require(posted["status"] == 303 and re.fullmatch(r"preview\.php\?id=[1-9][0-9]*", location) is not None, f"{sample}: POST redirect")
    listing = fetch(sample, "list.php")
    preview = fetch(sample, location)
    require(listing["status"] == 200 and title in listing["parsed_text"], f"{sample}: list readback")
    require(preview["status"] == 200 and title in preview["parsed_text"] and body in preview["parsed_text"], f"{sample}: preview readback")
    report(sample, [form, posted, listing, preview], notes=["Sample rows reset before this flow and again after all flows."])


def check_link(sample: str) -> None:
    default = fetch(sample, "index.php")
    local_url = BASE + "/login.php"
    local = fetch_url(sample, "index.php", {"url": local_url})
    external = fetch_url(sample, "index.php", {"url": "https://example.org/"})
    require(default["status"] == local["status"] == external["status"] == 200, f"{sample}: link GET")
    require("https://example.org/" in default["parsed_links"], f"{sample}: default link")
    require(local_url in local["parsed_links"], f"{sample}: local link")
    require("https://example.org/" in external["parsed_links"], f"{sample}: external address in attribute")
    report(sample, [default, local, external], notes=["External example.org address was inspected in HTML only; it was not requested or clicked."])


def main() -> int:
    runtime = json.loads((ROOT / "environment" / "runtime_check.json").read_text(encoding="utf-8"))
    require(runtime["summary"] == {"total": 37, "passed": 37, "failed": 0, "unexpected_runtime_files": []}, "37/37 runtime checks required")
    require("d_source" in runtime, "D source commit missing from runtime report")
    try:
        for sample in ("S017", "S018"):
            check_guestbook(sample)
        for sample in ("S019", "S020"):
            check_preview_form(sample)
        for sample in ("S021", "S022"):
            check_draft(sample)
        for sample in ("S023", "S024"):
            check_link(sample)
    finally:
        for sample in STORED:
            reset_sample(sample)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
