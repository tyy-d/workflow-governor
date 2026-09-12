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

## Document workbench and persistence

- Replaced the production mock-driven workspace layout with a collapsible sidebar, workflow database list, document page, task/evidence dialog, and results/history sections.
- Server-authorized file selection; explicit create / generate / approve / execute steps.
- New workflows use Track A ArtifactStore / WorkflowStateLoader and Thomas's shared planner, validator, runner, context and result contracts. Historical workflow files are read-only; no implicit migration.
- New human tasks wait honestly for the missing operator routing module.
- Creation idempotency survives a lost response; execution readiness and operation locking reject duplicate task execution. Model concurrency is bounded to two and requests time out after 240 seconds.
- Preview service: workflow-governor-preview.service on loopback 8081, separate runtime and frontend build.
- 76 backend tests pass; frontend typecheck and build pass. Real Chromium acceptance is running; progress logs are in runtime/workbench-preview/browser.log.
- User confirmed GitHub permissions cannot be fixed now; continue local code and deployment only.
