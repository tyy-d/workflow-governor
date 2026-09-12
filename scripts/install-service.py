#!/usr/bin/env python3
"""Install this checkout as a user service; no model service mutation."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
logs=root/'runtime/deployment';logs.mkdir(parents=True,exist_ok=True)
unit=logs/'workflow-governor.service'
unit.write_text(f'''[Unit]
Description=Workflow Governor local runtime
After=network.target
[Service]
Type=simple
WorkingDirectory={root}
ExecStart={root}/scripts/run-server.sh
Environment=GOVERNOR_HOST=0.0.0.0
Environment=GOVERNOR_PORT=8080
Restart=on-failure
RestartSec=3
UMask=0077
StandardOutput=append:{logs}/server.log
StandardError=append:{logs}/server.log
[Install]
WantedBy=default.target
''')
for command in [['link',str(unit)],['daemon-reload'],['enable','--now','workflow-governor.service']]:
 subprocess.run(['systemctl','--user',*command],check=True)
