import hashlib,json
from pathlib import Path
root=Path('.')
ids=[('IGNORE_BASE','ignore_task','V0'),('IGNORE_DEF','ignore_task','V2'),('SAFE_BASE','force_safe_verdict','V0'),('SAFE_DEF','force_safe_verdict','V2'),('LEAK_BASE','request_hidden_rules','V0'),('LEAK_DEF','request_hidden_rules','V2'),('DIVERT_BASE','divert_output','V0'),('DIVERT_DEF','divert_output','V2')]
for suf,attack,v in ids:
 rid='INJ_SQLI_'+suf
 packet=root/'experiments/prompt_injection/official_packets/S001'/attack/'code_input.txt'
 prompt=root/'prompts'/f'SQLi_{v}.txt'
 sha=lambda p: hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
 meta={'run_id':rid,'sample_id':'S001','attack':attack,'condition':'baseline' if suf.endswith('BASE') else 'defended','prompt_version':v,'model_display_name':None,'model_settings':'深度思考=开；智能搜索=关','prompt_sha256':sha(prompt),'input_packet_sha256':sha(packet),'source':'s001(1).docx','settings_screenshot':'evidence/user_S001_settings/deep_thinking_on_search_off.png','poc_executed':False,'evidence_limit':'模型名称未在截图中显示，按用户要求跳过；不能由此证明页面模型标签。'}
 d=root/'runs'/rid; d.mkdir(parents=True,exist_ok=True); (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
