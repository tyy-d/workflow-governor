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

## Verified browser slice and deployment

- Browser-created `WF-07cf0279bdcb`: real Qwen proposal, explicit approval, deterministic T1 and Qwen T2 completed with citations. T3 waits for an authorized human; T4 remains pending.
- Chromium verified 1440/1280/1024/390 widths, evidence opening and page refresh. Preview backend restart restored the same results.
- Deployed initial shared-store release `2c20f13` through the existing systemd user service. Original model service unchanged. Saved workflow is available on the deployed instance.
- Final polish: mobile rows keep status visible; request identity generation works on LAN HTTP as well as localhost.
- Operational recovery/deployment/replay commands: docs/WORKBENCH_DEPLOYMENT.md. Baseline recovery script rehearsed in an independent directory.

## Final verification — 2026-09-12

- 77 backend tests passed in 2.68 seconds; TypeScript and production build passed.
- Real model plan and semantic execution completed; deterministic result and exact citations verified against the saved source lines. Network API state and artifact state agree.
- Fresh Chromium session on the LAN address passed for the persisted workflow at four widths. Mobile status is visible without horizontal scrolling. Save-failure and offline states were checked using browser-only network injection.
- Baseline restore, compatible application rollback/return with identical runtime SHA-256, and new replay draft creation all passed. No side-effecting task was replayed.
- User systemd lingering is enabled so the application can start without an interactive login. The existing Qwen service remains untouched.
- Local stage commits: 4101045 (baseline), 1fed5cd (upstream merge), 432859b (workbench), 2c20f13 (integration), 2ef8d51 (verified deployment and mobile polish).
- Deployed application release: 2ef8d51. Operations: docs/WORKBENCH_DEPLOYMENT.md. Live service port 8080; independent preview service port 8081.
- GitHub write access remains unavailable and the user asked to proceed locally. No main push was attempted or claimed.
- Remaining limits: human routing/authority module, external actions and multi-user authentication are unavailable; historical manifests are read-only. Full business evaluation, host reboot, prolonged load and exhaustive fault scenarios were not performed.

## Teammate synchronization at delivery

- Fetched and merged remote main `8e39566`, including Frank's human/operator modules and isolation hardening, without conflicts or overwriting local integration.
- Full combined regression: 117 passed in 3.00 seconds. Human submission is still unavailable in this deployment because trusted operator assignment and authorization are not configured; the new native modules are preserved for that integration.
- Original main remains at teammate commit `8e39566`; this work is local only, as agreed with the user.

## Additive contract compatibility fix

The final teammate merge added `TaskSpec.requested_decision_authority_scope` while retaining durable schema version 1. Strict loading initially rejected prior TaskSpec records. Rolled the application back before repair. The codec now accepts exactly that formerly absent field as `NO_DECISION` in memory; all other missing/unknown fields remain invalid. Existing plan files and hashes are unchanged. Regression includes a least-privilege, non-mutating compatibility test, and strict loading of the real saved workflow passes.

## Business overview for judges

- Added a business-facing default dashboard within the existing Notion-style workbench. All workflows remain available through a separate functional navigation item.
- The featured example is selected from current, readable workflows with saved AI analysis. Historical acceptance runs are excluded from dashboard totals; no invented ROI, time saved, production volume, or authority claims.
- The overview explains the product, summarizes actual work delivered, source documents and cited findings, shows task allocation, and makes remaining issues and proposed follow-up visible.
- Source references open the exact saved evidence line. Saved analysis, human handoff, full workflow, activity and new-workflow actions use existing live screens and APIs.
- Chromium acceptance verified API-to-display counts, evidence drill-down, analysis, waiting human handoff, draft state, all-workflow navigation, refresh and 1440/1280/1024/390 widths. Screenshots/logs: runtime/business-dashboard/.
- No backend, data model, model configuration, or workflow records were changed for this dashboard.

## Simplified pages and custom colors

- Removed the overview's repeated product introduction, explanation row and duplicate calls to action. Findings and open issues expand on demand; the plan and saved result remain visible.
- Added six page-color presets and an arbitrary custom color picker. Colors are saved per page in this browser and affect covers, icons and section accents, never business status.
- Workflow properties and the full brief now expand on demand. No saved business data was removed or rewritten.
- Browser checks passed for exact evidence drill-down, real counts, saved analysis, human handoff, all-workflow navigation, draft state, four widths, preset/custom color persistence and independent page colors. Production build/typecheck passed.
- GitHub permissions were rechecked: the connected account now has push access to the original repository. Delivery targets main, preserving all local stage history and archives.
