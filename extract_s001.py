import zipfile,re,html,os
from pathlib import Path
p=r'D:\网络安全\s001(1).docx'
s=zipfile.ZipFile(p).read('word/document.xml').decode()
s=re.sub(r'</w:p>','\n',s); s=re.sub(r'<w:tab[^>]*/>','\t',s); s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
needle='"sample_id": "S001"'
pos=[]; i=0
while True:
 i=s.find(needle,i)
 if i<0: break
 pos.append(i); i+=len(needle)
assert len(pos)==8, len(pos)
ids=['INJ_SQLI_IGNORE_BASE','INJ_SQLI_IGNORE_DEF','INJ_SQLI_SAFE_BASE','INJ_SQLI_SAFE_DEF','INJ_SQLI_LEAK_BASE','INJ_SQLI_LEAK_DEF','INJ_SQLI_DIVERT_BASE','INJ_SQLI_DIVERT_DEF']
root=Path('runs')
for n,(rid,start0) in enumerate(zip(ids,pos)):
 start=s.rfind('```json',0,start0)
 if start<0: start=s.rfind('{',0,start0)
 end=s.find('```json',start+7)
 if end<0: end=len(s)
 seg=s[start:end].strip()
 d=root/rid
 d.mkdir(parents=True,exist_ok=True)
 (d/'raw_output.txt').write_text(seg,encoding='utf-8')
 (d/'extraction_note.txt').write_text(f'Extracted from s001(1).docx by confirmed order; position {n+1}/8.\n',encoding='utf-8')
print('extracted',len(pos))
for rid in ids: print(rid,(root/rid/'raw_output.txt').stat().st_size)
