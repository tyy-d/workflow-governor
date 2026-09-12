# Quiet workbench on GB10

The existing user service serves the built React app and same-origin Python API on port 8080. Model transport uses the existing loopback vLLM OpenAI-compatible service, alias `qwen-local`; no model container configuration was changed.

## Operate

```bash
systemctl --user status workflow-governor.service
systemctl --user restart workflow-governor.service
journalctl --user -u workflow-governor.service -n 50
```

The application uses immutable source/build releases under `~/.local/state/workflow-governor/releases/`. The deployment record is `~/.local/state/workflow-governor/deployment.json`; current runtime stays in the original checkout's `runtime/`. The service drop-in selects a release, leaving the original service and model unchanged.

From the development checkout, after tests and preview browser acceptance:

```bash
python3 -u scripts/deploy-workbench.py             # preview
python3 -u scripts/deploy-workbench.py --apply
python3 -u scripts/deploy-workbench.py --rollback  # preview previous compatible release
python3 -u scripts/deploy-workbench.py --rollback --apply
```

Switching versions freezes only this application's writers for a consistent pre-switch runtime snapshot, thaws them, then restarts the application. It never replaces the runtime with old data. Rollback is between compatible workbench releases. The original pre-workbench application uses a different manifest format and must be restored independently for inspection, rather than pointed at new shared-store manifests.

## Baseline and recovery

The initial baseline archive is `~/.local/state/workflow-governor/change-archives/20260912T200009Z/`. It includes the Git bundle, dirty patches, untracked files, original source/build/runtime and restricted service/model configuration. Model weights and rebuildable dependencies are excluded; their locations and versions are recorded. Restore rehearsal verified 514 files and cloned the bundle successfully.

```bash
python3 -u scripts/restore-workbench.py ARCHIVE NEW_DIRECTORY
python3 -u scripts/restore-workbench.py ARCHIVE NEW_DIRECTORY --apply
```

Both the destination check and archive checksums are enforced. Restore never writes into the original checkout. Private configuration remains in the archive's restricted `private/` directory and is not committed.

## Inspect or replay saved work

```bash
python3 -u scripts/replay-workflow.py WORKFLOW_ID
python3 -u scripts/replay-workflow.py WORKFLOW_ID --new-draft
```

The default only inspects original results, source hashes, plan and run identity. A new draft requires explicit planning and approval in the UI. Model outputs can differ; no task or external action is replayed automatically.

## Validation and limits

```bash
.venv/bin/python -u -m pytest -v --durations=0 -o log_cli=true -o addopts=''
PATH="$HOME/openclaw-demo/runtime/tools/node/bin:$PATH" npm run typecheck --prefix frontend
PATH="$HOME/openclaw-demo/runtime/tools/node/bin:$PATH" npm run build --prefix frontend -- --outDir ../runtime/workbench-preview/frontend-dist
GOVERNOR_TEST_URL=http://127.0.0.1:8081 node scripts/workbench-acceptance.mjs
```

The real browser slice selects two CASE_001 workspace files, proposes and approves a plan, executes deterministic and local-model tasks, inspects evidence, and refreshes. It deliberately stops at the human task: authorized operator routing is not available. This is a structural workflow verification, not a hidden-answer business evaluation. Existing historical workflows remain visible and read-only without migration. Multi-user authentication and external business connectors are not provided. Use the existing trusted GB10 network.

Screenshots, real model records, test logs, and restart checks are under `runtime/workbench-preview/` and `runtime/workbench-deployed/`. Source delivery targets the original `tyy-d/workflow-governor` main branch. Local stage commits and restore bundles are retained independently.
