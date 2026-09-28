# Retailer integration register

Reviewed 2026-09-27. **Five working demo adapters; zero enabled live adapters.** Demo prices and quantities are synthetic. In live mode every retailer returns a typed unavailable status, with no fallback to demo data.

| Retailer | Implemented | Official access lead | Credentials / price | Verified live fields |
| --- | --- | --- | --- | --- |
| Walmart | Demo + explicit live-unavailable adapter | [Walmart I/O](https://walmart.io/) affiliate program | Requires approved access and permitted purpose; no current price verified | None tested; local pricing/quantity unverified |
| Target | Demo + explicit live-unavailable adapter | [Target Partners](https://partners.target.com/) | No suitable self-service personal API access verified | None tested |
| Home Depot | Demo + explicit live-unavailable adapter | [Official affiliate program](https://www.homedepot.com/c/SF_MS_The_Home_Depot_Affiliate_Program) | Affiliate access is not evidence of store-inventory API permission; no price verified | None tested |
| Lowe’s | Demo + explicit live-unavailable adapter | [Developer Hub](https://developer.lowes.com/) | Partner onboarding and permitted personal use require verification; no price verified | Developer portal advertises catalog/inventory capabilities, but none tested |
| Best Buy | Demo + explicit live-unavailable adapter | [Developer portal](https://developer.bestbuy.com/) and [API overview](https://developer.bestbuy.com/apis) | Register for a developer key; actual approval and current cost not verified | Documentation describes products/stores/availability; no authorized requests tested |

## Why live access remains unavailable

The user has no retailer credentials. No suitable unauthenticated source with verified permission and the required store-level semantics was established during this implementation. Public webpages, partner portals, and API documentation do not establish authorized access for this specific app. No retailer scraping or protected endpoints were attempted.

Best Buy is a promising first candidate, but its published [terms](https://developer.bestbuy.com/legal) restrict temporary content storage/cache to 72 hours. Permanent price history cannot simply be enabled. Its documentation does not establish inventory quantity or store-specific pricing for our implementation. Review current terms, apply for a key, and confirm permitted use before writing an enabled live adapter.

Walmart’s [terms](https://walmart.io/termsandcondition) tie API access to affiliate promotion and other restrictions; a personal comparison tool must not assume qualification. Seller inventory APIs are not a substitute for consumer store availability.

No paid integration is required. Future paid services can be evaluated only with documented pricing, retailer coverage, permitted use, actual store-level fields, and limits; no purchase is authorized by this project.

## Adding a retailer or enabling live access

1. Record source URL, review date, permitted use, access application steps, credentials, current price, limits, attribution, and retention. Confirm actual fields with authorized requests.
2. Add a retailer module under `backend/app/adapters/` implementing the five `RetailerAdapter` methods. `DemoAdapter` shares deterministic fixture behavior; live-unavailable classes intentionally reject requests rather than contain fake endpoint code.
3. Register it in the adapter factory, retailer catalog, and Pydantic retailer identifier type. Frontend selections are populated from `/api/status`; update its TypeScript identifier union when adding a new retailer.
4. Map errors to `ProviderError` states, set request timeout/rate policy, and validate normalized price and inventory models. Retry only safe transient failures according to source instructions; the current local/unavailable adapters make no network requests and need no retries.
5. Add listing/catalog persistence for the new live source. Current persistence expects the demo catalog to be seeded; it is not a complete ingestion pipeline for arbitrary new live products. Namespace identities by source/provenance and do not merge title-only matches automatically.
6. Extend source capabilities and price scope where necessary. The current demo offer contract represents store offers; a provider that supplies only online prices needs an explicit online-offer schema/UI path, not a fabricated store.
7. Enforce permitted retention for all source-derived catalog/listing/store content as well as observations, cache, and alerts. The shared observation/alert expiry mechanism alone is insufficient to authorize a live integration.
8. Add mocked adapter tests plus authorized smoke checks, failure/timeout tests, retention tests, and documented capability status. Never put credentials or response data requiring restricted retention in fixtures or logs.

## Demo capabilities

All five demo adapters return fictional store-level prices, addresses, distances, and inventory states. Known quantities are synthetic; Unknown stays null. Four fictional products include two drill variants that remain separate comparison groups. Coffee offers at the Best Buy demo adapter intentionally omit prices to exercise missing-data handling. There are no real product links for fictional products.
