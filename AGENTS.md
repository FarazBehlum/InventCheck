# Instructions for contributors and coding agents

Read README.md, docs/SPEC.md, docs/DECISIONS.md, ARCHITECTURE.md, RETAILERS.md, and docs/IMPLEMENTATION_PLAN.md before implementation.

This repository currently contains planning documents only. Do not claim that application code, integrations, tests, or workflows exist until implemented and verified. The original request is historical; later confirmed decisions in the specification and decision log take precedence.

- Keep the MVP local, single-user, and free of paid dependencies.
- Implement manual watchlist checks first. Scheduling and external notifications are future work.
- Never present synthetic data as live, or silently fall back to demo data in live mode.
- Do not invent retailer endpoints, permissions, prices, inventory, quantities, or API capabilities.
- Verify current official sources before implementing live adapters. Enforce source-specific retention limits.
- Do not bypass access controls, CAPTCHAs, anti-bot protections, or rate limits.
- Preserve leading zeros in identifiers and ZIP codes. Scope retailer SKUs to their retailer.
- Keep retailer logic behind adapters; isolate persistence so PostgreSQL can replace SQLite later.
- Run checks relevant to each implementation milestone and fix failures. Report blocked checks honestly.
- Update documentation when behavior changes, and record exact commands only after verification.
- Do not commit credentials, local databases, dependencies, or generated build output.
