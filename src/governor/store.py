import json
import os
import re
import threading
from pathlib import Path

class Store:
    def __init__(self, root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock()

    def directory(self, identity):
        if not re.fullmatch(r'WF-[a-f0-9]{12}',identity):
            raise ValueError('Invalid workflow identity')
        return self.root/identity

    def read(self, identity):
        with self.lock:
            return json.loads((self.directory(identity)/'manifest.json').read_text())

    def write_json(self, path, value):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_suffix(path.suffix+'.tmp')
        with open(temp,'w') as f:
            json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(temp,path)

    def save(self, value):
        with self.lock:
            self.write_json(self.directory(value['id'])/'manifest.json',value)

    def list(self):
        with self.lock:
            return sorted([json.loads(p.read_text()) for p in self.root.glob('WF-*/manifest.json')],key=lambda x:x['createdAt'],reverse=True)
