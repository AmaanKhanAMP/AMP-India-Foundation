"use client";

import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect, useState } from "react";
import { cn } from "@/utils/cn";

function AnimatedValue({ value }) {
  const numeric = typeof value === "number" ? value : Number(value);
  const isNumber = Number.isFinite(numeric);
  const mv = useMotionValue(0);
  const rounded = useTransform(mv, (v) => Math.round(v));
  const [display, setDisplay] = useState(isNumber ? 0 : value);

  useEffect(() => {
    if (!isNumber) {
      setDisplay(value);
      return;
    }
    const controls = animate(mv, numeric, { duration: 0.7, ease: "easeOut" });
    const unsub = rounded.on("change", (v) => setDisplay(v));
    return () => {
      controls.stop();
      unsub();
    };
  }, [value, isNumber, numeric, mv, rounded]);

  return <>{display}</>;
}

export default function StatCard({ title, value, icon: Icon, hint, className }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ type: "spring", stiffness: 400, damping: 28 }}
      className={cn(
        "group relative overflow-hidden rounded-[20px] border border-[#E2E8F0] bg-white p-5 shadow-[var(--shadow-sm)] transition-shadow hover:shadow-[var(--shadow-md)]",
        className
      )}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[3px] bg-gradient-to-r from-[#2563EB] via-[#3B82F6] to-transparent" />
      <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-[var(--primary-soft)] opacity-0 blur-2xl transition group-hover:opacity-100" />
      <div className="relative flex items-start justify-between gap-3">
        <div>
          <p className="text-[13px] font-semibold text-[#64748B]">{title}</p>
          <p className="font-display mt-2 text-3xl font-extrabold tracking-tight text-[#111827]">
            <AnimatedValue value={value} />
          </p>
          {hint ? <p className="mt-1.5 text-xs font-medium text-slate-400">{hint}</p> : null}
        </div>
        {Icon ? (
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#1E3A8A] text-white shadow-md shadow-blue-500/25">
            <Icon className="h-5 w-5" />
          </div>
        ) : null}
      </div>
    </motion.div>
  );
}
