"use client";

import { motion } from "framer-motion";
import Button from "@/components/ui/Button";

export default function FormShell({
  title,
  description,
  children,
  onSubmit,
  onCancel,
  loading,
  submitLabel = "Save",
  submitDisabled = false,
  dense = false,
  wide = false,
}) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (loading || submitDisabled) return;
        onSubmit?.();
      }}
      className={`mx-auto ${wide ? "max-w-5xl" : "max-w-4xl"} ${dense ? "space-y-4" : "space-y-6"}`}
    >
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className={`rounded-[20px] border border-[#E2E8F0] bg-white shadow-[var(--shadow-sm)] ${
          dense ? "p-4 sm:p-5" : "p-6 sm:p-8"
        }`}
      >
        <div
          className={`border-b border-[#E2E8F0] ${
            dense ? "mb-4 pb-3" : "mb-8 pb-5"
          }`}
        >
          <h2 className="font-display text-xl font-bold text-[#111827]">{title}</h2>
          {description ? (
            <p
              className={`text-sm leading-relaxed text-[#64748B] ${
                dense ? "mt-1" : "mt-1.5"
              }`}
            >
              {description}
            </p>
          ) : null}
        </div>
        <div className={dense ? "space-y-4" : "space-y-6"}>{children}</div>
      </motion.div>
      <div className="sticky bottom-4 z-10 flex items-center justify-end gap-2 rounded-2xl border border-[#E2E8F0] bg-white/90 p-3 shadow-[var(--shadow-md)] backdrop-blur-xl">
        {onCancel ? (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        ) : null}
        <Button type="submit" loading={loading} disabled={submitDisabled}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}
