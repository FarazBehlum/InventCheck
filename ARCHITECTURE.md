# Architecture

**Local demo implemented. Live adapters are explicit unavailable states; live catalog ingestion is deferred.**

## Components and flow

React/TypeScript with Vite and Tailwind renders the five UI pages and calls FastAPI JSON endpoints. FastAPI validates requests with Pydantic, resolves location, normalizes product identifiers, invokes selected adapters with bounded concurrency, aggregates comparable offers and per-retailer statuses, and persists permitted observations through SQLAlchemy. Alembic manages migrations.

Use `frontend/` and `backend/`; backend application packages should separate `api`, `models`, `schemas`, `services`, `adapters`, `database`, and `utils`, with tests under `backend/tests/`. Do not introduce microservices or a queue for the MVP.

SQLite is the initial database. Keep business rules outside ORM models and isolate session/engine configuration. Avoid SQLite-specific SQL so PostgreSQL/Supabase can replace the database with migrations and configuration changes rather than rewriting application logic.

## Adapter interface

Each retailer module implements a shared asynchronous contract for `search_product`, `get_product_details`, `get_nearby_stores`, `get_store_price`, and `get_inventory`. Capabilities describe supported product search, store lookup, local prices, inventory status/quantity, required credentials, caching, and retention.

Return typed normalized records with provenance, timestamps, product/store identifiers, optional values, and price scope (online or store). Distinguish unsupported capabilities from a legitimate empty response. Keep provider HTTP parsing and authentication inside adapters. Separate demo implementations from live implementations.

Provider failures map to stable statuses: unavailable, credentials required, timeout, rate limited, malformed response, or completed. Search returns successful offers plus all provider statuses. No silent demo fallback.

## Relational model

| Entity | Main fields and relationships |
| --- | --- |
| products | id, UPC/GTIN, brand, model, name, image URL, provenance, created_at |
| Product identifiers | UPC/GTIN/model stored on products; retailer SKU stored on listings (no separate table in MVP) |
| retailers | id, name, website |
| stores | retailer, store identifier, name, address/city/state/ZIP, coordinates, provenance |
| retailer_listings | product, retailer, retailer SKU, product URL, matching evidence/confidence |
| price_checks | listing/product, store (demo offers are store-scoped), current/regular price, currency, inventory status/quantity, observed_at, provenance, expires_at |
| watchlist | product, target price, ZIP, radius, provenance, created_at, last attempted/successful check |
| Watchlist retailer preferences | Validated JSON array on watchlist (no join table in MVP) |
| alerts | watchlist, deduplication identity, permitted offer details, created_at, read/dismissed state, expiration if required |

Store identifiers are unique per retailer and provenance. Use foreign keys and appropriate indexes. ZIP codes and identifiers are strings, money is decimal, timestamps use UTC, and unknown values remain null. The current offer type is store-scoped. An online-only live adapter requires a separately modeled price scope and optional store before it can be enabled.

## HTTP API

| Method and path | Purpose |
| --- | --- |
| GET /api/health | Service health |
| GET /api/search | Query, ZIP, radius, retailer selection; offers, match groups, provider statuses |
| GET /api/products/{id} | Product details |
| GET /api/products/{id}/prices | Current retained offers with provenance and timestamps |
| GET /api/products/{id}/history | Permitted historical observations |
| GET /api/stores | Nearby stores by location/radius/retailer |
| POST /api/watchlist | Create saved search settings |
| GET /api/watchlist | List saved products and check status |
| PATCH /api/watchlist/{id} | Update target and preferences |
| DELETE /api/watchlist/{id} | Remove saved item |
| POST /api/watchlist/refresh | Manually check saved items and evaluate alerts |
| GET /api/alerts | List in-app alerts |
| PATCH /api/alerts/{id} | Mark read or dismissed |
| GET /api/status | Safe mode/capability information for Settings/About |

Pydantic defines request/response models for search/products/stores and mutation input; remaining record responses serialize database fields. OpenAPI is served at `/docs`. Validate ZIP format and resolution, allowed radii, known retailers, positive targets, and nonempty search queries. Limit query lengths and request sizes. Bind locally by default and configure development CORS for the actual frontend origin.

## Cache, persistence, and alerts

Cache keys include provider, mode, normalized query, location, and relevant search parameters. TTL cannot exceed source permissions. A cache hit preserves observed_at and does not append history. Purge restricted observations and derived stored retailer content by expiry; do not keep forbidden history in a different table.

Watchlist refresh calls a shared check service. A notification service evaluates qualifying offers, deduplicates alerts, and writes permitted records. Future schedulers can call this service without changing routes or adapters. No scheduler runs in the MVP.

Apply bounded timeouts and retries only to safe transient failures, honor retry guidance, and log provider status/duration without credentials or sensitive request URLs. Partial search results are normal, explicit outcomes.

## Runtime behavior

Startup applies Alembic migrations, seeds the demo catalog once, and purges expired observations/alerts. API requests also purge expiry before reading records. The migration file is a schema snapshot, not a call to mutable model metadata. Tests can use temporary schema creation, while browser tests exercise real migrations.

Search accepts `q`, `zip_code`, `radius`, and repeated `retailers` parameters. It returns `query`, `location`, `radius`, `mode`, `offers`, and per-retailer `providers` statuses. The browser groups by canonical product ID and sorts/filters those groups locally. Unrecognized ZIPs or invalid parameters return 422; unknown or cross-mode entities return 404.

At most five retailer tasks run concurrently. A single-process search lock prevents duplicate cache/observation writes. Cache is capped at 256 entries with per-entry expiry; cache hits retain timestamps and do not append history. Each observation stores an optional source expiry. Currently only unlimited-retention demo data is ingested. Restricted catalog retention must be implemented for a live source before enabling it.

History returns retained observations for a product. The frontend can filter by store ZIP and graphs daily minimum prices with an accessible data table. Recent prices return the newest observation per store within the cache window (minimum 60 seconds). Seeded historical data is not presented as recent live data.

Watchlist refresh is serialized, uses the same search pipeline, and evaluates only available known-price offers. Deduplication identity combines watchlist item, offer, and exact price. Read/dismiss flags persist. Deleting a watch also deletes its alerts. A changed target does not re-notify an already alerted identical offer/price; this avoids repeated alerts across manual checks.

Vite proxies `/api` to loopback port 8000. The Python API also permits the configured frontend origin for direct calls. The app is unauthenticated and intended for local use only. `scripts/dev.sh` starts both services and terminates its child processes on exit.
