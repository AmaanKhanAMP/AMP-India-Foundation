/**
 * Factual Schema.org JSON-LD builders.
 * URLs come from NEXT_PUBLIC_SITE_URL. No CMS/API fetches.
 */
import { getSiteUrl, siteAbsoluteUrl } from '@/lib/siteUrl';

const SITE_NAME = 'AMP India Foundation';
const LOGO_PATH = '/assets/logo.png';

export function organizationJsonLd() {
  const url = getSiteUrl();
  return {
    '@type': 'Organization',
    '@id': `${url}/#organization`,
    name: SITE_NAME,
    url,
    logo: {
      '@type': 'ImageObject',
      url: siteAbsoluteUrl(LOGO_PATH),
    },
  };
}

export function websiteJsonLd() {
  const url = getSiteUrl();
  return {
    '@type': 'WebSite',
    '@id': `${url}/#website`,
    name: SITE_NAME,
    url,
  };
}

export function siteGraphJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@graph': [organizationJsonLd(), websiteJsonLd()],
  };
}

export function webPageJsonLd({ title, description, absoluteTitle, canonical }) {
  const url = siteAbsoluteUrl(canonical);
  const name = absoluteTitle || `${title} | ${SITE_NAME}`;
  return {
    '@type': 'WebPage',
    '@id': `${url}#webpage`,
    url,
    name,
    description,
    isPartOf: { '@id': `${getSiteUrl()}/#website` },
  };
}

export function breadcrumbJsonLd(items) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: siteAbsoluteUrl(item.path),
    })),
  };
}

/**
 * Page-level graph: WebPage plus BreadcrumbList when a real hierarchy exists.
 */
export function pageGraphJsonLd({
  title,
  description,
  absoluteTitle,
  canonical,
  breadcrumbs,
}) {
  const graph = [webPageJsonLd({ title, description, absoluteTitle, canonical })];
  if (Array.isArray(breadcrumbs) && breadcrumbs.length >= 2) {
    graph.push(breadcrumbJsonLd(breadcrumbs));
  }
  return {
    '@context': 'https://schema.org',
    '@graph': graph,
  };
}

export function projectBreadcrumbs(name, path) {
  return [
    { name: 'Home', path: '/' },
    { name: 'Projects', path: '/projects' },
    { name, path },
  ];
}

export function serializeJsonLd(data) {
  return JSON.stringify(data)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026')
    .replace(/\u2028/g, '\\u2028')
    .replace(/\u2029/g, '\\u2029');
}
