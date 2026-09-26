"use client";

import { cn } from "@/utils/cn";

export default function Select({ label, error, className, options = [], ...props }) {
  return (
    <label className="block space-y-1.5">
      {label ? (
        <span className="text-[13px] font-semibold text-slate-700">{label}</span>
      ) : null}
      <select
        className={cn(
          "cms-input appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 fill=%27none%27 viewBox=%270 0 24 24%27 stroke=%27%2394a3b8%27%3E%3Cpath stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27M19 9l-7 7-7-7%27/%3E%3C/svg%3E')] bg-[length:1rem] bg-[right_0.75rem_center] bg-no-repeat pr-10",
          error && "border-red-300 focus:!border-red-400 focus:!shadow-[0_0_0_4px_rgba(248,113,113,0.15)]",
          className
        )}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error ? <span className="text-xs font-medium text-red-600">{error}</span> : null}
    </label>
  );
}
