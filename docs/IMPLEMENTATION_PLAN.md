# Implementation milestones

The local demo is implemented. See docs/VERIFICATION.md for check results and RETAILERS.md for live-source limitations.

## 1. Foundation and backend

- [x] Select supported dependency versions; scaffold frontend/backend and example environment configuration.
- [x] Implement FastAPI validation, health/status endpoints, SQLite/SQLAlchemy persistence, and migrations.
- [x] Implement normalized data types, identifiers, calculations, adapter interface, and provider status handling.
- [x] Select a licensed nationwide ZIP source; document acquisition and coverage.
- [x] Verify backend startup, migration, and focused unit/database/API tests.

## 2. Demo search and interface

- [x] Build deterministic demo adapters for all five retailers and document fixture ZIPs/searches.
- [x] Implement search aggregation, product grouping, caching, and isolated failures.
- [x] Build responsive Search, Results, Details, Watchlist, and Settings/About pages.
- [x] Connect frontend/backend; implement sorting, filtering, highlights, confidence, provenance, and empty/error states.
- [x] Verify representative search, unknown fields, multiple products, no nearby stores, and partial retailer failure; build frontend.

## 3. History and watchlist

- [x] Persist observations without duplicating cache hits; implement source expiration and demo/live separation.
- [x] Add product comparison and history chart with synthetic historical fixtures.
- [x] Implement watchlist CRUD, retailer preferences, manual refresh, deduplicated alerts, and read/dismiss state.
- [x] Verify target-price behavior, cache timestamps, retention, and persistence across restarts.

## 4. Live-source feasibility

- [x] Review current official access and usage rules for all five retailers.
- [x] Update RETAILERS.md with evidence, capabilities, costs, credentials, and limitations.
- [x] Implement only legitimately accessible free sources; missing approval or credentials must not block demo completion.
- [ ] Verify live supported fields with authorized responses. Deferred: no live source has approved credentials/access; demo quantities and prices remain explicitly synthetic.

## 5. Completion checks and handoff

- [x] Run backend suite covering normalization/UPC, variants, prices/discounts, distance, failures, database operations, API validation, provenance, cache/retention, and watchlist alerts.
- [x] Include a mocked adapter integration test.
- [x] Run frontend production build.
- [x] Start application; verify health and demo search through the API and UI where tooling permits.
- [x] Verify sorting/filtering/highlights, product details/history, watchlist editing/deletion/refresh, alert deduplication, and restart persistence.
- [x] Exercise invalid ZIP, unavailable retailer, timeout, malformed response, missing credentials, rate limiting, and empty results.
- [x] Resolve failures; report any environment-blocked checks explicitly.
- [x] Update README with exact verified setup/run/test commands, environment variables, demo examples, and adapter extension instructions.
- [x] Report delivered features, live/demo status per retailer, verification results, limitations, and three next-feature recommendations.

Do not check off a milestone merely because files exist. Verify the associated behavior. Keep each increment runnable and resolve relevant failures before continuing.
