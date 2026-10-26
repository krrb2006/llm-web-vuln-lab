import json
from pathlib import Path
root=Path('evidence/S001_message_bound_2026-10-26')
ms=json.loads((root/'manifest.json').read_text(encoding='utf8'))
for m in ms:
 m['actual_sent_input_confirmation']={'confirmed_by':'user','statement':'每个 DeepSeek 会话中实际发送的完整输入与对应提交文件一致。','scope':'all eight S001 sessions','evidence_type':'explicit_user_attestation','independent_session_export':False}
 m['input_binding_status']='file_verified_and_user_confirmed_exact_submission'
 (root/m['run_id']/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(root/'manifest.json').write_text(json.dumps(ms,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=root/'source_binding_status.json';rows=json.loads(p.read_text(encoding='utf8'))
for r in rows:
 r['actual_sent_input']['status']='explicit_user_attestation_matches_candidate_file'
 r['actual_sent_input']['confirmation']='用户确认八条实际发送输入与对应文件完全一致；未取得独立会话导出。'
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(root/'USER_INPUT_CONFIRMATION.md').write_text('# 实际输入一致性确认\n\n用户在本对话明确确认：八个 DeepSeek 会话中实际发送的完整输入与各自提交文件一致。\n\n本确认补充来源绑定，证据类型为用户明确声明。对应文件路径和 input SHA-256 见各条 metadata 与 manifest。它不被标记为独立会话导出，也不证明精确模型版本或生成时设置。无需用户重复提交回答、截图或重新向模型提问；是否足以验收由 C/A 裁定。\n',encoding='utf8')
print('Updated eight metadata records and provenance table')
