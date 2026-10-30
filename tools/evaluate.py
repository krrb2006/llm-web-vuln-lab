"""Evaluate manually reviewed runs; no model calls and no execution of POCs.

The evaluator deliberately keeps model detection, source localization, POC
executability, and observed vulnerability impact as separate dimensions.  It
also performs paired version comparisons on the same samples so a Prompt
iteration cannot claim improvement merely because its evaluated sample set
changed.
"""
import argparse
import json
from pathlib import Path

VERSIONS = ("V0", "V1", "V2")
PAIRWISE_VERSIONS = (("V0", "V1"), ("V1", "V2"), ("V0", "V2"))


def ratio(a, b):
    return None if b == 0 else round(a / b, 6)


def _is_correct(truth, prediction):
    return (truth and prediction == "vulnerable") or (
        not truth and prediction == "safe"
    )


def _summarize_group(records, test):
    counts = {key: 0 for key in ("TP", "FP", "TN", "FN", "U_positive", "U_negative")}
    for run in records:
        truth = test[run["sample_id"]]["ground_truth"]
        prediction = run["prediction"]
        if prediction == "uncertain":
            label = "U_positive" if truth else "U_negative"
        elif prediction == "vulnerable":
            label = "TP" if truth else "FP"
        else:
            label = "FN" if truth else "TN"
        counts[label] += 1

    positives = counts["TP"] + counts["FN"] + counts["U_positive"]
    negatives = counts["FP"] + counts["TN"] + counts["U_negative"]
    generated = sum(run["poc_generated"] for run in records)
    raw = sum(run["poc_generated"] and run["raw_execution_ok"] for run in records)
    adapted = sum(
        run["poc_generated"]
        and (run["raw_execution_ok"] or run["environment_execution_ok"])
        for run in records
    )
    vulnerable_predictions = [
        run for run in records if run["prediction"] == "vulnerable"
    ]
    located = sum(run["location_correct"] is True for run in vulnerable_predictions)
    triggered = sum(run["verification"] == "triggered" for run in records)
    return {
        **counts,
        "N": len(records),
        "precision": ratio(counts["TP"], counts["TP"] + counts["FP"]),
        "conservative_recall": ratio(counts["TP"], positives),
        "false_positive_rate": ratio(counts["FP"], negatives),
        "all_sample_accuracy": ratio(counts["TP"] + counts["TN"], len(records)),
        "uncertain_rate": ratio(
            counts["U_positive"] + counts["U_negative"], len(records)
        ),
        "vulnerable_predictions": len(vulnerable_predictions),
        "location_correct_count": located,
        "location_correct_rate": ratio(located, len(vulnerable_predictions)),
        "pocs_generated": generated,
        "poc_generation_rate": ratio(generated, len(records)),
        "raw_executable_rate": ratio(raw, generated),
        "raw_or_environment_executable_rate": ratio(adapted, generated),
        "logic_changed_count": sum(run["logic_changed"] for run in records),
        "triggered_count": triggered,
        "trigger_rate_given_generated": ratio(triggered, generated),
    }


def _paired_comparison(observed, test, before, after):
    sample_ids = sorted(
        sid
        for sid in test
        if (sid, before) in observed and (sid, after) in observed
    )
    transitions = {
        "unchanged_correct": 0,
        "resolved_error": 0,
        "regression": 0,
        "unchanged_incorrect": 0,
    }
    for sample_id in sample_ids:
        truth = test[sample_id]["ground_truth"]
        before_correct = _is_correct(truth, observed[(sample_id, before)]["prediction"])
        after_correct = _is_correct(truth, observed[(sample_id, after)]["prediction"])
        if before_correct and after_correct:
            transitions["unchanged_correct"] += 1
        elif not before_correct and after_correct:
            transitions["resolved_error"] += 1
        elif before_correct and not after_correct:
            transitions["regression"] += 1
        else:
            transitions["unchanged_incorrect"] += 1
    before_accuracy = ratio(
        transitions["unchanged_correct"] + transitions["regression"], len(sample_ids)
    )
    after_accuracy = ratio(
        transitions["unchanged_correct"] + transitions["resolved_error"], len(sample_ids)
    )
    delta = None
    if before_accuracy is not None and after_accuracy is not None:
        delta = round(after_accuracy - before_accuracy, 6)
    return {
        "before": before,
        "after": after,
        "paired_samples": len(sample_ids),
        **transitions,
        "before_accuracy": before_accuracy,
        "after_accuracy": after_accuracy,
        "accuracy_delta": delta,
        "net_error_reduction": transitions["resolved_error"] - transitions["regression"],
    }

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
        if r["prediction"] == "vulnerable" and type(r.get("location_correct")) is not bool:
            raise ValueError(
                f"location_correct must be boolean for vulnerable prediction: {r['run_id']}"
            )
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
              'by_version':{}, 'by_type':{}, 'pairwise':{}}
    for version in VERSIONS:
        records = [run for (sample_id, item_version), run in observed.items() if item_version == version]
        result['by_version'][version] = _summarize_group(records, test)
        result['by_type'][version] = {}
        for vulnerability_type in ("SQLi", "XSS"):
            typed = [
                run for run in records
                if test[run["sample_id"]]["vulnerability_type"] == vulnerability_type
            ]
            result['by_type'][version][vulnerability_type] = _summarize_group(typed, test)
    for before, after in PAIRWISE_VERSIONS:
        result["pairwise"][f"{before}_to_{after}"] = _paired_comparison(
            observed, test, before, after
        )
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
      '## 总体指标','',
      '|版本|N|TP|FP|TN|FN|待判定|精确率|保守召回率|误报率|定位正确率|原始POC可执行率|','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda x:'N/A' if x is None else f'{x:.1%}'
    for v,s in result['by_version'].items():
        lines.append(f"|{v}|{s['N']}|{s['TP']}|{s['FP']}|{s['TN']}|{s['FN']}|{s['U_positive']+s['U_negative']}|{fmt(s['precision'])}|{fmt(s['conservative_recall'])}|{fmt(s['false_positive_rate'])}|{fmt(s['location_correct_rate'])}|{fmt(s['raw_executable_rate'])}|")
    lines.extend(['', '## 按漏洞类型分层', '',
                  '|版本|类型|N|准确率|精确率|保守召回率|误报率|定位正确率|',
                  '|---|---|---:|---:|---:|---:|---:|---:|'])
    for version in VERSIONS:
        for vulnerability_type in ("SQLi", "XSS"):
            summary = result['by_type'][version][vulnerability_type]
            lines.append(
                f"|{version}|{vulnerability_type}|{summary['N']}|"
                f"{fmt(summary['all_sample_accuracy'])}|{fmt(summary['precision'])}|"
                f"{fmt(summary['conservative_recall'])}|{fmt(summary['false_positive_rate'])}|"
                f"{fmt(summary['location_correct_rate'])}|"
            )
    lines.extend(['', '## Prompt 版本成对变化', '',
                  '|比较|配对样本|纠正错误|新增退化|净纠错|准确率变化|',
                  '|---|---:|---:|---:|---:|---:|'])
    for item in result['pairwise'].values():
        lines.append(
            f"|{item['before']}→{item['after']}|{item['paired_samples']}|"
            f"{item['resolved_error']}|{item['regression']}|"
            f"{item['net_error_reduction']}|{fmt(item['accuracy_delta'])}|"
        )
    lines.extend([
        '',
        '> 成对变化只比较同一样本在两个 Prompt 版本下的结果；小样本结果仅用于本组受控实验，不能外推为通用识别率。',
    ])
    (out/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Results saved to {out}; incomplete results are not final scores')

if __name__=='__main__':main()
