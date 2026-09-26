"use client";

import { useEffect, useState } from "react";

function normalizeTitle(title) {
  return String(title || "")
    .toLowerCase()
    .replace(/[—–−]/g, "-")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Look up an existing finalized fallback image by CMS item title.
 * Does not invent images — returns "" when no matching fallback exists.
 */
export function fallbackByTitle(items, title, imageKey = "image") {
  if (!title || !Array.isArray(items)) return "";
  const needle = normalizeTitle(title);
  const match = items.find(
    (item) => normalizeTitle(item.title || item.titleStart) === needle
  );
  if (!match) return "";
  return match[imageKey] || "";
}

/**
 * Prefer a working CMS image URL. If that URL 404s, switch to an existing
 * finalized local fallback. Reset when the CMS URL changes (image replaced).
 */
export function useCmsImageSrc(cmsSrc, fallbackSrc) {
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setFailed(false);
  }, [cmsSrc]);

  const src = failed && fallbackSrc ? fallbackSrc : cmsSrc || fallbackSrc || "";

  return {
    src,
    onError: () => {
      if (fallbackSrc && fallbackSrc !== cmsSrc && !failed) {
        setFailed(true);
      }
    },
  };
}
