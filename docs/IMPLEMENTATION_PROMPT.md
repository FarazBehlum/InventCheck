# Implementation prompt

Historical consolidated build prompt. The demo has now been implemented; consult README.md and docs/VERIFICATION.md for current status before using this as a scope reference:

---

Build the complete working InventCheck MVP described in this repository. Read AGENTS.md, README.md, docs/SPEC.md, docs/DECISIONS.md, ARCHITECTURE.md, RETAILERS.md, and docs/IMPLEMENTATION_PLAN.md first. Treat the specification and confirmed decisions as authoritative; docs/ORIGINAL_REQUEST.md supplies historical context only.

Implement a local single-user app with React, TypeScript, Vite, Tailwind CSS, Python, FastAPI, Pydantic, and SQLite. Use SQLAlchemy and migrations to support a later PostgreSQL migration. Deliver all specified workflows, not just a scaffold.

The required outcome is a fully working demo with no paid services and no credentials. Support nationwide US ZIP resolution with documented coverage and clearly fictional demo fixtures. Implement adapters for Walmart, Target, Home Depot, Lowe’s, and Best Buy. Add live access only where free access, permitted usage, capabilities, and retention are verified from current sources. Missing approval or credentials must not block the demo.

Implement product search/matching, comparable offer groups, sorting/filtering, product details, permitted price history, watchlist CRUD, manual watchlist checks, and persistent deduplicated in-app alerts. Scheduling, cloud deployment, email/SMS, and paid data are deferred.

Never fake live data, silently replace failed live results with demo data, invent API capabilities, infer unavailable inventory quantities, or label online prices as confirmed store prices. Preserve original observation times and keep demo/live records separate. Enforce source-specific retention, including stored retailer content in alerts. Never bypass retailer access controls or rate limits.

Work through the implementation milestones, run relevant checks after each increment, and fix failures. Research unresolved source and dataset facts; make reasonable reversible engineering choices within scope and record them. Do not purchase services or require paid dependencies. Document potentially useful paid options separately for future consideration.

Before finishing, run backend tests and the frontend build; start the application and verify health, a demo search, sorting/filtering, product details/history, watchlist persistence, manual checks, alerts, and partial-provider failures. Report exactly what ran and any blocked checks. Update the documentation to match actual behavior, including exact verified commands and retailer status.

Finish with a concise report of what was built, which integrations are live versus demo, exact run commands, test/build outcomes, known limitations, and the next three recommended features. Do not claim completion while required demo workflows remain unfinished.
