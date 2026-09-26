"use client";

import { cn } from "@/utils/cn";

export function Skeleton({ className }) {
  return <div className={cn("cms-skeleton rounded-xl", className)} />;
}

export default function LoadingSkeleton({ rows = 4, variant = "cards" }) {
  if (variant === "table") {
    return (
      <div className="space-y-3 rounded-[1.25rem] border border-slate-200 bg-white p-4 shadow-[var(--shadow-sm)]">
        <Skeleton className="h-11 w-full max-w-sm rounded-2xl" />
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    );
  }

  if (variant === "banners") {
    return (
      <div className="space-y-5">
        {Array.from({ length: rows }).map((_, i) => (
          <div
            key={i}
            className="overflow-hidden rounded-[1.25rem] border border-slate-200 bg-white shadow-[var(--shadow-sm)]"
          >
            <Skeleton className="aspect-[21/9] w-full rounded-none" />
            <div className="space-y-3 p-5">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-3 w-2/3" />
              <Skeleton className="h-3 w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="overflow-hidden rounded-[1.25rem] border border-slate-200 bg-white shadow-[var(--shadow-sm)]"
        >
          <Skeleton className="aspect-[16/10] w-full rounded-none" />
          <div className="space-y-3 p-5">
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-3 w-1/2" />
            <Skeleton className="h-8 w-full" />
          </div>
        </div>
      ))}
    </div>
  );
}
