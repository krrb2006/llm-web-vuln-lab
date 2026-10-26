import json,hashlib,zipfile
from pathlib import Path
r=Path('evidence/S001_message_bound_2026-10-26')
for name in ['CONDITIONAL_EXPLORATION.md','B_PRE_C_CHECK.md','REVIEW.md']:
 p=r/name;s=p.read_text(encoding='utf8')
 s=s.replace('仅候选重建文件','已核对文件，用户确认实际原样提交')
 s=s.replace('现有材料不足以完整证明实际发送输入、生成时设置及精确模型版本','用户已明确确认八条实际发送输入与文件完全一致；生成时设置及精确模型版本仍缺独立页面证明')
 s+='\n\n更新：用户已明确确认八条实际发送输入与对应文件完全一致，见 USER_INPUT_CONFIRMATION.md。input 为已核对文件及用户确认来源，不再列作“未获用户确认”。尚无独立会话输入导出。当前八条模型 POC 已实际启动执行但均连接失败，详情见 ../S001_poc_actual_2026-10-26/README.md；不能记为成功触发。\n'
 p.write_text(s,encoding='utf8')
index={'candidate_directory':str(r).replace('\\','/'),'supersedes':['evidence/S001_clean_rerun','runs/INJ_SQLI_* old raw_output_user.txt bindings'],'plan_status':'planned','user_input_confirmation':str(r/'USER_INPUT_CONFIRMATION.md').replace('\\','/'),'file_binding_audit':str(r/'self_check.json').replace('\\','/'),'run_manifest':str(r/'manifest.json').replace('\\','/'),'poc_execution_evidence':'evidence/S001_poc_actual_2026-10-26','poc_result':'8 original scripts attempted, endpoint requests failed; no successful trigger','review_scope':'C independently verifies; A decides status','files':[]}
for p in sorted(r.rglob('*')):
 if p.is_file():index['files'].append({'path':str(p).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n') if p.suffix in ['.txt','.md','.json'] else p.read_bytes()).hexdigest(),'hash_rule':'LF canonical text; binary exact'})
Path('results/B_S001_CURRENT_CANDIDATE.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
Path('results/B_S001_CURRENT_CANDIDATE.md').write_text('# S001 唯一待复核候选\n\n请仅验收 evidence/S001_message_bound_2026-10-26，逐条清单见该目录 manifest.json，完整文件索引及哈希见 B_S001_CURRENT_CANDIDATE.json。旧 S001_clean_rerun 和旧 runs 原文绑定均为审计历史。\n\n已解决：逐消息恢复原文；跨条残留；第6/7条重复；图文可见字段错配；normalized与raw不一致；8条URL、截图及三类哈希；用户对实际完整输入一致性的明确确认。新 SAFE_BASE 十字段齐全，格式通过，历史缺字段版本不变。\n\n尚需裁定：模型版本无页面证明；生成时设置仅有用户声明和事后截图；raw来自用户完整复制回答，非会话直接导出；截图覆盖部分回答。POC八条已真实启动但靶场连接失败，未验证触发。保持planned，不要求用户重跑DeepSeek。\n\nC只复核候选来源和文件，A决定验收及统计。\n',encoding='utf8')
print('Current candidate index and updated handoff created')
