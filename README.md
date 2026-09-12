# Workflow Governor

A local workflow workbench: create a goal, choose authorized files, ask the existing Qwen model for a plan, approve it, and execute bounded work with inspectable evidence and saved results.

The React interface uses a collapsible sidebar, a workflow list, document pages, and task/evidence details. The same-origin Python backend integrates the shared planner, validators, runner, ArtifactStore and WorkflowStateLoader. Browsers do not call the model service directly.

## On the configured GB10

Open port **8080** on the GB10 LAN address, or `http://127.0.0.1:8080/` locally.

1. Create a workflow and select files from an authorized workspace.
2. Generate a plan with the local model.
3. Review its tasks and evidence, then explicitly approve the plan.
4. Open a ready task and execute it. Results and references are saved server-side.
5. Refresh or reopen the workflow to continue inspecting saved work.

The current authorized workspace is CASE_001's `workspace/` only. No hidden answers, persona evaluators, or provenance are available. New human tasks wait for authorized operator routing, which is not yet connected; no human identity or business decision is fabricated. Historical pre-workbench workflows remain visible and read-only without a destructive migration.

The existing local service runs **Qwen/Qwen3.8-27B-FP8**, served as **qwen-local**, over the vLLM OpenAI-compatible API. Workbench calls disable thinking; only bounded inputs, final structured outputs, usage, errors and short audit metadata are stored. No cloud fallback is configured.

## Operations and recovery

See [deployment, rollback, restore and replay commands](docs/WORKBENCH_DEPLOYMENT.md) and [implementation progress](PROGRESS.md).

```bash
systemctl --user status workflow-governor.service
systemctl --user restart workflow-governor.service
.venv/bin/python -u -m pytest -v --durations=0 -o log_cli=true -o addopts=''
npm run typecheck --prefix frontend
```

The deployed service uses an immutable release; frontend builds for development go into the independent preview directory as documented. The model service is managed separately and was not replaced or restarted.

This is a trusted-network, single-workspace local application. Multi-user login, external business system writes, corporate authority verification, and automated human routing are not implemented. A completed local review does not activate a vendor, release a purchase order, or assert a full benchmark evaluation passed.

The older [GB10 integration handoff](docs/GB10_INTEGRATION.md) records the original integration baseline; current behavior and operational commands are documented above.
