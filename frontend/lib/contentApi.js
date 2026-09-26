import { API_URL, resolveApiAssetUrl } from "@/lib/api";
import {
  mergeEventsCms,
  mergeHomeCms,
  peekEventsCms,
  peekHomeCms,
  rememberEventsCms,
  rememberHomeCms,
} from "@/lib/cmsClientCache";

/**
 * Public content API helpers for the website.
 * On network/API failure, callers keep hardcoded fallbacks.
 * An empty published list is success — do not restore fallbacks.
 */

export const API_BASE = API_URL;

/** Fail fast when the CMS API is down so soft navigations are not held open. */
const FETCH_TIMEOUT_MS = 4000;

function withTimeout(init = {}) {
  return {
    ...init,
    signal: init.signal ?? AbortSignal.timeout(FETCH_TIMEOUT_MS),
  };
}

/**
 * Next.js Data Cache ignores / cannot store fetches that include AbortSignal.
 * Cached SSR reads must not attach a timeout signal or every Home/Events
 * navigation hits Render live (up to 4s, worse on cold start).
 */
function serverFetchInit(options = {}) {
  const revalidate = options.revalidate;
  if (typeof revalidate === "number") {
    const next = { revalidate };
    if (Array.isArray(options.tags) && options.tags.length) {
      next.tags = options.tags;
    }
    return { next };
  }
  return withTimeout({ cache: "no-store" });
}

export function resolveMediaUrl(url) {
  return resolveApiAssetUrl(url);
}

/**
 * Resolve logo/media URLs for the public site.
 * Frontend /assets/* stay on the Next.js host; uploads go through the API.
 */
export function resolveSiteAssetUrl(url) {
  if (!url) return "";
  if (
    url.startsWith("blob:") ||
    url.startsWith("data:") ||
    url.startsWith("/assets/")
  ) {
    return url;
  }
  return resolveApiAssetUrl(url);
}

export function mapNavbarItem(row) {
  return {
    id: row.id,
    label: row.label || "",
    href: row.href || "#",
    itemType: row.item_type || "link",
    itemKey: row.item_key || null,
    parentKey: row.parent_key || null,
    order: row.display_order ?? 0,
  };
}

export function mapFooterLink(row) {
  return {
    id: row.id,
    label: row.label || "",
    href: row.href || "/",
    order: row.display_order ?? 0,
  };
}

export function mapFooterFocusItem(row) {
  return {
    id: row.id,
    title: row.title || "",
    href: row.href || "/",
    dateLabel: row.date_label || "",
    order: row.display_order ?? 0,
  };
}

/**
 * Server-side published content fetch.
 *
 * Home/Events pages pass `revalidate` so ISR/soft navigations reuse the
 * Next.js Data Cache. Do not attach AbortSignal to those fetches — it
 * disables the Data Cache and forces a live Render round-trip.
 * Client / uncached callers keep `cache: "no-store"` plus a timeout.
 */
export async function fetchPublished(resource, options = {}) {
  const res = await fetch(
    `${API_URL}/api/content/${resource}`,
    serverFetchInit({
      ...options,
      tags: options.tags || [resource],
    })
  );
  if (!res.ok) throw new Error(`Failed to fetch ${resource}`);
  const json = await res.json();
  if (!json?.success || !Array.isArray(json.data)) {
    throw new Error(`Invalid response for ${resource}`);
  }
  // Empty published list is valid — callers should not fall back to hardcoded data
  return json.data;
}

/**
 * Map published rows. On success (including empty list) returns mapped array.
 * On network/API failure returns `null` so the caller can apply a local fallback.
 */
export async function loadPublished(resource, mapFn, options = {}) {
  try {
    const data = await fetchPublished(resource, options);
    return data.map(mapFn);
  } catch {
    return null;
  }
}

/** Singleton layout settings (navbar / footer). Returns null on failure. */
export async function loadLayoutSettings(kind) {
  try {
    const res = await fetch(
      `${API_URL}/api/layout/${kind}`,
      { next: { revalidate: 60, tags: ["layout"] } }
    );
    if (!res.ok) return null;
    const json = await res.json();
    if (!json?.success || !json.data || typeof json.data !== "object") {
      return null;
    }
    return json.data;
  } catch {
    return null;
  }
}

/** Section visibility flag. Fail-open: true when unreachable. */
export async function loadSectionVisibility(sectionName, options = {}) {
  try {
    const res = await fetch(
      `${API_URL}/api/sections/${sectionName}/visibility`,
      serverFetchInit({
        ...options,
        tags: options.tags || [`section-${sectionName}`],
      })
    );
    if (!res.ok) return true;
    const json = await res.json();
    if (json?.success && typeof json?.data?.is_visible === "boolean") {
      return json.data.is_visible;
    }
    return true;
  } catch {
    return true;
  }
}

/**
 * Client-side fetch (no Next cache). Kept for non-CMS utilities / escape hatches.
 * Returns { ok: true, data: array } on success (data may be empty).
 * Returns { ok: false, data: null } on network/API failure.
 */
export async function fetchContentClient(resource) {
  try {
    const res = await fetch(
      `${API_URL}/api/content/${resource}`,
      withTimeout({ cache: "no-store" })
    );
    if (!res.ok) return { ok: false, data: null };
    const json = await res.json();
    if (!json?.success || !Array.isArray(json.data)) {
      return { ok: false, data: null };
    }
    return { ok: true, data: json.data };
  } catch {
    return { ok: false, data: null };
  }
}

async function loadPublishedClient(resource, mapFn) {
  const result = await fetchContentClient(resource);
  if (!result.ok) return null;
  return result.data.map(mapFn);
}

/** Client visibility fetch. Fail-open: true when unreachable. */
export async function loadSectionVisibilityClient(sectionName) {
  try {
    const res = await fetch(
      `${API_URL}/api/sections/${sectionName}/visibility`,
      withTimeout({ cache: "no-store" })
    );
    if (!res.ok) return true;
    const json = await res.json();
    if (json?.success && typeof json?.data?.is_visible === "boolean") {
      return json.data.is_visible;
    }
    return true;
  } catch {
    return true;
  }
}

/**
 * Browser-side Home CMS load. Used so `/` and `/home` soft-navigations
 * are not blocked waiting for Render/localhost CMS responses.
 */
export async function loadHomeCmsClient() {
  const [
    heroBanners,
    homeProjects,
    homeEvents,
    homeGallery,
    testimonials,
    homeEventsVisible,
  ] = await Promise.all([
    loadPublishedClient("hero-banners", mapHeroBanner),
    loadPublishedClient("home-projects", mapHomeProject),
    loadPublishedClient("home-events", mapHomeEvent),
    loadPublishedClient("home-gallery", mapHomeGalleryItem),
    loadPublishedClient("testimonials", mapTestimonial),
    loadSectionVisibilityClient("home_events"),
  ]);

  const data = {
    heroBanners,
    homeProjects,
    homeEvents,
    homeGallery,
    testimonials,
    homeEventsVisible,
  };
  // Merge with any SSR/snapshot so a failed field (null) cannot wipe valid data
  // or poison sessionStorage — that was unmounting Upcoming Events after load.
  const merged = mergeHomeCms(peekHomeCms(), data);
  rememberHomeCms(merged);
  return merged;
}

/**
 * Browser-side Events CMS load — same non-blocking soft-nav pattern as Home.
 */
export async function loadEventsCmsClient() {
  const [featuredEvents, upcomingEvents, pastEvents, upcomingVisible] =
    await Promise.all([
      loadPublishedClient("featured-events", mapFeaturedEvent),
      loadPublishedClient("upcoming-events", mapUpcomingEvent),
      loadPublishedClient("past-events", mapPastEvent),
      loadSectionVisibilityClient("upcoming_events"),
    ]);

  const data = {
    featuredEvents,
    upcomingEvents,
    pastEvents,
    upcomingVisible,
  };
  const merged = mergeEventsCms(peekEventsCms(), data);
  rememberEventsCms(merged);
  return merged;
}

export function mapHeroBanner(row) {
  return {
    id: row.id,
    image: resolveMediaUrl(row.image_url),
    titleStart: row.title || "",
    titleAccent: row.title_accent || "",
    subtitle: row.subtitle || "",
    primaryBtnText: row.primary_btn_text || "Learn More",
    primaryLink: row.primary_btn_link || "/",
    secondaryBtnText: row.secondary_btn_text || "",
    secondaryLink: row.secondary_btn_link || "/",
  };
}

export function mapHomeProject(row) {
  return {
    id: row.id,
    image: resolveMediaUrl(row.image_url),
    title: row.title,
  };
}

export function mapHomeGalleryItem(row) {
  return {
    id: row.id,
    src: resolveMediaUrl(row.image_url),
    alt: row.alt_text || "",
    title: row.title || "",
    description: row.description || "",
    order: row.display_order ?? 0,
  };
}

export function mapHomeEvent(row) {
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    speaker: row.speaker,
    date: row.event_date,
    venue: row.venue,
    image: resolveMediaUrl(row.image_url),
    detailsLink: row.registration_link || "#",
  };
}

export function mapTestimonial(row) {
  return {
    id: row.id,
    name: row.name,
    role: row.designation || row.organisation || "",
    location: row.location || "",
    avatar: resolveMediaUrl(row.profile_image),
    quote: row.message?.startsWith('"') ? row.message : `"${row.message || ""}"`,
  };
}

export function mapFeaturedEvent(row) {
  return {
    id: row.id,
    title: row.title,
    date: row.event_date,
    time: row.event_time,
    venue: row.venue,
    description: row.description,
    image: resolveMediaUrl(row.banner_image),
  };
}

export function mapUpcomingEvent(row) {
  return {
    id: row.id,
    title: row.title,
    date: row.event_date,
    venue: row.venue,
    description: row.description,
    image: resolveMediaUrl(row.image_url),
  };
}

/** Maps CMS past-event rows into the shared EventCard shape. */
export function mapPastEvent(row) {
  return {
    id: row.id,
    title: row.title,
    date: row.event_date || row.year || null,
    venue: row.venue || row.location || null,
    // Prefer CMS description; empty string lets EventCard apply fallback only if needed
    description: row.description != null ? String(row.description) : '',
    image: resolveMediaUrl(row.image_url),
  };
}

export function mapGalleryItem(row) {
  return {
    id: row.id,
    name: row.title,
    year: row.year,
    location: row.location,
    image: resolveMediaUrl(row.image_url),
    tall: false,
  };
}
