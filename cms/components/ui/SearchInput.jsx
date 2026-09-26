"use client";

import { Search, X } from "lucide-react";
import { cn } from "@/utils/cn";

/**
 * Shared search field — icon 18px from left, 12px gap to text.
 */
export default function SearchInput({
  value = "",
  onChange,
  placeholder = "Search…",
  className,
  inputClassName,
}) {
  return (
    <div className={cn("relative flex w-full items-center", className)}>
      <Search
        className="pointer-events-none absolute left-[18px] top-1/2 z-[1] h-4 w-4 -translate-y-1/2 text-slate-400"
        aria-hidden="true"
      />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className={cn(
          "cms-input cms-search h-11 w-full rounded-[14px] placeholder:text-slate-400",
          "!pl-[46px]",
          value ? "!pr-11" : null,
          inputClassName
        )}
      />
      {value ? (
        <button
          type="button"
          onClick={() => onChange?.("")}
          className="absolute right-3 top-1/2 z-[1] -translate-y-1/2 rounded-lg p-1 text-slate-400 transition hover:bg-slate-200/70 hover:text-slate-700"
          aria-label="Clear search"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      ) : null}
    </div>
  );
}
