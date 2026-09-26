import {
  NAVBAR_ITEM_TYPE_OPTIONS,
  RESOURCES,
  STATUS_OPTIONS,
} from "@/utils/constants";

/**
 * CMS form field configs.
 * Character limits are applied centrally via utils/fieldLimits.js
 * (UI-driven) — do not hardcode arbitrary maxLength here unless overriding.
 */
export const resourceConfigs = {
  [RESOURCES.HERO_BANNERS]: {
    resource: RESOURCES.HERO_BANNERS,
    title: "Hero Banners",
    description: "Large homepage hero slides with CTAs.",
    basePath: "/home/hero-banners",
    imageKey: "image_url",
    large: true,
    folder: "hero-banners",
    fields: [
      { name: "image_url", label: "Banner image", type: "image", required: true, full: true, aspect: "video" },
      { name: "title", label: "Title", required: true },
      { name: "title_accent", label: "Title accent" },
      { name: "subtitle", label: "Subtitle" },
      // Homepage hero uses subtitle only — do not add a Description field.
      { name: "primary_btn_text", label: "Primary button text" },
      { name: "primary_btn_link", label: "Primary button link" },
      { name: "secondary_btn_text", label: "Secondary button text" },
      { name: "secondary_btn_link", label: "Secondary button link" },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.HOME_PROJECTS]: {
    resource: RESOURCES.HOME_PROJECTS,
    title: "Latest Projects",
    description: "Homepage project carousel — image and title only.",
    basePath: "/home/projects",
    folder: "home-projects",
    // Homepage Projects.jsx renders only image + title. Do not add description/CTA fields.
    fields: [
      {
        name: "image_url",
        label: "Project image",
        type: "image",
        required: true,
        full: true,
        aspect: "video",
      },
      { name: "title", label: "Project title", required: true, full: true },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.HOME_GALLERY]: {
    resource: RESOURCES.HOME_GALLERY,
    title: "Photo Gallery",
    description: "Homepage Photo Gallery tiles with title and short description.",
    basePath: "/home/gallery",
    folder: "home-gallery",
    titleKey: "title",
    fields: [
      {
        name: "image_url",
        label: "Gallery image",
        type: "image",
        required: true,
        full: true,
        aspect: "video",
      },
      {
        name: "title",
        label: "Gallery Title",
        required: true,
        full: true,
      },
      {
        name: "description",
        label: "Gallery Description",
        type: "textarea",
        required: true,
        full: true,
        rows: 3,
      },
      {
        name: "alt_text",
        label: "Alt text",
        required: true,
        full: true,
        hint: "Describes the image for accessibility (shown as the image alt attribute).",
      },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.HOME_EVENTS]: {
    resource: RESOURCES.HOME_EVENTS,
    title: "Home Upcoming Events",
    description: "Event teasers shown on the homepage.",
    basePath: "/home/events",
    folder: "home-events",
    fields: [
      { name: "image_url", label: "Event image", type: "image", required: true, full: true },
      { name: "title", label: "Title", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "venue", label: "Venue" },
      { name: "event_date", label: "Event date" },
      // Homepage event cards show date only — do not add Event time.
      { name: "speaker", label: "Speaker" },
      { name: "registration_link", label: "Registration link" },
      { name: "button_text", label: "Button text" },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.TESTIMONIALS]: {
    resource: RESOURCES.TESTIMONIALS,
    title: "Testimonials",
    description: "Homepage testimonials and quotes.",
    basePath: "/home/testimonials",
    imageKey: "profile_image",
    titleKey: "name",
    folder: "testimonials",
    fields: [
      { name: "profile_image", label: "Profile image", type: "image", aspect: "square" },
      { name: "name", label: "Name", required: true },
      { name: "designation", label: "Designation" },
      { name: "organisation", label: "Organisation" },
      { name: "location", label: "Location" },
      { name: "message", label: "Message", type: "textarea", required: true },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.FEATURED_EVENTS]: {
    resource: RESOURCES.FEATURED_EVENTS,
    title: "Featured Events",
    description: "Highlighted events on the Events page.",
    basePath: "/events/featured",
    imageKey: "banner_image",
    large: true,
    folder: "featured-events",
    fields: [
      { name: "banner_image", label: "Banner image", type: "image", required: true, full: true },
      { name: "title", label: "Title", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "venue", label: "Venue" },
      { name: "event_date", label: "Event date" },
      { name: "event_time", label: "Event time" },
      // Events page featured card has no registration CTA.
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.UPCOMING_EVENTS]: {
    resource: RESOURCES.UPCOMING_EVENTS,
    title: "Upcoming Events",
    description: "Upcoming events grid on the Events page.",
    basePath: "/events/upcoming",
    folder: "upcoming-events",
    fields: [
      { name: "image_url", label: "Event image", type: "image", required: true, full: true },
      { name: "title", label: "Title", required: true },
      { name: "description", label: "Description", type: "textarea" },
      { name: "venue", label: "Venue" },
      { name: "event_date", label: "Event date" },
      // Event cards show date/venue only — no time or registration link.
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.PAST_EVENTS]: {
    resource: RESOURCES.PAST_EVENTS,
    title: "Past Events",
    description: "Past events shown on the Events page grid.",
    basePath: "/events/gallery",
    folder: "past-events",
    fields: [
      { name: "image_url", label: "Event image", type: "image", required: true, full: true },
      { name: "title", label: "Title", required: true },
      {
        name: "description",
        label: "Past Event Description",
        type: "textarea",
        required: true,
        rows: 5,
        hint: "Shown on each Past Event card on the public Events page.",
      },
      { name: "venue", label: "Venue" },
      { name: "event_date", label: "Event date" },
      // Past event cards show date/venue only — no time or registration link.
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.NAVBAR_ITEMS]: {
    resource: RESOURCES.NAVBAR_ITEMS,
    title: "Navbar",
    description: "Site navigation links and Projects dropdown items.",
    basePath: "/site/navbar",
    titleKey: "label",
    hideImage: true,
    folder: "navbar",
    fields: [
      { name: "label", label: "Label", required: true },
      { name: "href", label: "Link", required: true, placeholder: "/about" },
      {
        name: "item_type",
        label: "Item type",
        type: "select",
        options: NAVBAR_ITEM_TYPE_OPTIONS,
        required: true,
        hint: "Use Dropdown parent for PROJECTS. Children nest under its dropdown key.",
      },
      {
        name: "item_key",
        label: "Dropdown key",
        placeholder: "projects",
        hint: "Required for dropdown parents. Children reference this key.",
      },
      {
        name: "parent_key",
        label: "Parent dropdown",
        type: "select",
        optionsResource: "navbar-items",
        optionsEmptyLabel: "— Top-level item —",
        optionsFilter: (item) =>
          item.item_type === "dropdown" && Boolean(item.item_key),
        optionsMap: (items) =>
          items.map((item) => ({
            value: item.item_key,
            label: `${item.label} (${item.item_key})`,
          })),
        hint: "Only set for dropdown children (e.g. Education under projects).",
      },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.FOOTER_LINKS]: {
    resource: RESOURCES.FOOTER_LINKS,
    title: "Footer Useful Links",
    description: "Links in the Footer Useful Links column.",
    basePath: "/site/footer/links",
    titleKey: "label",
    hideImage: true,
    fields: [
      { name: "label", label: "Label", required: true },
      { name: "href", label: "Link", required: true, placeholder: "/about" },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
  [RESOURCES.FOOTER_FOCUS]: {
    resource: RESOURCES.FOOTER_FOCUS,
    title: "Footer Recent Focus",
    description: "Items in the Footer Recent Focus column.",
    basePath: "/site/footer/focus",
    hideImage: true,
    fields: [
      { name: "title", label: "Title", required: true },
      { name: "href", label: "Link", required: true, placeholder: "/projects/education" },
      { name: "date_label", label: "Date label", required: true, placeholder: "July 2026" },
      { name: "display_order", label: "Display order", type: "number" },
      { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
    ],
  },
};

export function crumbsFor(config, extra = []) {
  return [
    { label: "Dashboard", href: "/dashboard" },
    { label: config.title, href: config.basePath },
    ...extra,
  ];
}
