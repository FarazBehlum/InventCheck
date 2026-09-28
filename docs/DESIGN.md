# Interface direction

A personal comparison workspace for a shopper deciding whether a store trip is worthwhile. Search and comparable offers are the primary actions; watchlists support a deliberate manual check.

- Palette: evergreen `#216b56`, dark green `#173d36`, ink `#233c37`, muted `#62746e`, pale mint `#eaf2ec`, white surfaces on `#f5f7f6`.
- Typography: locally available Avenir Next/Avenir with Segoe UI/system sans fallbacks; restrained display headings, compact labels, tabular price figures. No remote font dependency.
- Layout: persistent desktop navigation, central search form, three illustrated sample products, grouped comparison tables; compact top navigation and stacked cards on mobile.
- Signature: small shopping-product illustrations and practical offer labels for lowest price, nearest in-stock store, and largest discount. The green visual accent belongs to useful actions and price signals.
- Accessibility: visible labels and keyboard focus, native dialog focus management, reduced-motion support, chart data table, descriptive empty/error/loading states, scroll-contained comparison tables, and textual inventory/provenance labels.

The UI/UX skill suggested a subscription pricing-page pattern, which does not match a product-search application. The implementation uses its accessibility guidance and a task-oriented comparison layout instead. Illustrations are original code-authored SVG demo assets, not retailer product photography or logos.
