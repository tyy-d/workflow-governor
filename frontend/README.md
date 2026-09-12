# Workflow Governor interface

Static frontend shell for the Workflow Governor workflow navigator and coordination console. It supports workflow home, workflow detail, and new-workflow states using local React state. All displayed workflow, task, evidence, operator, and activity data is typed demo data from `src/mock/workflow.ts`; workflows created in the interface reset on refresh.

This package performs no persistence, filesystem access, model calls, runtime execution, or backend requests.

```bash
npm install
npm run dev
```

Use `npm run build` for a production build and `npm run typecheck` for a standalone type check.
