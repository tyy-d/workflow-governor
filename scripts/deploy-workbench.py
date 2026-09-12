#!/usr/bin/env python3
"""Deploy an immutable tested checkout build, or roll back without replacing runtime."""
import argparse,json,os,shutil,subprocess,tarfile,datetime
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--rollback',action='store_true');args=p.parse_args()
repo=Path(__file__).resolve().parents[1];state=Path.home()/'.local/state/workflow-governor';state.mkdir(parents=True,exist_ok=True,mode=0o700)
record=state/'deployment.json';previous=json.loads(record.read_text()) if record.exists() else {}
commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
target=Path(previous['previous']) if args.rollback and previous.get('previous') else state/'releases'/commit
if args.rollback and not previous.get('previous'):p.error('No previous compatible workbench release has been deployed')
print('Release:',target,'\nRuntime retained:',repo/'runtime','\nAction:','rollback' if args.rollback else 'deploy')
if not args.apply:print('Preview only. Add --apply to switch the application service.');raise SystemExit(0)
if not args.rollback and not target.exists():
 target.mkdir(parents=True,mode=0o700)
 archive=target/'source.tar'
 with archive.open('wb') as f:subprocess.run(['git','-C',str(repo),'archive','HEAD'],stdout=f,check=True)
 with tarfile.open(archive) as t:t.extractall(target,filter='data')
 shutil.copytree(repo/'runtime/workbench-preview/frontend-dist',target/'frontend/dist')
# Snapshot current runtime while all application writers are frozen.
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=state/'change-archives'/('deployment-'+stamp);backup.mkdir(parents=True,mode=0o700)
subprocess.run(['systemctl','--user','freeze','workflow-governor.service'],check=True)
try:
 with tarfile.open(backup/'latest-runtime.tar.gz','w:gz') as t:
  t.add(repo/'runtime/workflows',arcname='workflows')
finally:subprocess.run(['systemctl','--user','thaw','workflow-governor.service'],check=True)
(backup/'service.txt').write_bytes(subprocess.check_output(['systemctl','--user','cat','workflow-governor.service']))
config=Path.home()/'.config/systemd/user/workflow-governor.service.d';config.mkdir(parents=True,exist_ok=True)
(config/'workbench.conf').write_text(f'[Service]\nWorkingDirectory={target}\nExecStart=\nExecStart={repo}/.venv/bin/python -u -m governor.server\nEnvironment=PYTHONPATH={target}/src\nEnvironment=GOVERNOR_RUNTIME={repo}/runtime\nEnvironment=GOVERNOR_FRONTEND_DIR={target}/frontend/dist\n')
subprocess.run(['systemctl','--user','daemon-reload'],check=True);subprocess.run(['systemctl','--user','restart','workflow-governor.service'],check=True)
record.write_text(json.dumps({'current':str(target),'previous':previous.get('current'),'runtime':str(repo/'runtime'),'backup':str(backup)},indent=2))
print('Service switched. Current data was retained; pre-switch snapshot:',backup)
