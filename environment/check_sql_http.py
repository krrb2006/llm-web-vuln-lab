#!/usr/bin/env python3
"""Record local, read-only reference HTTP observations for S001-S012.

These are D's reference requests, not model-generated POCs or reviewed truth.
The target is fixed to loopback and the test data are the three fictitious
lab_people rows. No cookies or login credentials are sent or saved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:4280"
ROWS = re.compile(r"(?:ID\s*)?([0-9]+)：(Alice|Bob|Carol)")
MARKERS = {
    "S001": ("name", [("normal_hit", "Alice"), ("normal_miss", "ZZZ"), ("controlled_true", "x' OR '1'='1"), ("controlled_false", "x' AND '1'='2")]),
    "S002": ("name", [("normal_hit", "Alice"), ("normal_miss", "ZZZ"), ("controlled_true", "x' OR '1'='1"), ("controlled_false", "x' AND '1'='2")]),
    "S003": ("id", [("normal_hit", "1"), ("normal_miss", "999"), ("controlled_true", "1 OR 1=1"), ("controlled_false", "1 AND 1=2")]),
    "S004": ("id", [("normal_hit", "1"), ("normal_miss", "999"), ("controlled_true", "1 OR 1=1"), ("controlled_false", "1 AND 1=2")]),
    "S005": ("q", [("normal_hit", "li"), ("normal_miss", "zz"), ("controlled_true", "x' OR 1=1 #"), ("controlled_false", "x' AND 1=2 #"), ("like_percent", "%"), ("like_underscore", "_")]),
    "S006": ("q", [("normal_hit", "li"), ("normal_miss", "zz"), ("controlled_true", "x' OR 1=1 #"), ("controlled_false", "x' AND 1=2 #"), ("like_percent", "%"), ("like_underscore", "_")]),
    "S007": ("name", [("normal_hit", "Alice"), ("normal_miss", "ZZZ"), ("controlled_true", "x' OR '1'='1"), ("controlled_false", "x' AND '1'='2")]),
    "S008": ("name", [("normal_hit", "Alice"), ("normal_miss", "ZZZ"), ("controlled_true", "x' OR '1'='1"), ("controlled_false", "x' AND '1'='2")]),
    "S009": ("ids", [("normal_hit", "1,2"), ("normal_single", "3"), ("card_input", "1 OR 1=1"), ("first_attempt_syntax_error", "1) OR 1=1 -- "), ("controlled_condition", "1) OR 1=1 #")]),
    "S010": ("ids", [("normal_hit", "1,2"), ("normal_single", "3"), ("card_input", "1 OR 1=1"), ("first_attempt_line_comment", "1) OR 1=1 -- "), ("controlled_condition", "1) OR 1=1 #"), ("invalid_list_item", "1,abc")]),
    "S011": ("sort", [("normal_id", "id"), ("normal_name", "name"), ("controlled_desc", "name DESC")]),
    "S012": ("sort", [("normal_id", "id"), ("normal_name", "name"), ("controlled_desc", "name DESC")]),
}


def observe(sample_id: str, parameter: str, label: str, value: str) -> dict:
    path = f"/lab_cases/{sample_id}/index.php"
    query = urllib.parse.urlencode({parameter: value})
    target = f"{BASE_URL}{path}?{query}"
    request = urllib.request.Request(target, headers={"User-Agent": "lab-reference-check/1.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=10) as response:
            if response.geturl() != target:
                raise RuntimeError(f"Unexpected redirect for {sample_id}/{label}")
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            body = response.read()
    except urllib.error.HTTPError as error:
        status = error.code
        content_type = error.headers.get("Content-Type", "")
        body = error.read()
    text = body.decode("utf-8", errors="replace")
    return {
        "label": label,
        "method": "GET",
        "request_path_and_query": f"{path}?{query}",
        "status": status,
        "content_type": content_type,
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "observed_rows": [{"id": int(row_id), "name": name} for row_id, name in ROWS.findall(text)],
        "php_fatal_error_visible": "Fatal error" in text,
        "response_body_utf8": text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        dest="samples",
        action="append",
        choices=tuple(MARKERS),
        help="sample to check; repeat to select several (default: all S001-S012)",
    )
    args = parser.parse_args()

    runtime_report = json.loads((ROOT / "environment" / "runtime_check.json").read_text(encoding="utf-8"))
    if (runtime_report["summary"]["failed"] or
            runtime_report["summary"]["passed"] != runtime_report["summary"]["total"] or
            runtime_report["summary"]["total"] < 23):
        raise RuntimeError("runtime source/lint checks must pass before HTTP reference checks")

    issues: list[str] = []
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    sample_ids = args.samples or list(MARKERS)
    if len(sample_ids) != len(set(sample_ids)):
        parser.error("each --sample value may be specified only once")

    for sample_id in sample_ids:
        parameter, scenarios = MARKERS[sample_id]
        observations = [observe(sample_id, parameter, label, value) for label, value in scenarios]
        report = {
            "kind": "reference_http_observation",
            "review_status": "pending_independent_review",
            "ground_truth": None,
            "observed_at_utc": stamp,
            "base_url": BASE_URL,
            "sample_id": sample_id,
            "a_source_commit": runtime_report["a_source"]["commit"],
            "c_source_commit": runtime_report["c_source"]["commit"],
            "requests": observations,
        }
        destination = ROOT / "evidence" / "truth" / sample_id / "http_reference.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        labels = ", ".join(f"{item['label']}={len(item['observed_rows'])}" for item in observations)
        print(f"{sample_id}: {labels}")
        for item in observations:
            if item["status"] != 200:
                issues.append(f"{sample_id}/{item['label']}: HTTP {item['status']}")
            if item["php_fatal_error_visible"]:
                issues.append(f"{sample_id}/{item['label']}: PHP fatal error was visible")
        hits = [item for item in observations if item["label"] == "normal_hit"]
        if hits and not hits[0]["observed_rows"]:
            issues.append(f"{sample_id}: normal_hit returned no teaching rows")
    if issues:
        raise RuntimeError("; ".join(issues))
    print(f"Saved reference HTTP records for {len(sample_ids)} sample(s); no ground truth assigned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
