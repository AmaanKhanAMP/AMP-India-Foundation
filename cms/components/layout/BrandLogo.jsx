"use client";

import { cn } from "@/utils/cn";

/**
 * Exact official AMP logo from the public website:
 * frontend/public/assets/logo.png → /brand/logo.png
 */
const LOGO_SRC = "/brand/logo.png";

export default function BrandLogo({ collapsed = false, className }) {
  if (collapsed) {
    return (
      <div
        className={cn(
          "flex w-full items-center justify-center transition-opacity duration-200",
          className
        )}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={LOGO_SRC}
          alt="AMP India Foundation"
          className="h-9 w-auto max-w-[48px] object-contain"
        />
      </div>
    );
  }

  return (
    <div className={cn("flex min-w-0 items-center overflow-hidden", className)}>
      <div className="min-w-0 max-w-[200px] shrink overflow-hidden">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={LOGO_SRC}
          alt="AMP India Foundation"
          className="h-auto w-[200px] max-w-full object-contain object-left"
        />
      </div>

      <span aria-hidden className="ml-4 h-9 w-px shrink-0 bg-[#E5E7EB]" />

      <div className="ml-4 flex shrink-0 flex-col justify-center leading-none">
        <span className="whitespace-nowrap text-[11px] font-medium tracking-wide text-[#1f2937]">
          Admin
        </span>
        <span className="mt-0.5 whitespace-nowrap text-[14px] font-semibold text-[#1f2937]">
          CMS
        </span>
      </div>
    </div>
  );
}
