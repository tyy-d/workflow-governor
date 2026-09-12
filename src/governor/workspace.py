import hashlib
import json
import re
from pathlib import Path
from workflow_governor.core.config import RuntimeConfig
from workflow_governor.workspace import WorkspaceScout, WorkspaceGrant, DiscoveryLimits, RetrievalLimits

SUPPORTED = {'.md', '.txt', '.json', '.csv'}
FORBIDDEN = {'ground_truth', 'provenance', 'personas', 'persona_memory'}

class Workspace:
    def __init__(self, repo, grants):
        self.repo = Path(repo).resolve()
        self.grants = grants

    def safe(self, relative):
        p = Path(relative)
        if p.is_absolute() or '..' in p.parts or FORBIDDEN.intersection(p.parts) or p.name == 'evaluator.json':
            raise ValueError('Path is outside the authorized evidence boundary')
        resolved = (self.repo / p).resolve()
        if not resolved.is_relative_to(self.repo) or resolved != self.repo / p:
            raise ValueError('Symlinks and paths outside the repository are not granted')
        return resolved

    def inventory(self, key):
        grant=WorkspaceGrant(key,self.grants[key]['root'])
        scout=WorkspaceScout(RuntimeConfig(self.repo),grants=(grant,))
        workspace_map=scout.discover(grant,DiscoveryLimits(max_files=500,max_bytes_per_file=60000,max_total_bytes=2000000,max_preview_chars=0))
        return [{'id':'E-'+hashlib.sha256((grant.root+'/'+f.relative_path).encode()).hexdigest()[:10],
                 'path':grant.root+'/'+f.relative_path,'name':f.name,'size':f.size,
                 'extractable':Path(f.relative_path).suffix.lower() in SUPPORTED and f.size<=60000}
                for f in workspace_map.files]

    def extract(self, record, sections=None):
        p = self.safe(record['path'])
        if p.suffix.lower() not in SUPPORTED or p.stat().st_size > 60000:
            raise ValueError('Unsupported file or evidence exceeds 60 KB limit')
        raw = p.read_text(encoding='utf-8')
        numbered = []
        active = sections is None
        for n, line in enumerate(raw.splitlines(), 1):
            heading = re.match(r'^#{2,3}\s+(\d+(?:\.\d+)*\.?)\s', line)
            if sections and heading:
                section = heading.group(1).rstrip('.')
                active = any(section == s.rstrip('.') or section.startswith(s.rstrip('.') + '.') for s in sections)
            if active:
                numbered.append({'line': n, 'text': line})
        content = '\n'.join(f"L{x['line']}: {x['text']}" for x in numbered)
        if len(content) > 24000:
            raise ValueError('Selected evidence exceeds per-document context limit')
        return dict(record, content=content, lines=numbered, sha256=hashlib.sha256(raw.encode()).hexdigest(), policy=sections is not None)

    def policies(self, key):
        return [self.extract({'id': 'P-' + hashlib.sha256(p['path'].encode()).hexdigest()[:10],
                              'path': p['path'], 'name': Path(p['path']).name}, p['sections'])
                for p in self.grants[key]['policies']]

    def selected(self, key, ids):
        available = {r['id']: r for r in self.inventory(key)}
        if len(ids) > 10 or not ids or len(set(ids)) != len(ids):
            raise ValueError('Select 1–10 distinct authorized sources')
        return [self.extract(available[i]) for i in ids]

    def referenced_pending(self, key, selected, limit=2):
        """Follow explicit filenames on unresolved record lines, never hidden paths.
        Generic one-hop evidence discovery; no business-specific filenames or IDs.
        """
        inventory=self.inventory(key)
        existing={s['id'] for s in selected};found=[]
        for s in selected:
            for line in s['lines']:
                if not re.search(r'\b(?:REVIEW|FAIL|BLOCKED|PENDING|MISSING|EXPIRED)\b',line['text'],re.I):continue
                for record in inventory:
                    if record['id'] not in existing and record['extractable'] and record['name'] in line['text']:
                        extract=self.extract(record)
                        extract['discoveryRef']={'sourceId':s['id'],'line':line['line'],'reason':'Explicit filename in a pending/review/failure record'}
                        found.append(extract);existing.add(record['id'])
                        if len(found)>=limit:return found
        return found
