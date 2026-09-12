# Workflow Governor — local GB10 application

Thomas's React frontend is served with a persistent Python backend. Model work uses the existing local Qwen service; no cloud API, model download or model-service restart is required.

## Start and operate

On the configured GB10:

```bash
cd ~/workflow-governor
systemctl --user start workflow-governor.service
systemctl --user stop workflow-governor.service
systemctl --user restart workflow-governor.service
systemctl --user status workflow-governor.service
tail -f runtime/deployment/server.log
```

Open port **8080** on the GB10's LAN IP, or http://127.0.0.1:8080/ on the GB10 itself. Frontend and backend share this origin; browser clients never connect directly to the model. The user service is enabled and restarts after process failure. LAN access currently assumes a trusted demo network: multi-user login/authorization is not implemented. Workflow approval is not corporate authorization.

Create a workflow, select Northstar Vendor Activation, and enter the minimal request:

> Can you figure out what we need to do to get this vendor live by Friday?

Wait for the model proposal, inspect evidence and tasks, then **Approve Plan**. Select each ready task and **Execute Task**. For Human work, supply reviewer name, judgment and reason. Clarification/narrowing/reassignment/authority refusal creates a blocked task; **Resume Task** requires a recovery reason. After human review, execute final synthesis. Refreshing preserves the current workflow URL and server state; human draft fields are also retained in that browser.

Completed means the review tasks are complete. Read remaining business blockers and authority boundaries in the final result; it never means a vendor was actually activated or a purchase order transmitted.

## Existing model and OpenClaw

- Actual model: **Qwen/Qwen3.8-27B-FP8**; served alias **qwen-local**.
- API: **http://127.0.0.1:8000/v1**, chat completions, context 16384; Governor requests disable thinking to bound latency.
- Existing model management: `cd ~/model-serving && python3 scripts/compose.py up -d`; logs with `python3 scripts/compose.py logs -f vllm`.
- vLLM 0.29.0 runs in the existing ARM64 GPU container; this deployment does not modify it.
- OpenClaw 2026.9.4 independent file-read/write/readback test passed in 133.64 seconds, 4 tool calls, zero errors. Its UI remains http://127.0.0.1:18789/ and `~/openclaw-demo/openclaw dashboard` opens an authenticated session.
- OpenClaw is **not integrated as a Governor executor**. Current real execution is deterministic Python + direct local vLLM + browser human input.

Baseline evidence and model image/revision details are copied to `runtime/deployment/openclaw-verification.json`, `model-versions.json`, and `baseline.json`.

## Reproduce from this checkout

Python 3.11+ and Node compatible with the locked frontend dependencies are needed. This GB10 reuses Node 24.19.0 already installed by OpenClaw.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
export PATH="$HOME/openclaw-demo/runtime/tools/node/bin:$PATH"
npm ci --prefix frontend
npm run build --prefix frontend
python3 scripts/install-service.py
```

Foreground backend: `scripts/run-server.sh`. Optional environment variables: `GOVERNOR_HOST`, `GOVERNOR_PORT`, `GOVERNOR_RUNTIME`, `GOVERNOR_MODEL_URL`, `GOVERNOR_MODEL_ID`. Model URL is restricted to loopback. Default grants are explicit repository-relative paths in `config/workspaces.json`. Adding a workspace requires a deliberate server configuration change; arbitrary browser filesystem paths and hidden fixture access are rejected.

## State, logs and evidence

`runtime/workflows/<id>/` contains:

- `manifest.json`: authoritative persisted workflow and source snapshots.
- `input/workspace-map.json`, `input/sources.json`: metadata-first discovery and granted extracts with source hashes/line numbers.
- `plans/`, `plan.md`: model draft, shared contracts and explicit approval history.
- `model/`: actual local-model requests, responses, usage, elapsed time and errors.
- `tasks/<id>/`: task/context/result and execution attempts, including shared runner events with `mock_assisted: false`.
- `artifacts/human/`: durable human judgment and clarification/recovery history.
- `final/summary.json`, `final/summary.md`: refreshed real findings, blockers, actions and authority notes.

Findings require an existing source ID and nonempty actual source line; the server attaches the exact original text rather than asking the model to reproduce it. Click citations to inspect the original numbered source snapshot. Failures remain blocked and recoverable. Server restart changes an interrupted operation to explicit Blocked rather than claiming completion. Original case fixtures remain read-only.

## Validation

```bash
.venv/bin/python -m pytest
npm run build --prefix frontend
```

Browser acceptance setup (test tooling only):

```bash
npm install --prefix runtime/browser playwright
runtime/browser/node_modules/.bin/playwright install chromium
GOVERNOR_TEST_URL=http://127.0.0.1:8080 node scripts/browser-acceptance.mjs
```

This executes real local-model planning/synthesis and browser interactions. It fills human input as an explicitly labeled automated demonstration operator, not an actual employee. Logs/screenshots/results live in `runtime/deployment/`. The browser test creates a new workflow and uses the selected fixture read-only.

## Team handoff and remaining scope

See `docs/GB10_INTEGRATION.md` for the synchronized upstream commit, ownership, exact shared interfaces consumed, and known lifecycle gaps. Teammate backend modules remain unchanged; the UI/persistence/local-model transport adapters are isolated under `src/governor/`.

Not connected: external business system execution, real corporate authority verification, OpenClaw execution, persona simulation, operator learning/routing, multi-user login, file uploads/new evidence grants, post-execution plan replacement and CASE_002–004. This is an operational CASE_001 review slice, not a formal hidden-truth benchmark score.
