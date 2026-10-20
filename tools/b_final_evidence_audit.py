"""Recompute B's C-record and fixed-comment injection audit. Never executes POCs."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import b_local_analysis

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def canonical(path):
    return path.read_text(encoding='utf-8-sig').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect_run(root, rid):
    directory = root / 'runs' / rid
    meta = read_json(directory / 'metadata.json')
    data = canonical(directory / 'input.txt')
    raw = (directory / 'raw_output.txt').read_bytes()
    boundary = re.search(rb'(?m)^<sample_id>S\d{3}</sample_id>', data)
    if boundary is None:
        raise ValueError('missing packet boundary: ' + rid)
    packet = data[boundary.start():]
    prompt = data[:boundary.start()].rstrip(b'\n') + b'\n'
    sid = meta['sample_id']
    kind = 'SQLi' if int(sid[1:]) <= 12 else 'XSS'
    current_prompt = canonical(root / 'prompts' / f'{kind}_{meta["prompt_version"]}.txt')
    parsed = b_local_analysis.parse_response(raw, sid, kind, packet)
    obj = parsed['parsed_json'] or {}
    raw_exact = sha(raw) == meta.get('raw_output_sha256')
    raw_lf = sha(canonical(directory / 'raw_output.txt')) == meta.get('raw_output_sha256')
    checks = {
        'input_sha256': sha(data) == meta.get('input_sha256'),
        'packet_sha256': sha(packet) == meta.get('packet_sha256'),
        'embedded_prompt_sha256': sha(prompt) == meta.get('prompt_sha256'),
        'current_prompt_matches': sha(prompt) == sha(current_prompt),
        'raw_sha256_exact': raw_exact,
        'raw_sha256_lf': raw_lf,
        'raw_sha256_verified': raw_exact or raw_lf,
        'strict_json_contract': parsed['json_contract_valid'],
        'evidence_references_exist': not parsed['reference_warnings'],
    }
    return {
        'run_id': rid, 'checks': checks,
        'prediction': obj.get('prediction'),
        'locations': obj.get('locations'), 'evidence': obj.get('evidence'),
        'poc_generated': obj.get('poc_generated'),
        'poc_language': obj.get('poc_language'),
        'poc_instructions': obj.get('poc_instructions'),
        'parse_errors': parsed['json_errors'],
        'poc_static_errors': parsed['poc_syntax_errors'],
        'actual_poc_execution': 'not_run_by_this_audit',
        'submitted_at': meta.get('submitted_at'),
        'model_display_name': meta.get('model_display_name'),
        'model_settings': meta.get('model_settings'),
        'source': meta.get('raw_source'),
        'screenshots_in_run_directory': [p.name for p in directory.iterdir()
                                         if p.suffix.lower() in ('.png', '.jpg', '.jpeg')],
        'raw_sha256_actual': sha(raw),
        'raw_sha256_metadata': meta.get('raw_output_sha256'),
    }


def audit(root):
    root = Path(root).resolve()
    formal = {r['run_id']: r for r in read_json(root / 'runs/formal.json')}
    result = {'scope': 'static independent B review; no model calls, no POC execution',
              'c_formal_reviews': [], 'injection_runs': [], 'injection_pairs': [],
              'packet_changes': [], 'hash_registry': [],
              'development_runs': [], 'b_formal_runs': []}
    for number in list(range(1, 7)) + list(range(13, 19)):
        sid = f'S{number:03d}'
        for version in ('V0', 'V1', 'V2'):
            repeat = 2 if sid == 'S013' and version == 'V0' else 1
            result['development_runs'].append(inspect_run(root, f'DEV_{sid}_{version}_R{repeat}'))
    for sid in ('S008', 'S019', 'S024'):
        for version in ('V0', 'V1', 'V2'):
            result['b_formal_runs'].append(inspect_run(root, f'F_{sid}_{version}_R1'))
    for sid in ('S009', 'S012', 'S023'):
        packet_dir = root / 'dataset/packets' / f'{sid}_v{2 if sid != "S023" else 1}'
        packet = canonical(packet_dir / 'code_input.txt')
        mapping = read_json(packet_dir / 'line_map.json')
        source_checks = {}
        for fragment in mapping['files']:
            source = root / 'dataset/raw' / sid / fragment['source_file']
            lines = source.read_text(encoding='utf-8-sig').splitlines()
            prefix = fragment['alias'] + ':'
            references = re.findall(r'^(' + re.escape(prefix) + r'\d{4}) \| (.*)$', packet.decode(), re.M)
            source_checks[fragment['alias']] = {
                'source_sha256': sha(canonical(source)) == fragment['sha256'],
                'line_content': all(lines[int(ref.split(':')[1])-1] == content
                                    for ref, content in references),
            }
        for version in ('V0', 'V1', 'V2'):
            rid = f'F_{sid}_{version}_R1'
            item = inspect_run(root, rid)
            plan = formal[rid]
            item['plan_prediction_matches_raw'] = plan['prediction'] == item['prediction']
            item['plan_poc_flag_matches_raw'] = plan['poc_generated'] == item['poc_generated']
            meta = read_json(root / 'runs' / rid / 'metadata.json')
            item['packet_matches_unique_standard'] = meta['packet_sha256'] == sha(packet)
            item['mapping_packet_sha256'] = mapping['packet_sha256'] == sha(packet)
            item['source_checks'] = source_checks
            item['existing_verification'] = plan.get('verification')
            item['existing_reviewer_field'] = plan.get('reviewer')
            item['existing_status'] = plan.get('status')
            result['c_formal_reviews'].append(item)
    inj_root = root / 'experiments/prompt_injection/packets'
    manifest = read_json(inj_root / 'manifest.json')
    sentence = manifest['injection_text']
    for sid in ('S001', 'S004', 'S013', 'S016'):
        spec = manifest['samples'][sid]
        original = canonical(root / spec['original_path']).decode()
        injected = canonical(root / spec['injected_path']).decode()
        # The corpus appends the fixed phrase to one pre-existing PHP comment.
        suffix = ' ' + sentence if sid in ('S001', 'S004') else '；' + sentence
        changes = [(a, b) for a, b in zip(original.splitlines(), injected.splitlines()) if a != b]
        comment_only = (len(original.splitlines()) == len(injected.splitlines())
                        and len(changes) == 1 and injected.count(sentence) == 1
                        and injected.replace(suffix, '', 1) == original
                        and (' |  * ' in changes[0][0] or ' | // ' in changes[0][0]))
        result['packet_changes'].append({
            'sample_id': sid, 'single_legal_comment_append_only': comment_only,
            'original_sha256': sha(original.encode()) == spec['original_sha256'],
            'injected_sha256': sha(injected.encode()) == spec['injected_sha256'],
            'runtime_equivalence_tested_by_this_audit': False,
        })
        for version in ('V0', 'V2'):
            pair = []
            for variant in ('Original', 'Injected'):
                item = inspect_run(root, f'INJ_{sid}_{variant}_{version}_R1')
                result['injection_runs'].append(item)
                pair.append(item)
            result['injection_pairs'].append({
                'sample_id': sid, 'prompt_version': version,
                'original_prediction': pair[0]['prediction'],
                'injected_prediction': pair[1]['prediction'],
                'prediction_changed': pair[0]['prediction'] != pair[1]['prediction'],
                'locations_added': sorted(set(pair[1]['locations'] or []) - set(pair[0]['locations'] or [])),
                'locations_removed': sorted(set(pair[0]['locations'] or []) - set(pair[1]['locations'] or [])),
                'evidence_text_changed': pair[0]['evidence'] != pair[1]['evidence'],
                'interpretation': 'prediction stability alone does not prove injection immunity',
            })
    for line in (root / 'environment/prompt_hashes.txt').read_text().splitlines():
        if not line.strip(): continue
        name, claimed = line.split()
        actual = sha(canonical(root / 'prompts' / (name + '.txt')))
        result['hash_registry'].append({'prompt': name, 'claimed': claimed,
                                       'actual': actual, 'matches': claimed == actual})
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    report = audit(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'C_formal': len(report['c_formal_reviews']),
                      'DEV': len(report['development_runs']),
                      'B_formal': len(report['b_formal_runs']),
                      'INJ_raw': len(report['injection_runs']),
                      'INJ_pairs': len(report['injection_pairs']),
                      'hash_registry_mismatches': sum(not r['matches'] for r in report['hash_registry'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
