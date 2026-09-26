/**
 * Static page metadata helpers. Titles use the root title template
 * (`%s | AMP India Foundation`) unless `absoluteTitle` is set.
 * No CMS/API fetches — copy is based on existing page content.
 *
 * Canonical paths are relative; Next.js resolves them with metadataBase
 * from NEXT_PUBLIC_SITE_URL.
 */

const SITE_NAME = 'AMP India Foundation';

const PATH_ALIASES = {
  '/home': '/',
  '/what-we-do': '/about',
  '/support': '/support-us',
  '/projects/healthcare': '/projects/medical',
};

/**
 * Map a duplicate/internal href to its primary canonical path.
 * Preserves hash and query. Leaves external and in-page hashes unchanged.
 */
export function toCanonicalPath(href) {
  if (!href || typeof href !== 'string') return href;
  if (
    href.startsWith('http://') ||
    href.startsWith('https://') ||
    href.startsWith('mailto:') ||
    href.startsWith('tel:') ||
    href.startsWith('#')
  ) {
    return href;
  }

  const hashIndex = href.indexOf('#');
  const queryIndex = href.indexOf('?');
  let splitAt = -1;
  if (hashIndex >= 0 && queryIndex >= 0) splitAt = Math.min(hashIndex, queryIndex);
  else if (hashIndex >= 0) splitAt = hashIndex;
  else if (queryIndex >= 0) splitAt = queryIndex;

  const path = splitAt >= 0 ? href.slice(0, splitAt) : href;
  const suffix = splitAt >= 0 ? href.slice(splitAt) : '';
  const normalized = path.replace(/\/+$/, '') || '/';
  const mapped = PATH_ALIASES[normalized] || normalized;
  return mapped + suffix;
}

export function pageMeta({ title, description, absoluteTitle, canonical }) {
  const resolvedTitle = absoluteTitle || `${title} | ${SITE_NAME}`;
  const canonicalPath = canonical ? toCanonicalPath(canonical) : undefined;
  return {
    title: absoluteTitle ? { absolute: absoluteTitle } : title,
    description,
    openGraph: {
      type: 'website',
      locale: 'en_IN',
      siteName: SITE_NAME,
      title: resolvedTitle,
      description,
      ...(canonicalPath ? { url: canonicalPath } : {}),
      images: [
        {
          url: '/assets/logo.png',
          alt: SITE_NAME,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: resolvedTitle,
      description,
      images: ['/assets/logo.png'],
    },
    ...(canonicalPath
      ? {
          alternates: {
            canonical: canonicalPath,
          },
        }
      : {}),
  };
}

export const homeMetadata = pageMeta({
  absoluteTitle: SITE_NAME,
  description:
    'AMP India Foundation is a registered non-profit working with underprivileged communities through education, employment support, medical relief, economic empowerment, student mentorship, employability initiatives, and job fairs.',
  canonical: '/',
});
