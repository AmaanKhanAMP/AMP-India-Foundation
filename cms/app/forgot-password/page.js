"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Mail } from "lucide-react";
import Button from "@/components/ui/Button";
import IconInput from "@/components/ui/IconInput";
import { useToast } from "@/contexts/ToastContext";
import authService from "@/services/authService";

export default function ForgotPasswordPage() {
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await authService.forgotPassword(email.trim());
      setSent(true);
      toast.success(res.message || "Reset link sent if the account exists.");
    } catch (err) {
      toast.error(err.response?.data?.message || "Unable to send reset link.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.18),_transparent_42%),radial-gradient(circle_at_bottom_right,_rgba(15,23,42,0.06),_transparent_40%)]" />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-md rounded-[1.5rem] border border-slate-200/80 bg-white p-8 shadow-[var(--shadow-lg)] sm:p-10"
      >
        <Link
          href="/login"
          className="mb-6 inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-[var(--primary)]"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>

        <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[var(--primary)]">
          Account recovery
        </p>
        <h1 className="font-display mt-2 text-2xl font-extrabold text-slate-900">
          Forgot password
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-slate-500">
          Enter your admin email and we&apos;ll send a secure reset link.
        </p>

        {sent ? (
          <div className="mt-8 rounded-2xl border border-emerald-100 bg-emerald-50/80 p-4 text-sm text-emerald-800">
            If an account exists for <strong>{email}</strong>, a reset link has been sent. Check
            your inbox — or the Flask terminal in local development.
          </div>
        ) : (
          <form onSubmit={onSubmit} className="mt-8 space-y-4">
            <label className="block space-y-1.5">
              <span className="text-[13px] font-semibold text-slate-700">Email</span>
              <IconInput
                icon={Mail}
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@ampindiafoundation.org"
              />
              {error ? <span className="text-xs font-medium text-red-600">{error}</span> : null}
            </label>

            <Button type="submit" className="w-full" size="lg" loading={loading}>
              Send reset link
            </Button>
          </form>
        )}
      </motion.div>
    </div>
  );
}
