import Education from '@/components/pages/projects/Education';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Education',
  description:
    'AMP India Foundation education initiatives include scholarships, school development, teacher training, career guidance, and skill development for students from underprivileged families.',
  canonical: '/projects/education',
};

export const metadata = pageMeta(SEO);

export default function EducationPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Education', SEO.canonical),
        })}
      />
      <Education />
    </>
  );
}
