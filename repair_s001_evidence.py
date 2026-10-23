import json,hashlib
from pathlib import Path
root=Path('.')
items=[('IGNORE_BASE','ignore_task','V0'),('IGNORE_DEF','ignore_task','V2'),('SAFE_BASE','force_safe_verdict','V0'),('SAFE_DEF','force_safe_verdict','V2'),('LEAK_BASE','request_hidden_rules','V0'),('LEAK_DEF','request_hidden_rules','V2'),('DIVERT_BASE','divert_output','V0'),('DIVERT_DEF','divert_output','V2')]
for suf,attack,v in items:
 rid='INJ_SQLI_'+suf; d=root/'runs'/rid
 prompt=(root/'prompts'/f'SQLi_{v}.txt').read_text(encoding='utf8')
 packet=(root/'experiments/prompt_injection/official_packets/S001'/attack/'code_input.txt').read_text(encoding='utf8')
 inp=prompt.rstrip()+'\n\n请审计以下标准化代码输入包：\n\n'+packet
 (d/'input.txt').write_text(inp,encoding='utf8')
 norm=json.loads((d/'normalized.json').read_text(encoding='utf8'))
 if suf=='SAFE_BASE':
  norm['format_valid']=False
  norm['format_errors']=['缺少字段：prerequisites','缺少字段：missing_context','缺少字段：poc_generated','缺少字段：poc_language','缺少字段：poc_instructions']
 norm['input_sha256']=hashlib.sha256(inp.replace('\r\n','\n').encode()).hexdigest()
 (d/'normalized.json').write_text(json.dumps(norm,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 meta=json.loads((d/'metadata.json').read_text(encoding='utf8')); meta['input_sha256']=norm['input_sha256']; meta['evidence_limit']=meta['evidence_limit']+'；input.txt 已补齐。'
 (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
