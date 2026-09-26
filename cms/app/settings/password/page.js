"use client";

import { useState } from "react";
import AdminLayout from "@/layouts/AdminLayout";
import PageHeader from "@/components/common/PageHeader";
import FormShell from "@/components/common/FormShell";
import Input from "@/components/ui/Input";
import { useToast } from "@/contexts/ToastContext";
import authService from "@/services/authService";

export default function PasswordSettingsPage() {
  const toast = useToast();
  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    const next = {};
    if (!form.current_password) next.current_password = "Current password is required.";
    if (!form.new_password || form.new_password.length < 8) {
      next.new_password = "New password must be at least 8 characters.";
    }
    if (form.new_password !== form.confirm_password) {
      next.confirm_password = "Passwords do not match.";
    }
    setErrors(next);
    if (Object.keys(next).length) return;

    setLoading(true);
    try {
      await authService.changePassword({
        current_password: form.current_password,
        new_password: form.new_password,
      });
      toast.success("Password updated.");
      setForm({ current_password: "", new_password: "", confirm_password: "" });
    } catch (err) {
      toast.error(err.response?.data?.message || "Update failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminLayout
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Settings" },
        { label: "Change Password" },
      ]}
    >
      <PageHeader
        title="Change password"
        description="Keep your admin account secure with a strong password."
      />
      <FormShell
        title="Security"
        description="Use a strong password of at least 8 characters."
        onSubmit={onSubmit}
        loading={loading}
        submitLabel="Update password"
      >
        <div className="mx-auto grid max-w-lg gap-5">
          <Input
            label="Current password"
            type="password"
            value={form.current_password}
            onChange={(e) => setForm((f) => ({ ...f, current_password: e.target.value }))}
            error={errors.current_password}
          />
          <Input
            label="New password"
            type="password"
            value={form.new_password}
            onChange={(e) => setForm((f) => ({ ...f, new_password: e.target.value }))}
            error={errors.new_password}
          />
          <Input
            label="Confirm new password"
            type="password"
            value={form.confirm_password}
            onChange={(e) => setForm((f) => ({ ...f, confirm_password: e.target.value }))}
            error={errors.confirm_password}
          />
        </div>
      </FormShell>
    </AdminLayout>
  );
}
