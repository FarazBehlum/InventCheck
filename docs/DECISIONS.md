# Decision log

## Confirmed by the user

| Decision | Outcome |
| --- | --- |
| Delivery | Fully working demo; live integrations where available |
| Existing implementation | Start fresh; no prior application work |
| Cost | No paid services for MVP; consider paid improvements later |
| Credentials | None currently available; demo must not require them |
| Geography | Nationwide US location search; documented source limitations |
| Watchlist | Manual checks first |
| Current task | Implement the documented working local demo |
| Repository publication | Public GitHub repository at https://github.com/FarazBehlum/InventCheck; continue updating it as the project develops |

## Recorded implementation defaults

These are proposed engineering defaults derived from the agreed scope, not claims of additional user requests.

- Local single-user app without login, public deployment, or cloud synchronization.
- SQLite with SQLAlchemy and Alembic; portable relational types and service boundaries for future PostgreSQL.
- US coverage means all 50 states and DC; territories are not an MVP requirement.
- Fictional demo store fixtures may cover selected documented ZIPs; ZIP resolution itself targets nationwide coverage.
- Backend-controlled environment configuration; the UI reports mode and capability status.
- Manual refresh uses the same provider pipeline as search, with no scheduler dependency.
- Long-term history is conditional on source permissions; provider retention supersedes the original “save every check” wording.
- Local Git repository with public GitHub remote `FarazBehlum/InventCheck`; `main` tracks `origin/main`.

## Facts to resolve during implementation

| Unknown | Resolution required |
| --- | --- |
| Retailer access and cost | Verify current official registration, approval, allowed use, limits, and price before enabling an adapter |
| Store pricing/inventory | Verify actual fields and semantics; use Unknown/unsupported where absent |
| Source retention | Record allowed caching/history and enforce expiration before storing live data |
| ZIP dataset | Select and document license, provenance, coverage, updates, and installation |
| Exact dependencies | Select compatible supported versions, lock them, and verify the build |
| Live credentials | Provide registration instructions; absence does not block demo delivery |

## Deferred

Scheduled checks, always-on hosting, email/SMS/push, paid data services, multi-user accounts, Supabase migration, and additional retailers. Changes require a documented scope update; no purchase is implied by future consideration.

## Implementation decisions (2026-09-27)

- User requested the installed using-git-worktrees skill. Work continues on `feature/mvp` in `.worktrees/mvp`; the project-local worktree directory is ignored by Git. No native worktree tool was available, so Git worktree was used.
- ZIP coordinates: bundled GeoNames US postal snapshot, CC BY 4.0, transformed to 40,977 ZIP rows covering 50 states and DC. No runtime geocoding request.
- The four demo products have inline UPC/GTIN/model fields and retailer listings hold SKU. A separate identifier table is deferred until multiple identifiers per type are needed.
- Preferred retailers are a validated bounded JSON list on each watchlist row rather than a join table. SQLAlchemy JSON remains portable; a join table can be migrated in later.
- Alerts require an In stock or Limited stock offer at or below target. Unknown/out-of-stock offers do not trigger shopping alerts.
- Demo fixtures have no retailer product URL because fictional products do not have actual retailer listings.
- Live adapters remain explicitly unavailable: no approved credentials or verified suitable unauthenticated access. Enabling a live source requires its catalog persistence and full retention policy as documented in RETAILERS.md.
- No automatic HTTP retries are implemented for demo/unavailable adapters because they make no network requests. Live retry policy belongs to each future provider’s verified rules.
