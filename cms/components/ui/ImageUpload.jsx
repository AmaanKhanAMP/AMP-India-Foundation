"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ImagePlus, Loader2, X } from "lucide-react";
import uploadService from "@/services/uploadService";
import { resolveImageUrl } from "@/utils/imageUrl";
import { useToast } from "@/contexts/ToastContext";
import { cn } from "@/utils/cn";

function isFinePointerHoverDevice() {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return true;
  }
  return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

export default function ImageUpload({
  value,
  onChange,
  folder = "general",
  label = "Image",
  className,
  aspect = "video",
}) {
  const toast = useToast();
  const inputRef = useRef(null);
  const containerRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [actionsOpen, setActionsOpen] = useState(false);

  const handleFile = useCallback(
    async (file) => {
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        toast.error("Please upload an image file.");
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Image must be under 5MB.");
        return;
      }
      setUploading(true);
      setProgress(15);
      const tick = setInterval(() => {
        setProgress((p) => (p < 85 ? p + 10 : p));
      }, 120);
      try {
        const res = await uploadService.uploadFile(file, folder);
        setProgress(100);
        onChange(res.url);
        toast.success("Image uploaded.");
      } catch (err) {
        toast.error(err.response?.data?.message || "Upload failed.");
      } finally {
        clearInterval(tick);
        setUploading(false);
        setTimeout(() => setProgress(0), 400);
      }
    },
    [folder, onChange, toast]
  );

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    handleFile(file);
  };

  // Hide touch overlay when tapping outside the uploader.
  useEffect(() => {
    if (!actionsOpen) return undefined;
    const onPointerDown = (e) => {
      if (!containerRef.current?.contains(e.target)) {
        setActionsOpen(false);
      }
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [actionsOpen]);

  useEffect(() => {
    if (!value) setActionsOpen(false);
  }, [value]);

  return (
    <div ref={containerRef} className={cn("space-y-1.5", className)}>
      {label ? <p className="text-[13px] font-semibold text-slate-700">{label}</p> : null}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          "relative overflow-hidden rounded-2xl border-2 border-dashed transition",
          aspect === "square" && "aspect-square",
          aspect === "video" && "aspect-video",
          aspect === "logo" && "flex h-28 items-center justify-center sm:h-32",
          !["square", "video", "logo"].includes(aspect) && "aspect-video",
          dragging
            ? "border-[var(--primary)] bg-blue-50 shadow-[0_0_0_4px_rgba(59,130,246,0.12)]"
            : "border-slate-200 bg-gradient-to-b from-slate-50 to-white",
          value && "border-solid border-slate-200"
        )}
      >
        {value ? (
          <>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={resolveImageUrl(value)}
              alt="Upload preview"
              className={cn(
                "h-full w-full",
                aspect === "logo" ? "object-contain p-3" : "object-cover"
              )}
            />
            <div
              className={cn(
                "absolute inset-0 flex items-end justify-between bg-gradient-to-t from-black/50 to-transparent p-3 opacity-0 transition hover:opacity-100 focus-within:opacity-100",
                // Touch / coarse pointer: reveal after tap (desktop still uses hover).
                actionsOpen && "opacity-100"
              )}
              onClick={(e) => {
                // Desktop mouse uses hover; do not force-open on click.
                if (isFinePointerHoverDevice()) return;
                // First tap reveals overlay; action buttons stopPropagation.
                if (!actionsOpen) {
                  e.preventDefault();
                  setActionsOpen(true);
                }
              }}
            >
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setActionsOpen(false);
                  inputRef.current?.click();
                }}
                className="rounded-lg bg-white/90 px-3 py-1.5 text-xs font-semibold text-slate-800"
              >
                Replace
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setActionsOpen(false);
                  onChange("");
                }}
                className="rounded-lg bg-white/90 p-1.5 text-slate-700"
                aria-label="Remove image"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </>
        ) : (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="flex h-full w-full flex-col items-center justify-center gap-2 text-slate-500"
          >
            {uploading ? (
              <Loader2 className="h-8 w-8 animate-spin text-[var(--primary)]" />
            ) : (
              <ImagePlus className="h-8 w-8 text-slate-400" />
            )}
            <span className="text-sm font-medium">
              {uploading ? "Uploading…" : "Drag & drop or click to upload"}
            </span>
            <span className="text-xs text-slate-400">PNG, JPG, WEBP up to ~5MB</span>
          </button>
        )}
        {uploading ? (
          <div className="absolute inset-x-0 bottom-0 h-1.5 bg-slate-200">
            <div
              className="h-full bg-[var(--primary)] transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        ) : null}
        {uploading && value ? (
          <div className="absolute inset-0 flex items-center justify-center bg-white/60">
            <Loader2 className="h-8 w-8 animate-spin text-[var(--primary)]" />
          </div>
        ) : null}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
    </div>
  );
}
