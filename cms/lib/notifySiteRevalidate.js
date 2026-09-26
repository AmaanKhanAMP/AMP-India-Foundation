/**
 * After a successful CMS mutation, ask the public site to drop stale ISR.
 * Never throws — save success must not depend on revalidation.
 */
export async function notifySiteRevalidate(resource) {
  if (!resource) return;
  try {
    const res = await fetch("/api/revalidate-site", {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      redirect: "manual",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resource }),
      signal: AbortSignal.timeout(8000),
    });
    if (res.type === "opaqueredirect" || res.status < 200 || res.status >= 300) {
      console.error("[notifySiteRevalidate] proxy error", resource, res.status);
      return;
    }
    const data = await res.json().catch(() => null);
    if (!data?.ok) {
      console.error("[notifySiteRevalidate] skipped or failed", resource);
    }
  } catch (error) {
    console.error("[notifySiteRevalidate] failed", resource, error);
  }
}
