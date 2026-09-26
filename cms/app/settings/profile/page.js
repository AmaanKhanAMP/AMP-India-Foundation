"use client";

import { useEffect, useRef, useState } from "react";
import { User } from "lucide-react";
import AdminLayout from "@/layouts/AdminLayout";
import PageHeader from "@/components/common/PageHeader";
import FormShell from "@/components/common/FormShell";
import Input from "@/components/ui/Input";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/contexts/ToastContext";
import authService from "@/services/authService";

function normalizeEmail(value) {
  return String(value || "")
    .trim()
    .toLowerCase();
}

export default function ProfileSettingsPage() {
  const { user, setUser } = useAuth();
  const toast = useToast();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Server baseline — updated only when admin id loads or after a successful save.
  const baselineEmailRef = useRef("");

  useEffect(() => {
    if (!user?.id) return;
    baselineEmailRef.current = normalizeEmail(user.email);
    setName(user.name || "");
    setEmail(user.email || "");
    setCurrentPassword("");
    setErrors({});
  }, [user?.id]);

  const emailChanged = normalizeEmail(email) !== baselineEmailRef.current;
  const saveDisabled = emailChanged && !String(currentPassword).trim();

  const onSubmit = async () => {
    const nextErrors = {};
    if (!name.trim()) nextErrors.name = "Name is required.";
    if (!email.trim()) nextErrors.email = "Email is required.";
    if (emailChanged && !String(currentPassword).trim()) {
      nextErrors.current_password = "Current password is required.";
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setLoading(true);
    try {
      const payload = {
        name: name.trim(),
        email: email.trim(),
      };
      if (emailChanged) {
        payload.current_password = currentPassword;
      }

      const res = await authService.updateProfile(payload);
      const admin = res.admin;
      setUser(admin);
      baselineEmailRef.current = normalizeEmail(admin.email);
      setName(admin.name || "");
      setEmail(admin.email || "");
      setCurrentPassword("");
      setErrors({});
      toast.success("Profile updated.");
    } catch (err) {
      const message = err.response?.data?.message || "Update failed.";
      toast.error(message);
      if (err.response?.status === 401 || /password/i.test(message)) {
        setErrors((prev) => ({ ...prev, current_password: message }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminLayout
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Settings" },
        { label: "Profile" },
      ]}
    >
      <PageHeader
        title="Profile"
        description="Manage how you appear inside the AIF CMS."
      />

      <div className="mb-6 flex items-center gap-4 rounded-[1.25rem] border border-slate-200/90 bg-white p-5 shadow-[var(--shadow-sm)]">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-hover)] text-white shadow-md shadow-blue-500/25">
          <User className="h-6 w-6" />
        </div>
        <div>
          <p className="font-display text-lg font-bold text-slate-900">
            {user?.name || "Admin"}
          </p>
          <p className="text-sm text-slate-500">{user?.email}</p>
          {user?.role ? (
            <p className="mt-1 text-xs font-bold uppercase tracking-wide text-[var(--primary)]">
              {user.role}
            </p>
          ) : null}
        </div>
      </div>

      <FormShell
        title="Account details"
        description="Update your admin display name and email."
        onSubmit={onSubmit}
        loading={loading}
        submitDisabled={saveDisabled}
        submitLabel="Save profile"
      >
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={errors.name}
          />
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => {
              const value = e.target.value;
              setEmail(value);
              if (normalizeEmail(value) === baselineEmailRef.current) {
                setCurrentPassword("");
                setErrors((prev) => {
                  const { current_password: _drop, ...rest } = prev;
                  return rest;
                });
              }
            }}
            error={errors.email}
          />
        </div>

        {emailChanged ? (
          <Input
            label="Current Password *"
            type="password"
            name="current_password"
            autoComplete="current-password"
            value={currentPassword}
            onChange={(e) => {
              setCurrentPassword(e.target.value);
              if (errors.current_password) {
                setErrors((prev) => {
                  const { current_password: _drop, ...rest } = prev;
                  return rest;
                });
              }
            }}
            error={errors.current_password}
          />
        ) : null}
      </FormShell>
    </AdminLayout>
  );
}
