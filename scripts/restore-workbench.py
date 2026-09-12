#!/usr/bin/env python3
"""Preview by default; restore a baseline only into a new independent directory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('archive',type=Path);p.add_argument('destination',type=Path);p.add_argument('--apply',action='store_true')
a=p.parse_args();archive=a.archive.resolve();destination=a.destination.absolute()
if destination.exists() or any(part=='..' for part in a.destination.parts):p.error('Destination must be a new directory without parent traversal')
for ancestor in [destination,*destination.parents]:
 if ancestor.is_symlink():p.error('Symlink destinations are not accepted')
if not (archive/'checkout.tar.gz').is_file():p.error('Missing checkout archive')
print('Source:',archive,'\nIndependent destination:',destination,'\nOriginal checkout and current runtime will not be changed.')
if not a.apply:print('Preview only. Add --apply to restore.');raise SystemExit(0)
checks=json.loads((archive/'SHA256SUMS.json').read_text())
for name in ['checkout.tar.gz','repository.bundle']:
 if hashlib.sha256((archive/name).read_bytes()).hexdigest()!=checks[name]:raise SystemExit('Archive checksum mismatch: '+name)
destination.mkdir(parents=True,mode=0o700)
with tarfile.open(archive/'checkout.tar.gz') as t:t.extractall(destination,filter='data')
subprocess.run(['git','-C',str(destination/'checkout'),'bundle','verify',str(archive/'repository.bundle')],check=True)
print('Restored source, dirty Git state, untracked files, original build, and snapshotted runtime. Private service/environment configuration remains in the archive/private directory.')
