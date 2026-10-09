"""Evaluate manually reviewed runs; no model calls and no execution of POCs."""
import argparse
import json
from pathlib import Path

VERSIONS = ('V0','V1','V2')
def ratio(a,b):
    return None if b == 0 else round(a/b,6)

def summarize(manifest, runs, root, allow_partial=False):
    root = Path(root).resolve()
    test = {x['sample_id']: x for x in manifest if x['split']=='test'}
    if len(test) != sum(x['split']=='test' for x in manifest):
        raise ValueError('duplicate sample IDs')
    for sample in test.values():
        if type(sample.get('ground_truth')) is not bool:
            raise ValueError(f"unreviewed ground truth: {sample['sample_id']}")
        if not sample.get('truth_reviewer') or not sample.get('truth_evidence'):
            raise ValueError('truth reviewer and evidence required')
    def check_paths(paths):
        if not isinstance(paths,list) or not paths:
            raise ValueError('nonempty evidence path list required')
        for item in paths:
            path = (root/item).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f'missing or out-of-root evidence: {item}')
    for sample in test.values():
        check_paths(sample['truth_evidence'])
    expected = {(sid,version) for sid in test for version in VERSIONS}
    observed = {}
    for r in runs:
        if r.get('phase') != 'formal':
            continue
        key = (r['sample_id'],r['prompt_version'])
        if key not in expected:
            raise ValueError(f'unexpected formal run {key}')
        if key in observed:
            raise ValueError(f'duplicate formal run {key}; repeat experiments belong to phase repeat')
        if r.get('status') != 'reviewed':
            if allow_partial:
                continue
            raise ValueError(f'run not reviewed: {key}')
        if r['prediction'] not in ('vulnerable','safe','uncertain'):
            raise ValueError('invalid prediction')
        if not r.get('reviewer') or r.get('reviewer') == r.get('operator'):
            raise ValueError('a different reviewer is required')
        if r.get('operator') != test[key[0]]['owner']:
            raise ValueError('operator does not match planned owner')
        check_paths(r['evidence_paths'])
        if r.get('verification') not in ('triggered','not_triggered','execution_failed','not_applicable','not_run'):
            raise ValueError('invalid verification status')
        for field in ('poc_generated','raw_execution_ok','environment_execution_ok','logic_changed'):
            if type(r.get(field)) is not bool:
                raise ValueError(f'{field} must be boolean, not null or a string')
        if not r['poc_generated'] and (r['raw_execution_ok'] or r['environment_execution_ok'] or r['logic_changed']):
            raise ValueError('POC flags inconsistent with no POC generated')
        observed[key] = r
    missing = sorted(expected-observed.keys())
    if missing and not allow_partial:
        raise ValueError(f'missing {len(missing)} reviewed formal runs')
    result = {'complete': not missing, 'expected_records':len(expected),
              'observed_records':len(observed), 'missing': missing,
              'warning': 'Partial results are provisional.' if missing else 'Small paired classroom dataset; no generalization claim.',
              'by_version':{}}
    for version in VERSIONS:
        rs=[r for (sid,v),r in observed.items() if v==version]
        c={k:0 for k in ('TP','FP','TN','FN','U_positive','U_negative')}
        for r in rs:
            truth=test[r['sample_id']]['ground_truth']; pred=r['prediction']
            if pred=='uncertain': label='U_positive' if truth else 'U_negative'
            elif pred=='vulnerable': label='TP' if truth else 'FP'
            else: label='FN' if truth else 'TN'
            c[label]+=1
        positives=c['TP']+c['FN']+c['U_positive']
        negatives=c['FP']+c['TN']+c['U_negative']
        generated=sum(r['poc_generated'] for r in rs)
        raw=sum(r['poc_generated'] and r['raw_execution_ok'] for r in rs)
        adapted=sum(r['poc_generated'] and (r['raw_execution_ok'] or r['environment_execution_ok']) for r in rs)
        result['by_version'][version]={**c,'N':len(rs),
          'precision':ratio(c['TP'],c['TP']+c['FP']),
          'conservative_recall':ratio(c['TP'],positives),
          'false_positive_rate':ratio(c['FP'],negatives),
          'all_sample_accuracy':ratio(c['TP']+c['TN'],len(rs)),
          'uncertain_rate':ratio(c['U_positive']+c['U_negative'],len(rs)),
          'pocs_generated':generated,'raw_executable_rate':ratio(raw,generated),
          'raw_or_environment_executable_rate':ratio(adapted,generated),
          'logic_changed_count':sum(r['logic_changed'] for r in rs),
          'triggered_count':sum(r['verification']=='triggered' for r in rs)}
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',required=True);ap.add_argument('--runs',required=True)
    ap.add_argument('--root',default='.');ap.add_argument('--out',required=True)
    ap.add_argument('--allow-partial',action='store_true')
    a=ap.parse_args()
    read=lambda x:json.loads(Path(x).read_text(encoding='utf-8-sig'))
    result=summarize(read(a.manifest),read(a.runs),a.root,a.allow_partial)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for name in ('summary.json','summary.md'):
        if (out/name).exists():raise ValueError('output exists; choose a new results version')
    (out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 实验统计','',f"完整性：{result['complete']}；已复核 {result['observed_records']}/{result['expected_records']}",'',result['warning'],'',
      '|版本|N|TP|FP|TN|FN|待判定|精确率|保守召回率|原始POC可执行率|','|---|---|---|---|---|---|---|---|---|---|']
    fmt=lambda x:'N/A' if x is None else f'{x:.1%}'
    for v,s in result['by_version'].items():
        lines.append(f"|{v}|{s['N']}|{s['TP']}|{s['FP']}|{s['TN']}|{s['FN']}|{s['U_positive']+s['U_negative']}|{fmt(s['precision'])}|{fmt(s['conservative_recall'])}|{fmt(s['raw_executable_rate'])}|")
    (out/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Results saved to {out}; incomplete results are not final scores')

if __name__=='__main__':main()
