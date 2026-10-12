"""Prepare and record B's manual LLM sessions. No model calls or POC execution."""
import argparse
import hashlib
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV = ('S001','S002','S003','S004','S005','S006','S013','S014','S015','S016','S017','S018')
FORMAL = ('S008','S019','S024')
INJECT = ('S001','S004','S013','S016')
REVIEW = ('S009','S012','S023')
VERSIONS = ('V0','V1','V2')
LEAK = re.compile(r'ground_truth|expected_design|line_map|family_id|pair(?:ed)?[_ -]?label|(?:^|[/\\])(?:low|safe|fixed|vulnerable)(?:[/\\.]|$)', re.I | re.M)
LOC = re.compile(r'^F\d{2}:\d{4}$')
REQUIRED = {'sample_id':str,'prediction':str,'vulnerability_type':str,'locations':list,'evidence':dict,'prerequisites':list,'missing_context':list,'poc_generated':bool,'poc_language':str,'poc_instructions':str}

def digest(data): return hashlib.sha256(data).hexdigest()
def read(path): return Path(path).read_bytes()
def read_canonical_text(path):
    raw=read(path)
    raw.decode('utf-8-sig')
    return raw.replace(b'\r\n',b'\n')
def put_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out: out.write(data)
def kind(sid): return 'SQLi' if int(sid[1:]) <= 12 else 'XSS'
def run_id(phase,sid,version,variant=''):
    stem = f'{phase}_{sid}_{variant+"_" if variant else ""}{version}'
    n=1
    while (ROOT/'runs'/f'{stem}_R{n}').exists(): n+=1
    return f'{stem}_R{n}'
def validate(raw,sid,kind_name,packet=None):
    errors=[]
    try:
        s=raw.decode('utf-8-sig').strip()
        blocks=re.findall(r'```(?:json)?\s*([\s\S]*?)```',s,re.I)
        if not blocks: errors.append('missing JSON code fence')
        obj=json.loads(blocks[0] if blocks else s)
        if not isinstance(obj,dict): raise ValueError('JSON root must be object')
        for key,typ in REQUIRED.items():
            if key not in obj or type(obj[key]) is not typ: errors.append(f'{key}: missing or wrong type')
        if obj.get('sample_id')!=sid: errors.append('sample_id mismatch')
        if obj.get('prediction') not in ('vulnerable','safe','uncertain'): errors.append('invalid prediction')
        if obj.get('vulnerability_type') != ('SQL注入' if kind_name=='SQLi' else 'XSS'): errors.append('vulnerability_type mismatch')
        if isinstance(obj.get('locations'),list) and any(not isinstance(x,str) or not LOC.fullmatch(x) for x in obj['locations']): errors.append('invalid location')
        if packet is not None and isinstance(obj.get('locations'),list):
            available=set(re.findall(r'^(F\d{2}:\d{4}) \| ',packet.decode('utf-8-sig'),re.M))
            for location in obj['locations']:
                if isinstance(location,str) and LOC.fullmatch(location) and location not in available:
                    errors.append(f'location absent from input: {location}')
        ev=obj.get('evidence')
        if isinstance(ev,dict):
            for key in ('source','flow','guard','sink'):
                if not isinstance(ev.get(key),str) or not ev[key].strip(): errors.append(f'evidence.{key} missing')
        for key in ('prerequisites','missing_context'):
            if isinstance(obj.get(key),list) and any(not isinstance(x,str) for x in obj[key]): errors.append(f'{key} items must be strings')
        if obj.get('poc_language') not in ('python3','manual','none'): errors.append('invalid poc_language')
        if obj.get('poc_generated') is False and obj.get('poc_language')!='none': errors.append('POC flags inconsistent')
        if obj.get('poc_generated') is True and obj.get('poc_language')=='none': errors.append('POC flags inconsistent')
        return obj,errors
    except (UnicodeError,json.JSONDecodeError,ValueError) as exc:
        return None,errors+[f'JSON parse error: {exc}']

def prepare(a):
    sid=a.sample; version=a.version; phase=a.phase
    allowed={'DEV':DEV,'F':FORMAL,'INJ':INJECT}[phase]
    if sid not in allowed: raise ValueError('sample is outside this B task set')
    if phase=='F' and (not a.freeze_confirmed or not (ROOT/'environment'/'prompt_hashes.txt').is_file()):
        raise ValueError('formal inputs require confirmed freeze and prompt_hashes.txt')
    if phase=='INJ' and (a.variant not in ('Original','Injected')): raise ValueError('INJ requires --variant')
    if phase=='INJ' and version not in ('V0','V2'): raise ValueError('INJ uses V0 or V2')
    code=read_canonical_text(a.code_input)
    if f'<sample_id>{sid}</sample_id>'.encode() not in code: raise ValueError('packet sample_id mismatch')
    if not b'<untrusted_code>' in code or not b'</untrusted_code>' in code: raise ValueError('packet lacks code boundary')
    hit=LEAK.search(code.decode('utf-8-sig'))
    if hit: raise ValueError(f'possible answer leak: {hit.group()}')
    prompt=read_canonical_text(ROOT/'prompts'/f'{kind(sid)}_{version}.txt')
    packet_hash=digest(code)
    comparison=ROOT/'runs'/'b_packet_lock.json'
    locks=json.loads(comparison.read_text(encoding='utf-8')) if comparison.exists() else {}
    lock_key=f'{phase}:{sid}:{a.variant if phase=="INJ" else "Original"}'
    if lock_key in locks and locks[lock_key]!=packet_hash: raise ValueError('packet differs from prior version for this sample/variant')
    rid=run_id(phase,sid,version,a.variant if phase=='INJ' else '')
    path=ROOT/'runs'/rid
    data=prompt.rstrip(b'\r\n')+b'\n\n'+code
    meta={'run_id':rid,'phase':phase,'sample_id':sid,'variant':a.variant if phase=='INJ' else 'Original','prompt_version':version,'vulnerability_type':kind(sid),'status':'input_prepared','model_display_name':None,'model_settings':None,'submitted_at':None,'prompt_sha256':digest(prompt),'packet_sha256':packet_hash,'input_sha256':digest(data),'source_code_input':str(Path(a.code_input).resolve()),'raw_output_sha256':None}
    put_new(path/'input.txt',data)
    put_new(path/'metadata.json',(json.dumps(meta,ensure_ascii=False,indent=2)+'\n').encode())
    locks[lock_key]=packet_hash
    temp=comparison.with_suffix('.tmp'); temp.write_text(json.dumps(locks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); temp.replace(comparison)
    print(rid)

def record(a):
    path=ROOT/'runs'/a.run_id
    meta=json.loads((path/'metadata.json').read_text(encoding='utf-8'))
    raw=read(a.raw_output)
    submitted=datetime.fromisoformat(a.submitted_at.replace('Z','+00:00'))
    if submitted.tzinfo is None: raise ValueError('submitted-at must include timezone')
    obj,errors=validate(raw,meta['sample_id'],meta['vulnerability_type'],read(path/'input.txt'))
    put_new(path/'raw_output.txt',raw)
    norm={'run_id':a.run_id,'format_valid':not errors,'format_errors':errors,'parsed_json':obj,'human_verification':'pending'}
    put_new(path/'normalized.json',(json.dumps(norm,ensure_ascii=False,indent=2)+'\n').encode())
    meta.update(status='raw_recorded',model_display_name=a.model,model_settings=a.settings,submitted_at=a.submitted_at,recorded_at=datetime.now(timezone.utc).isoformat(),raw_output_sha256=digest(raw))
    (path/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{a.run_id}: format_valid={not errors}; raw preserved')

def plan(a):
    rng=random.Random(a.seed)
    cohorts=[[f'DEV_{s}_{v}' for s in DEV] for v in VERSIONS]
    cohorts += [[f'F_{s}_{v}' for s in FORMAL for v in VERSIONS],
                [f'INJ_{s}_{variant}_{v}' for s in INJECT for variant in ('Original','Injected') for v in ('V0','V2')]]
    for cohort in cohorts: rng.shuffle(cohort)
    tasks=[task for cohort in cohorts for task in cohort]
    existing={p.name.rsplit('_R',1)[0] for p in (ROOT/'runs').iterdir() if p.is_dir()}
    lines=['# B 实验进度','',f'排序种子：{a.seed}；只控制任务顺序，不控制模型随机性。','',f'已建输入：{sum(x in existing for x in tasks)}/{len(tasks)}。真实完成数以原始回答及人工验证记录为准。','','|任务|状态|','|---|---|']
    lines += [f'|{t}|{"input prepared" if t in existing else "pending"}|' for t in tasks]
    lines += ['', 'C 的 S009、S012、S023 各 V0/V1/V2：待 B 复核。']
    out=ROOT/'results'/'b_progress.md'; out.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print(out)

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare'); p.add_argument('--phase',choices=('DEV','F','INJ'),required=True); p.add_argument('--sample',required=True); p.add_argument('--version',choices=VERSIONS,required=True); p.add_argument('--code-input',required=True); p.add_argument('--variant',default=''); p.add_argument('--freeze-confirmed',action='store_true'); p.set_defaults(func=prepare)
    p=sub.add_parser('record'); p.add_argument('--run-id',required=True); p.add_argument('--raw-output',required=True); p.add_argument('--model',required=True); p.add_argument('--settings',required=True); p.add_argument('--submitted-at',required=True,help='actual model submission time with timezone, e.g. 2026-10-12T14:30:00+08:00'); p.set_defaults(func=record)
    p=sub.add_parser('plan'); p.add_argument('--seed',type=int,default=20261012); p.set_defaults(func=plan)
    a=ap.parse_args(); a.func(a)
if __name__=='__main__': main()
