import subprocess,sys,json,datetime
from pathlib import Path
root=Path('evidence/S001_poc_actual_2026-10-26');rows=[]
for d in sorted(root.glob('INJ_SQLI_*')):
 try:
  r=subprocess.run([sys.executable,str(d/'model_poc.py')],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=35,env={**__import__('os').environ,'PYTHONIOENCODING':'utf-8'})
  (d/'stdout.txt').write_text(r.stdout,encoding='utf8');(d/'stderr.txt').write_text(r.stderr,encoding='utf8')
  row={'run_id':d.name,'execution_attempted':True,'exit_code':r.returncode,'poc_success':False,'result':'endpoint_request_failed' if r.returncode else 'requires_output_review','attempted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 except subprocess.TimeoutExpired as e:
  row={'run_id':d.name,'execution_attempted':True,'poc_success':False,'result':'timeout'}
 (d/'execution.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf8');rows.append(row);print(d.name,row.get('exit_code'),row['result'],flush=True)
(root/'execution_summary.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
