import { siteAbsoluteUrl } from '@/lib/siteUrl';

/** Canonical public routes only. Aliases and non-page endpoints are omitted. */
const CANONICAL_PATHS = [
  '/',
  '/about',
  '/projects',
  '/projects/education',
  '/projects/medical',
  '/projects/employment',
  '/projects/empowerment',
  '/projects/mentorship',
  '/projects/training',
  '/projects/featured',
  '/events',
  '/volunteer',
  '/support-us',
  '/contact',
  '/terms-and-conditions',
  '/privacy-policy',
  '/refund-policy',
];

/** @returns {import('next').MetadataRoute.Sitemap} */
export default function sitemap() {
  return CANONICAL_PATHS.map((pathname) => ({
    url: siteAbsoluteUrl(pathname),
  }));
}
