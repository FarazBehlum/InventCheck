export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const data = await response
      .json()
      .catch(() => ({ detail: "Could not reach the local backend." }));
    const detail = Array.isArray(data.detail)
      ? data.detail.map((x: { msg: string }) => x.msg).join(". ")
      : data.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}
export const money = (value: string | number | null | undefined) =>
  value == null
    ? "Unknown"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(Number(value));
export const when = (value: string | null) =>
  value ? new Date(value).toLocaleString() : "Not checked yet";
