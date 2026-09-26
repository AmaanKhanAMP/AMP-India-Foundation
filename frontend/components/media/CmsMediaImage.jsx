"use client";

import Image from "next/image";
import { useCmsImageSrc } from "@/lib/cmsImage";

/**
 * CMS/media image through Next.js Image Optimization.
 * Keeps the original CMS URL as the source; Vercel resizes/caches it.
 */
export default function CmsMediaImage({
  cmsSrc,
  fallbackSrc,
  alt = "",
  fill = false,
  width,
  height,
  sizes,
  priority = false,
  loading,
  className,
  style,
  quality = 75,
  onLoad,
  fetchPriority,
}) {
  const { src, onError } = useCmsImageSrc(cmsSrc, fallbackSrc);
  if (!src) return null;

  return (
    <Image
      src={src}
      alt={alt}
      fill={fill}
      width={fill ? undefined : width}
      height={fill ? undefined : height}
      sizes={sizes}
      quality={quality}
      priority={priority}
      fetchPriority={fetchPriority}
      loading={priority ? undefined : loading}
      className={className}
      style={style}
      onError={onError}
      onLoad={onLoad}
    />
  );
}
