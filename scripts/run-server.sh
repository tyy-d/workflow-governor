#!/bin/bash
set -euo pipefail
GOVERNOR_REPO=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$GOVERNOR_REPO"
export PYTHONPATH="$GOVERNOR_REPO/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$GOVERNOR_REPO/.venv/bin/python" -u -m governor.server
