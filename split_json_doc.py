import hashlib,json,re
from pathlib import Path
s=Path('json_extract.txt').read_text(encoding='utf8')
needle='"sample_id": "S001"'; pos=[]; i=0
while True:
 i=s.find(needle,i)
 if i<0: break
 pos.append(i); i+=1
ids=['INJ_SQLI_IGNORE_BASE','INJ_SQLI_IGNORE_DEF','INJ_SQLI_SAFE_BASE','INJ_SQLI_SAFE_DEF','INJ_SQLI_LEAK_BASE','INJ_SQLI_LEAK_DEF','INJ_SQLI_DIVERT_BASE','INJ_SQLI_DIVERT_DEF']
for idx,(rid,p) in enumerate(zip(ids,pos)):
 start=s.rfind('```json',0,p)
 if start<0: start=s.rfind('{',0,p)
 end=pos[idx+1] if idx+1<len(pos) else len(s)
 # remove trailing separators only, preserve answer content
 raw=s[start:end].strip()
 d=Path('runs')/rid
 (d/'raw_output_user.txt').write_text(raw,encoding='utf8')
 sha=hashlib.sha256(raw.replace('\r\n','\n').encode()).hexdigest()
 m=json.loads((d/'metadata.json').read_text(encoding='utf8'))
 m['raw_output_user_sha256']=sha; m['raw_output_source']='D:/网络安全/json.docx'; m['raw_output_order']=idx+1
 (d/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(rid,len(raw),sha)
