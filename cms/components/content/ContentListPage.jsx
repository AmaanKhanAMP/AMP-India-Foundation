"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Plus, Sparkles } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import AdminLayout from "@/layouts/AdminLayout";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import BannerCard, { ContentCard } from "@/components/common/BannerCard";
import Button from "@/components/ui/Button";
import SearchInput from "@/components/ui/SearchInput";
import Modal, { ConfirmDialog } from "@/components/ui/Modal";
import StatusBadge from "@/components/ui/StatusBadge";
import { createContentService } from "@/services/contentService";
import { notifySiteRevalidate } from "@/lib/notifySiteRevalidate";
import { useToast } from "@/contexts/ToastContext";
import { resolveImageUrl } from "@/utils/imageUrl";

function matchesSearch(item, query) {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const haystack = [
    item.title,
    item.name,
    item.label,
    item.alt_text,
    item.href,
    item.subtitle,
    item.description,
    item.message,
    item.venue,
    item.event_date,
    item.date_label,
    item.designation,
    item.organisation,
    item.location,
    item.status,
    item.primary_btn_text,
    item.button_text,
    item.item_type,
    item.parent_key,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return haystack.includes(q);
}

export default function ContentListPage({
  resource,
  title,
  description,
  basePath,
  breadcrumbs,
  imageKey = "image_url",
  titleKey = "title",
  large = false,
  hideImage = false,
  headerExtra = null,
}) {
  const router = useRouter();
  const toast = useToast();
  const service = createContentService(resource);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dragIndex, setDragIndex] = useState(null);
  const [confirm, setConfirm] = useState({ open: false, id: null });
  const [deleting, setDeleting] = useState(false);
  const [preview, setPreview] = useState(null);

  const load = useCallback(async (opts = {}) => {
    const silent = Boolean(opts.silent);
    if (!silent) setLoading(true);
    try {
      const res = await service.list();
      setItems(res.data || []);
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to load items.");
    } finally {
      if (!silent) setLoading(false);
    }
  }, [resource]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      return matchesSearch(item, search);
    });
  }, [items, search, statusFilter]);

  const statusCounts = useMemo(() => {
    const all = items.length;
    const published = items.filter((i) => i.status === "published").length;
    const draft = items.filter((i) => i.status === "draft").length;
    return { all, published, draft };
  }, [items]);

  const handleDuplicate = async (id) => {
    try {
      await service.duplicate(id);
      await notifySiteRevalidate(resource);
      toast.success("Duplicated.");
      load({ silent: true });
    } catch (err) {
      toast.error(err.response?.data?.message || "Duplicate failed.");
    }
  };

  const handleTogglePublish = async (item) => {
    const isPublished = String(item.status || "").toLowerCase() === "published";
    try {
      const res = isPublished
        ? await service.unpublish(item.id)
        : await service.publish(item.id);
      await notifySiteRevalidate(resource);
      const updated = res?.data;
      if (updated?.id != null) {
        setItems((prev) =>
          prev.map((row) => (row.id === item.id ? { ...row, ...updated } : row))
        );
        setPreview((prev) =>
          prev?.id === item.id ? { ...prev, ...updated } : prev
        );
      }
      await load({ silent: true });
      toast.success(isPublished ? "Unpublished." : "Published.");
    } catch (err) {
      toast.error(err.response?.data?.message || "Status update failed.");
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await service.remove(confirm.id);
      await notifySiteRevalidate(resource);
      toast.success("Moved to Trash.");
      setConfirm({ open: false, id: null });
      load();
    } catch (err) {
      toast.error(err.response?.data?.message || "Delete failed.");
    } finally {
      setDeleting(false);
    }
  };

  const onDrop = async (toIndex) => {
    if (dragIndex === null || dragIndex === toIndex) return;
    // Reorder within full list when not searching
    if (search.trim()) {
      toast.info("Clear search to reorder items.");
      setDragIndex(null);
      return;
    }
    const next = [...items];
    const [moved] = next.splice(dragIndex, 1);
    next.splice(toIndex, 0, moved);
    setItems(next);
    setDragIndex(null);
    try {
      await service.reorder(next.map((i) => i.id));
      await notifySiteRevalidate(resource);
      toast.success("Order saved.");
    } catch (err) {
      toast.error(err.response?.data?.message || "Reorder failed.");
      load();
    }
  };

  const Card = large ? BannerCard : ContentCard;

  return (
    <AdminLayout breadcrumbs={breadcrumbs}>
      <PageHeader
        title={title}
        description={description}
        className={hideImage ? "mb-5" : undefined}
        actions={
          <Link href={`${basePath}/new`}>
            <Button>
              <Plus className="h-4 w-4" />
              Add new
            </Button>
          </Link>
        }
      />

      {headerExtra}

      <div className={`mb-5 space-y-3 ${hideImage ? "mt-0" : ""}`}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder={`Search ${title.toLowerCase()}…`}
            className="max-w-md"
          />
          <p className="text-xs font-semibold text-slate-400">
            {filtered.length} of {items.length} items
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            { key: "all", label: `All (${statusCounts.all})` },
            { key: "published", label: `Published (${statusCounts.published})` },
            { key: "draft", label: `Drafts (${statusCounts.draft})` },
          ].map((chip) => (
            <button
              key={chip.key}
              type="button"
              onClick={() => setStatusFilter(chip.key)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-bold transition ${
                statusFilter === chip.key
                  ? "bg-[var(--primary)] text-white shadow-sm shadow-blue-500/25"
                  : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
              }`}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton rows={large ? 3 : 6} variant={large ? "banners" : "cards"} />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Sparkles}
          title={`No ${title.toLowerCase()} yet`}
          description="Import website content with the seed script, or create your first item."
          actionLabel="Add new"
          onAction={() => router.push(`${basePath}/new`)}
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No matches"
          description={`Nothing matched “${search}”. Try a different keyword.`}
          actionLabel="Clear search"
          onAction={() => setSearch("")}
        />
      ) : (
        <motion.div
          layout
          className={
            large
              ? "space-y-5"
              : hideImage
                ? "grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
                : "grid gap-5 sm:grid-cols-2 xl:grid-cols-3"
          }
        >
          <AnimatePresence mode="popLayout">
            {filtered.map((item, index) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.2 }}
              >
                <Card
                  item={item}
                  href={`${basePath}/${item.id}`}
                  imageKey={imageKey}
                  titleKey={titleKey}
                  hideImage={hideImage}
                  onPreview={hideImage ? undefined : () => setPreview(item)}
                  onDuplicate={() => handleDuplicate(item.id)}
                  onTogglePublish={() => handleTogglePublish(item)}
                  onDelete={() => setConfirm({ open: true, id: item.id })}
                  onDragStart={() => setDragIndex(index)}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={() => onDrop(index)}
                  draggable={!search.trim()}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      <Link
        href={`${basePath}/new`}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--primary)] text-white shadow-xl shadow-blue-500/35 transition hover:scale-105 hover:bg-[var(--primary-dark)]"
        aria-label="Add new"
      >
        <Plus className="h-6 w-6" />
      </Link>

      <ConfirmDialog
        open={confirm.open}
        onClose={() => setConfirm({ open: false, id: null })}
        onConfirm={handleDelete}
        title="Move to Trash?"
        message="This item will be moved to Trash. You can restore it later or permanently delete it from Trash."
        confirmLabel="Move to Trash"
        danger
        loading={deleting}
      />

      <Modal
        open={Boolean(preview)}
        onClose={() => setPreview(null)}
        title={preview?.[titleKey] || preview?.name || "Preview"}
        wide
      >
        {preview ? (
          <div className="space-y-4">
            {preview[imageKey] || preview.banner_image || preview.profile_image ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={resolveImageUrl(
                  preview[imageKey] || preview.banner_image || preview.profile_image
                )}
                alt=""
                className="max-h-80 w-full rounded-2xl object-cover ring-1 ring-slate-100"
              />
            ) : null}
            <div className="flex items-center gap-2">
              <StatusBadge status={preview.status} />
              <span className="text-xs font-medium text-slate-400">
                Order {preview.display_order}
              </span>
            </div>
            {preview.subtitle || preview.description || preview.message ? (
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
                {preview.subtitle || preview.description || preview.message}
              </p>
            ) : null}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="secondary" onClick={() => setPreview(null)}>
                Close
              </Button>
              <Link href={`${basePath}/${preview.id}`}>
                <Button>Edit</Button>
              </Link>
            </div>
          </div>
        ) : null}
      </Modal>
    </AdminLayout>
  );
}
