"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";

const ToastContext = createContext(null);

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
};

const STYLES = {
  success: "border-emerald-200/80 bg-white text-emerald-900",
  error: "border-red-200/80 bg-white text-red-900",
  info: "border-blue-200/80 bg-white text-slate-900",
};

const ACCENT = {
  success: "bg-emerald-500",
  error: "bg-red-500",
  info: "bg-blue-500",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (message, type = "info") => {
      const id = `${Date.now()}-${Math.random()}`;
      setToasts((prev) => [...prev, { id, message, type }]);
      setTimeout(() => dismiss(id), 3800);
    },
    [dismiss]
  );

  const value = useMemo(
    () => ({
      toast: push,
      success: (message) => push(message, "success"),
      error: (message) => push(message, "error"),
      info: (message) => push(message, "info"),
    }),
    [push]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-5 right-5 z-[100] flex w-full max-w-sm flex-col gap-2.5">
        <AnimatePresence>
          {toasts.map((t) => {
            const Icon = ICONS[t.type] || Info;
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, y: 18, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.96 }}
                className={`pointer-events-auto relative overflow-hidden rounded-2xl border px-4 py-3.5 shadow-[var(--shadow-lg)] ${STYLES[t.type]}`}
              >
                <span className={`absolute inset-y-0 left-0 w-1 ${ACCENT[t.type]}`} />
                <div className="flex items-start gap-3 pl-1">
                  <Icon className="mt-0.5 h-5 w-5 shrink-0 opacity-90" />
                  <p className="flex-1 text-sm font-semibold leading-snug">{t.message}</p>
                  <button
                    type="button"
                    onClick={() => dismiss(t.id)}
                    className="rounded-md p-0.5 opacity-50 transition hover:opacity-100"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
