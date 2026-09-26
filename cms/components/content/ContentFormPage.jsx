"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import AdminLayout from "@/layouts/AdminLayout";
import FormShell from "@/components/common/FormShell";
import Input from "@/components/ui/Input";
import Textarea from "@/components/ui/Textarea";
import Select from "@/components/ui/Select";
import ImageUpload from "@/components/ui/ImageUpload";
import LoadingSkeleton, { Skeleton } from "@/components/common/LoadingSkeleton";
import { createContentService } from "@/services/contentService";
import { notifySiteRevalidate } from "@/lib/notifySiteRevalidate";
import { useToast } from "@/contexts/ToastContext";
import { STATUS_OPTIONS } from "@/utils/constants";
import { validateContentForm, withFieldLimits } from "@/utils/fieldLimits";

export default function ContentFormPage({
  resource,
  id,
  basePath,
  breadcrumbs,
  title,
  description,
  fields,
  folder,
  defaults = {},
}) {
  const router = useRouter();
  const toast = useToast();
  const service = createContentService(resource);
  const isNew = !id || id === "new";
  const [form, setForm] = useState({ status: "draft", ...defaults });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [dynamicOptions, setDynamicOptions] = useState({});

  // Hard block unused fields even if an old config/cache still lists them.
  const limitedFields = useMemo(() => {
    const blockedByResource = {
      "home-projects": new Set(["description", "button_text", "button_link"]),
      "hero-banners": new Set(["description"]),
      "home-events": new Set(["event_time"]),
      "featured-events": new Set(["registration_link"]),
      "upcoming-events": new Set(["event_time", "registration_link"]),
      "past-events": new Set(["event_time", "registration_link"]),
      "gallery-items": new Set(["event_time", "registration_link"]),
    };
    const blocked = blockedByResource[resource] || null;
    const next = withFieldLimits(resource, fields || []).filter(
      (field) => !blocked || !blocked.has(field.name)
    );
    return next;
  }, [resource, fields]);

  useEffect(() => {
    if (isNew) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await service.get(id);
        if (!cancelled) {
          const raw = { ...defaults, ...(res.data || {}) };
          // Drop unused keys so they never linger in form state / payloads.
          if (resource === "home-projects") {
            delete raw.description;
            delete raw.button_text;
            delete raw.button_link;
          }
          if (resource === "hero-banners") {
            delete raw.description;
          }
          if (resource === "home-events") {
            delete raw.event_time;
          }
          if (resource === "featured-events") {
            delete raw.registration_link;
          }
          if (
            resource === "upcoming-events" ||
            resource === "past-events" ||
            resource === "gallery-items"
          ) {
            delete raw.event_time;
            delete raw.registration_link;
          }
          setForm(raw);
        }
      } catch (err) {
        toast.error(err.response?.data?.message || "Failed to load item.");
        router.replace(basePath);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, isNew]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const optionFields = limitedFields.filter((f) => f.optionsResource);
    if (!optionFields.length) return;
    let cancelled = false;
    (async () => {
      const next = {};
      await Promise.all(
        optionFields.map(async (field) => {
          try {
            const svc = createContentService(field.optionsResource);
            const res = await svc.list();
            let items = res.data || [];
            if (typeof field.optionsFilter === "function") {
              items = items.filter(field.optionsFilter);
            }
            if (id && field.excludeSelf) {
              items = items.filter((item) => String(item.id) !== String(id));
            }
            const mapped = typeof field.optionsMap === "function"
              ? field.optionsMap(items)
              : items.map((item) => ({
                  value: item[field.optionsValueKey || "id"],
                  label: item[field.optionsLabelKey || "title"] || item.label || item.name,
                }));
            next[field.name] = [
              { value: "", label: field.optionsEmptyLabel || "— None —" },
              ...mapped.filter((opt) => opt.value != null && opt.value !== ""),
            ];
          } catch {
            next[field.name] = [
              { value: "", label: field.optionsEmptyLabel || "— None —" },
            ];
          }
        })
      );
      if (!cancelled) setDynamicOptions(next);
    })();
    return () => {
      cancelled = true;
    };
  }, [limitedFields, id]);

  const setField = (key, value) => {
    const field = limitedFields.find((f) => f.name === key);
    let next = value;
    if (
      field?.maxLength != null &&
      typeof next === "string" &&
      next.length > field.maxLength
    ) {
      next = next.slice(0, field.maxLength);
    }
    setForm((prev) => ({ ...prev, [key]: next }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const validate = () => {
    const next = validateContentForm(limitedFields, form);
    if (resource === "navbar-items" && form.item_type === "dropdown") {
      if (!String(form.item_key || "").trim()) {
        next.item_key = "Dropdown key is required for dropdown parents (e.g. projects).";
      }
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const onSubmit = async () => {
    if (!validate()) {
      toast.error("Please fix the highlighted fields.");
      return;
    }
    setSaving(true);
    try {
      const payload = {};
      limitedFields.forEach((f) => {
        let val = form[f.name];
        if (f.type === "number" && val !== "" && val != null) val = Number(val);
        if (
          (f.name === "parent_key" || f.name === "item_key") &&
          (val === "" || val == null)
        ) {
          val = null;
        }
        payload[f.name] = val;
      });
      if (isNew) await service.create(payload);
      else await service.update(id, payload);
      await notifySiteRevalidate(resource);
      toast.success(isNew ? "Created successfully." : "Saved successfully.");
      router.push(basePath);
    } catch (err) {
      const data = err.response?.data;
      if (data?.errors && typeof data.errors === "object") {
        setErrors(data.errors);
      }
      toast.error(data?.message || "Save failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AdminLayout breadcrumbs={breadcrumbs}>
      {loading ? (
        <div className="mx-auto max-w-4xl space-y-4">
          <Skeleton className="h-8 w-64" />
          <LoadingSkeleton rows={2} />
        </div>
      ) : (
        <FormShell
          title={title}
          description={description}
          onSubmit={onSubmit}
          onCancel={() => router.push(basePath)}
          loading={saving}
          submitLabel={isNew ? "Create" : "Save changes"}
        >
          <div className="grid gap-5 md:grid-cols-2">
            {limitedFields.map((field) => {
              if (field.type === "image") {
                return (
                  <div key={field.name} className={field.full ? "md:col-span-2" : ""}>
                    <ImageUpload
                      label={field.label}
                      value={form[field.name] || ""}
                      onChange={(url) => setField(field.name, url)}
                      folder={folder || resource}
                      aspect={field.aspect || "video"}
                    />
                    {errors[field.name] ? (
                      <p className="mt-1 text-xs text-red-600">{errors[field.name]}</p>
                    ) : null}
                  </div>
                );
              }
              if (field.type === "textarea") {
                return (
                  <div key={field.name} className="md:col-span-2">
                    <Textarea
                      label={field.label}
                      name={field.name}
                      value={form[field.name] || ""}
                      onChange={(e) => setField(field.name, e.target.value)}
                      error={errors[field.name]}
                      hint={field.hint}
                      rows={field.rows || 4}
                      maxLength={field.maxLength}
                    />
                  </div>
                );
              }
              if (field.type === "select") {
                const options =
                  dynamicOptions[field.name] || field.options || STATUS_OPTIONS;
                return (
                  <div
                    key={field.name}
                    className={`space-y-1 ${field.full ? "md:col-span-2" : ""}`}
                  >
                    <Select
                      label={field.label}
                      name={field.name}
                      value={form[field.name] ?? ""}
                      onChange={(e) => setField(field.name, e.target.value)}
                      options={options}
                      error={errors[field.name]}
                    />
                    {field.hint ? (
                      <p className="text-xs text-slate-400">{field.hint}</p>
                    ) : null}
                  </div>
                );
              }
              return (
                <div
                  key={field.name}
                  className={field.full ? "md:col-span-2" : undefined}
                >
                  <Input
                    label={field.label}
                    name={field.name}
                    type={field.type || "text"}
                    value={form[field.name] ?? ""}
                    onChange={(e) => setField(field.name, e.target.value)}
                    error={errors[field.name]}
                    placeholder={field.placeholder}
                    hint={field.hint}
                    maxLength={field.maxLength}
                    showCounter={field.type !== "number"}
                  />
                </div>
              );
            })}
          </div>
        </FormShell>
      )}
    </AdminLayout>
  );
}
