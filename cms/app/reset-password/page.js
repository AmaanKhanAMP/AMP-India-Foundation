"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, Eye, EyeOff, Lock } from "lucide-react";
import Button from "@/components/ui/Button";
import IconInput from "@/components/ui/IconInput";
import { useToast } from "@/contexts/ToastContext";
import authService from "@/services/authService";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const toast = useToast();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    const next = {};
    if (!token) next.token = "Reset token is missing. Request a new link.";
    if (!password || password.length < 8) {
      next.password = "Password must be at least 8 characters.";
    }
    if (password !== confirm) next.confirm = "Passwords do not match.";
    setErrors(next);
    if (Object.keys(next).length) return;

    setLoading(true);
    try {
      await authService.resetPassword({ token, new_password: password });
      toast.success("Password reset successfully. Please sign in.");
      router.replace("/login");
    } catch (err) {
      toast.error(err.response?.data?.message || "Unable to reset password.");
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
          Set new password
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-slate-500">
          Choose a strong password with at least 8 characters.
        </p>

        {!token ? (
          <div className="mt-8 rounded-2xl border border-amber-100 bg-amber-50 p-4 text-sm text-amber-800">
            This reset link is invalid.{" "}
            <Link href="/forgot-password" className="font-semibold underline">
              Request a new one
            </Link>
            .
          </div>
        ) : (
          <form onSubmit={onSubmit} className="mt-8 space-y-4">
            <label className="block space-y-1.5">
              <span className="text-[13px] font-semibold text-slate-700">New password</span>
              <IconInput
                icon={Lock}
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                rightSlot={
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="rounded-md p-1 text-slate-400 hover:bg-slate-100"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                }
              />
              {errors.password ? (
                <span className="text-xs font-medium text-red-600">{errors.password}</span>
              ) : null}
            </label>

            <label className="block space-y-1.5">
              <span className="text-[13px] font-semibold text-slate-700">Confirm password</span>
              <IconInput
                icon={Lock}
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="••••••••"
              />
              {errors.confirm ? (
                <span className="text-xs font-medium text-red-600">{errors.confirm}</span>
              ) : null}
              {errors.token ? (
                <span className="text-xs font-medium text-red-600">{errors.token}</span>
              ) : null}
            </label>

            <Button type="submit" className="w-full" size="lg" loading={loading}>
              Reset password
            </Button>
          </form>
        )}
      </motion.div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
          Loading…
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}
