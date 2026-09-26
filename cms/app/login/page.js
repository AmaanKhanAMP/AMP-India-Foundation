"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Eye, EyeOff, Lock, Mail, RefreshCw, ShieldCheck } from "lucide-react";
import Button from "@/components/ui/Button";
import IconInput from "@/components/ui/IconInput";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/contexts/ToastContext";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const onSubmit = async (e) => {
    e.preventDefault();
    const nextErrors = {};
    if (!email.trim()) nextErrors.email = "Email is required.";
    if (!password) nextErrors.password = "Password is required.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setLoading(true);
    try {
      await login({ email: email.trim(), password, remember });
      toast.success("Welcome back.");
      const next = searchParams.get("next") || "/dashboard";
      router.replace(next);
    } catch (err) {
      toast.error(err.response?.data?.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.2),_transparent_42%),radial-gradient(circle_at_bottom_right,_rgba(15,23,42,0.08),_transparent_40%)]" />
      <div className="pointer-events-none absolute inset-0 opacity-[0.35] [background-image:linear-gradient(rgba(15,23,42,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(15,23,42,0.03)_1px,transparent_1px)] [background-size:28px_28px]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 grid w-full max-w-4xl overflow-hidden rounded-[1.75rem] border border-slate-200/80 bg-white shadow-[var(--shadow-lg)] lg:grid-cols-2"
      >
        <div className="relative hidden min-h-[580px] overflow-hidden bg-gradient-to-br from-[#2F5FEA] via-[#1E4FD8] to-[#173A9B] px-9 py-11 text-white lg:flex lg:items-center">
          {/* Subtle depth */}
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_10%_15%,rgba(255,255,255,0.16),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_90%_90%,rgba(23,58,155,0.55),transparent_55%)]" />
            <div className="absolute -right-16 -top-10 h-72 w-72 rounded-full border border-white/[0.08]" />
            <div className="absolute -right-6 top-8 h-48 w-48 rounded-full border border-white/[0.05]" />
            <div className="absolute bottom-16 left-8 h-40 w-40 rounded-full bg-[#60A5FA]/15 blur-[80px]" />
          </div>

          <div className="relative z-[1] w-full">
            {/* Logo — compact white card, left aligned */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="inline-flex items-center justify-center self-start rounded-[18px] border border-black/[0.06] bg-white p-5 shadow-[0_12px_32px_rgba(15,23,42,0.22)]"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/brand/logo.png"
                alt="AMP India Foundation"
                className="h-12 w-auto max-w-[150px] object-contain object-center"
              />
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.06, ease: "easeOut" }}
              className="font-display mt-7 text-left text-[40px] font-bold leading-none tracking-[-0.03em] text-white"
            >
              AIF CMS
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1, ease: "easeOut" }}
              className="mt-3.5 max-w-[340px] text-left text-[18px] leading-[1.7] text-[#E8EEF9]"
            >
              Manage the AMP India Foundation website through a secure, modern Content Management
              System.
            </motion.p>

            {/* Stacked horizontal glass feature cards */}
            <div className="mt-8 flex w-full max-w-[340px] flex-col gap-5">
              {[
                {
                  icon: ShieldCheck,
                  title: "JWT-secured admin access",
                  detail: "Only authorized administrators can access the CMS.",
                },
                {
                  icon: RefreshCw,
                  title: "Live website content sync",
                  detail: "Content updates appear instantly on the website.",
                },
              ].map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.16 + index * 0.08, ease: "easeOut" }}
                    className="group flex h-[100px] w-full cursor-default items-center gap-4 rounded-[18px] border border-white/15 bg-[#173A9B]/35 px-6 py-5 shadow-[0_8px_24px_rgba(15,23,42,0.18)] backdrop-blur-md transition duration-300 hover:-translate-y-0.5 hover:border-white/25 hover:bg-[#173A9B]/45 hover:shadow-[0_14px_32px_rgba(15,23,42,0.28)]"
                  >
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/20 bg-white/10 text-white transition duration-300 group-hover:border-white/30 group-hover:bg-white/15">
                      <Icon className="h-5 w-5" strokeWidth={1.75} />
                    </span>
                    <div className="min-w-0 text-left">
                      <p className="text-[13px] font-semibold leading-snug tracking-wide text-white">
                        {feature.title}
                      </p>
                      <p className="mt-1 text-[12px] leading-relaxed text-[#E8EEF9]/80">
                        {feature.detail}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="flex min-h-[580px] flex-col justify-center p-8 sm:p-10 lg:p-12">
          <div className="mb-10">
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[var(--primary)]">
              AMP India Foundation
            </p>
            <h1 className="font-display mt-3 text-2xl font-extrabold text-slate-900">
              Sign in to CMS
            </h1>
            <p className="mt-2.5 text-sm text-slate-500">Use your admin credentials to continue.</p>
          </div>

          <form onSubmit={onSubmit} className="space-y-5">
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
              {errors.email ? (
                <span className="text-xs font-medium text-red-600">{errors.email}</span>
              ) : null}
            </label>

            <label className="block space-y-1.5">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[13px] font-semibold text-slate-700">Password</span>
                <Link
                  href="/forgot-password"
                  className="text-xs font-semibold text-[var(--primary)] hover:underline"
                >
                  Forgot Password?
                </Link>
              </div>
              <IconInput
                icon={Lock}
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                rightSlot={
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
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

            <label className="flex items-center gap-2.5 text-sm font-medium text-slate-600">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-[var(--primary)]"
              />
              Remember me for 30 days
            </label>

            <Button type="submit" className="mt-3 w-full" size="lg" loading={loading}>
              Sign in
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
          Loading…
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
