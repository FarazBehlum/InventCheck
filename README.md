# InventCheck

A planned personal price-comparison and local inventory web application inspired by BrickSeek, using permitted data sources and explicitly labeled demo data.

**Status: planning repository. No application has been implemented yet.** There are no install, run, or test commands for an application at this stage. This repository records the agreed requirements before development begins.

## Confirmed direction

- Start from scratch with a reliable, fully working local demo.
- React, TypeScript, Vite, and Tailwind CSS frontend; Python, FastAPI, and SQLite backend.
- Single user, running locally; no paid services or API credentials required.
- US ZIP-code search across all 50 states and Washington, DC, subject to documented dataset coverage.
- Architecture for Walmart, Target, Home Depot, Lowe’s, and Best Buy.
- Live integrations only when access, permitted use, and capabilities are verified.
- Manual watchlist checks and persistent in-app alerts first; scheduling later.
- No purchase or paid dependency. Paid options may be documented for later consideration.

## Documentation map

| Document | Purpose |
| --- | --- |
| [Product specification](docs/SPEC.md) | Authoritative MVP requirements and acceptance criteria |
| [Decision log](docs/DECISIONS.md) | Confirmed choices, implementation defaults, and unresolved facts |
| [Architecture](ARCHITECTURE.md) | Planned components, data model, interfaces, and data flow |
| [Retailers](RETAILERS.md) | Integration status, research leads, and verification requirements |
| [Implementation plan](docs/IMPLEMENTATION_PLAN.md) | Ordered milestones and verification checklist |
| [Implementation prompt](docs/IMPLEMENTATION_PROMPT.md) | Copy-ready instructions for the future build |
| [Original request](docs/ORIGINAL_REQUEST.md) | Historical source; later confirmed decisions supersede conflicts |

The specification and decision log define current scope. Architecture describes how to implement it. Update these documents together when a decision changes. Historical requests and research leads must not be treated as verified capabilities.

## Development prerequisites and future setup

Development will require Git, Node.js with a package manager, and Python. Exact supported versions, dependency installation, database setup, environment variables, demo examples, and run/test commands will be recorded after implementation and verification. Do not assume untested commands work.

The implementation must include `.env.example`, backend tests, frontend build instructions, an appropriately licensed ZIP dataset or documented acquisition procedure, and instructions for adding adapters. Secrets belong in local environment files, never in Git.

## Limitations

Nationwide location support does not guarantee nationwide live inventory. Retailer prices, quantities, access, and data retention depend on verified source capabilities. Demo data will be synthetic. Inventory and pricing can change quickly; users must verify with the retailer before traveling.

The public repository is [FarazBehlum/InventCheck](https://github.com/FarazBehlum/InventCheck). The local `main` branch tracks `origin/main`. Keep the specification, decisions, and implementation status current as the project develops.
