"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

/**
 * Loads Hide/Show visibility for a website section.
 * Three-state while resolving: null → unknown (do not render), then boolean.
 * Fail-open after the request: unreachable API → true.
 *
 * @param {string} sectionName e.g. "upcoming_events"
 * @returns {{ isVisible: boolean | null, loading: boolean }}
 */
export default function useSectionVisibility(sectionName) {
  const [isVisible, setIsVisible] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(
          `${API_URL}/api/sections/${sectionName}/visibility`,
          { cache: "no-store" }
        );
        if (!res.ok) {
          if (!cancelled) {
            setIsVisible(true);
            setLoading(false);
          }
          return;
        }
        const json = await res.json();
        if (cancelled) return;
        if (json?.success && typeof json?.data?.is_visible === "boolean") {
          setIsVisible(json.data.is_visible);
        } else {
          setIsVisible(true);
        }
      } catch {
        if (!cancelled) setIsVisible(true);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sectionName]);

  return { isVisible, loading };
}
