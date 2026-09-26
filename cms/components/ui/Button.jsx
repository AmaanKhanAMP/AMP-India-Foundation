"use client";

import { cn } from "@/utils/cn";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  className,
  loading,
  disabled,
  type = "button",
  ...props
}) {
  const variants = {
    primary:
      "bg-gradient-to-b from-[#3B82F6] to-[#2563EB] text-white shadow-[0_1px_2px_rgba(37,99,235,0.3),0_6px_16px_rgba(37,99,235,0.22)] hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(37,99,235,0.3)] active:translate-y-0",
    secondary:
      "bg-white text-[#111827] border border-[#E2E8F0] shadow-sm hover:-translate-y-0.5 hover:bg-slate-50 hover:border-slate-300 hover:shadow-md active:translate-y-0",
    outline:
      "bg-transparent text-[var(--primary)] border border-blue-200 hover:bg-[var(--primary-soft)] active:scale-[0.98]",
    ghost: "bg-transparent text-slate-600 hover:bg-slate-100/90 hover:text-[#111827]",
    danger:
      "bg-red-50 text-[var(--danger)] border border-red-100 hover:bg-red-100 hover:-translate-y-0.5 active:translate-y-0",
    soft: "bg-[var(--primary-soft)] text-[var(--primary)] hover:bg-blue-100",
  };
  const sizes = {
    sm: "h-8 px-3 text-xs rounded-[10px] gap-1.5",
    md: "h-10 px-4 text-sm rounded-[12px] gap-2",
    lg: "h-11 px-5 text-sm rounded-[12px] gap-2",
    icon: "h-9 w-9 rounded-[12px] p-0",
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center font-semibold transition duration-200 disabled:cursor-not-allowed disabled:opacity-55 disabled:hover:translate-y-0",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {loading ? (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
      ) : null}
      {children}
    </button>
  );
}
