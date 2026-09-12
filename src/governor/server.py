import json
import mimetypes
import os
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,unquote
from .store import Store
from .workspace import Workspace
from .service import Service
from .model import BASE,MODEL

REPO=Path(__file__).resolve().parents[2]
RUNTIME=Path(os.getenv('GOVERNOR_RUNTIME',str(REPO/'runtime')))
GRANTS=json.loads((REPO/'config/workspaces.json').read_text())
SERVICE=Service(Store(RUNTIME/'workflows'),Workspace(REPO,GRANTS))

class Handler(BaseHTTPRequestHandler):
    def send_json(self,status,value):
        data=json.dumps(value,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)

    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        try:
            if path=='/api/health':return self.send_json(200,{'ok':True,'model':MODEL,'modelUrl':BASE,'execution':'local-vllm','openclaw':'not integrated'})
            if path=='/api/workspaces':return self.send_json(200,[{'id':k,'label':v['label']} for k,v in GRANTS.items()])
            if path=='/api/workflows':return self.send_json(200,SERVICE.store.list())
            parts=path.strip('/').split('/')
            if len(parts)==3 and parts[:2]==['api','workflows']:return self.send_json(200,SERVICE.store.read(parts[2]))
            if path.startswith('/api/'):return self.send_json(404,{'error':'Not found'})
            root=(REPO/'frontend/dist').resolve();file=(root/path.lstrip('/')).resolve()
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
            if parts==['api','workflows']:return self.send_json(202,SERVICE.create(data))
            if len(parts)<4 or parts[:2]!=['api','workflows']:return self.send_json(404,{'error':'Not found'})
            identity=parts[2];action=parts[3]
            if action=='approve':value=SERVICE.approve(identity)
            elif action=='plan':value=SERVICE.plan(identity)
            elif action=='revise':value=SERVICE.revise(identity,data['note'])
            elif action=='evidence' and len(parts)==5:value=SERVICE.evidence_action(identity,parts[4],data['action'])
            elif action=='tasks' and len(parts)==6:
                task=parts[4]
                if parts[5]=='execute':value=SERVICE.execute(identity,task)
                elif parts[5]=='human':value=SERVICE.human(identity,task,data)
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
