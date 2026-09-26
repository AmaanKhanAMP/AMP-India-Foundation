"use client";

import { cn } from "@/utils/cn";

/**
 * Shared text input with a left Lucide icon.
 * Used by login, forgot/reset password, and any future icon fields.
 *
 * Icon: left 16px, vertically centered (top 50% + translateY(-50%)).
 * Text starts at 48px via .cms-input--with-icon so it never overlaps the icon.
 */
export default function IconInput({
  icon: Icon,
  className,
  inputClassName,
  rightSlot,
  type = "text",
  ...props
}) {
  return (
    <div className={cn("relative w-full", className)}>
      {Icon ? (
        <Icon
          className="pointer-events-none absolute left-4 top-1/2 z-[1] h-4 w-4 -translate-y-1/2 text-slate-400"
          aria-hidden="true"
        />
      ) : null}
      <input
        type={type}
        className={cn(
          "cms-input cms-input--with-icon",
          rightSlot && "cms-input--with-right",
          inputClassName
        )}
        {...props}
      />
      {rightSlot ? (
        <div className="absolute right-3 top-1/2 z-[1] -translate-y-1/2">{rightSlot}</div>
      ) : null}
    </div>
  );
}
