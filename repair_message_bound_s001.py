import json,re,hashlib,shutil
from pathlib import Path
p=max(Path(r'C:/Users/Saoirse/.codex/sessions/2026/10/19').glob('*01a152ed*.jsonl'),key=lambda x:x.stat().st_size)
found={}
for line in p.open(encoding='utf8'):
 o=json.loads(line); q=o.get('payload',{})
 if q.get('role')!='user':continue
 s='\n'.join(c.get('text','') for c in q.get('content',[]) if isinstance(c,dict))
 m=re.search(r'这是([1-8])(?:模型输出的结果)?\s*$',s)
 if m and s.startswith('```json'):
  found[int(m[1])]=(s[:m.start()].rstrip()+'\n',o['timestamp'],q.get('id'))
assert set(found)==set(range(1,9)),list(found)
ids=['IGNORE_BASE','IGNORE_DEF','SAFE_BASE','SAFE_DEF','LEAK_BASE','LEAK_DEF','DIVERT_BASE','DIVERT_DEF']
old=json.loads(Path('evidence/S001_clean_rerun/manifest.json').read_text(encoding='utf8'))
root=Path('evidence/S001_message_bound_2026-10-26');root.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
required=['sample_id','prediction','vulnerability_type','locations','evidence','prerequisites','missing_context','poc_generated','poc_language','poc_instructions']
manifest=[]
for i,x in enumerate(ids,1):
 rid='INJ_SQLI_'+x;d=root/rid;d.mkdir(exist_ok=True); raw,t,mid=found[i]
 duplicates=[]
 def pairs(ps):
  r={}
  for k,v in ps:
   if k in r:duplicates.append(k)
   r[k]=v
  return r
 blocks=re.findall(r'```json\s*\n(.*?)\n```',raw,re.S);assert len(blocks)==1,(rid,len(blocks))
 obj=json.loads(blocks[0],object_pairs_hook=pairs);missing=[k for k in required if k not in obj]
 (d/'raw_output.txt').write_bytes(raw.encode())
 inp=Path('runs')/rid/'input.txt';(d/'input.txt').write_bytes(inp.read_bytes().replace(b'\r\n',b'\n'))
 prompt=Path('prompts')/('SQLi_V0.txt' if x.endswith('BASE') else 'SQLi_V2.txt')
 shutil.copy2('evidence/user_S001_rerun_screenshots/'+f'{i:03}_answer.png',d/'answer_settings_session.png')
 norm={'run_id':rid,'format_valid':not missing and not duplicates,'format_errors':['missing:'+k for k in missing]+['duplicate:'+k for k in duplicates],'parsed_json':obj,'poc_execution':'not_run_for_this_response'}
 (d/'normalized.json').write_text(json.dumps(norm,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 meta={'run_id':rid,'session_url':old[i-1]['session_url'],'source':'User message in current Codex conversation','source_message_id':mid,'received_at':t,'run_timestamp':None,'prompt_path':str(prompt).replace('\\','/'),'prompt_sha256':sha(prompt.read_bytes().replace(b'\r\n',b'\n')),'input_sha256':sha((d/'input.txt').read_bytes()),'raw_output_sha256':sha((d/'raw_output.txt').read_bytes()),'screenshot_sha256':sha((d/'answer_settings_session.png').read_bytes()),'input_provenance':'Reconstructed from the supplied submission file; not exported from DeepSeek session','model_display_name':None,'settings_evidence':'Screenshot shows deep thinking enabled and intelligent search unselected; submission-time state not independently captured','review_status':'pending_C_review','historical_SAFE_BASE':'Old incomplete response retained in historical directories; this message has all ten required fields'}
 (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8');manifest.append(meta)
 assert raw.count('"sample_id"')==1
 assert obj['prediction']=='vulnerable'
 print(rid,len(raw),norm['format_valid'],len(obj['locations']),obj['evidence']['source'][:45])
assert len({m['raw_output_sha256'] for m in manifest})==8
assert len({m['session_url'] for m in manifest})==8
(root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
