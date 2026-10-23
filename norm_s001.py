import json,re
from pathlib import Path
for d in sorted(Path('runs').glob('INJ_SQLI_*')):
 raw=(d/'raw_output.txt').read_text(encoding='utf8')
 m=re.search(r'\{\s*"sample_id"\s*:',raw)
 if not m: print('NO',d); continue
 try:
  obj=json.JSONDecoder().raw_decode(raw[m.start():])[0]
  (d/'normalized.json').write_text(json.dumps({'run_id':d.name,'format_valid':True,'parsed_json':obj,'poc_executed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  print('OK',d.name,obj.get('prediction'))
 except Exception as e: print('ERR',d,e)
