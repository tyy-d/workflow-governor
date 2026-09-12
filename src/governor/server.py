import json
import mimetypes
import os
import hashlib
import urllib.request
from workflow_governor.core.config import confined
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,unquote
from .store import Store
from .workspace import Workspace
from .service import Service
from .model import BASE,MODEL
from workflow_governor.human.interaction import FileHumanInteractionStore

REPO=Path(__file__).resolve().parents[2]
RUNTIME=Path(os.getenv('GOVERNOR_RUNTIME',str(REPO/'runtime')))
GRANTS=json.loads((REPO/'config/workspaces.json').read_text(encoding='utf-8'))
SERVICE=Service(Store(RUNTIME/'workflows',REPO,GRANTS),Workspace(REPO,GRANTS),human_interactions=FileHumanInteractionStore(RUNTIME))

class Handler(BaseHTTPRequestHandler):
    def send_json(self,status,value):
        data=json.dumps(value,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)

    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        try:
            if path=='/api/health':
                reachable=False
                try:
                    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(BASE+'/models',timeout=3) as response:
                        reachable=any(m['id']==MODEL for m in json.load(response)['data'])
                except Exception:pass
                return self.send_json(200,{'ok':True,'model':MODEL,'modelReachable':reachable,'protocol':'OpenAI-compatible','humanRouting':SERVICE.human_validator is not None})
            if path=='/api/workspaces':return self.send_json(200,[{'id':k,'label':v['label']} for k,v in GRANTS.items()])
            if path=='/api/workflows':return self.send_json(200,SERVICE.store.list())
            parts=path.strip('/').split('/')
            if len(parts)==4 and parts[:2]==['api','workspaces'] and parts[3]=='files':
                if parts[2] not in GRANTS:raise ValueError('Workspace is not authorized')
                return self.send_json(200,SERVICE.workspace.inventory(parts[2]))
            if len(parts)==4 and parts[:2]==['api','workflows'] and parts[3]=='history':
                w=SERVICE.store.read(parts[2]);root=SERVICE.store.directory(parts[2])
                records=[]
                for folder in ['artifacts/runs','artifacts/plans']:
                    for p in sorted(confined(root,folder).glob('*.json')):
                        records.append({'file':p.name,'record':json.loads(confined(root,p.relative_to(root).as_posix()).read_text(encoding='utf-8'))})
                return self.send_json(200,{'records':records})
            if len(parts)==3 and parts[:2]==['api','workflows']:return self.send_json(200,SERVICE.store.read(parts[2]))
            if len(parts)==6 and parts[:2]==['api','workflows'] and parts[3]=='tasks' and parts[5]=='handoff':
                return self.send_json(200,SERVICE.human_handoff(parts[2],parts[4]).to_dict())
            if path.startswith('/api/'):return self.send_json(404,{'error':'Not found'})
            root=Path(os.getenv('GOVERNOR_FRONTEND_DIR',str(REPO/'frontend/dist'))).resolve();file=confined(root,path.lstrip('/') or 'index.html')
            if not file.is_relative_to(root):raise ValueError('Invalid static path')
            if not file.is_file():file=root/'index.html'
            data=file.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(file))[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(data)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
        except FileNotFoundError:self.send_json(404,{'error':'Not found'})
        except Exception as e:self.send_json(400,{'error':str(e)})

    def do_POST(self):
        try:
            origin=self.headers.get('Origin')
            if origin and urlparse(origin).netloc!=self.headers.get('Host'):return self.send_json(403,{'error':'Cross-origin mutations are not permitted'})
            if not self.headers.get('Content-Type','').startswith('application/json'):raise ValueError('JSON content type required')
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=32000:raise ValueError('Request size out of bounds')
            data=json.loads(self.rfile.read(size));parts=urlparse(self.path).path.strip('/').split('/')
            if parts==['api','workflows']:
                if not set(data)<={'name','objective','workspace','sourceIds'}:raise ValueError('Unknown workflow fields')
                key=self.headers.get('Idempotency-Key','')
                if not 16<=len(key)<=128:raise ValueError('A valid request identity is required')
                identity='WF-'+hashlib.sha256(key.encode()).hexdigest()[:12]
                with SERVICE.store.lock:
                    if (SERVICE.store.directory(identity)/'manifest.json').exists():
                        value=SERVICE.store.read(identity)
                        if value['objective']!=data['objective'].strip() or value['workspaceKey']!=data['workspace'] or value.get('selectedSourceIds')!=data.get('sourceIds',[]):raise ValueError('Request identity was already used with different inputs')
                    else:value=SERVICE.create(dict(data,_identity=identity))
                return self.send_json(202,value)
            if len(parts)<4 or parts[:2]!=['api','workflows']:return self.send_json(404,{'error':'Not found'})
            identity=parts[2];action=parts[3]
            if SERVICE.store.read(identity).get('readOnly'):raise ValueError('This saved workflow is read-only; create a new workflow to continue')
            if action=='approve':value=SERVICE.approve(identity)
            elif action=='plan':value=SERVICE.plan(identity)
            elif action=='revise':value=SERVICE.revise(identity,data['note'])
            elif action=='evidence' and len(parts)==5:value=SERVICE.evidence_action(identity,parts[4],data['action'])
            elif action=='tasks' and len(parts)==6:
                task=parts[4]
                if parts[5]=='execute':value=SERVICE.execute(identity,task)
                elif parts[5]=='human':value=SERVICE.human(identity,task,data,session_id=self.headers.get('X-Session-Id',''))
                elif parts[5]=='resume':value=SERVICE.resume(identity,task,data['note'])
                else:raise ValueError('Unsupported task action')
            else:raise ValueError('Unsupported workflow action')
            return self.send_json(200,value)
        except FileNotFoundError:self.send_json(404,{'error':'Workflow not found'})
        except (ValueError,KeyError,StopIteration) as e:self.send_json(409,{'error':str(e) or 'Invalid state or reference'})
        except Exception as e:self.send_json(500,{'error':str(e)})

if __name__=='__main__':
    address=(os.getenv('GOVERNOR_HOST','0.0.0.0'),int(os.getenv('GOVERNOR_PORT','8080')))
    print('Workflow Governor serving',address,'model',BASE,MODEL,flush=True)
    ThreadingHTTPServer(address,Handler).serve_forever()
