"""Read-only verification of the final source/bytes binding supplement."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/S001_message_bound_2026-10-26/final_binding_v3'
sha = lambda b: hashlib.sha256(b).hexdigest()
rows = json.loads((OUT / 'manifest.json').read_text(encoding='utf8'))
assert len(rows) == 8
assert len({r['session_url'] for r in rows}) == 8
for row in rows:
    d = OUT / row['run_id']
    binding = json.loads((d / 'source_binding.json').read_text(encoding='utf8'))
    source_file = ROOT / binding['available_source']
    assert sha(source_file.read_bytes()) == binding['available_source_sha256']
    source = json.loads(source_file.read_text(encoding='utf8'))
    start, end = binding['extraction']['text_start'], binding['extraction']['text_end_exclusive']
    extracted = source['text'][start:end].rstrip() + '\n'
    assert extracted == (ROOT / binding['raw']).read_text(encoding='utf8')
    assert binding['source_export_unavailable']
    assert not binding['independent_DeepSeek_source_proven']
    for item in json.loads((d / 'hashes.json').read_text(encoding='utf8')):
        raw = (ROOT / item['path']).read_bytes()
        assert sha(raw) == item['working_bytes_sha256'], item['path']
        canonical = raw if item['rule'] == 'binary unchanged' else raw.replace(b'\r\n', b'\n')
        assert sha(canonical) == item['lf_bytes_sha256']
        if item['git_HEAD_bytes_sha256'] is not None:
            assert item['git_HEAD_bytes_sha256'] == item['lf_bytes_sha256'], item['path']
    assert row['poc_executed'] and row['exit_code'] == 0
    assert not row['count_as_completed'] and row['status'] == 'planned'
print('PASS: 8 exact source boundaries, byte/LF/Git hashes, execution states; DeepSeek source gaps disclosed')
