# Implementation milestones

All application milestones below are pending. Documentation is the only completed work.

## 1. Foundation and backend

- [ ] Select supported dependency versions; scaffold frontend/backend and example environment configuration.
- [ ] Implement FastAPI validation, health/status endpoints, SQLite/SQLAlchemy persistence, and migrations.
- [ ] Implement normalized data types, identifiers, calculations, adapter interface, and provider status handling.
- [ ] Select a licensed nationwide ZIP source; document acquisition and coverage.
- [ ] Verify backend startup, migration, and focused unit/database/API tests.

## 2. Demo search and interface

- [ ] Build deterministic demo adapters for all five retailers and document fixture ZIPs/searches.
- [ ] Implement search aggregation, product grouping, caching, and isolated failures.
- [ ] Build responsive Search, Results, Details, Watchlist, and Settings/About pages.
- [ ] Connect frontend/backend; implement sorting, filtering, highlights, confidence, provenance, and empty/error states.
- [ ] Verify representative search, unknown fields, multiple products, no nearby stores, and partial retailer failure; build frontend.

## 3. History and watchlist

- [ ] Persist observations without duplicating cache hits; implement source expiration and demo/live separation.
- [ ] Add product comparison and history chart with synthetic historical fixtures.
- [ ] Implement watchlist CRUD, retailer preferences, manual refresh, deduplicated alerts, and read/dismiss state.
- [ ] Verify target-price behavior, cache timestamps, retention, and persistence across restarts.

## 4. Live-source feasibility

- [ ] Review current official access and usage rules for all five retailers.
- [ ] Update RETAILERS.md with evidence, capabilities, costs, credentials, and limitations.
- [ ] Implement only legitimately accessible free sources; missing approval or credentials must not block demo completion.
- [ ] Verify supported fields with authorized responses; never claim quantity or local pricing without evidence.

## 5. Completion checks and handoff

- [ ] Run backend suite covering normalization/UPC, variants, prices/discounts, distance, failures, database operations, API validation, provenance, cache/retention, and watchlist alerts.
- [ ] Include a mocked adapter integration test.
- [ ] Run frontend production build.
- [ ] Start application; verify health and demo search through the API and UI where tooling permits.
- [ ] Verify sorting/filtering/highlights, product details/history, watchlist editing/deletion/refresh, alert deduplication, and restart persistence.
- [ ] Exercise invalid ZIP, unavailable retailer, timeout, malformed response, missing credentials, rate limiting, and empty results.
- [ ] Resolve failures; report any environment-blocked checks explicitly.
- [ ] Update README with exact verified setup/run/test commands, environment variables, demo examples, and adapter extension instructions.
- [ ] Report delivered features, live/demo status per retailer, verification results, limitations, and three next-feature recommendations.

Do not check off a milestone merely because files exist. Verify the associated behavior. Keep each increment runnable and resolve relevant failures before continuing.
