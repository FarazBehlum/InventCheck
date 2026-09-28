# InventCheck

A local, personal price-comparison and inventory demo. Search fictional products, compare nearby sample offers, explore price history, and save products for manual target-price checks.

**Working demo, not a live inventory service.** Walmart, Target, Home Depot, Lowe’s, and Best Buy have demo adapters. No retailer currently has an enabled live integration. There are no required credentials, paid services, or runtime external requests.

## Quick start

Prerequisites: Python 3.11+ (3.13 used for development), Node.js 22.12+ or a compatible newer version, npm, and Git. Internet is needed to install dependencies; the demo runs offline afterward. Windows users can run the backend/frontend commands separately in PowerShell using `.venv\Scripts\python.exe`.

From a fresh clone:

```sh
git clone https://github.com/FarazBehlum/InventCheck.git
cd InventCheck
git switch feature/mvp
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
bash scripts/dev.sh
```

Open **http://127.0.0.1:5173**. Stop both servers with Ctrl+C. The backend automatically applies database migrations and seeds synthetic fixtures on first startup.

For the existing development worktree on this computer, dependencies are already installed:

```sh
cd /Users/faraz/Documents/InventCheck/.worktrees/mvp
bash scripts/dev.sh
```

Keep commands in the worktree while developing `feature/mvp`. The main checkout remains separate. Do not run two copies against the same ports.

### Run servers separately

Terminal 1, from the project/worktree root:

```sh
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Terminal 2:

```sh
cd frontend
npm run dev
```

The frontend proxies `/api` to port 8000. API documentation: http://127.0.0.1:8000/docs. Health: http://127.0.0.1:8000/api/health. Bind to loopback only; this is an unauthenticated personal app, not a public deployment.

## Try the complete workflow

1. Search **FW-D20** with ZIP **53703**, radius **25 miles**, and all retailers. Expect 10 demo offers for the drill kit.
2. Sort by distance or discount, filter by in-stock or price, and compare the highlighted offers. Search **drill** to see kit and tool-only variants kept in separate groups.
3. Open a product title for retained demo history and recent observations. Select a store area or expand the accessible chart-data table.
4. Choose **Watch price**, enter a target of **85**, and save with all retailers near 53703.
5. Open **Watchlist** and choose **Check watchlist**. Three available demo offers qualify. Repeating the same check creates no duplicate alerts.
6. Edit the target or area, mark alerts read/dismissed, reload to verify persistence, or remove a saved product.

Other searches: `headphones`, `coffee`, UPC `012345678905`, GTIN `00012345678905`, retailer SKU `DEMO-WALMART-DRILL`.

Fictional stores are available near: **53703, 10001, 60601, 94103, 90012, 73301, 98101, 20001, 02108, 33130, 99501, 96813**. ZIP lookup supports 40,977 entries across all 50 states and DC. Elsewhere, a valid ZIP can resolve but return no nearby demo stores. Some new or special-purpose ZIPs are absent. Distances are straight-line approximations.

All demo brands, identifiers, prices, stock, quantities, store street addresses, illustrations, and history are synthetic. Demo products have no real retailer product-page links; the interface states this explicitly.

## Configuration

Defaults work without an environment file. Optionally copy `.env.example` to `.env` at the project/worktree root:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEMO_MODE` | `true` | Synthetic adapters; false reports live adapters unavailable without substituting demo data |
| `DATABASE_URL` | Absolute path to `backend/inventcheck.sqlite3` | SQLAlchemy database connection |
| `CACHE_SECONDS` | `300` | Observation cache lifetime, 0–3600 seconds |
| `REQUEST_TIMEOUT` | `5` | Per-retailer timeout in seconds, greater than 0 and at most 30 |
| `FRONTEND_ORIGIN` | `http://127.0.0.1:5173` | Allowed browser origin for direct API requests |

Restart the backend after configuration changes. Never commit `.env`, credentials, or local database files. The app does not accept or use retailer API keys yet; see [retailer access](RETAILERS.md) for next steps.

## Tests and production build

```sh
cd backend
.venv/bin/python -m pytest -q
cd ../frontend
npm run build
npx playwright install chromium
npm run test:e2e
```

Browser tests start their own servers on 8000 and 5174 and use `/tmp/inventcheck-browser-tests.sqlite3`, separate from your normal database. Stop normal servers before running them. Tests clean only that dedicated test watchlist, and reports/screenshots stay ignored by Git. The browser runner's temporary database URL is for macOS/Linux; adjust it for Windows.

On this machine, the Miniconda Python 3.13 `readline` extension crashes when pytest loads terminal capture/debugging plugins. The application itself does not import readline. To run the same test suite here without those optional plugins:

```sh
cd backend
.venv/bin/python -m pytest -q -p no:capture -p no:debugging
```

Alternatively, recreate the virtual environment using a Python installation whose `import readline` succeeds. Do not modify system Python for this project. See [verification record](docs/VERIFICATION.md) for actual check results.

`npm run build` creates a frontend bundle; it does not deploy or bundle FastAPI. `npm run dev` is the supported local workflow.

## Architecture and extension

React/TypeScript/Vite/Tailwind call FastAPI/Pydantic endpoints. SQLAlchemy and Alembic handle SQLite persistence. Adapter-specific modules isolate retailer behavior, while shared services handle matching, cache, observation storage, and in-app notification evaluation.

- [Product requirements](docs/SPEC.md) and [decisions](docs/DECISIONS.md)
- [Architecture and endpoint map](ARCHITECTURE.md)
- [Retailer status and adding an adapter](RETAILERS.md)
- [Milestone checklist](docs/IMPLEMENTATION_PLAN.md)
- [Design choices](docs/DESIGN.md)
- [Original build prompt](docs/IMPLEMENTATION_PROMPT.md) and [historical request](docs/ORIGINAL_REQUEST.md)
- [ZIP data source, license, and refresh procedure](backend/data/README.md)

ZIP coordinates derive from [GeoNames](https://www.geonames.org/) under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see the attribution and transformations above. Store/product SVG illustrations are original demo assets.

## Limitations and next steps

- No live retailer integration, guaranteed inventory, or real purchase links. All five retailer adapters have explicit unavailable states in live mode.
- Manual checks only; no scheduler, email/SMS, push notifications, or monitoring while the app is closed.
- Matching is conservative exact-identifier/model or title-token matching over four fixtures, not a production product catalog search.
- Long-term live history requires source-specific permission. The app has expiring observations/alerts, but a future live integration must additionally implement its complete catalog retention and attribution policy before activation.
- SQLAlchemy avoids SQLite-specific business queries; a PostgreSQL driver, migration verification, and live deployment setup are still required for a database migration.
- Demo retention is unlimited. The chart summarizes daily lowest prices within the selected demo area; current observations expire from the “recent” view when older than the cache window (minimum 60 seconds).
- The app is designed for one local process/user. Public deployment, authentication, and multi-worker coordination are out of scope.

Recommended next features: an approved free live adapter with verified field semantics; optional scheduled local watchlist checks; expanded product fixtures and matching review for additional variants.

Store inventory and pricing can change quickly. Verify with the retailer before traveling to the store.
