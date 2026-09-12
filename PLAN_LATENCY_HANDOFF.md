# Local Qwen plan latency — measured 2026-09-12

The production Web UI on port 8080 already uses `http://127.0.0.1:8000/v1`, model `qwen-local`, with `enable_thinking=false`. Model health is good. No cloud provider or OpenClaw invocation is in the web planning path.

Actual persisted requests:
- Earlier verbose plans: 1,764 completion tokens, 223–230 seconds, plus 17–19 seconds of discovery.
- Latest selected-source plan `WF-2cbf31f0234c`: 686 completion tokens, 93.734 seconds. It completed at 20:42:29 UTC and is PROPOSED, four tasks, no error, awaiting plan approval.
- An earlier attempt was interrupted when the web service was redeployed at 20:36:49 UTC. The persisted activity explicitly records the interrupted operation. Repeated app deployments during generation can therefore make planning appear impossible even when the model works.

This branch shortens the model wire format. The old prompt already fixes four roles and their dependencies; code now constructs those repeated fields. Qwen still generates the actual task titles, objectives, evidence selections, assumptions and questions. Compact source indexes resolve only against the granted source list. The expanded response retains PLAN_SCHEMA, existing task IDs, executors and dependencies, and passes both UI and shared planner validation. No frontend or workflow state changes.

Same objective and the same two authorized source extracts as the 93.734-second request, using actual local Qwen: **28.681 seconds, 213 completion tokens**, thinking tokens 0. About 69% less wall time / 3.27× faster in this single measured comparison. This is not a universal latency guarantee; GPU contention and larger evidence sets still affect latency. Discovery is unchanged and is skipped when users explicitly select materials.

Proof is in this worktree under `runtime/plan-speed-check/plan-request.json`, `plan-response.json`, `expanded-plan.json`. No canned business answer or mocked model was used for this measurement. Fifteen compact-plan, workbench and bridge regression tests pass:

```bash
PYTHONPATH=src "$HOME/workflow-governor/.venv/bin/python" -m pytest tests/test_compact_plan.py tests/test_workbench.py tests/test_bridge.py -q
```

The patch is isolated on `fix/local-qwen-plan-latency`, in `$HOME/workflow-governor-plan-speed`. The production service runs an immutable release under `$HOME/.local/state/workflow-governor/releases/`, not the main checkout. Merely changing the checkout will not apply it. Merge/cherry-pick into the deployment branch and build a new release through the existing deploy workflow, retaining the frontend build. Switch the web application only when no workflow operation is active; Qwen and OpenClaw require no restart. After explicit user approval, the web backend was switched as recorded below; the model and OpenClaw services were not restarted.


## Live deployment verified

Deployed release `0dd1e660d6497fa534c3a2abe4327afb6af913bd` to the existing port 8080. Preserved the frontend build byte-for-byte and all five existing workflows. Backup: `$HOME/.local/state/workflow-governor/change-archives/plan-speed-20260912T204904Z`. The deployment record retains the previous release for rollback. Only the web backend was restarted, with no workflow operation in flight.

A fresh request through the production HTTP API created verification workflow `WF-69b457fa669d` and completed in **28.41 seconds**, with four validated tasks, `planState=PROPOSED`, no error, and actual local `qwen-local` inference. The verification plan is left unapproved; no execution or external action was triggered. Evidence: this worktree's `runtime/plan-speed-check/live-deployment.json` and the production runtime's `workflows/WF-69b457fa669d/model/` request/response logs. All three services (web backend, OpenClaw gateway, OpenClaw adapter) are active.
