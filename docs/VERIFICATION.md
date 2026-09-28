# Verification record

Local verification on 2026-09-27, branch `feature/mvp`, isolated worktree `.worktrees/mvp`.

## Completed checks

- Backend: **22 tests passed** using `.venv/bin/python -m pytest -q -p no:capture -p no:debugging`.
- Coverage: identifier checksums/leading zeros, SKU scoping, variant separation, title confidence, discount/unknown values, distance, 51-state/DC coverage, API validation, demo search and caching, partial failures, timeout cancellation, missing credentials/rate limits/malformed response mapping, persistence across app restarts, mode separation, expiry purge, history, stores, watchlist CRUD, target alerts, deduplication, and read/dismiss behavior.
- Frontend: TypeScript check and Vite production build passed.
- Actual HTTP smoke check: `/api/health` returned `ok`; `/api/search?q=FW-D20&zip_code=53703&radius=25` returned 10 demo offers and statuses for all five retailers.
- Playwright: all three scenarios passed (two on the initial run; the full search/watchlist scenario passed on a targeted rerun after correcting an ambiguous test selector). Covers price/distance sorting and filtering, product history chart/data table, watchlist save/edit/delete, persistence after reload, manual checks, three qualifying alerts, repeat-check deduplication, mark-read behavior, mobile search/examples/empty results/invalid ZIP, and desktop screenshots.
- Visual inspection: desktop 1440px and phone 375px screenshots, clear demo banner, responsive navigation, no page-wide horizontal overflow. Wide result tables scroll inside their container.

## Environment notes

The system Miniconda Python 3.13 `readline` native extension crashes on import before pytest collects tests. Disabling pytest’s optional capture and debugging plugins avoids that extension; all application tests still execute. This workaround is local only, not an application code change. A standard Python installation with working readline can use the ordinary pytest command. FastAPI/Starlette also emitted an httpx test-client deprecation warning; requests and assertions passed.

## Not claimed

No live retailer HTTP integration, PostgreSQL deployment, public hosting, multi-user security, scheduled monitoring, or real product/store inventory was tested or delivered. GitHub Actions is configured to run checks after push; local results do not imply a completed hosted CI run.
