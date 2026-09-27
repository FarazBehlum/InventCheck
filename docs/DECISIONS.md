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
| Current task | Create repository and document agreed requirements before implementation |
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
