import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, BookmarkPlus, TrendingDown } from "lucide-react";
import { api, money, when } from "./api";
import type { Observation, Product, Status } from "./types";
import WatchForm from "./WatchForm";

export default function ProductPage({ status }: { status: Status | null }) {
  const { id } = useParams();
  const [data, setData] = useState<{
    product: Product;
    history: Observation[];
    prices: Observation[];
  } | null>(null);
  const [error, setError] = useState("");
  const [watch, setWatch] = useState(false);
  const [notice, setNotice] = useState("");
  const [zipFilter, setZipFilter] = useState("53703");
  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError("");
    Promise.all([
      api<Product>(`/products/${id}`, { signal: controller.signal }),
      api<Observation[]>(`/products/${id}/history`, {
        signal: controller.signal,
      }),
      api<Observation[]>(`/products/${id}/prices`, {
        signal: controller.signal,
      }),
    ])
      .then(([product, history, prices]) =>
        setData({ product, history, prices }),
      )
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => controller.abort();
  }, [id]);
  const history = useMemo(
    () =>
      data?.history.filter((h) => !zipFilter || h.zip_code === zipFilter) ?? [],
    [data, zipFilter],
  );
  const prices =
    data?.prices.filter((p) => !zipFilter || p.zip_code === zipFilter) ?? [];
  const values = history
    .filter((h) => h.price !== null)
    .map((h) => Number(h.price));
  const current = prices
    .filter((p) => p.price !== null)
    .map((p) => Number(p.price));
  if (error)
    return (
      <div className="error" role="alert">
        {error} <Link to="/">Back to search</Link>
      </div>
    );
  if (!data)
    return (
      <div className="empty" role="status">
        Loading product and history…
      </div>
    );
  return (
    <>
      <Link className="back-link" to="/">
        <ArrowLeft size={16} /> Back to search
      </Link>
      <section className="product-hero">
        <div className="product-art">
          <img
            src={data.product.image_url}
            alt={`Illustration of ${data.product.name}`}
            width="260"
            height="210"
          />
        </div>
        <div>
          <span className="eyebrow">
            {data.product.provenance.toUpperCase()} PRODUCT ·{" "}
            {data.product.brand}
          </span>
          <h1>{data.product.name}</h1>
          <p>
            Model {data.product.model_number} · UPC {data.product.upc}
          </p>
          <button
            className="primary"
            onClick={() => setWatch(true)}
            disabled={!status}
          >
            <BookmarkPlus size={18} /> Watch this price
          </button>
        </div>
      </section>
      {notice && (
        <div className="success" role="status">
          {notice} <Link to="/watchlist">Open watchlist</Link>
        </div>
      )}
      <div className="section-heading">
        <h2>The price over time</h2>
        <label>
          Store area
          <select
            value={zipFilter}
            onChange={(e) => setZipFilter(e.target.value)}
          >
            <option value="">All demo areas</option>
            {status?.demo_zips.map((zip) => (
              <option key={zip} value={zip}>
                {zip}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="stat-grid">
        <div>
          <span>Current lowest observed</span>
          <strong>{money(current.length ? Math.min(...current) : null)}</strong>
          <small>Recent checks only</small>
        </div>
        <div>
          <span>Lowest in retained history</span>
          <strong>{money(values.length ? Math.min(...values) : null)}</strong>
          <small>{data.product.provenance} observations</small>
        </div>
        <div>
          <span>Highest in retained history</span>
          <strong>{money(values.length ? Math.max(...values) : null)}</strong>
          <small>Across selected stores</small>
        </div>
      </div>
      <section className="panel">
        <div className="section-heading">
          <h2>
            <TrendingDown size={20} /> Daily lowest observed price
          </h2>
          <span className="pill">{data.product.provenance} history</span>
        </div>
        <HistoryChart history={history} />
        <p className="hint">
          Synthetic history illustrates how tracking works. It is not a record
          of actual retailer prices.
        </p>
      </section>
      <section className="panel">
        <h2>Recent retailer observations</h2>
        {prices.length ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Store</th>
                  <th>Price</th>
                  <th>Inventory</th>
                  <th>Observed</th>
                </tr>
              </thead>
              <tbody>
                {prices.map((p) => (
                  <tr key={p.id}>
                    <td>
                      {p.store_name}
                      <small className="block">ZIP {p.zip_code}</small>
                    </td>
                    <td>
                      <strong>{money(p.price)}</strong>
                    </td>
                    <td>{p.inventory_status}</td>
                    <td>{when(p.observed_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>
            No recent checks in this area.{" "}
            <Link
              to={`/?q=${encodeURIComponent(data.product.model_number)}&zip_code=${zipFilter || "53703"}&radius=25`}
            >
              Search nearby offers
            </Link>{" "}
            to record a fresh observation.
          </p>
        )}
      </section>
      {watch && status && (
        <WatchForm
          product={data.product}
          status={status}
          zip={zipFilter || "53703"}
          onClose={() => setWatch(false)}
          onSaved={() => setNotice("Saved to your watchlist.")}
        />
      )}
    </>
  );
}
function HistoryChart({ history }: { history: Observation[] }) {
  const points = useMemo(() => {
    const map = new Map<string, number>();
    history.forEach((h) => {
      if (h.price !== null) {
        const date = h.observed_at.slice(0, 10);
        map.set(date, Math.min(map.get(date) ?? Infinity, Number(h.price)));
      }
    });
    return [...map].sort(([a], [b]) => a.localeCompare(b));
  }, [history]);
  if (!points.length)
    return <div className="empty">No retained observations for this area.</div>;
  const min = Math.min(...points.map((p) => p[1])) - 5,
    max = Math.max(...points.map((p) => p[1])) + 5;
  const first = Date.parse(points[0][0]),
    last = Date.parse(points.at(-1)![0]);
  const x = (date: string) =>
    60 + ((Date.parse(date) - first) / Math.max(last - first, 1)) * 770;
  const y = (price: number) => 200 - ((price - min) / (max - min)) * 155;
  return (
    <>
      <svg
        className="history-chart"
        viewBox="0 0 880 250"
        role="img"
        aria-label="Daily lowest demo price. Exact prices are in the table below."
      >
        {[min, (min + max) / 2, max].map((value) => (
          <g key={value}>
            <line
              x1="60"
              x2="850"
              y1={y(value)}
              y2={y(value)}
              stroke="var(--border)"
            />
            <text x="0" y={y(value) + 4} fill="var(--muted)" fontSize="12">
              {money(value)}
            </text>
          </g>
        ))}
        <polyline
          points={points
            .map(([date, price]) => `${x(date)},${y(price)}`)
            .join(" ")}
          fill="none"
          stroke="var(--accent)"
          strokeWidth="3"
        />
        {points.map(([date, price]) => (
          <g key={date}>
            <circle cx={x(date)} cy={y(price)} r="5" fill="var(--accent)">
              <title>
                {date}: {money(price)}
              </title>
            </circle>
            <text
              x={x(date)}
              y="232"
              textAnchor="middle"
              fill="var(--muted)"
              fontSize="12"
            >
              {date.slice(5)}
            </text>
          </g>
        ))}
      </svg>
      <details>
        <summary>View chart data</summary>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Lowest demo price</th>
            </tr>
          </thead>
          <tbody>
            {points.map(([date, price]) => (
              <tr key={date}>
                <td>{date}</td>
                <td>{money(price)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </>
  );
}
