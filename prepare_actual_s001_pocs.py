import re,json,hashlib,ast
from pathlib import Path
root=Path('evidence/S001_message_bound_2026-10-26');out=Path('evidence/S001_poc_actual_2026-10-26');out.mkdir(exist_ok=True)
rows=[]
for d in sorted(root.glob('INJ_SQLI_*')):
 raw=(d/'raw_output.txt').read_text(encoding='utf8');blocks=re.findall(r'```python(?:3)?\s*\n(.*?)\n```',raw,re.S);assert len(blocks)==1,d
 code=blocks[0]+'\n';ast.parse(code)
 assert '127.0.0.1' in code and '4280' in code
 dst=out/d.name;dst.mkdir(exist_ok=True);(dst/'model_poc.py').write_text(code,encoding='utf8')
 rows.append({'run_id':d.name,'source_raw':str(d/'raw_output.txt'),'script_sha256':hashlib.sha256(code.encode()).hexdigest(),'syntax_valid':True})
(out/'scripts.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
print('8 original model scripts extracted, syntax valid, localhost targets checked')
