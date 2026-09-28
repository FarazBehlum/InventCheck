import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Search,
  MapPin,
  ArrowRight,
  BookmarkPlus,
  ExternalLink,
  SlidersHorizontal,
  PackageSearch,
  Check,
  Tag,
} from "lucide-react";
import { api, money, when } from "./api";
import type { Product, Offer, SearchResult, RetailerId, Status } from "./types";
import WatchForm from "./WatchForm";

const EXAMPLES = [
  {
    q: "FW-D20",
    name: "Cordless drill kit",
    image: "drill",
    description: "For the next weekend project",
  },
  {
    q: "headphones",
    name: "Wireless headphones",
    image: "headphones",
    description: "A little more listening, a little less spending",
  },
  {
    q: "coffee",
    name: "Coffee maker",
    image: "coffee",
    description: "A better start to your morning",
  },
];
export default function SearchPage({ status }: { status: Status | null }) {
  const [params, setParams] = useSearchParams();
  const paramString = params.toString();
  const [searchVersion, setSearchVersion] = useState(0);
  const [query, setQuery] = useState(params.get("q") ?? "");
  const [zip, setZip] = useState(params.get("zip_code") ?? "53703");
  const [radius, setRadius] = useState(Number(params.get("radius") ?? 25));
  const [selected, setSelected] = useState<RetailerId[]>(
    params.getAll("retailers") as RetailerId[],
  );
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [sort, setSort] = useState("price");
  const [onlyStock, setOnlyStock] = useState(false);
  const [retailerFilter, setRetailerFilter] = useState("");
  const [maxDistance, setMaxDistance] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [watch, setWatch] = useState<Product | null>(null);
  useEffect(() => {
    const next = new URLSearchParams(paramString);
    setQuery(next.get("q") ?? "");
    setZip(next.get("zip_code") ?? "53703");
    setRadius(Number(next.get("radius") ?? 25));
    setSelected(next.getAll("retailers") as RetailerId[]);
    if (!next.get("q")) {
      setResult(null);
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    setError("");
    setResult(null);
    setOnlyStock(false);
    setRetailerFilter("");
    setMaxDistance("");
    setMinPrice("");
    setMaxPrice("");
    api<SearchResult>(`/search?${next}`, { signal: controller.signal })
      .then(setResult)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [paramString, searchVersion]);
  function search(q = query) {
    const next = new URLSearchParams({
      q,
      zip_code: zip,
      radius: String(radius),
    });
    selected.forEach((r) => next.append("retailers", r));
    setParams(next);
    setSearchVersion((v) => v + 1);
    setNotice("");
  }
  function submit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) {
      setError("Enter a product name or identifier.");
      return;
    }
    search();
  }
  const filtered = useMemo(() => {
    const offers =
      result?.offers.filter(
        (o) =>
          (!onlyStock || o.inventory_status === "In stock") &&
          (!retailerFilter || o.retailer_id === retailerFilter) &&
          (!maxDistance || o.distance <= Number(maxDistance)) &&
          (!minPrice ||
            (o.price !== null && Number(o.price) >= Number(minPrice))) &&
          (!maxPrice ||
            (o.price !== null && Number(o.price) <= Number(maxPrice))),
      ) ?? [];
    const stockOrder: Record<string, number> = {
      "In stock": 0,
      "Limited stock": 1,
      Unknown: 2,
      "Out of stock": 3,
    };
    return offers.sort((a, b) =>
      sort === "distance"
        ? a.distance - b.distance
        : sort === "discount"
          ? (b.discount ?? -1) - (a.discount ?? -1)
          : sort === "stock"
            ? stockOrder[a.inventory_status] - stockOrder[b.inventory_status]
            : (a.price === null ? Infinity : Number(a.price)) -
              (b.price === null ? Infinity : Number(b.price)),
    );
  }, [
    result,
    sort,
    onlyStock,
    retailerFilter,
    maxDistance,
    minPrice,
    maxPrice,
  ]);
  const groups = useMemo(() => {
    const map = new Map<string, Offer[]>();
    filtered.forEach((o) =>
      map.set(o.product.id, [...(map.get(o.product.id) ?? []), o]),
    );
    return [...map.values()];
  }, [filtered]);
  return (
    <>
      <div className="page-heading">
        <span className="eyebrow">LESS GUESSWORK. BETTER SHOPPING.</span>
        <h1>
          Find your price.
          <br />
          <span>Then make your move.</span>
        </h1>
        <p>Compare prices and availability nearby, all in one place.</p>
      </div>
      <section className="search-panel" aria-label="Product search">
        <form onSubmit={submit}>
          <div className="search-fields">
            <label className="product-input">
              What are you looking for?
              <span className="input-wrap">
                <Search size={19} />
                <input
                  name="q"
                  required
                  maxLength={160}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Product name, UPC, model, or retailer SKU"
                />
              </span>
            </label>
            <label className="zip-input">
              ZIP code
              <span className="input-wrap">
                <MapPin size={18} />
                <input
                  name="zip"
                  required
                  pattern="[0-9]{5}"
                  inputMode="numeric"
                  maxLength={5}
                  value={zip}
                  onChange={(e) => setZip(e.target.value)}
                />
              </span>
            </label>
            <label>
              Within
              <select
                aria-label="Search radius"
                value={radius}
                onChange={(e) => setRadius(Number(e.target.value))}
              >
                {[5, 10, 25, 50].map((n) => (
                  <option key={n} value={n}>
                    {n} miles
                  </option>
                ))}
              </select>
            </label>
            <button
              className="primary search-button"
              disabled={loading || !status}
            >
              <Search size={18} />
              {loading ? "Searching…" : "Compare prices"}
            </button>
          </div>
          <fieldset className="retailer-field">
            <legend>
              Check retailers <span>(all if none selected)</span>
            </legend>
            <div className="retailer-chips">
              {status?.retailers.map((r) => (
                <button
                  type="button"
                  key={r.id}
                  aria-pressed={selected.includes(r.id)}
                  className={`retailer-chip ${selected.includes(r.id) ? "selected" : ""}`}
                  onClick={() =>
                    setSelected(
                      selected.includes(r.id)
                        ? selected.filter((id) => id !== r.id)
                        : [...selected, r.id],
                    )
                  }
                >
                  {selected.includes(r.id) && <Check size={13} />}
                  <span className={`retailer-dot ${r.id}`} />
                  {r.name}
                </button>
              ))}
            </div>
          </fieldset>
        </form>
      </section>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="success" role="status">
          {notice} <Link to="/watchlist">Open watchlist →</Link>
        </div>
      )}
      {loading && (
        <div className="empty" role="status">
          <span className="spinner" />
          <h2>Checking selected retailers…</h2>
          <p>Matching products and nearby stores.</p>
        </div>
      )}
      {!result && !loading && (
        <>
          <div className="section-heading">
            <div>
              <span className="eyebrow">TAKE IT FOR A SPIN</span>
              <h2>Start with a demo find.</h2>
            </div>
            <span className="muted">
              Fictional products · no purchase links
            </span>
          </div>
          <div className="example-grid">
            {EXAMPLES.map((item) => (
              <button
                className="example-card"
                key={item.q}
                onClick={() => {
                  setQuery(item.q);
                  search(item.q);
                }}
              >
                <div className={`product-art ${item.image}`}>
                  <img
                    src={`/images/${item.image}.svg`}
                    alt={`Illustration of ${item.name.toLowerCase()}`}
                    width="240"
                    height="180"
                  />
                </div>
                <div className="example-copy">
                  <span className="eyebrow">SAMPLE PRODUCT</span>
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <span className="text-link">
                    Compare demo offers <ArrowRight size={17} />
                  </span>
                </div>
              </button>
            ))}
          </div>
          <div className="local-note">
            <MapPin size={23} />
            <div>
              <strong>Start close to home.</strong>
              <p>
                ZIP lookup covers the US. Fictional demo stores are available
                near Madison (53703), New York (10001), Chicago (60601), and
                nine other cities. <Link to="/about">See demo locations</Link>
              </p>
            </div>
          </div>
        </>
      )}
      {result && (
        <section aria-label="Search results">
          <div className="section-heading">
            <div>
              <span className="eyebrow">YOUR COMPARISON</span>
              <h2>
                {filtered.length} offers near {result.location.city},{" "}
                {result.location.state}
              </h2>
              <p className="muted">
                Within {result.radius} miles · straight-line distance ·{" "}
                {result.mode} data
              </p>
            </div>
          </div>
          <details className="provider-status">
            <summary>
              Retailer check status ·{" "}
              {result.providers.filter((p) => p.status === "completed").length}/
              {result.providers.length} completed
            </summary>
            <ul>
              {result.providers.map((p) => (
                <li key={p.retailer_id}>
                  <strong>
                    {status?.retailers.find((r) => r.id === p.retailer_id)
                      ?.name ?? p.retailer_id}
                  </strong>
                  : {p.status} — {p.message}
                </li>
              ))}
            </ul>
          </details>
          <div className="filters">
            <SlidersHorizontal size={18} />
            <label>
              Sort by
              <select value={sort} onChange={(e) => setSort(e.target.value)}>
                <option value="price">Lowest price</option>
                <option value="discount">Largest discount</option>
                <option value="distance">Closest store</option>
                <option value="stock">In-stock first</option>
              </select>
            </label>
            <label>
              Retailer
              <select
                value={retailerFilter}
                onChange={(e) => setRetailerFilter(e.target.value)}
              >
                <option value="">All retailers</option>
                {status?.retailers.map((r) => (
                  <option value={r.id} key={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Max. miles
              <input
                type="number"
                min="0"
                max={result.radius}
                value={maxDistance}
                onChange={(e) => setMaxDistance(e.target.value)}
                placeholder={String(result.radius)}
              />
            </label>
            <label>
              Min. price
              <input
                type="number"
                min="0"
                step="0.01"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                placeholder="$0"
              />
            </label>
            <label>
              Max. price
              <input
                type="number"
                min="0"
                step="0.01"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                placeholder="Any"
              />
            </label>
            <label className="check-label">
              <input
                type="checkbox"
                checked={onlyStock}
                onChange={(e) => setOnlyStock(e.target.checked)}
              />
              In stock only
            </label>
            <button
              className="text-button"
              onClick={() => {
                setOnlyStock(false);
                setRetailerFilter("");
                setMaxDistance("");
                setMinPrice("");
                setMaxPrice("");
              }}
            >
              Reset filters
            </button>
          </div>
          {groups.length === 0 ? (
            <div className="empty">
              <PackageSearch size={42} />
              <h2>No offers to compare.</h2>
              <p>
                {result.offers.length
                  ? "Try widening your filters."
                  : "Try “FW-D20” near 53703 in demo mode, or check retailer availability above."}
              </p>
            </div>
          ) : (
            groups.map((offers) => (
              <OfferGroup
                key={offers[0].product.id}
                offers={offers}
                onWatch={setWatch}
              />
            ))
          )}
        </section>
      )}
      {watch && status && (
        <WatchForm
          product={watch}
          status={status}
          zip={result?.location.zip_code ?? zip}
          radius={result?.radius ?? radius}
          onClose={() => setWatch(null)}
          onSaved={() => setNotice("Product saved to your watchlist.")}
        />
      )}
    </>
  );
}
function OfferGroup({
  offers,
  onWatch,
}: {
  offers: Offer[];
  onWatch: (p: Product) => void;
}) {
  const product = offers[0].product;
  const priced = offers.filter((o) => o.price !== null);
  const cheapest = priced.reduce<Offer | undefined>(
    (best, o) => (!best || Number(o.price) < Number(best.price) ? o : best),
    undefined,
  );
  const nearest = offers
    .filter((o) => o.inventory_status === "In stock")
    .reduce<Offer | undefined>(
      (best, o) => (!best || o.distance < best.distance ? o : best),
      undefined,
    );
  const discount = offers
    .filter((o) => o.discount !== null && o.discount > 0)
    .reduce<Offer | undefined>(
      (best, o) => (!best || o.discount! > best.discount! ? o : best),
      undefined,
    );
  return (
    <article className="offer-group">
      <header className="group-header">
        <img src={product.image_url} alt="" width="72" height="72" />
        <div>
          <span className="eyebrow">
            {product.brand} · {product.model_number}
          </span>
          <h3>
            <Link to={`/products/${product.id}`}>{product.name}</Link>
          </h3>
          <span className="muted">
            UPC {product.upc} · {offers[0].match_reason} ({offers[0].confidence}
            %)
          </span>
        </div>
        <button className="secondary" onClick={() => onWatch(product)}>
          <BookmarkPlus size={17} /> Watch price
        </button>
      </header>
      <div className="table-scroll">
        <table className="offers-table">
          <thead>
            <tr>
              <th>Retailer & store</th>
              <th>Distance</th>
              <th>Price</th>
              <th>Availability</th>
              <th>Checked / source</th>
            </tr>
          </thead>
          <tbody>
            {offers.map((o) => (
              <tr key={o.id} data-testid="offer-row">
                <td>
                  <div className="retailer-name">
                    <span className={`retailer-dot ${o.retailer_id}`} />
                    {o.retailer_name}
                  </div>
                  <p>{o.store.name}</p>
                  <small>
                    {o.store.address}
                    <br />
                    {o.store.city}, {o.store.state} {o.store.zip_code}
                  </small>
                  <div className="offer-labels">
                    {o.id === cheapest?.id && (
                      <span>
                        <Tag size={11} />
                        Lowest price
                      </span>
                    )}
                    {o.id === nearest?.id && <span>Nearest in stock</span>}
                    {o.id === discount?.id && <span>Largest discount</span>}
                  </div>
                </td>
                <td>{o.distance.toFixed(1)} mi</td>
                <td>
                  <strong className="offer-price">{money(o.price)}</strong>
                  {o.regular_price !== null &&
                    o.price !== null &&
                    Number(o.regular_price) > Number(o.price) && (
                      <div>
                        <del>{money(o.regular_price)}</del>
                        {o.discount !== null && (
                          <span className="discount">−{o.discount}%</span>
                        )}
                      </div>
                    )}
                </td>
                <td>
                  <span
                    className={`inventory ${o.inventory_status.toLowerCase().replaceAll(" ", "-")}`}
                  >
                    {o.inventory_status}
                  </span>
                  <small className="block">
                    {o.inventory_quantity !== null
                      ? `${o.inventory_quantity} units · demo quantity`
                      : "Quantity unavailable"}
                  </small>
                </td>
                <td>
                  <span className="data-label">
                    {o.provenance} data{o.cached ? " · cached" : ""}
                  </span>
                  <small className="block">{when(o.observed_at)}</small>
                  {o.product_url ? (
                    <a href={o.product_url} target="_blank" rel="noreferrer">
                      Retailer product <ExternalLink size={12} />
                    </a>
                  ) : (
                    <small>Fictional product; no retailer link</small>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
