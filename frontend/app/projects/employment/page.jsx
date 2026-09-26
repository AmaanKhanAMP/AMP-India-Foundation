import Employment from '@/components/pages/projects/Employment';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Employment Support',
  description:
    'AMP India Foundation helps young people find work through career guidance, employability programmes, job drives, and mega job fairs that connect job seekers with employers.',
  canonical: '/projects/employment',
};

export const metadata = pageMeta(SEO);

export default function EmploymentPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Employment Support', SEO.canonical),
        })}
      />
      <Employment />
    </>
  );
}
