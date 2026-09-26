"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Copy, Eye, EyeOff, GripVertical, Pencil, Trash2 } from "lucide-react";
import StatusBadge from "@/components/ui/StatusBadge";
import { resolveImageUrl } from "@/utils/imageUrl";
import { cn } from "@/utils/cn";

function formatDate(value) {
  if (!value) return null;
  try {
    return new Date(value).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return null;
  }
}

function ActionButton({ onClick, href, label, danger, children }) {
  const className = cn("cms-action", danger && "cms-action--danger");
  if (href) {
    return (
      <Link href={href} className={className} aria-label={label} title={label}>
        {children}
      </Link>
    );
  }
  return (
    <button type="button" onClick={onClick} className={className} aria-label={label} title={label}>
      {children}
    </button>
  );
}

export default function BannerCard({
  item,
  href,
  imageKey = "image_url",
  titleKey = "title",
  hideImage = false,
  onDelete,
  onDuplicate,
  onTogglePublish,
  onPreview,
  onDragStart,
  onDragOver,
  onDrop,
  draggable = true,
  className,
}) {
  const image = hideImage ? null : item[imageKey];
  const title = item[titleKey] || item.name || "Untitled";
  const subtitle = item.subtitle || item.description || item.message || item.href;
  const ctaText = item.primary_btn_text || item.button_text;
  const ctaLink = item.primary_btn_link || item.button_link || item.registration_link;
  const created = formatDate(item.created_at);
  const updated = formatDate(item.updated_at);
  const metaBits = [
    item.item_type === "dropdown" ? "Dropdown" : null,
    item.parent_key ? `Child of ${item.parent_key}` : null,
    item.date_label || null,
    item.event_date,
    item.venue,
    item.designation,
  ].filter(Boolean);

  return (
    <motion.article
      layout
      whileHover={{ y: -5 }}
      transition={{ type: "spring", stiffness: 380, damping: 28 }}
      draggable={draggable}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDrop={onDrop}
      className={cn(
        "group overflow-hidden rounded-[20px] border border-[#E2E8F0] bg-white shadow-[var(--shadow-sm)] transition-shadow duration-300 hover:shadow-[var(--shadow-md)]",
        className
      )}
    >
      {!hideImage ? (
        <div className="relative aspect-[21/9] overflow-hidden bg-slate-100">
          {image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={resolveImageUrl(image)}
              alt={title}
              className="h-full w-full object-cover transition duration-700 ease-out group-hover:scale-[1.07]"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-slate-400">
              No image
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-[#111827]/65 via-[#111827]/10 to-transparent" />
          <div className="absolute left-3.5 top-3.5 flex items-center gap-2">
            {draggable ? (
              <span className="cursor-grab rounded-xl bg-white/95 p-1.5 text-slate-500 shadow-sm backdrop-blur active:cursor-grabbing">
                <GripVertical className="h-4 w-4" />
              </span>
            ) : null}
            <StatusBadge status={item.status} />
          </div>
          <div className="absolute right-3.5 top-3.5 rounded-full bg-[#111827]/60 px-2.5 py-1 text-[11px] font-semibold text-white backdrop-blur">
            #{item.display_order ?? 0}
          </div>
          {onPreview ? (
            <button
              type="button"
              onClick={onPreview}
              className="absolute bottom-3.5 right-3.5 rounded-xl bg-white/95 px-3 py-1.5 text-xs font-bold text-[#111827] opacity-0 shadow-sm transition group-hover:opacity-100"
            >
              Preview
            </button>
          ) : null}
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2 border-b border-[#E2E8F0] px-3.5 py-2">
          <div className="flex items-center gap-2">
            {draggable ? (
              <span className="cursor-grab rounded-lg bg-slate-100 p-1 text-slate-500 active:cursor-grabbing">
                <GripVertical className="h-3.5 w-3.5" />
              </span>
            ) : null}
            <StatusBadge status={item.status} />
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-500">
            #{item.display_order ?? 0}
          </span>
        </div>
      )}

      <div className={cn("space-y-3", hideImage ? "p-3.5" : "space-y-4 p-5")}>
        <div className="min-w-0">
          <h3 className="font-display truncate text-[15px] font-bold text-[#111827]">{title}</h3>
          {subtitle ? (
            <p
              className={cn(
                "line-clamp-2 text-sm leading-relaxed text-[#64748B]",
                hideImage ? "mt-1" : "mt-1.5"
              )}
            >
              {subtitle}
            </p>
          ) : null}
          {ctaText ? (
            <p className="mt-2 text-xs text-[#64748B]">
              CTA: <span className="font-semibold text-slate-700">{ctaText}</span>
              {ctaLink ? <span className="text-slate-400"> → {ctaLink}</span> : null}
            </p>
          ) : null}
          {metaBits.length > 0 ? (
            <p className={cn("text-xs text-slate-400", hideImage ? "mt-1" : "mt-1.5")}>
              {metaBits.join(" · ")}
            </p>
          ) : null}
          {(created || updated) && !hideImage ? (
            <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-[11px] font-medium text-slate-400">
              {created ? <span>Created {created}</span> : null}
              {updated ? <span>Updated {updated}</span> : null}
            </div>
          ) : null}
        </div>

        <div
          className={cn(
            "flex items-center gap-1.5 border-t border-[#E2E8F0]",
            hideImage ? "pt-2.5" : "pt-3.5"
          )}
        >
          <ActionButton href={href} label="Edit">
            <Pencil className="h-4 w-4" />
          </ActionButton>
          {onTogglePublish ? (
            <ActionButton
              onClick={onTogglePublish}
              label={
                String(item.status || "").toLowerCase() === "published"
                  ? "Unpublish"
                  : "Publish"
              }
            >
              {String(item.status || "").toLowerCase() === "published" ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </ActionButton>
          ) : null}
          {onDuplicate ? (
            <ActionButton onClick={onDuplicate} label="Duplicate">
              <Copy className="h-4 w-4" />
            </ActionButton>
          ) : null}
          <div className="flex-1" />
          {onDelete ? (
            <ActionButton onClick={onDelete} label="Delete" danger>
              <Trash2 className="h-4 w-4" />
            </ActionButton>
          ) : null}
        </div>
      </div>
    </motion.article>
  );
}

export function ContentCard(props) {
  return (
    <BannerCard
      {...props}
      className={cn(
        // Only force media aspect on image cards — text-only cards must hug content.
        !props.hideImage && "[&>div:first-child]:aspect-[16/10]",
        props.className
      )}
    />
  );
}
