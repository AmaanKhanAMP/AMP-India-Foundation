/**
 * Server CMS loaders for layout + Home/Events first paint.
 *
 * Fetches use Next.js ISR (`revalidate`) so warm navigations are served from
 * the Data Cache / CDN and do not wait on a Render cold start.
 * Do not wrap these loaders in a Promise.race timeout: aborting the serverless
 * function mid-fetch prevents the Data Cache from filling, so every click
 * becomes a cache miss.
 * Cached fetches must not use AbortSignal (see contentApi serverFetchInit).
 */

import { cache } from "react";
import {
  loadLayoutSettings,
  loadPublished,
  loadSectionVisibility,
  mapFeaturedEvent,
  mapFooterFocusItem,
  mapFooterLink,
  mapHeroBanner,
  mapHomeEvent,
  mapHomeGalleryItem,
  mapHomeProject,
  mapNavbarItem,
  mapPastEvent,
  mapTestimonial,
  mapUpcomingEvent,
} from "@/lib/contentApi";

/** Seconds — Next data cache / ISR for Home, Events, and the site shell. */
const HOME_EVENTS_REVALIDATE = 60;

const EMPTY_SHELL = {
  navbarSettings: null,
  navbarItems: null,
  footerSettings: null,
  footerLinks: null,
  footerFocus: null,
};

export const loadSiteShellCms = cache(async () => {
  try {
    const shellCache = { revalidate: 60 };
    const [navbarSettings, navbarItems, footerSettings, footerLinks, footerFocus] =
      await Promise.all([
        loadLayoutSettings("navbar"),
        loadPublished("navbar-items", mapNavbarItem, shellCache),
        loadLayoutSettings("footer"),
        loadPublished("footer-links", mapFooterLink, shellCache),
        loadPublished("footer-focus", mapFooterFocusItem, shellCache),
      ]);

    return {
      navbarSettings,
      navbarItems,
      footerSettings,
      footerLinks,
      footerFocus,
    };
  } catch {
    return EMPTY_SHELL;
  }
});

export const loadHomeCms = cache(async () => {
  const cacheOpts = { revalidate: HOME_EVENTS_REVALIDATE };
  const [
    heroBanners,
    homeProjects,
    homeEvents,
    homeGallery,
    testimonials,
    homeEventsVisible,
  ] = await Promise.all([
    loadPublished("hero-banners", mapHeroBanner, cacheOpts),
    loadPublished("home-projects", mapHomeProject, cacheOpts),
    loadPublished("home-events", mapHomeEvent, cacheOpts),
    loadPublished("home-gallery", mapHomeGalleryItem, cacheOpts),
    loadPublished("testimonials", mapTestimonial, cacheOpts),
    loadSectionVisibility("home_events", cacheOpts),
  ]);

  return {
    heroBanners,
    homeProjects,
    homeEvents,
    homeGallery,
    testimonials,
    homeEventsVisible,
  };
});

export const loadEventsCms = cache(async () => {
  const cacheOpts = { revalidate: HOME_EVENTS_REVALIDATE };
  const [featuredEvents, upcomingEvents, pastEvents, upcomingVisible] =
    await Promise.all([
      loadPublished("featured-events", mapFeaturedEvent, cacheOpts),
      loadPublished("upcoming-events", mapUpcomingEvent, cacheOpts),
      loadPublished("past-events", mapPastEvent, cacheOpts),
      loadSectionVisibility("upcoming_events", cacheOpts),
    ]);

  return {
    featuredEvents,
    upcomingEvents,
    pastEvents,
    upcomingVisible,
  };
});
