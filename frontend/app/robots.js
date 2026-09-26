import { siteAbsoluteUrl } from '@/lib/siteUrl';

/** @returns {import('next').MetadataRoute.Robots} */
export default function robots() {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
    },
    sitemap: siteAbsoluteUrl('/sitemap.xml'),
  };
}
