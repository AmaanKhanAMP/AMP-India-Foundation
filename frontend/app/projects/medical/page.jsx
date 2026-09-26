import Medical from '@/components/pages/projects/Medical';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Medical Relief',
  description:
    'AMP India Foundation provides healthcare support through medical camps, medicine distribution, and assistance for individuals and families who cannot afford treatment.',
  canonical: '/projects/medical',
};

export const metadata = pageMeta(SEO);

export default function MedicalPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Medical Relief', SEO.canonical),
        })}
      />
      <Medical />
    </>
  );
}
