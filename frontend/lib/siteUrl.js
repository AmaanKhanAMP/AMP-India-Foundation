/**
 * Public frontend origin for sitemap/robots.
 * Uses NEXT_PUBLIC_SITE_URL only — never NEXT_PUBLIC_API_URL.
 */
export function getSiteUrl() {
  const url = (process.env.NEXT_PUBLIC_SITE_URL || '').replace(/\/$/, '');
  if (!url) {
    throw new Error('NEXT_PUBLIC_SITE_URL is required for sitemap and robots.');
  }
  return url;
}

export function siteAbsoluteUrl(pathname) {
  const origin = getSiteUrl();
  if (!pathname || pathname === '/') return origin;
  return `${origin}${pathname.startsWith('/') ? pathname : `/${pathname}`}`;
}
