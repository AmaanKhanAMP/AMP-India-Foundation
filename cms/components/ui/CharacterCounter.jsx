"use client";

import { cn } from "@/utils/cn";
import { getCounterTone } from "@/utils/fieldLimits";

/**
 * Live character counter: "32 / 60"
 * Grey → orange (within 10 of limit) → red (at limit).
 */
export default function CharacterCounter({ length = 0, maxLength }) {
  if (maxLength == null || maxLength <= 0) return null;

  const tone = getCounterTone(length, maxLength);

  return (
    <span
      className={cn(
        "text-[11px] font-medium tabular-nums transition-colors",
        tone === "danger" && "text-red-600",
        tone === "warn" && "text-orange-500",
        tone === "default" && "text-slate-400"
      )}
      aria-live="polite"
    >
      {length} / {maxLength}
    </span>
  );
}
