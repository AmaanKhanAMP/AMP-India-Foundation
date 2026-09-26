"use client";

import { useCallback, useEffect, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import Switch from "@/components/ui/Switch";
import {
  getSectionVisibility,
  updateSectionVisibility,
} from "@/services/sectionVisibilityService";
import { notifySiteRevalidate } from "@/lib/notifySiteRevalidate";
import { useToast } from "@/contexts/ToastContext";

/**
 * Reusable Hide/Show Section control for CMS list pages.
 * @param {string} sectionName - DB key, e.g. "upcoming_events"
 * @param {string} sectionLabel - Human label for toasts / copy
 */
export default function SectionVisibilityPanel({
  sectionName,
  sectionLabel = "Section",
}) {
  const toast = useToast();
  const [visible, setVisible] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getSectionVisibility(sectionName);
      setVisible(Boolean(res?.data?.is_visible));
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to load section visibility.");
    } finally {
      setLoading(false);
    }
  }, [sectionName]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    load();
  }, [load]);

  const handleToggle = async (next) => {
    const previous = visible;
    setVisible(next);
    setSaving(true);
    try {
      const res = await updateSectionVisibility(sectionName, next);
      await notifySiteRevalidate(`section-${sectionName}`);
      toast.success(
        res?.message ||
          (next
            ? `${sectionLabel} section is now visible.`
            : `${sectionLabel} section hidden successfully.`)
      );
    } catch (err) {
      setVisible(previous);
      toast.error(err.response?.data?.message || "Failed to update visibility.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mb-5 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm sm:p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <div
            className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
              visible
                ? "bg-emerald-50 text-emerald-600"
                : "bg-slate-100 text-slate-500"
            }`}
          >
            {visible ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900">Section Visibility</p>
            <p className="mt-0.5 text-xs leading-relaxed text-slate-500">
              Control whether the entire {sectionLabel} section appears on the website.
              Event records are never deleted.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 sm:shrink-0">
          <div className="text-right">
            <p
              className={`text-xs font-bold ${
                visible ? "text-emerald-600" : "text-slate-500"
              }`}
            >
              {loading ? "Loading…" : visible ? "Visible" : "Hidden"}
            </p>
            <p className="text-[11px] font-medium text-slate-400">
              {visible ? "Show Section" : "Hide Section"}
            </p>
          </div>
          <Switch
            checked={visible}
            onChange={handleToggle}
            disabled={loading || saving}
            label={`${sectionLabel} section visibility`}
          />
        </div>
      </div>
    </div>
  );
}
