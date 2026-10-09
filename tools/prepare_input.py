"""Build a traceable, numbered code packet. Never calls an LLM or runs code."""
import argparse
import hashlib
import json
from pathlib import Path

def build(root, spec):
    root = Path(root).resolve()
    sid = spec['sample_id']
    context = spec['context']
    if not isinstance(context, str) or not context.strip():
        raise ValueError('context must describe actual runtime assumptions')
    blocks = [f'<sample_id>{sid}</sample_id>', '<runtime_context>', context,
              '</runtime_context>', '<untrusted_code>']
    mapping = []
    aliases = {}
    nlines = 0
    for fragment in spec['fragments']:
        path = (root / fragment['file']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('source file must be inside source-root')
        raw = path.read_bytes()
        lines = raw.decode('utf-8-sig').splitlines()
        start, end = fragment['start'], fragment['end']
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError(f'invalid original line range for {path.name}')
        relative = path.relative_to(root).as_posix()
        alias = aliases.setdefault(relative, f'F{len(aliases)+1:02}')
        blocks.append(f'FILE {alias} ORIGINAL_LINES {start}-{end}')
        for number in range(start, end+1):
            blocks.append(f'{alias}:{number:04d} | {lines[number-1]}')
        nlines += end-start+1
        mapping.append({'alias': alias, 'source_file': relative,
                        'start': start, 'end': end,
                        'sha256': hashlib.sha256(raw).hexdigest()})
    blocks.append('</untrusted_code>')
    output = '\n'.join(blocks)+'\n'
    if nlines > 200 or len(output) > 8000:
        raise ValueError('packet exceeds 200 code lines or 8000 characters; manually select semantic fragments')
    return output, {'sample_id': sid, 'code_lines': nlines,
                    'packet_sha256': hashlib.sha256(output.encode()).hexdigest(),
                    'files': mapping}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', required=True)
    ap.add_argument('--spec', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8-sig'))
    output, mapping = build(a.source_root, spec)
    target = Path(a.out)
    target.mkdir(parents=True, exist_ok=True)
    if (target/'code_input.txt').exists() or (target/'line_map.json').exists():
        raise ValueError('output exists; choose a new packet version directory')
    (target/'code_input.txt').write_text(output, encoding='utf-8')
    (target/'line_map.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Created {target}; mapping is internal and must not be sent to the model')

if __name__ == '__main__':
    main()
