# Retailer integration register

**No adapters or credentials currently exist. All capabilities require implementation verification.**

| Retailer | Current implementation | Research lead | Credentials/cost | Local price / quantity |
| --- | --- | --- | --- | --- |
| Walmart | None; demo planned | Official Walmart I/O affiliate program | Approval and allowed purpose require review; no verified quote | Unverified / unverified |
| Target | None; demo planned | Research approved access | No suitable access verified | Unverified / unverified |
| Home Depot | None; demo planned | Research approved access | No suitable access verified | Unverified / unverified |
| Lowe’s | None; demo planned | Research approved access | No suitable access verified | Unverified / unverified |
| Best Buy | None; demo planned | Official developer portal | Developer key registration; approval and current cost unverified | Unverified / unverified |

## Sources reviewed during prompt planning

Recorded 2026-09-27. These are research leads, not a guarantee of current access or approval.

- [Best Buy developer portal](https://developer.bestbuy.com/): registration entry point for API keys.
- [Best Buy API overview](https://developer.bestbuy.com/apis): describes product pricing/availability and store queries. Catalog pricing must not be assumed to be store-specific pricing; inventory status must not be assumed to include quantity.
- [Best Buy terms](https://developer.bestbuy.com/legal): published terms reviewed during planning limit temporary storage/cache to 72 hours. Long-term price history must not be enabled without permission allowing it. Recheck current terms and permitted use before integration.
- [Walmart I/O](https://walmart.io/): affiliate/developer entry point.
- [Walmart I/O terms](https://walmart.io/termsandcondition): access is tied to affiliate product promotion and restrictions. Do not assume this personal use case qualifies or that local inventory is included.

No suitable official source was verified for Target, Home Depot, or Lowe’s during planning. This is an unresolved research task, not a claim that no source exists.

## Required evidence before enabling a live adapter

Record official source URL and review date, registration steps, required credentials, permitted use, documented pricing, rate limits, supported fields, regional coverage, store-price semantics, inventory/quantity availability, cache limits, and history permissions. Validate real responses with authorized credentials. Mark capabilities separately rather than labeling an entire retailer simply “supported.”

If approval or credentials are unavailable, document exactly what is missing. Demo mode remains functional; live mode reports unavailable. Never circumvent blocks. Paid services can be proposed with verified costs and capabilities for later review but are not an MVP dependency.
