"use client";

import { useState } from "react";

export function useConfirm() {
  const [state, setState] = useState({
    open: false,
    title: "Confirm",
    message: "Are you sure?",
    confirmLabel: "Confirm",
    danger: false,
    onConfirm: null,
  });

  const ask = (opts) =>
    new Promise((resolve) => {
      setState({
        open: true,
        title: opts.title || "Confirm",
        message: opts.message || "Are you sure?",
        confirmLabel: opts.confirmLabel || "Confirm",
        danger: Boolean(opts.danger),
        onConfirm: () => {
          setState((s) => ({ ...s, open: false }));
          resolve(true);
        },
      });
      // store reject path via close
      setState((s) => ({
        ...s,
        onClose: () => {
          setState((prev) => ({ ...prev, open: false }));
          resolve(false);
        },
      }));
    });

  const close = () => {
    state.onClose?.();
    setState((s) => ({ ...s, open: false }));
  };

  return { state, ask, close, confirm: () => state.onConfirm?.() };
}
