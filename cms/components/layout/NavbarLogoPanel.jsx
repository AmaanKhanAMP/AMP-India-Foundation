"use client";

import { useCallback, useEffect, useState } from "react";
import ImageUpload from "@/components/ui/ImageUpload";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import {
  getNavbarSettings,
  updateNavbarSettings,
} from "@/services/layoutService";
import { notifySiteRevalidate } from "@/lib/notifySiteRevalidate";
import { useToast } from "@/contexts/ToastContext";

const DEFAULTS = {
  logo_url: "/assets/logo.png",
  logo_alt: "AMP Logo",
  logo_link: "/",
};

export default function NavbarLogoPanel() {
  const toast = useToast();
  const [form, setForm] = useState(DEFAULTS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getNavbarSettings();
      setForm({ ...DEFAULTS, ...(res.data || {}) });
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to load navbar logo.");
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    load();
  }, [load]);

  const setField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const onSave = async () => {
    setSaving(true);
    try {
      const res = await updateNavbarSettings({
        logo_url: form.logo_url,
        logo_alt: form.logo_alt,
        logo_link: form.logo_link,
      });
      setForm({ ...DEFAULTS, ...(res.data || {}) });
      await notifySiteRevalidate("layout-navbar");
      toast.success(res.message || "Navbar logo saved.");
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to save navbar logo.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mb-4 rounded-2xl border border-slate-200/80 bg-white p-3.5 shadow-sm sm:p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="min-w-0">
          <p className="text-sm font-bold text-slate-900">Website Logo</p>
          <p className="mt-0.5 text-xs text-slate-500">
            Logo shown in the site navbar. Upload to replace the default asset.
          </p>
        </div>
        <Button
          size="sm"
          onClick={onSave}
          loading={saving || loading}
          disabled={loading}
        >
          Save logo
        </Button>
      </div>

      <div className="grid gap-3 md:grid-cols-[220px_minmax(0,1fr)] md:items-start">
        <ImageUpload
          label="Logo image"
          value={form.logo_url || ""}
          onChange={(url) => setField("logo_url", url)}
          folder="navbar"
          aspect="logo"
        />
        <div className="grid gap-3 sm:grid-cols-2">
          <Input
            label="Logo alt text"
            value={form.logo_alt || ""}
            onChange={(e) => setField("logo_alt", e.target.value)}
            maxLength={120}
          />
          <Input
            label="Logo link"
            value={form.logo_link || ""}
            onChange={(e) => setField("logo_link", e.target.value)}
            placeholder="/"
            maxLength={500}
            showCounter={false}
          />
        </div>
      </div>
    </div>
  );
}
