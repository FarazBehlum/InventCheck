import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { X, Bookmark } from "lucide-react";
import { api } from "./api";
import type { Product, RetailerId, Status, Watch } from "./types";

export default function WatchForm({
  product,
  status,
  zip = "53703",
  radius = 25,
  existing,
  onClose,
  onSaved,
}: {
  product: Product;
  status: Status;
  zip?: string;
  radius?: number;
  existing?: Watch;
  onClose: () => void;
  onSaved: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [target, setTarget] = useState(
    existing ? String(existing.target_price) : "",
  );
  const [zipCode, setZip] = useState(existing?.zip_code ?? zip);
  const [distance, setDistance] = useState(existing?.radius ?? radius);
  const [retailers, setRetailers] = useState<RetailerId[]>(
    existing?.retailers ?? status.retailers.map((r) => r.id),
  );
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    dialog.current?.showModal();
    return () => dialog.current?.close();
  }, []);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!retailers.length) {
      setError("Select at least one retailer.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await api(existing ? `/watchlist/${existing.id}` : "/watchlist", {
        method: existing ? "PATCH" : "POST",
        body: JSON.stringify({
          ...(!existing ? { product_id: product.id } : {}),
          target_price: target,
          zip_code: zipCode,
          radius: distance,
          retailers,
        }),
      });
      onSaved();
      onClose();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }
  return (
    <dialog
      ref={dialog}
      className="watch-dialog"
      onCancel={onClose}
      aria-labelledby="watch-title"
    >
      <form onSubmit={submit}>
        <div className="dialog-heading">
          <span className="small-icon">
            <Bookmark size={21} />
          </span>
          <button
            type="button"
            className="icon-button"
            aria-label="Close watchlist form"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>
        <span className="eyebrow">
          {product.provenance.toUpperCase()} WATCHLIST
        </span>
        <h2 id="watch-title">
          {existing ? "Edit saved product" : "Keep an eye on this one."}
        </h2>
        <p>
          {product.brand} {product.name}
        </p>
        <label>
          Target price ($)
          <input
            autoFocus
            type="number"
            min="0.01"
            max="1000000"
            step="0.01"
            required
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="e.g. 85.00"
          />
        </label>
        <div className="form-pair">
          <label>
            ZIP code
            <input
              required
              inputMode="numeric"
              pattern="[0-9]{5}"
              maxLength={5}
              value={zipCode}
              onChange={(e) => setZip(e.target.value)}
            />
          </label>
          <label>
            Search radius
            <select
              value={distance}
              onChange={(e) => setDistance(Number(e.target.value))}
            >
              {[5, 10, 25, 50].map((n) => (
                <option key={n} value={n}>
                  {n} miles
                </option>
              ))}
            </select>
          </label>
        </div>
        <fieldset>
          <legend>Preferred retailers</legend>
          <div className="checkbox-grid">
            {status.retailers.map((r) => (
              <label key={r.id}>
                <input
                  type="checkbox"
                  checked={retailers.includes(r.id)}
                  onChange={() =>
                    setRetailers(
                      retailers.includes(r.id)
                        ? retailers.filter((id) => id !== r.id)
                        : [...retailers, r.id],
                    )
                  }
                />
                {r.name}
              </label>
            ))}
          </div>
        </fieldset>
        <p className="hint">
          Check your watchlist manually to see target-price alerts. No
          background monitoring.
        </p>
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
        <button className="primary w-full" disabled={saving}>
          {saving ? "Saving…" : existing ? "Save changes" : "Save to watchlist"}
        </button>
      </form>
    </dialog>
  );
}
