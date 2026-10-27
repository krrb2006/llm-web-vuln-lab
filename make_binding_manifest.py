import json,hashlib
from pathlib import Path
ids=['IGNORE_BASE','IGNORE_DEF','SAFE_BASE','SAFE_DEF','LEAK_BASE','LEAK_DEF','DIVERT_BASE','DIVERT_DEF']
shots={'IGNORE_BASE':'001_answer.png','IGNORE_DEF':'002_answer.png','SAFE_BASE':'003_answer.png','SAFE_DEF':'004_answer.png','LEAK_BASE':'005_answer.png','LEAK_DEF':'006_answer.png','DIVERT_BASE':'007_answer.png','DIVERT_DEF':'008_answer.png'}
urls={'IGNORE_BASE':'b593ee08-c9eb-417e-b011-97350d747734','IGNORE_DEF':'d65cdc79-c39c-498f-83d1-f89a2ca11f0f','SAFE_BASE':'4f287957-d470-4540-bd20-40aec8d8fe11','SAFE_DEF':'c928f67d-93ff-49ef-90a6-4956cb2ed675','LEAK_BASE':'b8ceab65-32d0-4646-9bdd-ab309fdc8b65','LEAK_DEF':'60692dc6-be17-47c9-ba25-324b30900abe','DIVERT_BASE':'7913a3a9-1fb4-4b33-9ce4-23abb4c1aee3','DIVERT_DEF':'a1c98934-16e2-4efe-8bc8-ec07884089ff'}
out=[]
for x in ids:
 d=Path('runs')/('INJ_SQLI_'+x); m=json.loads((d/'metadata.json').read_text(encoding='utf8')); raw=(d/'raw_output_user.txt').read_bytes().replace(b'\r\n',b'\n'); inp=(d/'input.txt').read_bytes().replace(b'\r\n',b'\n'); out.append({'run_id':'INJ_SQLI_'+x,'session_url':'https://chat.deepseek.com/a/chat/s/'+urls[x],'screenshot':'evidence/user_S001_rerun_screenshots/'+shots[x],'raw_output_sha256':hashlib.sha256(raw).hexdigest(),'input_sha256':hashlib.sha256(inp).hexdigest(),'prompt_sha256':m.get('prompt_sha256'),'settings':'shared screenshot: deep thinking on, intelligent search off','poc_executed':False})
Path('results/B_S001_rerun_binding_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
