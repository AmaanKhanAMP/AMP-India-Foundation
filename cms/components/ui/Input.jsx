"use client";

import { useId, useState } from "react";
import { cn } from "@/utils/cn";
import CharacterCounter from "@/components/ui/CharacterCounter";

/**
 * Premium input with floating label.
 * Floating fields use a taller box so the label never overlaps the value.
 * Supports maxLength + live character counter.
 */
export default function Input({
  label,
  error,
  hint,
  className,
  id,
  value,
  defaultValue,
  placeholder,
  onChange,
  onFocus,
  onBlur,
  maxLength,
  showCounter = true,
  type,
  ...props
}) {
  const autoId = useId();
  const inputId = id || props.name || autoId;
  const [focused, setFocused] = useState(false);
  const stringValue =
    value !== undefined && value !== null
      ? String(value)
      : defaultValue !== undefined && defaultValue !== null
        ? String(defaultValue)
        : "";
  const hasValue = stringValue.length > 0;
  const floated = focused || hasValue || Boolean(placeholder);
  const length = stringValue.length;
  const inputType = type || "text";
  const isTextLike =
    inputType === "text" || inputType === "url" || inputType === "email" || inputType === "tel";
  const counterVisible = showCounter && maxLength != null && isTextLike;

  const handleChange = (e) => {
    if (maxLength != null && e.target.value.length > maxLength) {
      e.target.value = e.target.value.slice(0, maxLength);
    }
    onChange?.(e);
  };

  if (!label) {
    return (
      <div className="block space-y-1.5">
        {counterVisible ? (
          <div className="flex justify-end">
            <CharacterCounter length={length} maxLength={maxLength} />
          </div>
        ) : null}
        <input
          id={inputId}
          type={inputType}
          value={value}
          defaultValue={defaultValue}
          placeholder={placeholder}
          className={cn("cms-input", error && "border-red-300", className)}
          {...props}
          maxLength={maxLength}
          onChange={handleChange}
        />
        {error ? <span className="text-xs font-medium text-red-600">{error}</span> : null}
        {!error && hint ? <span className="text-xs text-slate-400">{hint}</span> : null}
      </div>
    );
  }

  return (
    <div className="block space-y-1.5">
      <div className="relative">
        <input
          id={inputId}
          type={inputType}
          value={value}
          defaultValue={defaultValue}
          placeholder={floated ? placeholder || " " : " "}
          className={cn(
            "peer cms-input !h-14 px-3.5 pb-2.5 pt-6 text-sm leading-snug",
            counterVisible && "pr-16",
            error &&
              "border-red-300 focus:!border-red-400 focus:!shadow-[0_0_0_4px_rgba(248,113,113,0.15)]",
            className
          )}
          {...props}
          maxLength={maxLength}
          onChange={handleChange}
          onFocus={(e) => {
            setFocused(true);
            onFocus?.(e);
          }}
          onBlur={(e) => {
            setFocused(false);
            onBlur?.(e);
          }}
        />
        <label
          htmlFor={inputId}
          className={cn(
            "pointer-events-none absolute left-3.5 text-slate-400 transition-all duration-150",
            floated
              ? "top-2 text-[10px] font-bold uppercase tracking-[0.06em] text-[var(--primary)]"
              : "top-1/2 -translate-y-1/2 text-sm"
          )}
        >
          {label}
        </label>
        {counterVisible ? (
          <div className="pointer-events-none absolute right-3 top-2">
            <CharacterCounter length={length} maxLength={maxLength} />
          </div>
        ) : null}
      </div>
      {error ? <span className="text-xs font-medium text-red-600">{error}</span> : null}
      {!error && hint ? <span className="text-xs text-slate-400">{hint}</span> : null}
    </div>
  );
}
