/**
 * Shared public API base URL for the AIF website (Next.js).
 *
 * Local:   NEXT_PUBLIC_API_URL=http://localhost:5000
 * Vercel:  NEXT_PUBLIC_API_URL=https://aif-backend-6jwe.onrender.com
 *
 * Never hardcode the production backend host in application code —
 * set it via environment variables on Vercel.
 */
export const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"
).replace(/\/$/, "");

/**
 * Rewrite absolute localhost backend URLs (often stored from local CMS uploads)
 * to the current API_URL so production never requests http://localhost:5000.
 */
function isLoopbackApi(url) {
  try {
    const hostname = new URL(url).hostname;
    return hostname === "localhost" || hostname === "127.0.0.1";
  } catch {
    return false;
  }
}

export function resolveApiAssetUrl(url) {
  if (!url) return "";
  if (url.startsWith("blob:") || url.startsWith("data:")) return url;

  const rewritten = String(url).replace(
    /^https?:\/\/(localhost|127\.0\.0\.1):5000/i,
    API_URL
  );

  const absolute =
    rewritten.startsWith("http://") ||
    rewritten.startsWith("https://") ||
    rewritten.startsWith("blob:") ||
    rewritten.startsWith("data:")
      ? rewritten
      : rewritten.startsWith("/")
        ? `${API_URL}${rewritten}`
        : `${API_URL}/${rewritten}`;

  // Local dev: keep upload paths on this Next server. The optimizer then
  // treats them as internal images instead of a private-IP remote fetch.
  if (!isLoopbackApi(API_URL)) return absolute;
  try {
    const asset = new URL(absolute);
    const api = new URL(API_URL);
    if (
      asset.protocol === api.protocol &&
      asset.hostname === api.hostname &&
      asset.port === api.port &&
      asset.pathname.startsWith("/uploads/")
    ) {
      return `${asset.pathname}${asset.search}`;
    }
  } catch {
    return absolute;
  }
  return absolute;
}
