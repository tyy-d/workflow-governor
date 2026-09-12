# Workbench implementation progress

## Baseline — 2026-09-12

- Existing GB10 integration is uncommitted on `integration/gb10-case001`, based on `797ccaf`.
- Source, untracked integration, runtime and service configuration archived outside checkout under the user state directory. Runtime consistency: systemd cgroup freeze/thaw; model untouched.
- Independent archive extraction: 514 regular files verified; Git bundle verified and cloned. Baseline 36 tests passed.
- Before screenshots: home and workflow, 1440 x 1000. Local Qwen real inference returned 42 in 0.44 seconds, reasoning disabled.
- Upstream `47cdd71` includes Track A `856b1dd`; integrate its existing storage contracts.
- GitHub connector account MeowzillaBang has pull=true, push=false. Original main delivery is blocked pending write access.
- Deployment: existing user service `workflow-governor.service`, port 8080; model service unchanged on loopback 8000.
- Local archive pointer: `/tmp/governor-current-archive` (durable archive is under ~/.local/state/workflow-governor/change-archives/).

## Continue

Inspect Git status and this record, then run `.venv/bin/python -u -m pytest -v --durations=0 -o log_cli=true -o addopts=''`.
Next: preserve the existing integration in a baseline commit; merge current upstream; build document workbench and wire shared persistence.
