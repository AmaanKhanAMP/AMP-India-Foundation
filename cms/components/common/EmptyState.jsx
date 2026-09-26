"use client";

import { motion } from "framer-motion";
import { Inbox } from "lucide-react";
import Button from "@/components/ui/Button";

export default function EmptyState({
  title = "Nothing here yet",
  description = "Create your first item to get started.",
  actionLabel,
  onAction,
  icon: Icon = Inbox,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative flex flex-col items-center justify-center overflow-hidden rounded-[20px] border border-dashed border-[#E2E8F0] bg-gradient-to-b from-white via-white to-[var(--primary-soft)]/40 px-6 py-20 text-center shadow-[var(--shadow-sm)]"
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(37,99,235,0.1),transparent_55%)]" />
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        className="relative mb-2 flex h-20 w-20 items-center justify-center"
      >
        <div className="absolute inset-0 rounded-[1.5rem] bg-[var(--primary-soft)]" />
        <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#1E3A8A] text-white shadow-lg shadow-blue-500/30">
          <Icon className="h-7 w-7" />
        </div>
      </motion.div>
      <h3 className="font-display relative mt-4 text-xl font-bold text-[#111827]">{title}</h3>
      <p className="relative mt-2 max-w-md text-sm leading-relaxed text-[#64748B]">{description}</p>
      {actionLabel && onAction ? (
        <Button className="relative mt-7" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </motion.div>
  );
}
