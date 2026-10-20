"""Offline V1 intake and V0 comparison. Never executes POCs or changes source records."""
import argparse
import csv
import hashlib
import html
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import b_runs

ROOT = Path(__file__).resolve().parents[1]
PENDING = '待复核'
FIELDS = ['sample_id', 'v0_run_id', 'v1_run_id', 'intake_status',
          'v0_prediction', 'v1_prediction', 'prediction_changed',
          'json_check', 'locations_added', 'locations_removed',
          'evidence_fields_changed', 'v0_poc_generated', 'v1_poc_generated',
          'poc_syntax_check', 'input_check', 'session_check',
          'prediction_correctness', 'location_relevance', 'evidence_quality',
          'poc_safety', 'poc_triggered', 'overall_improvement',
          'issues', 'raw_sha256', 'source_file']
MANUAL = ['prediction_correctness', 'location_relevance', 'evidence_quality',
          'poc_safety', 'poc_triggered', 'overall_improvement']
TITLES = dict(zip(FIELDS, ['样本', 'V0运行编号', 'V1运行编号', '原文状态',
    'V0预测', 'V1预测', '预测是否改变', 'JSON检查', '新增行号', '删除行号',
    '文字改变的证据字段', 'V0生成POC', 'V1生成POC', 'POC静态语法检查',
    '输入同包与完整性', '会话元数据', '预测正确性', '行号相关性', '证据质量',
    'POC安全', 'POC实际触发', '是否改善', '问题提示', '原文SHA256', '原文路径']))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False) + '\n', encoding='utf-8')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('重复 JSON 键: ' + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('非标准 JSON 常量: ' + value)


def parse_response(raw, sid, kind, packet):
    """Parse only an entire JSON document or one explicitly labelled JSON fence."""
    result = {'parsed_json': None, 'json_parse_valid': False,
              'json_contract_valid': False, 'json_errors': [],
              'format_warnings': [], 'reference_warnings': [], 'poc_syntax_errors': []}
    try:
        # Parse a newline-normalized view; keep raw bytes and their hashes intact.
        text = raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    except UnicodeError as exc:
        result['json_errors'].append('原文不是 UTF-8: ' + str(exc))
        return result
    blocks = re.findall(r'^\s*```json[^\S\r\n]*\r?\n([\s\S]*?)^\s*```[^\S\r\n]*$',
                        text, re.I | re.M)
    if len(blocks) > 1:
        result['json_errors'].append('存在多个 JSON 代码块，禁止自动选择结论；需人工确认')
        return result
    if blocks:
        candidate = blocks[0]
    else:
        candidate = text.strip()
        result['format_warnings'].append('没有单一完整的 json 代码块；尝试仅解析全文 JSON')
    try:
        obj = json.loads(candidate, object_pairs_hook=unique_object,
                         parse_constant=reject_constant)
        if not isinstance(obj, dict):
            raise ValueError('JSON 根必须为对象')
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        result['json_errors'].append('JSON 无法严格解析: ' + str(exc))
        return result
    result['parsed_json'] = obj
    result['json_parse_valid'] = True
    # Reuse schema and actual-line validation, after strict parsing of the original.
    wrapped = ('```json\n' + json.dumps(obj, ensure_ascii=False) + '\n```').encode()
    _, errors = b_runs.validate(wrapped, sid, kind, packet)
    if not isinstance(obj.get('locations'), list):
        pass  # Already reported by the shared schema checker.
    elif not obj['locations']:
        result['format_warnings'].append('locations 为空；是否合理待复核')
    for key in ('sample_id', 'vulnerability_type', 'poc_instructions'):
        if isinstance(obj.get(key), str) and not obj[key].strip():
            errors.append(key + ' 不能为空字符串')
    extras = set(obj) - set(b_runs.REQUIRED)
    if extras:
        result['format_warnings'].append('额外 JSON 字段: ' + ', '.join(sorted(extras)))
    result['json_errors'] = errors
    result['json_contract_valid'] = not errors
    available = set(re.findall(r'^(F\d{2}:\d{4}) \| ', packet.decode('utf-8-sig'), re.M))
    if isinstance(obj.get('evidence'), dict):
        for field, value in obj['evidence'].items():
            if isinstance(value, str):
                absent = sorted(set(re.findall(r'F\d{2}:\d{4}', value))-available)
                if absent:
                    result['reference_warnings'].append('evidence.' + field + ' 引用输入未包含的行号: ' + ', '.join(absent))
    result['poc_syntax_errors'] = b_runs.validate_poc(raw, obj)
    return result


def prepared(root, rid):
    if not re.fullmatch(r'DEV_S\d{3}_V[01]_R\d+', rid):
        raise ValueError('非法 DEV run_id: ' + str(rid))
    directory = root / 'runs' / rid
    meta = read_json(directory / 'metadata.json')
    if not isinstance(meta, dict):
        raise ValueError(rid + ' 的 metadata 必须为对象')
    data = (directory / 'input.txt').read_bytes()
    errors = []
    if meta.get('run_id') != rid:
        errors.append(rid + ' 的 metadata.run_id 不一致')
    if sha(data) != meta.get('input_sha256'):
        errors.append(rid + ' 的完整输入 SHA-256 不一致')
    match = re.search(rb'(?m)^<sample_id>S\d{3}</sample_id>', data)
    if not match:
        raise ValueError(rid + ' 无标准化 sample_id 边界')
    packet = data[match.start():]
    if sha(packet) != meta.get('packet_sha256'):
        errors.append(rid + ' 的 code_input SHA-256 不一致')
    prefix = data[:match.start()].rstrip(b'\r\n') + b'\n'
    if sha(prefix) != meta.get('prompt_sha256'):
        errors.append(rid + ' 的内嵌 Prompt SHA-256 不一致')
    if f"<sample_id>{meta.get('sample_id')}</sample_id>".encode() not in packet:
        errors.append(rid + ' 的输入 sample_id 与元数据不一致')
    return meta, data, errors


def raw_candidates(inbox, rid):
    return [p for p in (inbox / rid / 'raw_output.txt',
                        inbox / (rid + '_raw_output.txt'), inbox / (rid + '.txt'))
            if p.is_file()]


def session_check(source, meta):
    # Session data is supplied by the user, never inferred from model prose.
    path = (source.parent / 'session.json' if source.name == 'raw_output.txt'
            else source.with_suffix('.session.json'))
    errors = []
    if not path.is_file():
        return None, ['缺少 session.json；实际模型、设置与提交时间待复核']
    try:
        session = read_json(path)
        if not isinstance(session, dict):
            raise ValueError('session 必须是 JSON 对象')
    except (ValueError, OSError) as exc:
        return None, ['session 无法读取: ' + str(exc)]
    expected = {'model_display_name': meta.get('planned_model_display_name'),
                'model_settings': meta.get('planned_model_settings')}
    for field, value in expected.items():
        if not session.get(field):
            errors.append(field + ' 未填')
        elif value and session[field] != value:
            errors.append(field + ' 与计划配置不同，不能直接作为同条件对照')
    submitted = session.get('submitted_at')
    try:
        if not isinstance(submitted, str):
            raise ValueError('提交时间未填')
        stamp = datetime.fromisoformat(submitted.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('提交时间无时区')
    except ValueError as exc:
        errors.append(str(exc))
    if session.get('new_independent_chat') is not True:
        errors.append('独立新会话未确认')
    if session.get('additional_user_messages') != 0 or type(session.get('additional_user_messages')) is not int:
        errors.append('追加消息数量未填或不为 0；首轮条件待复核')
    return session, errors


def display(value):
    if value is None:
        return '未知'
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def compare_value(a, b):
    return '是（仅文本/结构变化）' if a != b else '否'


def analyze_one(root, inbox, sid, snapshots, watch):
    rid = f'DEV_{sid}_V1_R1'
    row = {field: '' for field in FIELDS}
    row.update(sample_id=sid, v1_run_id=rid, intake_status='待保存原文')
    row.update({field: PENDING for field in MANUAL})
    detail = {'sample_id': sid, 'v1_run_id': rid, 'manual_review': {f: PENDING for f in MANUAL},
              'issues': [], 'field_differences': {}, 'original_unchanged': None}
    issues = detail['issues']
    try:
        meta, v1_input, integrity = prepared(root, rid)
        v0rid = meta.get('v0_reference_run_id')
        if not isinstance(v0rid, str) or not v0rid.startswith('DEV_' + sid + '_V0_'):
            raise ValueError('V1 缺少本样本的有效 v0_reference_run_id，禁止猜测基线')
        old_meta, v0_input, old_integrity = prepared(root, v0rid)
        if meta.get('sample_id') != sid or meta.get('prompt_version') != 'V1':
            integrity.append('V1 元数据的样本/版本不一致')
        if meta.get('packet_sha256') != old_meta.get('packet_sha256'):
            integrity.append('V0/V1 code_input SHA-256 不同，不能归因于 Prompt')
        issues.extend(integrity + old_integrity)
        row['input_check'] = '通过（哈希/同包）' if not (integrity or old_integrity) else '不通过'
        row['v0_run_id'] = v0rid
        detail.update(v0_run_id=v0rid, v1_metadata=meta, v0_metadata=old_meta)
        old_raw = (root / 'runs' / v0rid / 'raw_output.txt').read_bytes()
        if sha(old_raw) != old_meta.get('raw_output_sha256'):
            issues.append('V0 原文哈希不匹配，基线完整性不通过')
            row['input_check'] = '不通过'
        old_result = parse_response(old_raw, sid, meta['vulnerability_type'], v0_input)
        detail['v0_check'] = old_result
        old = old_result['parsed_json'] or {}
        row['v0_prediction'] = display(old.get('prediction'))
        row['v0_poc_generated'] = display(old.get('poc_generated'))
        if not old_result['json_contract_valid']:
            issues.append('V0 JSON 契约不通过；对照只能做有限结构比较')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        issues.append('准备记录或 V0 基线错误: ' + str(exc))
        row.update(intake_status='准备/基线错误', input_check='不通过')
        row['issues'] = '\n'.join(issues)
        return row, detail
    candidates = raw_candidates(inbox, rid)
    if not candidates:
        row['issues'] = '\n'.join(issues)
        return row, detail
    if len(candidates) > 1:
        issues.append('找到多个原文文件，禁止自动挑选: ' + ', '.join(str(p) for p in candidates))
        row.update(intake_status='多份原文冲突', issues='\n'.join(issues))
        return row, detail
    source = candidates[0]
    try:
        raw = source.read_bytes()
    except OSError as exc:
        issues.append('原文读取失败: ' + str(exc))
        row.update(intake_status='原文读取失败', issues='\n'.join(issues))
        return row, detail
    digest = sha(raw)
    watch.append((source, digest))
    snapshot = snapshots / (rid + '_raw_output.txt')
    snapshot.write_bytes(raw)
    if sha(snapshot.read_bytes()) != digest:
        raise ValueError('原文快照哈希不一致')
    result = parse_response(raw, sid, meta['vulnerability_type'], v1_input)
    session, session_errors = session_check(source, meta)
    issues.extend(session_errors)
    issues.extend(result['json_errors'] + result['format_warnings'] + result['reference_warnings'] + result['poc_syntax_errors'])
    obj = result['parsed_json'] or {}
    detail.update(v1_check=result, source_file=str(source.resolve()), raw_sha256=digest,
                  raw_snapshot=str(snapshot.name), session=session,
                  session_issues=session_errors)
    row.update(intake_status='已读取（本地分析）', source_file=str(source.resolve()), raw_sha256=digest,
               json_check=('通过' if result['json_contract_valid'] and not result['format_warnings']
                           else '字段通过；格式有提示' if result['json_contract_valid'] else '不通过'),
               v1_prediction=display(obj.get('prediction')),
               v1_poc_generated=display(obj.get('poc_generated')),
               session_check='待补充/复核' if session_errors else '自报字段与计划一致',
               poc_syntax_check=('失败（仅静态）' if result['poc_syntax_errors'] else
                                 'Python 静态语法通过；仍待复核' if obj.get('poc_language') == 'python3' and obj.get('poc_generated') is True
                                 else '手工步骤待复核' if obj.get('poc_generated') is True
                                 else '未生成 POC' if obj.get('poc_generated') is False else '未知'))
    if result['json_parse_valid'] and old_result['json_parse_valid']:
        valid_predictions = ('vulnerable', 'safe', 'uncertain')
        row['prediction_changed'] = (compare_value(old.get('prediction'), obj.get('prediction'))
                                     if old.get('prediction') in valid_predictions and obj.get('prediction') in valid_predictions
                                     else '不可比较（prediction 无效/缺失）')
        if isinstance(old.get('locations'), list) and isinstance(obj.get('locations'), list):
            left = {x for x in old['locations'] if isinstance(x, str)}
            right = {x for x in obj['locations'] if isinstance(x, str)}
            row['locations_added'] = ', '.join(sorted(right-left))
            row['locations_removed'] = ', '.join(sorted(left-right))
        if isinstance(old.get('evidence'), dict) and isinstance(obj.get('evidence'), dict):
            row['evidence_fields_changed'] = ', '.join(k for k in ('source', 'flow', 'guard', 'sink')
                                                      if old['evidence'].get(k) != obj['evidence'].get(k))
        for field in b_runs.REQUIRED:
            if old.get(field) != obj.get(field):
                detail['field_differences'][field] = {'v0': old.get(field), 'v1': obj.get(field)}
    row['issues'] = '\n'.join(issues)
    return row, detail


def csv_safe(value):
    text = display(value)
    # Prevent model/user text becoming a spreadsheet formula when CSV is opened.
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text


def render_html(rows, details, summary):
    esc = lambda x: html.escape(display(x), quote=True)
    labels = {'sample_id': '样本', 'intake_status': '原文状态', 'v0_prediction': 'V0 判断',
              'v1_prediction': 'V1 判断', 'prediction_changed': '判断是否改变',
              'json_check': 'JSON', 'input_check': '输入同包/完整性',
              'locations_added': '新增行号', 'locations_removed': '删除行号',
              'evidence_fields_changed': '证据字段文字变化', 'v1_poc_generated': 'V1 生成 POC',
              'poc_syntax_check': 'POC 静态检查', 'session_check': '会话元数据',
              'overall_improvement': '是否改善', 'issues': '问题提示'}
    columns = list(labels)
    body = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">',
            '<title>B 本地 V1 对照分析</title><style>body{font:15px/1.6 system-ui,sans-serif;margin:28px;color:#17212b}table{border-collapse:collapse;width:100%}td,th{border:1px solid #d5dce3;padding:8px;text-align:left;vertical-align:top}th{background:#edf2f7}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7f9;padding:14px}summary{cursor:pointer;font-weight:600}h1{font-size:24px}.scroll{overflow:auto}td{min-width:100px}</style>',
            '<h1>B 本地 V1 / V0 对照</h1>',
            '<p>只读本地分析；不调用模型、不执行 POC、不修改原文或 runs。文字改变不等于证据改善，格式通过不等于漏洞判断正确。</p>',
            '<pre>' + esc(summary) + '</pre><div class="scroll"><table><tr>',
            ''.join('<th>'+esc(labels[k])+'</th>' for k in columns), '</tr>']
    for row in rows:
        body.append('<tr>' + ''.join('<td>'+esc(row[k]).replace('\n', '<br>')+'</td>' for k in columns) + '</tr>')
    body.append('</table></div><h2>逐例详情与人工核对</h2>')
    for detail in details:
        body.extend(['<details><summary>'+esc(detail['sample_id'])+'</summary>',
                     '<p>人工判断：预测正确性、行号相关性、证据充分性、POC 安全与触发、总体改善，全部待复核。</p>',
                     '<pre>'+esc(json.dumps(detail, ensure_ascii=False, indent=2))+'</pre></details>'])
    body.append('</html>')
    return '\n'.join(body)


def analyze(root, inbox, output, samples):
    root, inbox, output = Path(root).resolve(), Path(inbox).resolve(), Path(output).resolve()
    if not inbox.is_dir():
        raise ValueError('找不到收件箱；先执行 init 或指定 --inbox')
    # Output cannot be an ancestor/descendant of the input inbox or repository evidence.
    if output == inbox or output.is_relative_to(inbox) or inbox.is_relative_to(output):
        raise ValueError('报告目录必须与 inbox 分离')
    for protected in (root/'runs', root/'prompts', root/'dataset', root/'pocs', root/'evidence'):
        if output == protected or output.is_relative_to(protected) or protected.is_relative_to(output):
            raise ValueError('报告目录不得覆盖实验或源码目录')
    output.mkdir(parents=True, exist_ok=False)
    snapshots = output/'raw_snapshots'; snapshots.mkdir()
    watch, rows, details = [], [], []
    for sid in samples:
        row, detail = analyze_one(root, inbox, sid, snapshots, watch)
        rows.append(row); details.append(detail)
    for source, expected in watch:
        if sha(source.read_bytes()) != expected:
            raise ValueError('分析期间原文发生变化，报告作废，请另开输出目录重跑: ' + str(source))
    for detail in details:
        if 'raw_sha256' in detail:
            detail['original_unchanged'] = True
    summary = {'expected': len(samples), 'raw_read': len(watch),
               'json_contract_pass': sum(bool(d.get('v1_check', {}).get('json_contract_valid')) for d in details),
               'same_packet_integrity_pass': sum(r['input_check'].startswith('通过') for r in rows),
               'missing_or_conflicting_raw': len(samples)-len(watch),
               'manual_review': PENDING, 'poc_execution': '未执行',
               'repository_record_status': '只读分析；未导入或修改 runs',
               'created_at': datetime.now(timezone.utc).isoformat()}
    known = {p.resolve() for sid in samples for p in raw_candidates(inbox, f'DEV_{sid}_V1_R1')}
    summary['unrecognized_text_files'] = [str(p.resolve()) for p in inbox.rglob('*.txt')
                                           if p.name != 'README.txt' and p.resolve() not in known]
    write_json(output/'analysis.json', {'summary': summary, 'rows': rows, 'details': details})
    stream = io.StringIO(newline='')
    writer = csv.writer(stream); writer.writerow([TITLES[k] for k in FIELDS])
    for row in rows: writer.writerow([csv_safe(row[k]) for k in FIELDS])
    (output/'analysis.csv').write_bytes(stream.getvalue().encode('utf-8-sig'))
    (output/'analysis.html').write_text(render_html(rows, details, summary), encoding='utf-8')
    review = ['# V1 人工复核表', '', '本表初始全部待复核；自动分析不填准确率或提升。', '',
              '|样本|预测正确性|行号相关性|证据充分性|POC 安全|POC 真实触发|总体改善|证据路径/意见|',
              '|---|---|---|---|---|---|---|---|']
    review.extend('|'+r['sample_id']+'|'+'|'.join([PENDING]*6)+'||' for r in rows)
    (output/'human_review.md').write_text('\n'.join(review)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))
    print('报告: ' + str(output/'analysis.html'))
    return summary


def initialize(root, inbox, samples):
    inbox = Path(inbox).resolve()
    root = Path(root).resolve()
    for protected in (root/'runs', root/'prompts', root/'dataset', root/'pocs', root/'evidence'):
        if inbox == protected or inbox.is_relative_to(protected) or protected.is_relative_to(inbox):
            raise ValueError('inbox 不得位于实验或源码目录中')
    if inbox.exists():
        raise ValueError('inbox 已存在；为防覆盖请选择新目录')
    metadata = {sid: read_json(root/'runs'/f'DEV_{sid}_V1_R1'/'metadata.json') for sid in samples}
    inbox.mkdir(parents=True)
    for sid in samples:
        rid = f'DEV_{sid}_V1_R1'
        meta = metadata[sid]
        d = inbox/rid; d.mkdir()
        write_json(d/'session.json', {
            'model_display_name': None, 'model_settings': None, 'submitted_at': None,
            'new_independent_chat': None, 'additional_user_messages': None,
            'notes': '', 'planned_model_display_name': meta.get('planned_model_display_name'),
            'planned_model_settings': meta.get('planned_model_settings')})
    (inbox/'README.txt').write_text(
        '把每条完整首轮回答保存到对应 run_id 文件夹下 raw_output.txt（UTF-8）。\n'
        '不要修复 JSON 或删掉模型解释。session.json 上半部分填写实际网页信息；未知留 null。\n'
        'submitted_at 示例 2026-10-19T15:30+08:00；不要把模型自报时间当作网页提交时间。\n'
        '这是本地收件箱，不会自动上传、执行代码或写入仓库运行记录。\n', encoding='utf-8')
    print('已创建本地收件箱: ' + str(inbox))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'analyze'))
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--inbox', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--samples', nargs='+', choices=b_runs.DEV, default=list(b_runs.DEV))
    args = parser.parse_args()
    if len(set(args.samples)) != len(args.samples): parser.error('samples 重复')
    inbox = args.inbox or args.root/'local'/'b_v1_inbox'
    try:
        if args.command == 'init':
            initialize(args.root, inbox, args.samples)
        else:
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            output = args.out or args.root/'local'/'b_v1_reports'/stamp
            analyze(args.root, inbox, output, args.samples)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, '错误: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
