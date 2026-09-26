"use client";

import { useCallback, useEffect, useState } from "react";
import AdminLayout from "@/layouts/AdminLayout";
import FormShell from "@/components/common/FormShell";
import Input from "@/components/ui/Input";
import Textarea from "@/components/ui/Textarea";
import LoadingSkeleton, { Skeleton } from "@/components/common/LoadingSkeleton";
import {
  getFooterSettings,
  updateFooterSettings,
} from "@/services/layoutService";
import { notifySiteRevalidate } from "@/lib/notifySiteRevalidate";
import { useToast } from "@/contexts/ToastContext";

const SECTIONS = [
  {
    title: "Top CTA bar",
    fields: [
      { name: "cta_heading", label: "CTA heading", type: "textarea", full: true, max: 160, rows: 2 },
      { name: "cta_button_text", label: "CTA button text", max: 40 },
      { name: "cta_button_link", label: "CTA button link", max: 500 },
    ],
  },
  {
    title: "About column",
    fields: [
      { name: "about_heading", label: "About heading", max: 40 },
      { name: "about_link_text", label: "About link text", max: 40 },
      { name: "about_text", label: "About text", type: "textarea", full: true, max: 600, rows: 3 },
      { name: "about_link_href", label: "About link URL", max: 500, full: true },
    ],
  },
  {
    title: "Column headings",
    fields: [
      { name: "useful_links_heading", label: "Useful links heading", max: 40 },
      { name: "recent_focus_heading", label: "Recent focus heading", max: 40 },
      { name: "contact_heading", label: "Contact heading", max: 40 },
      { name: "follow_heading", label: "Follow us heading", max: 40 },
    ],
  },
  {
    title: "Contact details",
    fields: [
      { name: "address_label", label: "Address label", max: 40 },
      { name: "phone_label", label: "Phone label", max: 40 },
      { name: "address_text", label: "Address", type: "textarea", full: true, max: 200, rows: 2 },
      { name: "phone_text", label: "Phone number", max: 40 },
      { name: "email_label", label: "Email label", max: 40 },
      { name: "email_text", label: "Email address", max: 120 },
    ],
  },
  {
    title: "Social & copyright",
    fields: [
      { name: "facebook_url", label: "Facebook URL", max: 500 },
      { name: "instagram_url", label: "Instagram URL", max: 500 },
      { name: "copyright_text", label: "Copyright text", max: 255 },
      { name: "copyright_highlight", label: "Copyright highlight", max: 120 },
    ],
  },
];

const ALL_FIELDS = SECTIONS.flatMap((section) => section.fields);

function FieldBlock({ field, form, errors, setField }) {
  if (field.type === "textarea") {
    return (
      <div className={field.full ? "md:col-span-2" : undefined}>
        <Textarea
          label={field.label}
          name={field.name}
          value={form[field.name] || ""}
          onChange={(e) => setField(field.name, e.target.value, field.max)}
          error={errors[field.name]}
          rows={field.rows || 2}
          maxLength={field.max}
        />
      </div>
    );
  }
  return (
    <div className={field.full ? "md:col-span-2" : undefined}>
      <Input
        label={field.label}
        name={field.name}
        value={form[field.name] || ""}
        onChange={(e) => setField(field.name, e.target.value, field.max)}
        error={errors[field.name]}
        maxLength={field.max}
        showCounter={field.max < 200}
      />
    </div>
  );
}

export default function FooterSettingsPage() {
  const toast = useToast();
  const [form, setForm] = useState({});
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getFooterSettings();
      setForm(res.data || {});
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to load footer settings.");
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    load();
  }, [load]);

  const setField = (key, value, max) => {
    let next = value;
    if (max != null && typeof next === "string" && next.length > max) {
      next = next.slice(0, max);
    }
    setForm((prev) => ({ ...prev, [key]: next }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const onSubmit = async () => {
    setSaving(true);
    try {
      const payload = {};
      ALL_FIELDS.forEach((f) => {
        payload[f.name] = form[f.name] ?? "";
      });
      const res = await updateFooterSettings(payload);
      await notifySiteRevalidate("layout-footer");
      setForm(res.data || payload);
      setErrors({});
      toast.success(res.message || "Footer settings saved.");
    } catch (err) {
      const data = err.response?.data;
      if (data?.errors) setErrors(data.errors);
      toast.error(data?.message || "Save failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AdminLayout
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Footer", href: "/site/footer" },
      ]}
    >
      {loading ? (
        <div className="mx-auto max-w-5xl space-y-4">
          <Skeleton className="h-8 w-64" />
          <LoadingSkeleton rows={3} />
        </div>
      ) : (
        <FormShell
          title="Footer"
          description="Edit CTA, about, contact, social, and copyright. Useful Links and Recent Focus are in the submenu."
          onSubmit={onSubmit}
          onCancel={() => load()}
          loading={saving}
          submitLabel="Save footer"
          dense
          wide
        >
          <div className="space-y-4">
            {SECTIONS.map((section) => (
              <section
                key={section.title}
                className="rounded-xl border border-slate-100 bg-slate-50/60 p-3 sm:p-3.5"
              >
                <h3 className="mb-2.5 text-xs font-bold uppercase tracking-wide text-slate-500">
                  {section.title}
                </h3>
                <div className="grid gap-3 md:grid-cols-2">
                  {section.fields.map((field) => (
                    <FieldBlock
                      key={field.name}
                      field={field}
                      form={form}
                      errors={errors}
                      setField={setField}
                    />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </FormShell>
      )}
    </AdminLayout>
  );
}
