import Training from '@/components/pages/projects/Training';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Employment Training',
  description:
    'The Employability Training Programme (ETP) at AMP India Foundation helps job seekers prepare resumes, interviews, workplace behaviour, and professional communication.',
  canonical: '/projects/training',
};

export const metadata = pageMeta(SEO);

export default function TrainingPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Employment Training', SEO.canonical),
        })}
      />
      <Training />
    </>
  );
}
