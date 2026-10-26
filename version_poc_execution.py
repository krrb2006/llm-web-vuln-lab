import json,hashlib
from pathlib import Path
cand=Path('evidence/S001_message_bound_2026-10-26'); p=Path('evidence/S001_poc_verified_2026-10-26');
summary=json.loads((p/'execution_summary.json').read_text(encoding='utf8'))
for row in summary:
 rid=row['run_id']; d=cand/rid; ed=p/rid
 script=(ed/'model_poc.py').read_bytes(); raw=(d/'raw_output.txt').read_bytes();
 exec_record={'schema_version':'poc-execution-v2','run_id':rid,'executed_at':row.get('started_at_utc'),'exit_code':row['exit_code'],'success_observed':row['exit_code']==0,'poc_script_path':str(ed/'model_poc.py').replace('\\','/'),'stdout_path':str(ed/'stdout.txt').replace('\\','/'),'stderr_path':str(ed/'stderr.txt').replace('\\','/'),'script_sha256_raw_bytes':hashlib.sha256(script).hexdigest(),'script_sha256_lf':hashlib.sha256(script.replace(b'\r\n',b'\n')).hexdigest(),'stdout_sha256':row['stdout_sha256'],'stderr_sha256':row['stderr_sha256'],'request_capture_scope':'local POC stdout plus shared request/response captures; per-run raw HTTP capture not present','database_write':False,'historical_poc_fields':'Earlier metadata fields remain unchanged for audit history'}
 (d/'poc_execution_v2.json').write_text(json.dumps(exec_record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 m=json.loads((d/'metadata.json').read_text(encoding='utf8'));m['poc_execution_v2_path']=str(d/'poc_execution_v2.json').replace('\\','/');m['poc_execution_status']='executed_success_observed';m['poc_execution_note']='Versioned execution record added; legacy poc_executed fields are preserved, not overwritten.'
 (d/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('updated',len(summary))
