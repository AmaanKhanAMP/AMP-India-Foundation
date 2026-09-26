"use client";

import { useEffect, useState } from "react";
import { fetchContentClient } from "@/lib/contentApi";

/**
 * @deprecated CMS sections now load on the server (see lib/loadCms.js) and
 * receive data as props. Client-side fetch caused FALLBACK → API flicker on
 * Vercel (especially with slow Render cold starts). Prefer server props.
 *
 * Kept only as an escape hatch for non-page utilities.
 */
export default function usePublishedContent(resource, fallback, mapFn) {
  const [items, setItems] = useState(fallback);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const result = await fetchContentClient(resource);
      if (cancelled) return;
      if (!result.ok) return; // network/API error → keep fallback
      try {
        setItems(result.data.map(mapFn));
      } catch {
        // mapping error → keep fallback
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [resource]); // eslint-disable-line react-hooks/exhaustive-deps

  return items;
}
