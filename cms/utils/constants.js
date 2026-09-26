export const TOKEN_KEY = "cms_token";
export const REMEMBER_KEY = "cms_remember";
export const AUTH_COOKIE = "cms_auth";

export const RESOURCES = {
  HERO_BANNERS: "hero-banners",
  HOME_PROJECTS: "home-projects",
  HOME_GALLERY: "home-gallery",
  HOME_EVENTS: "home-events",
  TESTIMONIALS: "testimonials",
  FEATURED_EVENTS: "featured-events",
  UPCOMING_EVENTS: "upcoming-events",
  PAST_EVENTS: "past-events",
  /** @deprecated Use PAST_EVENTS — same backend resource */
  GALLERY_ITEMS: "past-events",
  NAVBAR_ITEMS: "navbar-items",
  FOOTER_LINKS: "footer-links",
  FOOTER_FOCUS: "footer-focus",
};

export const NAVBAR_ITEM_TYPE_OPTIONS = [
  { value: "link", label: "Link" },
  { value: "dropdown", label: "Dropdown parent" },
];

export const STATUS_OPTIONS = [
  { value: "draft", label: "Draft" },
  { value: "published", label: "Published" },
];
