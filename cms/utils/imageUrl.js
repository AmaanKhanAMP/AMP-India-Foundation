import { API_URL, getApiBaseUrl } from "@/lib/api";

export { API_URL, getApiBaseUrl } from "@/lib/api";

/** Public website origin for frontend-only assets under /assets/. */
function getSiteUrl() {
  const fromEnv = (process.env.NEXT_PUBLIC_SITE_URL || "").trim().replace(/\/$/, "");
  if (fromEnv && !/localhost|127\.0\.0\.1/i.test(fromEnv)) {
    return fromEnv;
  }
  // Browser on a deployed CMS host — never fall back to developer localhost.
  if (
    typeof window !== "undefined" &&
    window.location.hostname &&
    !/^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname)
  ) {
    return fromEnv || "https://amp-aif.vercel.app";
  }
  return fromEnv || "http://localhost:3000";
}

/**
 * Resolve media URLs for CMS previews.
 * Rewrites absolute localhost API/site URLs so production never hits the
 * developer's machine.
 */
export function resolveImageUrl(url) {
  if (!url) return "";
  if (url.startsWith("blob:") || url.startsWith("data:")) return url;

  const api = getApiBaseUrl();
  const site = getSiteUrl();

  let rewritten = String(url)
    // Backend uploads / API host
    .replace(/^https?:\/\/(localhost|127\.0\.0\.1):5000/i, api)
    // Accidental absolute website URLs stored or composed with localhost:3000
    .replace(
      /^https?:\/\/(localhost|127\.0\.0\.1):3000(\/uploads\/.*)/i,
      (_, __, path) => `${api}${path}`
    )
    .replace(/^https?:\/\/(localhost|127\.0\.0\.1):3000(\/assets\/.*)/i, (_, __, path) => `${site}${path}`)
    .replace(/^https?:\/\/(localhost|127\.0\.0\.1):3000/i, site);

  if (
    rewritten.startsWith("http://") ||
    rewritten.startsWith("https://") ||
    rewritten.startsWith("blob:")
  ) {
    return rewritten;
  }

  // Default navbar logo lives on the CMS as /brand/logo.png (copied from frontend).
  if (rewritten === "/assets/logo.png") {
    return "/brand/logo.png";
  }

  // Other frontend public assets — resolve against the public site host.
  if (rewritten.startsWith("/assets/")) {
    return `${site}${rewritten}`;
  }

  // /uploads/... and other API-relative paths
  return rewritten.startsWith("/") ? `${api}${rewritten}` : `${api}/${rewritten}`;
}
