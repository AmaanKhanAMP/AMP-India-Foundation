import FeaturedInitiatives from '@/components/layout/FeaturedInitiative';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Featured Initiatives',
  description:
    "An overview of AMP India Foundation's main initiatives: education, medical relief, employment support, economic empowerment, student mentorship, and employability training.",
  canonical: '/projects/featured',
};

export const metadata = pageMeta(SEO);

export default function FeaturedProjectsPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Featured Initiatives', SEO.canonical),
        })}
      />
      <FeaturedInitiatives />
    </>
  );
}
