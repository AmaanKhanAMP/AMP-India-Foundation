"use client";

import { cn } from "@/utils/cn";

const MAP = {
  published: "bg-emerald-50 text-emerald-700 ring-emerald-200/70",
  draft: "bg-slate-100 text-slate-600 ring-slate-200/70",
  archived: "bg-amber-50 text-amber-700 ring-amber-200/70",
  New: "bg-blue-50 text-blue-700 ring-blue-200/70",
  Read: "bg-slate-100 text-slate-600 ring-slate-200/70",
};

const DOT = {
  published: "bg-[#22C55E]",
  draft: "bg-slate-400",
  archived: "bg-[#F59E0B]",
  New: "bg-[#2563EB]",
  Read: "bg-slate-400",
};

export default function StatusBadge({ status, className }) {
  const raw = status || "draft";
  const key =
    typeof raw === "string" && ["published", "draft", "archived"].includes(raw.toLowerCase())
      ? raw.toLowerCase()
      : raw;
  const label =
    typeof key === "string" ? key.charAt(0).toUpperCase() + key.slice(1) : key;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-bold capitalize ring-1 shadow-sm",
        MAP[key] || "bg-slate-100 text-slate-600 ring-slate-200",
        className
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", DOT[key] || "bg-slate-400")} />
      {label}
    </span>
  );
}
