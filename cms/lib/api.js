/**
 * Shared public API base URL for the AIF CMS (Next.js).
 *
 * Local:   NEXT_PUBLIC_API_URL=http://localhost:5000
 * Vercel:  NEXT_PUBLIC_API_URL=https://aif-backend-6jwe.onrender.com
 */

const DEPLOYED_API_URL = "https://aif-backend-6jwe.onrender.com";

function isLocalHost(urlOrHost) {
  return /localhost|127\.0\.0\.1/i.test(urlOrHost || "");
}

/**
 * Resolve API base for axios + media URLs.
 * Ignores a localhost API URL when the CMS itself is served from a non-local
 * host (deployed Vercel), so /uploads images keep working in production.
 */
export function getApiBaseUrl() {
  const fromEnv = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");

  if (fromEnv && !isLocalHost(fromEnv)) {
    return fromEnv;
  }

  if (
    typeof window !== "undefined" &&
    window.location.hostname &&
    !isLocalHost(window.location.hostname)
  ) {
    return DEPLOYED_API_URL;
  }

  return fromEnv || "http://localhost:5000";
}

export const API_URL = getApiBaseUrl();
