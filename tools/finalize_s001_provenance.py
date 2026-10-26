"""Export only the eight already-bound user messages, without inventing DeepSeek logs."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / 'evidence/S001_message_bound_2026-10-26'
OUT = CANDIDATE / 'final_binding_v3'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def file_record(path, original_capture_hash=None):
    data = path.read_bytes()
    binary = path.suffix == '.png'
    lf = data if binary else data.replace(b'\r\n', b'\n')
    rel = path.relative_to(ROOT).as_posix()
    blob = subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True)
    return {'path': rel, 'working_bytes_sha256': digest(data),
            'lf_bytes_sha256': digest(lf),
            'git_HEAD_bytes_sha256': digest(blob.stdout) if blob.returncode == 0 else None,
            'original_capture_sha256': original_capture_hash,
            'original_capture_available': original_capture_hash is not None,
            'rule': 'binary unchanged' if binary else 'LF canonical: replace CRLF with LF; no other conversion',
            'working_has_crlf': b'\r\n' in data if not binary else None}


def main():
    manifest = json.loads((CANDIDATE / 'manifest.json').read_text(encoding='utf8'))
    wanted = {m['source_message_id'] for m in manifest}
    messages = {}
    # Only this chat's logs, and only the eight message IDs already present in metadata.
    codex = Path.home() / '.codex'
    logs = list((codex / 'sessions/2026/10/19').glob('*01a152ed*.jsonl'))
    logs += list((codex / 'archived_sessions').glob('*01a152ed*.jsonl'))
    for log in logs:
        for number, line in enumerate(log.open(encoding='utf8'), 1):
            if not any(mid in line for mid in wanted):
                continue
            item = json.loads(line)
            payload = item.get('payload', {})
            if payload.get('role') == 'user' and payload.get('id') in wanted:
                text = '\n'.join(c.get('text', '') for c in payload['content'])
                messages[payload['id']] = (text, item.get('timestamp'), log.name, number)
    assert len(messages) == 8, 'Bound source messages not found; do not reconstruct them.'
    execution_root = ROOT / 'evidence/S001_poc_verified_2026-10-26'
    executions = json.loads((execution_root / 'execution_summary.json').read_text(encoding='utf8'))
    execution_map = {e['run_id']: e for e in executions}
    OUT.mkdir(exist_ok=False)
    summary = []
    for m in manifest:
        run_id = m['run_id']
        d = OUT / run_id
        d.mkdir()
        text, received, log_name, line_no = messages[m['source_message_id']]
        suffix = re.search(r'这是([1-8])(?:模型输出的结果)?\s*$', text)
        assert suffix
        extracted = text[:suffix.start()].rstrip() + '\n'
        raw_path = ROOT / m['raw_output_path']
        assert raw_path.read_text(encoding='utf8') == extracted
        source_path = d / 'source_user_message.json'
        write_json(source_path, {'message_id': m['source_message_id'], 'received_at': received,
                                'source_type': 'Codex user message; not DeepSeek export', 'text': text})
        binding = {'run_id': run_id, 'session_url': m['session_url'],
                   'source_export_unavailable': True, 'unavailable_source': 'DeepSeek original conversation export',
                   'available_source': source_path.relative_to(ROOT).as_posix(),
                   'available_source_sha256': digest(source_path.read_bytes()),
                   'local_log_name': log_name, 'local_log_line_1_based': line_no,
                   'extraction': {'text_start': 0, 'text_end_exclusive': suffix.start(),
                                  'postprocessing': 'rstrip whitespace then append one LF',
                                  'excluded_suffix': text[suffix.start():], 'raw_equal': True},
                   'actual_sent_input': 'User explicitly confirms equality; input is not independently exported',
                   'screenshot': m['screenshot_path'], 'raw': m['raw_output_path'],
                   'normalized': m['normalized_path'],
                   'independent_DeepSeek_source_proven': False}
        write_json(d / 'source_binding.json', binding)
        e = execution_map[run_id]
        eroot = execution_root / run_id
        hashes = [file_record(ROOT / m[k]) for k in
                  ['input_path', 'raw_output_path', 'prompt_path', 'packet_path', 'normalized_path', 'screenshot_path']]
        hashes += [file_record(eroot / 'model_poc.py', e['script_sha256']),
                   file_record(eroot / 'stdout.txt', e['stdout_sha256']),
                   file_record(eroot / 'stderr.txt', e['stderr_sha256'])]
        for h in hashes[-3:]:
            h['capture_hash_provenance'] = 'Original execution_summary recorded the hash; original capture bytes were not separately preserved'
            h['original_capture_bytes_preserved'] = h['original_capture_sha256'] == h['git_HEAD_bytes_sha256']
        write_json(d / 'hashes.json', hashes)
        state = {'schema_version': 3, 'run_id': run_id, 'session_url': m['session_url'],
                 'poc_executed': True, 'poc_execution': 'executed_success_observed',
                 'execution_record': (execution_root / 'execution_summary.json').relative_to(ROOT).as_posix(),
                 'exit_code': e['exit_code'], 'start_time': e['started_at_utc'],
                 'end_time': None, 'command': None, 'interpreter_path': None, 'working_directory': None,
                 'missing_execution_fields': 'Not captured contemporaneously; not retroactively invented',
                 'per_run_full_http_capture': False, 'shared_HTTP_evidence_scope': 'environment auxiliary only',
                 'source_binding_path': (d / 'source_binding.json').relative_to(ROOT).as_posix(),
                 'model_version_proven': False, 'generation_settings_proven': False,
                 'status': 'planned', 'count_as_completed': False}
        write_json(d / 'metadata.json', state)
        summary.append(state)
    write_json(OUT / 'manifest.json', summary)
    print('PASS: eight exact user-message exports, source boundaries, hash inventories and versioned execution states')


if __name__ == '__main__':
    main()
