# Planned architecture

**Design only; not implemented.**

## Components and flow

React/TypeScript with Vite and Tailwind renders the five UI pages and calls FastAPI JSON endpoints. FastAPI validates requests with Pydantic, resolves location, normalizes product identifiers, invokes selected adapters with bounded concurrency, aggregates comparable offers and per-retailer statuses, and persists permitted observations through SQLAlchemy. Alembic manages migrations.

Use `frontend/` and `backend/`; backend application packages should separate `api`, `models`, `schemas`, `services`, `adapters`, `database`, and `utils`, with tests under `backend/tests/`. Do not introduce microservices or a queue for the MVP.

SQLite is the initial database. Keep business rules outside ORM models and isolate session/engine configuration. Avoid SQLite-specific SQL so PostgreSQL/Supabase can replace the database with migrations and configuration changes rather than rewriting application logic.

## Adapter interface

Each retailer module implements a shared asynchronous contract for `search_product`, `get_product_details`, `get_nearby_stores`, `get_store_price`, and `get_inventory`. Capabilities describe supported product search, store lookup, local prices, inventory status/quantity, required credentials, caching, and retention.

Return typed normalized records with provenance, timestamps, product/store identifiers, optional values, and price scope (online or store). Distinguish unsupported capabilities from a legitimate empty response. Keep provider HTTP parsing and authentication inside adapters. Separate demo implementations from live implementations.

Provider failures map to stable statuses: unavailable, credentials required, timeout, rate limited, malformed response, or completed. Search returns successful offers plus all provider statuses. No silent demo fallback.

## Planned relational model

| Entity | Main fields and relationships |
| --- | --- |
| products | id, UPC/GTIN, brand, model, name, image URL, provenance, created_at |
| product_identifiers | product, identifier type/value, retailer scope when needed |
| retailers | id, name, website |
| stores | retailer, store identifier, name, address/city/state/ZIP, coordinates, provenance |
| retailer_listings | product, retailer, retailer SKU, product URL, matching evidence/confidence |
| price_checks | listing/product, optional store, price scope, current/regular price, currency, inventory status/quantity, observed_at, provenance, expires_at |
| watchlist | product, target price, ZIP, radius, provenance, created_at, last attempted/successful check |
| watchlist_retailers | watchlist-to-retailer preferences |
| alerts | watchlist, deduplication identity, permitted offer details, created_at, read/dismissed state, expiration if required |

Store identifiers are unique per retailer and provenance. Use foreign keys and appropriate indexes. ZIP codes and identifiers are strings, money is decimal, timestamps use UTC, and unknown values remain null. An online offer may lack a store and cannot receive a store distance or local stock claim.

## Planned HTTP API

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

Define and document exact request/response schemas during implementation using Pydantic/OpenAPI. Validate ZIP format and resolution, allowed radii, known retailers, positive targets, and nonempty search queries. Limit query lengths and request sizes. Bind locally by default and configure development CORS for the actual frontend origin.

## Cache, persistence, and alerts

Cache keys include provider, mode, normalized query, location, and relevant search parameters. TTL cannot exceed source permissions. A cache hit preserves observed_at and does not append history. Purge restricted observations and derived stored retailer content by expiry; do not keep forbidden history in a different table.

Watchlist refresh calls a shared check service. A notification service evaluates qualifying offers, deduplicates alerts, and writes permitted records. Future schedulers can call this service without changing routes or adapters. No scheduler runs in the MVP.

Apply bounded timeouts and retries only to safe transient failures, honor retry guidance, and log provider status/duration without credentials or sensitive request URLs. Partial search results are normal, explicit outcomes.
