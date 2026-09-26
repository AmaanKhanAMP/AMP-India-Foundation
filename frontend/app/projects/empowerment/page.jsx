import Empowerment from '@/components/pages/projects/Empowerment';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Economic Empowerment',
  description:
    'AMP India Foundation supports self-employment and livelihoods by helping people start small businesses, access early financial support, and reach customers and markets.',
  canonical: '/projects/empowerment',
};

export const metadata = pageMeta(SEO);

export default function EmpowermentPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Economic Empowerment', SEO.canonical),
        })}
      />
      <Empowerment />
    </>
  );
}
