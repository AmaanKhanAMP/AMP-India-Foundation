"use client";

import { useLayoutEffect } from 'react';

/**
 * Reset viewport to the top when a page mounts after client-side navigation.
 * Next.js Link + `html { scroll-behavior: smooth }` can leave leftover
 * homepage scroll, so Framer `whileInView` sections stay at opacity 0.
 */
export default function ScrollToTop() {
  useLayoutEffect(() => {
    if (typeof window === 'undefined') return;

    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }

    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }, []);

  return null;
}
