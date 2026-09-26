/**
 * Allowlisted CMS resources → Next.js cache tags and public routes.
 * The revalidate API never accepts arbitrary paths from the caller.
 */

export const CMS_REVALIDATE_MAP = {
  "hero-banners": {
    tags: ["hero-banners"],
    paths: ["/", "/home"],
  },
  "home-projects": {
    tags: ["home-projects"],
    paths: ["/", "/home"],
  },
  "home-events": {
    tags: ["home-events", "section-home_events"],
    paths: ["/", "/home"],
  },
  "home-gallery": {
    tags: ["home-gallery"],
    paths: ["/", "/home"],
  },
  testimonials: {
    tags: ["testimonials"],
    paths: ["/", "/home"],
  },
  "featured-events": {
    tags: ["featured-events"],
    paths: ["/events"],
  },
  "upcoming-events": {
    tags: ["upcoming-events", "section-upcoming_events"],
    paths: ["/events"],
  },
  "past-events": {
    tags: ["past-events"],
    paths: ["/events"],
  },
  "gallery-items": {
    tags: ["past-events"],
    paths: ["/events"],
  },
  "navbar-items": {
    tags: ["layout", "navbar-items"],
    paths: [],
    layout: true,
  },
  "footer-links": {
    tags: ["layout", "footer-links"],
    paths: [],
    layout: true,
  },
  "footer-focus": {
    tags: ["layout", "footer-focus"],
    paths: [],
    layout: true,
  },
  "layout-navbar": {
    tags: ["layout"],
    paths: [],
    layout: true,
  },
  "layout-footer": {
    tags: ["layout"],
    paths: [],
    layout: true,
  },
  "section-home_events": {
    tags: ["section-home_events"],
    paths: ["/", "/home"],
  },
  "section-upcoming_events": {
    tags: ["section-upcoming_events"],
    paths: ["/events"],
  },
};

export function resolveCmsRevalidateTarget(resource) {
  if (!resource || typeof resource !== "string") return null;
  return CMS_REVALIDATE_MAP[resource] || null;
}
