/**
 * In-memory + sessionStorage snapshots of Home/Events CMS payloads.
 *
 * Critical: client revalidation must NEVER replace a successful published
 * array with `null` (fetch failure). That unmounts Upcoming Events because
 * the render gate requires Array.isArray(events).
 */

const HOME_KEY = "aif:cms:home:v1";
const EVENTS_KEY = "aif:cms:events:v1";

let homeMem = null;
let eventsMem = null;

function hasCmsList(cms) {
  if (!cms || typeof cms !== "object") return false;
  return Object.values(cms).some((value) => Array.isArray(value));
}

function readStorage(key) {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function writeStorage(key, value) {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Quota / private mode — memory cache still helps soft nav.
  }
}

export function peekHomeCms() {
  if (homeMem) return homeMem;
  homeMem = readStorage(HOME_KEY);
  return homeMem;
}

export function peekEventsCms() {
  if (eventsMem) return eventsMem;
  eventsMem = readStorage(EVENTS_KEY);
  return eventsMem;
}

export function rememberHomeCms(data) {
  if (!hasCmsList(data)) return;
  homeMem = data;
  writeStorage(HOME_KEY, data);
}

export function rememberEventsCms(data) {
  if (!hasCmsList(data)) return;
  eventsMem = data;
  writeStorage(EVENTS_KEY, data);
}

export function cmsSnapshotEqual(a, b) {
  if (a === b) return true;
  if (!a || !b) return false;
  try {
    return JSON.stringify(a) === JSON.stringify(b);
  } catch {
    return false;
  }
}

/**
 * Prefer a successful published list over `null` (request failure).
 * Do not let a transient empty list wipe a previously valid list —
 * genuine CMS hide uses the visibility flag.
 */
function keepPublishedList(next, prev) {
  if (!Array.isArray(next)) return prev;
  if (next.length === 0 && Array.isArray(prev) && prev.length > 0) {
    return prev;
  }
  return next;
}

function keepVisibility(next, prev) {
  return typeof next === "boolean" ? next : prev;
}

/**
 * Hold a previously renderable Upcoming Events snapshot through transient
 * null/undefined/empty revalidation. Hide only on explicit CMS `false`.
 * Valid events remain shown even when the visibility flag is still unknown.
 */
export function holdRenderableEvents(held, visible, events) {
  if (visible === false) {
    return {
      visible: false,
      events: Array.isArray(events) ? events : held?.events,
    };
  }

  const heldEvents = Array.isArray(held?.events) ? held.events : null;
  const nextEvents = Array.isArray(events) ? events : heldEvents;

  if (
    Array.isArray(nextEvents) &&
    nextEvents.length === 0 &&
    Array.isArray(heldEvents) &&
    heldEvents.length > 0
  ) {
    return { visible: true, events: heldEvents };
  }

  if (Array.isArray(nextEvents)) {
    return { visible: true, events: nextEvents };
  }

  if (Array.isArray(heldEvents)) {
    return { visible: true, events: heldEvents };
  }

  return { visible, events: nextEvents };
}

export { hasCmsList };

/** Merge client revalidation into existing SSR/snapshot without null wipes. */
export function mergeHomeCms(prev, next) {
  const base = prev && typeof prev === "object" ? prev : {};
  const incoming = next && typeof next === "object" ? next : {};
  return {
    heroBanners: keepPublishedList(incoming.heroBanners, base.heroBanners),
    homeProjects: keepPublishedList(incoming.homeProjects, base.homeProjects),
    homeEvents: keepPublishedList(incoming.homeEvents, base.homeEvents),
    homeGallery: keepPublishedList(incoming.homeGallery, base.homeGallery),
    testimonials: keepPublishedList(incoming.testimonials, base.testimonials),
    homeEventsVisible: keepVisibility(
      incoming.homeEventsVisible,
      base.homeEventsVisible
    ),
  };
}

export function mergeEventsCms(prev, next) {
  const base = prev && typeof prev === "object" ? prev : {};
  const incoming = next && typeof next === "object" ? next : {};
  return {
    featuredEvents: keepPublishedList(
      incoming.featuredEvents,
      base.featuredEvents
    ),
    upcomingEvents: keepPublishedList(
      incoming.upcomingEvents,
      base.upcomingEvents
    ),
    pastEvents: keepPublishedList(incoming.pastEvents, base.pastEvents),
    upcomingVisible: keepVisibility(
      incoming.upcomingVisible,
      base.upcomingVisible
    ),
  };
}
