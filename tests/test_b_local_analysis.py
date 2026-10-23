"""Synthetic software tests only; no real model observations or POC execution."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import b_local_analysis as local


def answer(sid='S001', prediction='safe', location='F01:0001', source='input'):
    return {'sample_id': sid, 'prediction': prediction, 'vulnerability_type': 'SQL注入',
            'locations': [location], 'evidence': {'source': source, 'flow': 'flow',
                                                'guard': 'guard', 'sink': 'sink'},
            'prerequisites': [], 'missing_context': [], 'poc_generated': False,
            'poc_language': 'none', 'poc_instructions': 'none'}


def encode(obj):
    return ('```json\n' + json.dumps(obj, ensure_ascii=False) + '\n```\n').encode('utf-8')


class LocalAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'repo'; self.root.mkdir()
        self.inbox = Path(self.temp.name)/'inbox'; self.inbox.mkdir()
        self.out = Path(self.temp.name)/'report'
        self.rid = 'DEV_S001_V1_R1'
        self.directory = self.inbox/self.rid; self.directory.mkdir()
        self.raw = self.directory/'raw_output.txt'
        packet = b'<sample_id>S001</sample_id>\n<untrusted_code>\nF01:0001 | sample\n</untrusted_code>\n'
        self.packet = packet
        self.baseline = 'DEV_S001_V0_R1'
        for version in ('V0', 'V1'):
            rid = f'DEV_S001_{version}_R1'
            d = self.root/'runs'/rid; d.mkdir(parents=True)
            prompt = (version+' prompt\n').encode()
            content = prompt+b'\n'+packet
            (d/'input.txt').write_bytes(content)
            meta = {'run_id': rid, 'sample_id': 'S001', 'prompt_version': version,
                    'vulnerability_type': 'SQLi', 'input_sha256': local.sha(content),
                    'packet_sha256': local.sha(packet), 'prompt_sha256': local.sha(prompt),
                    'planned_model_display_name': 'Synthetic model',
                    'planned_model_settings': 'Synthetic settings'}
            if version == 'V0':
                raw = encode(answer()); (d/'raw_output.txt').write_bytes(raw)
                meta['raw_output_sha256'] = local.sha(raw)
            else:
                meta['v0_reference_run_id'] = self.baseline
            local.write_json(d/'metadata.json', meta)

    def analyze(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return local.analyze(self.root, self.inbox, self.out, ['S001'])

    def report(self):
        return local.read_json(self.out/'analysis.json')

    def test_end_to_end_original_and_repository_unchanged(self):
        raw = encode(answer(prediction='vulnerable'))
        self.raw.write_bytes(raw)
        before = {str(p): p.read_bytes() for p in (self.root/'runs').rglob('*') if p.is_file()}
        summary = self.analyze()
        self.assertEqual(summary['raw_read'], 1)
        self.assertEqual(self.raw.read_bytes(), raw)
        self.assertEqual((self.out/'raw_snapshots'/f'{self.rid}_raw_output.txt').read_bytes(), raw)
        self.assertEqual(before, {str(p): p.read_bytes() for p in (self.root/'runs').rglob('*') if p.is_file()})
        row = self.report()['rows'][0]
        self.assertEqual(row['prediction_changed'], '是（仅文本/结构变化）')
        self.assertEqual(row['overall_improvement'], '待复核')
        self.assertIn('待补充', row['session_check'])
        self.assertTrue(self.report()['details'][0]['original_unchanged'])

    def test_refusal_and_invalid_location_preserved(self):
        self.raw.write_bytes('无法完成此请求'.encode())
        self.analyze()
        self.assertFalse(self.report()['details'][0]['v1_check']['json_parse_valid'])
        self.assertEqual(self.raw.read_bytes(), '无法完成此请求'.encode())
        check = local.parse_response(encode(answer(location='F01:9999')), 'S001', 'SQLi', self.packet)
        self.assertTrue(check['json_parse_valid'])
        self.assertFalse(check['json_contract_valid'])
        self.assertTrue(any('absent' in e for e in check['json_errors']))
        check = local.parse_response(encode(answer(source='F01:9999 not supplied')), 'S001', 'SQLi', self.packet)
        self.assertTrue(check['json_contract_valid'])
        self.assertTrue(check['reference_warnings'])

    def test_strict_json_rejects_duplicates_constants_and_multiple_blocks(self):
        values = [b'```json\n{"sample_id":"S001","sample_id":"S002"}\n```',
                  b'```json\n{"x":NaN}\n```',
                  encode(answer())+encode(answer(prediction='vulnerable'))]
        for raw in values:
            with self.subTest(raw=raw[:30]):
                check = local.parse_response(raw, 'S001', 'SQLi', self.packet)
                self.assertFalse(check['json_parse_valid'])
        check = local.parse_response(json.dumps(answer(), ensure_ascii=False).encode(), 'S001', 'SQLi', self.packet)
        self.assertTrue(check['json_contract_valid'])
        self.assertTrue(check['format_warnings'])

    def test_input_tampering_detected(self):
        self.raw.write_bytes(encode(answer()))
        p = self.root/'runs'/self.rid/'input.txt'
        p.write_bytes(p.read_bytes()+b'changed\n')
        self.analyze()
        self.assertEqual(self.report()['rows'][0]['input_check'], '不通过')

    def test_conflicting_files_not_selected(self):
        self.raw.write_bytes(encode(answer()))
        (self.inbox/(self.rid+'.txt')).write_bytes(encode(answer(prediction='vulnerable')))
        summary = self.analyze()
        self.assertEqual(summary['raw_read'], 0)
        self.assertEqual(self.report()['rows'][0]['intake_status'], '多份原文冲突')

    def test_html_csv_and_poc_never_executed(self):
        obj = answer(source='<script>alert(1)</script>')
        obj.update(poc_generated=True, poc_language='python3')
        sentinel = Path(self.temp.name)/'SHOULD_NOT_EXIST'
        raw = encode(obj) + ('```python\nfrom pathlib import Path\nPath('+repr(str(sentinel))+').touch()\n```\n').encode()
        self.raw.write_bytes(raw)
        self.analyze()
        page = (self.out/'analysis.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertFalse(sentinel.exists())
        self.assertTrue(local.csv_safe('=SUM(1,2)').startswith("'"))
        self.assertTrue(local.csv_safe('  @bad').startswith("'"))

    def test_output_refuses_overwrite(self):
        self.raw.write_bytes(encode(answer()))
        self.analyze()
        report_hash = local.sha((self.out/'analysis.json').read_bytes())
        with self.assertRaises(FileExistsError): self.analyze()
        self.assertEqual(local.sha((self.out/'analysis.json').read_bytes()), report_hash)

    def test_session_mismatch_and_unknown_time(self):
        self.raw.write_bytes(encode(answer()))
        local.write_json(self.directory/'session.json', {'model_display_name': 'Other model',
                         'model_settings': 'Other settings', 'submitted_at': None,
                         'new_independent_chat': False, 'additional_user_messages': 2})
        self.analyze()
        issues = self.report()['details'][0]['session_issues']
        self.assertTrue(any('不同' in x for x in issues))
        self.assertTrue(any('时间' in x for x in issues))
        self.assertTrue(any('独立' in x for x in issues))

    def test_missing_raw_not_observation_and_unrecognized_name(self):
        (self.inbox/'wrong_name.txt').write_bytes(encode(answer()))
        summary = self.analyze()
        self.assertEqual(summary['raw_read'], 0)
        self.assertEqual(self.report()['rows'][0]['intake_status'], '待保存原文')
        self.assertEqual(len(summary['unrecognized_text_files']), 1)

    def test_declared_v0_baseline_does_not_pick_pilot(self):
        old = self.root/'runs'/self.baseline
        new_rid = 'DEV_S001_V0_R2'
        new = self.root/'runs'/new_rid; new.mkdir()
        for file in old.iterdir(): (new/file.name).write_bytes(file.read_bytes())
        meta = local.read_json(new/'metadata.json');meta['run_id'] = new_rid
        raw = encode(answer(prediction='vulnerable'));(new/'raw_output.txt').write_bytes(raw)
        meta['raw_output_sha256'] = local.sha(raw);local.write_json(new/'metadata.json', meta)
        meta = local.read_json(self.root/'runs'/self.rid/'metadata.json')
        meta['v0_reference_run_id'] = new_rid
        local.write_json(self.root/'runs'/self.rid/'metadata.json', meta)
        self.raw.write_bytes(encode(answer(prediction='vulnerable')))
        self.analyze()
        self.assertEqual(self.report()['rows'][0]['v0_run_id'], new_rid)
        self.assertEqual(self.report()['rows'][0]['prediction_changed'], '否')


if __name__ == '__main__':
    unittest.main()
