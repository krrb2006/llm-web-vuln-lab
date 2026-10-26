"""Read archived POC evidence without rerunning Docker or mutating historical files."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
r = root / 'evidence/S001_poc_verified_2026-10-26'
summary = json.loads((r / 'execution_summary.json').read_text(encoding='utf8'))
assert len(summary) == 8
for m in summary:
    raw = (root / 'evidence/S001_message_bound_2026-10-26' / m['run_id'] / 'raw_output.txt').read_text(encoding='utf8')
    code = re.findall(r'```python(?:3)?\s*\n(.*?)\n```', raw, re.S)[0] + '\n'
    actual = (r / m['run_id'] / 'model_poc.py').read_text(encoding='utf8')
    assert actual == code
    assert m['matches_model_raw_code'] is True
    assert m['source_raw_sha256_lf'] == hashlib.sha256(raw.encode()).hexdigest()
    assert m['exit_code'] == 0
expected = {'normal': ['Alice'], 'true': ['Alice'], 'false': [],
            'or': ['Alice', 'Bob', 'Carol'], 'comment': ['Alice', 'Bob', 'Carol']}
for k, v in expected.items():
    text = (r / (k + '_response.html')).read_text(encoding='utf8')
    names = re.findall(r'<p>ID \d+：([^<]+)</p>', text)
    assert names == v, (k, names)
assert re.match(r'^[0-9a-f]{64}  /var/www/html/lab_cases/S001/index.php\s*$',
                (r / 'runtime_source_hash.txt').read_text(encoding='utf8'))
print('PASS: 8 code blocks identical; 5 archived auxiliary HTTP business-result comparisons verified')
