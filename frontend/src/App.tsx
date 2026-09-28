import { useEffect, useState } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import {
  Search,
  Bookmark,
  Settings,
  ScanLine,
  ArrowUpRight,
  CircleHelp,
} from "lucide-react";
import { api } from "./api";
import type { Status } from "./types";
import SearchPage from "./SearchPage";
import ProductPage from "./ProductPage";
import WatchlistPage from "./WatchlistPage";

export default function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [error, setError] = useState("");
  const location = useLocation();
  useEffect(() => {
    const controller = new AbortController();
    api<Status>("/status", { signal: controller.signal })
      .then(setStatus)
      .catch((e) => {
        if (e.name !== "AbortError")
          setError(
            "Backend unavailable. Start the backend, then reload this page.",
          );
      });
    return () => controller.abort();
  }, []);
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <Link to="/" className="brand">
          <span className="brand-icon">
            <ScanLine size={25} />
          </span>
          InventCheck<span className="brand-dot">.</span>
        </Link>
        <div className="nav-label">YOUR SHOPPING TOOLKIT</div>
        <nav aria-label="Main navigation">
          <NavLink to="/" end>
            <Search size={19} /> Find a product
          </NavLink>
          <NavLink to="/watchlist">
            <Bookmark size={19} /> Watchlist
          </NavLink>
          <NavLink to="/about">
            <Settings size={19} /> Settings & about
          </NavLink>
        </nav>
        <div className="sidebar-bottom">
          <div className="small-icon">
            <CircleHelp size={19} />
          </div>
          <strong>Compare before you go.</strong>
          <p>Check a price. Save a favorite. Make the trip count.</p>
          <a
            href="https://github.com/FarazBehlum/InventCheck"
            target="_blank"
            rel="noreferrer"
          >
            Project & documentation <ArrowUpRight size={14} />
          </a>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <span>Personal price explorer</span>
          <span className="mode-tag">
            <span className="status-dot" />
            {status
              ? status.mode === "demo"
                ? "Demo workspace"
                : "Live workspace"
              : "Connecting…"}
          </span>
        </header>
        {status?.mode === "demo" && (
          <div className="demo-banner">
            <span className="badge">DEMO</span>
            <span>
              Explore with fictional products, stores, and prices. These are not
              real retailer offers.
            </span>
          </div>
        )}
        <main id="main">
          {error && (
            <div className="error" role="alert">
              {error}{" "}
              <button onClick={() => window.location.reload()}>
                Retry connection
              </button>
            </div>
          )}
          <Routes>
            <Route path="/" element={<SearchPage status={status} />} />
            <Route
              path="/products/:id"
              element={<ProductPage status={status} />}
            />
            <Route
              path="/watchlist"
              element={<WatchlistPage status={status} />}
            />
            <Route path="/about" element={<About status={status} />} />
            <Route
              path="*"
              element={
                <div className="empty">
                  <h1>Page not found</h1>
                  <Link to="/">Return to search</Link>
                </div>
              }
            />
          </Routes>
        </main>
        <footer>
          Store inventory and pricing can change quickly. Verify with the
          retailer before traveling to the store.
        </footer>
      </div>
    </div>
  );
}
function About({ status }: { status: Status | null }) {
  return (
    <>
      <div className="page-heading">
        <span className="eyebrow">THE DETAILS</span>
        <h1>A little clarity goes a long way.</h1>
        <p>Your data sources, settings, and the limits of this local MVP.</p>
      </div>
      <section className="panel prose">
        <h2>Local and personal</h2>
        <p>
          InventCheck runs on your computer. Your watchlist and alerts are
          stored in a local SQLite database. No account, subscription, or
          browser location is required.
        </p>
        <dl className="settings-list">
          <div>
            <dt>Current mode</dt>
            <dd>{status?.mode ?? "Connecting"}</dd>
          </div>
          <div>
            <dt>Watchlist monitoring</dt>
            <dd>Manual checks only</dd>
          </div>
          <div>
            <dt>Result cache</dt>
            <dd>{status?.cache_seconds ?? "—"} seconds</dd>
          </div>
          <div>
            <dt>ZIP coverage</dt>
            <dd>
              {status?.zip_count.toLocaleString() ?? "—"} ZIPs · 50 states + DC
            </dd>
          </div>
        </dl>
        <p>
          Change backend settings in the root <code>.env</code> file and restart
          the backend. Live mode currently reports all retailers unavailable; it
          does not substitute fictional prices.
        </p>
      </section>
      <section className="panel">
        <h2>Retailer connections</h2>
        <div className="connection-list">
          {status?.retailers.map((r) => (
            <div key={r.id}>
              <strong>{r.name}</strong>
              <span className="pill">
                {r.status === "demo" ? "Demo adapter" : "Live unavailable"}
              </span>
              <span>No verified live pricing or inventory</span>
            </div>
          ))}
        </div>
      </section>
      <section className="panel prose">
        <h2>Location and history</h2>
        <p>
          ZIP coordinates are derived from{" "}
          <a href="https://www.geonames.org/" target="_blank" rel="noreferrer">
            GeoNames
          </a>
          , under{" "}
          <a
            href="https://creativecommons.org/licenses/by/4.0/"
            target="_blank"
            rel="noreferrer"
          >
            CC BY 4.0
          </a>
          . The bundled snapshot filters to US states and DC. Some new,
          military, and special-purpose ZIPs may be missing. Distances are
          approximate straight-line distances, not driving routes.
        </p>
        <p>
          Demo stores exist around these ZIPs: {status?.demo_zips.join(", ")}.
          All store names, street addresses, offers, illustrations, and price
          histories in demo mode are fictional.
        </p>
        <p>
          Live history will depend on each provider’s storage permissions.
          Scheduled checks, email/SMS alerts, paid data services, and cloud
          hosting are not part of this version.
        </p>
      </section>
    </>
  );
}
