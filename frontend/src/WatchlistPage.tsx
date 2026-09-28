import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bookmark,
  RefreshCw,
  Bell,
  Pencil,
  Trash2,
  Check,
  X,
} from "lucide-react";
import { api, money, when } from "./api";
import type { Alert, Status, Watch } from "./types";
import WatchForm from "./WatchForm";

export default function WatchlistPage({ status }: { status: Status | null }) {
  const [watches, setWatches] = useState<Watch[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [edit, setEdit] = useState<Watch | null>(null);
  async function load() {
    const [items, notifications] = await Promise.all([
      api<Watch[]>("/watchlist"),
      api<Alert[]>("/alerts"),
    ]);
    setWatches(items);
    setAlerts(notifications);
  }
  useEffect(() => {
    let active = true;
    Promise.all([api<Watch[]>("/watchlist"), api<Alert[]>("/alerts")])
      .then(([items, notifications]) => {
        if (active) {
          setWatches(items);
          setAlerts(notifications);
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  async function action(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await fn();
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function refresh() {
    await action(async () => {
      const result = await api<{ checked: number; new_alerts: number }>(
        "/watchlist/refresh",
        { method: "POST" },
      );
      setNotice(
        `Checked ${result.checked} saved products. ${result.new_alerts} new alerts. Repeat checks of the same price do not create duplicate alerts.`,
      );
    });
  }
  return (
    <>
      <div className="page-heading heading-with-action">
        <div>
          <span className="eyebrow">GOOD FINDS, KEPT CLOSE</span>
          <h1>Your watchlist.</h1>
          <p>Set your price. Check when you’re ready.</p>
        </div>
        <button
          className="primary"
          disabled={busy || !watches.length}
          onClick={refresh}
        >
          <RefreshCw size={18} className={busy ? "spin" : ""} />
          {busy ? "Checking…" : "Check watchlist"}
        </button>
      </div>
      <div className="info-note">
        <Bell size={18} />
        <span>
          Manual checks only. Alerts appear here when a known, available offer
          meets your target. Nothing runs in the background.
        </span>
      </div>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="success" role="status">
          {notice}
        </div>
      )}
      {loading ? (
        <div className="empty" role="status">
          Loading saved products…
        </div>
      ) : watches.length === 0 ? (
        <div className="empty panel">
          <Bookmark size={42} />
          <h2>A good price is worth remembering.</h2>
          <p>
            Find a demo product and choose “Watch price” to save your first
            item.
          </p>
          <Link className="primary" to="/">
            Find a product
          </Link>
        </div>
      ) : (
        <div className="watch-grid">
          {watches.map((w) => (
            <article className="watch-card" key={w.id}>
              <div className="watch-card-top">
                <img src={w.product.image_url} alt="" width="100" height="90" />
                <div>
                  <span className="eyebrow">
                    {w.provenance} · {w.product.brand}
                  </span>
                  <h2>
                    <Link to={`/products/${w.product.id}`}>
                      {w.product.name}
                    </Link>
                  </h2>
                  <span className="muted">{w.product.model_number}</span>
                </div>
              </div>
              <div className="watch-target">
                <span>Your target</span>
                <strong>{money(w.target_price)}</strong>
              </div>
              <p>
                {w.zip_code} · within {w.radius} miles
                <br />
                <span className="muted">
                  {w.retailers
                    .map(
                      (id) =>
                        status?.retailers.find((r) => r.id === id)?.name ?? id,
                    )
                    .join(", ")}
                </span>
              </p>
              <div className="watch-status">
                <strong>{w.check_status}</strong>
                <small>Last attempt: {when(w.last_attempted_at)}</small>
                <small>Last observation: {when(w.last_successful_at)}</small>
              </div>
              <div className="watch-actions">
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() => setEdit(w)}
                >
                  <Pencil size={15} />
                  Edit settings
                </button>
                <button
                  className="text-button danger"
                  disabled={busy}
                  aria-label={`Remove ${w.product.name}`}
                  onClick={() =>
                    action(async () => {
                      await api(`/watchlist/${w.id}`, { method: "DELETE" });
                      setNotice("Product removed from your watchlist.");
                    })
                  }
                >
                  <Trash2 size={16} />
                  Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
      <section className="panel alerts-panel">
        <div className="section-heading">
          <h2>
            <Bell size={20} /> In-app alerts
          </h2>
          <span className="pill">
            {alerts.filter((a) => !a.read).length} unread
          </span>
        </div>
        {!alerts.length ? (
          <p className="muted">
            No alerts yet. Try a target of $85 for the drill kit near 53703,
            then check your watchlist.
          </p>
        ) : (
          alerts.map((a) => (
            <article className={`alert-row ${a.read ? "read" : ""}`} key={a.id}>
              <span className="small-icon">
                <Check size={18} />
              </span>
              <div>
                <span className="eyebrow">
                  {a.provenance} TARGET REACHED{a.read ? " · READ" : ""}
                </span>
                <p>{a.message}</p>
                <small>{when(a.created_at)}</small>
              </div>
              {!a.read && (
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() =>
                    action(async () => {
                      await api(`/alerts/${a.id}`, {
                        method: "PATCH",
                        body: JSON.stringify({ read: true }),
                      });
                    })
                  }
                >
                  Mark read
                </button>
              )}
              <button
                className="icon-button"
                disabled={busy}
                aria-label="Dismiss alert"
                onClick={() =>
                  action(async () => {
                    await api(`/alerts/${a.id}`, {
                      method: "PATCH",
                      body: JSON.stringify({ dismissed: true }),
                    });
                  })
                }
              >
                <X size={18} />
              </button>
            </article>
          ))
        )}
      </section>
      {edit && status && (
        <WatchForm
          product={edit.product}
          status={status}
          existing={edit}
          onClose={() => setEdit(null)}
          onSaved={() => {
            load().catch((e) => setError(e.message));
            setNotice("Watchlist settings updated.");
          }}
        />
      )}
    </>
  );
}
