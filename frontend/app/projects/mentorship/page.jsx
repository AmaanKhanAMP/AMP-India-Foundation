import Mentorship from '@/components/pages/projects/Mentorship';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd, projectBreadcrumbs } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Student Mentorship',
  description:
    'AMP India Foundation connects students with experienced professionals for guidance on education, careers, internships, professional skills, and personal development.',
  canonical: '/projects/mentorship',
};

export const metadata = pageMeta(SEO);

export default function MentorshipPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: projectBreadcrumbs('Student Mentorship', SEO.canonical),
        })}
      />
      <Mentorship />
    </>
  );
}
