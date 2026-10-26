import json
from pathlib import Path
root=Path('evidence/S001_message_bound_2026-10-26')
ms=json.loads((root/'manifest.json').read_text(encoding='utf8')); rows=[]
for m in ms:
 row={'run_id':m['run_id'],'session_url':{'value':m['session_url'],'source':m['screenshot_path'],'status':'visible_in_user_screenshot'},'actual_sent_input':{'value':None,'candidate_file':m['input_path'],'candidate_sha256':m['input_sha256'],'status':'insufficient_session_export_missing'},'full_answer':{'file':m['raw_output_path'],'sha256':m['raw_output_sha256'],'source_message_id':m['source_message_id'],'status':'user_supplied_full_text_not_direct_session_export'},'answer_screenshot':{'file':m['screenshot_path'],'sha256':m['screenshot_sha256'],'status':'partial_answer_visible'},'prompt':{'file':m['prompt_path'],'sha256':m['prompt_sha256'],'version':m['prompt_version'],'status':'repository_candidate_verified'},'model_version':{'value':None,'status':'not_observed'},'generation_settings':{'declared':'deep thinking on; intelligent search off','observed':'same settings visible at screenshot capture','status':'generation_time_not_independently_proven'},'disposition':'conditional_exploration_only','count_as_completed':False,'plan_status':'planned','poc_execution':'no_model_poc_execution_evidence'}
 rows.append(row)
 m['review_status']='source_evidence_insufficient_conditional_exploration';m['count_as_completed']=False
 m.pop('historical_SAFE_BASE',None)
 if m['run_id']=='INJ_SQLI_SAFE_BASE':m['historical_format_note']='Old incomplete response remains in history; this separately sourced answer has ten fields and format_valid=true.'
 (root/m['run_id']/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(root/'manifest.json').write_text(json.dumps(ms,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(root/'source_binding_status.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# S001 条件探索与来源绑定说明','', '本说明落实用户提供的课程口径；未重新审阅课程原文件，课程要求引用由 A 最终核定。','', 'S001 八条完成文件层检查，可用于讨论四类注释注入的设计与模型静态回答。现有材料不足以完整证明实际发送输入、生成时设置及精确模型版本，因此继续 planned，不计入已完成加分数量。','', '|run_id|会话URL|实际输入|完整回答来源|截图|三类哈希|模型/生成设置|处置|','|---|---|---|---|---|---|---|---|']
for m in ms:lines.append('|'+m['run_id']+'|[截图所示会话]('+m['session_url']+')|仅候选重建文件|用户逐条消息|部分回答与开关可见|已核对候选文件|版本缺失，生成时未证明|条件探索，不计数|')
lines+=['','逐条完整路径、哈希和来源 ID 见 source_binding_status.json、manifest.json；文件内容自检见 self_check.json。','', '报告可引用：在 S001 四类 PHP 注释注入的八份用户提供回答中，静态 SQLi 判断均为 vulnerable。文件层核对未发现本候选的跨条 raw、重复原文或 normalized 错配。完整实际输入尚未由会话导出，回答截图未覆盖全文，模型版本和生成设置证据受限，模型 POC 未获得实操验证，因此仅作为条件接受的探索结果，不纳入完成数量或完整验证结论。','', '后续仅从已有 DeepSeek 会话导出输入及完整回合并保留来源；不补写缺失证据，不要求重新向模型提问。C 复核，A 裁定状态。历史材料保持原样。']
(root/'CONDITIONAL_EXPLORATION.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('8 per-run source status rows written; count_as_completed=false for all')
