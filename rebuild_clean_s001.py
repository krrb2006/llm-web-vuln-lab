import json,hashlib,re,shutil
from pathlib import Path
s=Path('json_extract.txt').read_text(encoding='utf8')
ms=list(re.finditer(r'"sample_id"\s*:\s*"S001"',s)); ids=['IGNORE_BASE','IGNORE_DEF','SAFE_BASE','SAFE_DEF','LEAK_BASE','LEAK_DEF','DIVERT_BASE','DIVERT_DEF']
shots=['001_answer.png','002_answer.png','003_answer.png','004_answer.png','005_answer.png','006_answer.png','007_answer.png','008_answer.png']
urls=['b593ee08-c9eb-417e-b011-97350d747734','d65cdc79-c39c-498f-83d1-f89a2ca11f0f','4f287957-d470-4540-bd20-40aec8d8fe11','c928f67d-93ff-49ef-90a6-4956cb2ed675','b8ceab65-32d0-4646-9bdd-ab309fdc8b65','60692dc6-be17-47c9-ba25-324b30900abe','7913a3a9-1fb4-4b33-9ce4-23abb4c1aee3','a1c98934-16e2-4efe-8bc8-ec07884089ff']
root=Path('evidence/S001_clean_rerun'); root.mkdir(parents=True,exist_ok=True); manifest=[]
for i,(rid,m) in enumerate(zip(ids,ms)):
 start=s.rfind('```json',0,m.start()); start=start if start>=0 else s.rfind('{',0,m.start()); end=ms[i+1].start() if i+1<len(ms) else len(s); raw=s[start:end].strip(); d=root/('INJ_SQLI_'+rid); d.mkdir(exist_ok=True); (d/'raw_output.txt').write_text(raw,encoding='utf8'); shutil.copy2('evidence/user_S001_rerun_screenshots/'+shots[i],d/'answer_settings_session.png'); sha=hashlib.sha256(raw.replace('\r\n','\n').encode()).hexdigest(); manifest.append({'run_id':'INJ_SQLI_'+rid,'session_url':'https://chat.deepseek.com/a/chat/s/'+urls[i],'raw_output':'evidence/S001_clean_rerun/INJ_SQLI_'+rid+'/raw_output.txt','answer_settings_session':'evidence/S001_clean_rerun/INJ_SQLI_'+rid+'/answer_settings_session.png','raw_output_sha256':sha,'source':'D:/网络安全/json.docx','settings':'deep thinking on; intelligent search off','poc_executed':False})
(root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('clean archive created',len(manifest))
