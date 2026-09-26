"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

/**
 * Load singleton layout settings (navbar logo / footer copy).
 * Fail-open: keep provided fallback when the API is unreachable.
 */
export default function useLayoutSettings(kind, fallback) {
  const [data, setData] = useState(fallback);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/layout/${kind}`, {
          cache: "no-store",
        });
        if (!res.ok) {
          if (!cancelled) setLoading(false);
          return;
        }
        const json = await res.json();
        if (cancelled) return;
        if (json?.success && json.data && typeof json.data === "object") {
          setData({ ...fallback, ...json.data });
        }
      } catch {
        // keep fallback
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [kind]); // eslint-disable-line react-hooks/exhaustive-deps

  return { data, loading };
}
