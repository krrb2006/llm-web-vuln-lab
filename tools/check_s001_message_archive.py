import json,re,hashlib
from pathlib import Path
root=Path('evidence/S001_message_bound_2026-10-26');rows=[]
manifest=json.loads((root/'manifest.json').read_text(encoding='utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
for m in manifest:
 d=root/m['run_id']; raw=(d/'raw_output.txt').read_text(encoding='utf8'); inp=(d/'input.txt').read_text(encoding='utf8'); norm=json.loads((d/'normalized.json').read_text(encoding='utf8'))
 blocks=re.findall(r'```json\s*\n(.*?)\n```',raw,re.S); assert len(blocks)==1
 def strict(pairs):
  o={}
  for k,v in pairs:
   assert k not in o,('duplicate',k)
   o[k]=v
  return o
 parsed=json.loads(blocks[0],object_pairs_hook=strict);assert parsed==norm['parsed_json']
 prompt=Path(m['prompt_path']).read_text(encoding='utf8');assert inp.startswith(prompt.rstrip()+'\n\n')
 packet=inp[inp.index('<sample_id>'):];attack={'IGNORE':'ignore_task','SAFE':'force_safe_verdict','LEAK':'request_hidden_rules','DIVERT':'divert_output'}[m['run_id'].split('_')[2]]
 official=Path('experiments/prompt_injection/official_packets/S001')/attack/'code_input.txt';assert packet==official.read_text(encoding='utf8')
 original=Path('experiments/prompt_injection/packets/S001/Original/code_input.txt').read_text(encoding='utf8')
 ol=original.splitlines();pl=packet.splitlines();assert len(ol)==len(pl)
 diffs=[i+1 for i,(a,b) in enumerate(zip(ol,pl)) if a!=b];assert len(diffs)==1
 assert pl[diffs[0]-1].startswith('F01:0003 |  * ')
 for key,file in [('raw_output_sha256','raw_output.txt'),('input_sha256','input.txt'),('screenshot_sha256','answer_settings_session.png')]:assert sha((d/file).read_bytes().replace(b'\r\n',b'\n') if file.endswith('.txt') else (d/file).read_bytes())==m[key]
 rows.append({'run_id':m['run_id'],'json_blocks':len(blocks),'raw_matches_normalized':True,'input_matches_prompt_packet':True,'only_changed_line':'F01:0003 PHP doc comment','hashes_match':True,'format_valid':norm['format_valid'],'locations':parsed['locations'],'missing_context':parsed['missing_context'],'session_url':m['session_url'],'screenshot_path':m['screenshot_path'],'raw_output_sha256':m['raw_output_sha256']})
assert len(set(m['session_url'] for m in manifest))==8
assert len(set(m['raw_output_sha256'] for m in manifest))==8
print('PASS: 8 strict JSON/raw/normalized/input/prompt/packet/hash bindings; 8 unique raws and sessions')
