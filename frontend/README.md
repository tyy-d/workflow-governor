# Workflow Governor frontend

Thomas's interface is now connected to the local same-origin `/api` backend. Production runtime imports no mock workflow data. Plans and task results come from persisted backend workflows; local AI work calls the existing Qwen GPU service. Human tasks capture judgment/reason, and blocked tasks offer recovery.

Run `npm ci` and `npm run build`, then start the Python server described in the repository README. Vite development mode can use an `/api` proxy to the local backend if configured; production is served directly from `dist/` by the backend.

The historical `src/mock/` and old pure demo-state helpers are retained for reference but are not imported by the application runtime.
