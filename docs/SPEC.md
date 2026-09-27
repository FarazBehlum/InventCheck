# MVP specification

## Objective and boundaries

Deliver a complete, locally runnable personal shopping tool. A working demo is mandatory; live integrations are optional and must be verified. No paid services, required credentials, hosted infrastructure, browser GPS, authentication system, background scheduler, email, or SMS are required for the MVP. This application must not copy proprietary systems or bypass subscriptions.

## Search and comparison

- Accept UPC, GTIN, retailer SKU, manufacturer model number, or product name.
- Accept US ZIP codes and radii of 5, 10, 25, or 50 miles; allow selecting one or more of the five retailers.
- Support location resolution across all 50 states and DC using a licensed source. Document missing ZIP coverage, including unsupported special-purpose codes. Distances are approximate straight-line distances from ZIP coordinates.
- For ambiguous queries, show product candidates or separate comparison groups. Do not compare unrelated variants as equivalent.
- Display image, product name, retailer, store name/address, distance, regular/current prices, valid discount percentage, inventory status, quantity when explicitly available, original observation timestamp, retailer link, match confidence, and provenance.
- Inventory states: In stock, Limited stock, Out of stock, Unknown. Unknown is not out of stock; unavailable prices are not zero. Online prices must not be labeled as confirmed local prices.
- Sort by lowest price, largest discount, closest store, and in-stock first. Filter by retailer, maximum distance, in-stock only, and price range. Missing values sort after known values.
- Highlight the cheapest comparable offer, nearest in-stock store, and largest valid discount within the displayed comparison group and filters.
- Show: “Store inventory and pricing can change quickly. Verify with the retailer before traveling to the store.”

## Matching and calculations

Preserve leading zeros, normalize and validate UPC/GTIN identifiers, and keep SKUs retailer-specific. Exact normalized UPC/GTIN matches receive highest confidence. Brand/model evidence is strong only when variants and pack sizes agree. Title-only matches carry visible confidence and never silently merge uncertain products.

Use decimal monetary values and explicit currency. Calculate discount only with valid positive regular price greater than or equal to current price; missing or inconsistent reference prices have no discount badge. Compare compatible products and currencies. Use timezone-aware timestamps.

## Demo and live behavior

`DEMO_MODE=true` must work without credentials, with deterministic fictional products, stores, offers, inventory states, and historical observations. Provide documented example searches and ZIP codes. Synthetic fixtures may have limited geographic coverage; clearly state that limitation and return a useful empty state elsewhere rather than pretending real nearby stock exists.

Label demo results, charts, watchlists, and alerts. Keep demo and live records partitioned. In live mode, missing credentials, blocked sources, or failed retailers produce explicit statuses, never substituted demo offers. One retailer failure must not remove successful results.

Prefer official APIs, then permitted public endpoints, structured data, and public pages. Mere public accessibility does not prove permission. Never bypass logins, paywalls, CAPTCHAs, anti-bot controls, or rate limits; never use unauthorized private APIs or evasive proxy rotation.

## History

Persist successful observations only as permitted by the source. Cache hits retain the original timestamp and do not create new observations. Enforce source-specific storage limits and expiration. Long-term history must be disabled for sources that do not permit it; do not retain restricted data indirectly in alerts or exports.

Product details show current lowest available price, highest/lowest observed prices within retained history, a history chart, and retailer comparisons. Distinguish historical observations from current results and demo from live data. Demonstrate full history with synthetic observations.

## Watchlist and alerts

Support create, view, edit, and delete with product, target price, preferred retailers, ZIP, and radius. A “Check watchlist” button checks saved products through the same search services, records check status/time, and produces persisted in-app alerts when an observed price is at or below target. Failed or unknown prices must not trigger alerts.

Deduplicate repeated notifications for the same qualifying product/store/price and watchlist entry. A changed qualifying price may produce a new alert. Keep demo and live entries separate. Distinguish last attempted check from last successful observation. Include read/dismiss behavior for alerts. Source retention limits apply to any retailer content stored with alerts.

Manual checks are the only MVP trigger. No monitoring occurs while idle unless explicitly initiated. A future scheduler and email/SMS delivery can reuse separate checking and notification interfaces.

## Interface and error handling

Pages: Search, Search Results, Product Details, Watchlist, Settings/About. Use a practical responsive dashboard with accessible controls and clear loading, empty, error, partial-success, demo, and source-unavailable states. Settings/About explains mode, retailer capabilities, data limitations, and inventory caveats without exposing secrets.

Handle not found, invalid/unresolvable ZIP, no stores, missing credentials, timeouts, malformed responses, rate limits, and retailer outages. Use bounded concurrent retailer requests, timeouts, conservative transient retries, configurable caching, and structured logs without secrets.

## Acceptance criteria

- A fresh local installation can run the demo without secrets or paid services.
- Search, matching groups, comparisons, sorting/filtering, details, and history work end to end.
- Watchlist settings and alerts survive a backend restart; manual checks trigger appropriate deduplicated alerts.
- Demo data never appears as live; unavailable live sources remain visibly unavailable.
- A failed adapter does not discard other retailers’ results.
- Backend tests and frontend production build pass; health and main workflows are exercised.
- Tests cover normalization/UPC matching, variants, monetary/discount calculations, distances, failures, persistence, provenance separation, API validation, watchlist alerts, and a mocked adapter integration.
- Retention enforcement and cache timestamp behavior are tested.
- README includes verified setup/run/test commands, environment configuration, demo examples, source licenses, and known limitations.
