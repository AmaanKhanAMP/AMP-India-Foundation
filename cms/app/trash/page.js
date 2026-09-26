"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { RotateCcw, Trash2 } from "lucide-react";
import AdminLayout from "@/layouts/AdminLayout";
import PageHeader from "@/components/common/PageHeader";
import Surface from "@/components/common/Surface";
import EmptyState from "@/components/common/EmptyState";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import Button from "@/components/ui/Button";
import StatusBadge from "@/components/ui/StatusBadge";
import SearchInput from "@/components/ui/SearchInput";
import Select from "@/components/ui/Select";
import { ConfirmDialog } from "@/components/ui/Modal";
import trashService from "@/services/trashService";
import { notifySiteRevalidate } from "@/lib/notifySiteRevalidate";
import { useToast } from "@/contexts/ToastContext";
import { resolveImageUrl } from "@/utils/imageUrl";
import { RESOURCES } from "@/utils/constants";

const MODULE_OPTIONS = [
  { value: "", label: "All modules" },
  { value: RESOURCES.HERO_BANNERS, label: "Hero Banners" },
  { value: RESOURCES.HOME_PROJECTS, label: "Home Projects" },
  { value: RESOURCES.HOME_GALLERY, label: "Photo Gallery" },
  { value: RESOURCES.HOME_EVENTS, label: "Home Events" },
  { value: RESOURCES.TESTIMONIALS, label: "Testimonials" },
  { value: RESOURCES.FEATURED_EVENTS, label: "Featured Events" },
  { value: RESOURCES.UPCOMING_EVENTS, label: "Upcoming Events" },
  { value: RESOURCES.PAST_EVENTS, label: "Past Events" },
  { value: RESOURCES.NAVBAR_ITEMS, label: "Navbar" },
  { value: RESOURCES.FOOTER_LINKS, label: "Footer Links" },
  { value: RESOURCES.FOOTER_FOCUS, label: "Footer Focus" },
];

const SORT_OPTIONS = [
  { value: "deleted_at_desc", label: "Newest deleted" },
  { value: "deleted_at_asc", label: "Oldest deleted" },
];

function formatWhen(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

export default function TrashPage() {
  const toast = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [moduleFilter, setModuleFilter] = useState("");
  const [sort, setSort] = useState("deleted_at_desc");
  const [busyKey, setBusyKey] = useState(null);
  const [purge, setPurge] = useState({ open: false, item: null });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await trashService.list({
        search: search.trim() || undefined,
        module: moduleFilter || undefined,
        sort,
      });
      setItems(res.data || []);
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to load Trash.");
    } finally {
      setLoading(false);
    }
  }, [search, moduleFilter, sort]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(load, 200);
    return () => clearTimeout(t);
  }, [load]);

  const handleRestore = async (item) => {
    const key = `${item.resource}-${item.id}-restore`;
    setBusyKey(key);
    try {
      await trashService.restore(item.resource, item.id);
      await notifySiteRevalidate(item.resource);
      toast.success("Restored to original module.");
      setItems((prev) => prev.filter((r) => !(r.resource === item.resource && r.id === item.id)));
    } catch (err) {
      toast.error(err.response?.data?.message || "Restore failed.");
    } finally {
      setBusyKey(null);
    }
  };

  const handlePermanent = async () => {
    const item = purge.item;
    if (!item) return;
    const key = `${item.resource}-${item.id}-purge`;
    setBusyKey(key);
    try {
      await trashService.permanentDelete(item.resource, item.id);
      await notifySiteRevalidate(item.resource);
      toast.success("Permanently deleted.");
      setPurge({ open: false, item: null });
      setItems((prev) => prev.filter((r) => !(r.resource === item.resource && r.id === item.id)));
    } catch (err) {
      toast.error(err.response?.data?.message || "Permanent delete failed.");
    } finally {
      setBusyKey(null);
    }
  };

  const countLabel = useMemo(() => {
    if (loading) return "Loading…";
    return `${items.length} item${items.length === 1 ? "" : "s"} in Trash`;
  }, [items.length, loading]);

  return (
    <AdminLayout breadcrumbs={[{ label: "Trash" }]}>
      <PageHeader
        title="Trash"
        description="Soft-deleted content from all modules. Restore anytime, or permanently delete."
      />

      <Surface className="mb-6 p-4 sm:p-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          <div className="min-w-0 flex-1">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Search by title, module, or admin…"
            />
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Select
              value={moduleFilter}
              onChange={(e) => setModuleFilter(e.target.value)}
              className="min-w-[180px]"
              options={MODULE_OPTIONS}
            />
            <Select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="min-w-[180px]"
              options={SORT_OPTIONS}
            />
          </div>
        </div>
        <p className="mt-3 text-xs font-medium text-slate-500">{countLabel}</p>
      </Surface>

      {loading ? (
        <LoadingSkeleton rows={4} variant="cards" />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Trash2}
          title="Trash is empty"
          description="Deleted items from any module will appear here until restored or permanently removed."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => {
            const restoreBusy = busyKey === `${item.resource}-${item.id}-restore`;
            const purgeBusy = busyKey === `${item.resource}-${item.id}-purge`;
            return (
              <motion.article
                key={`${item.resource}-${item.id}`}
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="overflow-hidden rounded-[20px] border border-[#E2E8F0] bg-white shadow-[var(--shadow-sm)] transition hover:shadow-[var(--shadow-md)]"
              >
                <div className="relative aspect-[16/10] overflow-hidden bg-slate-100">
                  {item.thumbnail ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={resolveImageUrl(item.thumbnail)}
                      alt=""
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-slate-300">
                      <Trash2 className="h-10 w-10" />
                    </div>
                  )}
                  <div className="absolute left-3 top-3">
                    <span className="rounded-full bg-white/95 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-slate-700 shadow-sm ring-1 ring-slate-200">
                      {item.module}
                    </span>
                  </div>
                </div>

                <div className="space-y-3 p-4">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-display line-clamp-2 text-sm font-bold text-[#111827]">
                      {item.title}
                    </h3>
                    <StatusBadge status={item.status} />
                  </div>

                  <div className="space-y-1 text-xs text-slate-500">
                    <p>
                      Deleted by{" "}
                      <span className="font-semibold text-slate-700">
                        {item.deleted_by_name || "Unknown"}
                      </span>
                    </p>
                    <p>{formatWhen(item.deleted_at)}</p>
                  </div>

                  <div className="flex gap-2 border-t border-[#E2E8F0] pt-3">
                    <Button
                      variant="secondary"
                      size="sm"
                      className="flex-1"
                      loading={restoreBusy}
                      onClick={() => handleRestore(item)}
                    >
                      <RotateCcw className="h-3.5 w-3.5" />
                      Restore
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      className="flex-1"
                      disabled={purgeBusy}
                      onClick={() => setPurge({ open: true, item })}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      Delete
                    </Button>
                  </div>
                </div>
              </motion.article>
            );
          })}
        </div>
      )}

      <ConfirmDialog
        open={purge.open}
        onClose={() => setPurge({ open: false, item: null })}
        onConfirm={handlePermanent}
        title="Permanently delete?"
        message="This cannot be undone. The record will be removed from the database, and unused uploaded files will be deleted."
        confirmLabel="Permanently delete"
        danger
        loading={Boolean(purge.item && busyKey === `${purge.item.resource}-${purge.item.id}-purge`)}
      />
    </AdminLayout>
  );
}
