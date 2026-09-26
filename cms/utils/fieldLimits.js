/**
 * UI-driven character limits for CMS content fields.
 *
 * Limits are derived from how each field renders on the public site
 * (line clamps, card sizes, hero typography) — not arbitrary caps.
 * URL / image fields match DB String(500) capacity.
 */

export const URL_MAX = 500;
export const IMAGE_URL_MAX = 500;

/** @type {Record<string, Record<string, number>>} */
export const FIELD_LIMITS = {
  "hero-banners": {
    // Hero H1 ~2 lines @ 52px / 650px; accent is a short highlight word/phrase
    title: 48,
    title_accent: 24,
    // Subtitle is the lead paragraph (~3–4 lines); description is unused
    subtitle: 280,
    primary_btn_text: 22,
    primary_btn_link: URL_MAX,
    secondary_btn_text: 22,
    secondary_btn_link: URL_MAX,
    image_url: IMAGE_URL_MAX,
  },
  "home-projects": {
    // Overlay shows title only on 360×280 (desktop) / 290×245 (mobile) cards
    title: 55,
    image_url: IMAGE_URL_MAX,
  },
  "home-gallery": {
    // Accessibility alt + compact caption under each tile
    alt_text: 160,
    title: 80,
    description: 280,
    image_url: IMAGE_URL_MAX,
  },
  "home-events": {
    // Homepage row cards — no line-clamp; keep rows compact
    title: 80,
    description: 280,
    venue: 50,
    event_date: 32,
    speaker: 40,
    registration_link: URL_MAX,
    button_text: 22,
    image_url: IMAGE_URL_MAX,
  },
  testimonials: {
    // Quote area ~760px / 5–6 lines; meta lines stay single-line
    name: 40,
    designation: 100,
    organisation: 50,
    location: 40,
    message: 500,
    profile_image: IMAGE_URL_MAX,
  },
  "featured-events": {
    // Large split featured card — roomier than grid cards
    title: 70,
    description: 240,
    venue: 50,
    event_date: 32,
    event_time: 28,
    banner_image: IMAGE_URL_MAX,
  },
  "upcoming-events": {
    // EventCard: title clamp 2 lines, description clamp 3 lines
    title: 80,
    description: 200,
    venue: 50,
    event_date: 32,
    image_url: IMAGE_URL_MAX,
  },
  "past-events": {
    // Past Events card body — allow fuller CMS copy (~3–4 lines on card)
    title: 60,
    description: 380,
    event_date: 32,
    venue: 50,
    image_url: IMAGE_URL_MAX,
  },
  "gallery-items": {
    title: 60,
    description: 380,
    event_date: 32,
    venue: 50,
    image_url: IMAGE_URL_MAX,
  },
  "navbar-items": {
    label: 40,
    href: URL_MAX,
    item_key: 40,
    parent_key: 40,
  },
  "footer-links": {
    label: 40,
    href: URL_MAX,
  },
  "footer-focus": {
    title: 80,
    href: URL_MAX,
    date_label: 32,
  },
};

/**
 * @param {string} resource
 * @param {string} fieldName
 * @returns {number | undefined}
 */
export function getFieldMaxLength(resource, fieldName) {
  const limit = FIELD_LIMITS[resource]?.[fieldName];
  return typeof limit === "number" ? limit : undefined;
}

/**
 * Attach maxLength from FIELD_LIMITS onto configured form fields.
 * @param {string} resource
 * @param {Array<{ name: string, maxLength?: number }>} fields
 */
export function withFieldLimits(resource, fields) {
  return fields.map((field) => {
    if (field.maxLength != null) return field;
    const maxLength = getFieldMaxLength(resource, field.name);
    return maxLength != null ? { ...field, maxLength } : field;
  });
}

/**
 * Validate required + maxLength for CMS form values.
 * Does not mutate or truncate values.
 *
 * @param {Array<{ name: string, label: string, required?: boolean, maxLength?: number, type?: string }>} fields
 * @param {Record<string, unknown>} form
 * @returns {Record<string, string>}
 */
export function validateContentForm(fields, form) {
  /** @type {Record<string, string>} */
  const errors = {};

  fields.forEach((field) => {
    if (field.type === "image" || field.type === "select" || field.type === "number") {
      if (field.required && !String(form[field.name] ?? "").trim()) {
        errors[field.name] = `${field.label} is required.`;
      }
      // Image URLs still respect length when present
      if (field.type === "image" && field.maxLength != null) {
        const raw = String(form[field.name] ?? "");
        if (raw.length > field.maxLength) {
          errors[field.name] = `${field.label} must be at most ${field.maxLength} characters.`;
        }
      }
      return;
    }

    const value = String(form[field.name] ?? "");
    const trimmed = value.trim();

    if (field.required && !trimmed) {
      errors[field.name] = `${field.label} is required.`;
      return;
    }

    if (field.maxLength != null && value.length > field.maxLength) {
      errors[field.name] = `${field.label} must be at most ${field.maxLength} characters.`;
    }
  });

  return errors;
}

/**
 * Counter tone based on remaining capacity.
 * @param {number} length
 * @param {number} maxLength
 * @returns {'default' | 'warn' | 'danger'}
 */
export function getCounterTone(length, maxLength) {
  if (length >= maxLength) return "danger";
  if (length >= maxLength - 10) return "warn";
  return "default";
}
