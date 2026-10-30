import hashlib,json,re
from pathlib import Path
s=Path('json_extract.txt').read_text(encoding='utf8')
ms=list(re.finditer(r'"sample_id"\s*:\s*"S001"',s)); ids=['INJ_SQLI_IGNORE_BASE','INJ_SQLI_IGNORE_DEF','INJ_SQLI_SAFE_BASE','INJ_SQLI_SAFE_DEF','INJ_SQLI_LEAK_BASE','INJ_SQLI_LEAK_DEF','INJ_SQLI_DIVERT_BASE','INJ_SQLI_DIVERT_DEF']
for idx,(rid,m) in enumerate(zip(ids,ms)):
 start=s.rfind('```json',0,m.start()); start=start if start>=0 else s.rfind('{',0,m.start())
 end=ms[idx+1].start() if idx+1<len(ms) else len(s)
 raw=s[start:end].strip(); d=Path('runs')/rid; (d/'raw_output_user.txt').write_text(raw,encoding='utf8')
 sha=hashlib.sha256(raw.replace('\r\n','\n').encode()).hexdigest(); meta=json.loads((d/'metadata.json').read_text(encoding='utf8')); meta['raw_output_user_sha256']=sha; meta['raw_output_order']=idx+1; meta['raw_output_source']='D:/网络安全/json.docx'; (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8'); print(rid,len(raw),sha)
