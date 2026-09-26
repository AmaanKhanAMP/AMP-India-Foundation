"use client";

import { cn } from "@/utils/cn";

/** Shared surface for dashboard panels and content sections */
export default function Surface({
  children,
  className,
  title,
  description,
  action,
  padded = true,
}) {
  return (
    <section
      className={cn(
        "overflow-hidden rounded-[20px] border border-[#E2E8F0] bg-white shadow-[var(--shadow-sm)]",
        className
      )}
    >
      {(title || action) && (
        <div className="flex items-start justify-between gap-3 border-b border-[#E2E8F0] bg-gradient-to-r from-slate-50/90 to-white px-5 py-4">
          <div className="min-w-0">
            {title ? (
              <h2 className="font-display text-[15px] font-bold text-[#111827]">{title}</h2>
            ) : null}
            {description ? (
              <p className="mt-0.5 text-sm text-[#64748B]">{description}</p>
            ) : null}
          </div>
          {action ? <div className="shrink-0">{action}</div> : null}
        </div>
      )}
      <div className={cn(padded && "p-5 sm:p-6")}>{children}</div>
    </section>
  );
}
