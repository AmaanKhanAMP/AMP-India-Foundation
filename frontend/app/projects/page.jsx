import ProjectsPage from '@/components/pages/ProjectsPage';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Projects',
  description:
    'Explore AMP India Foundation projects in education, medical relief, employment support, economic empowerment, student mentorship, and employment training.',
  canonical: '/projects',
};

export const metadata = pageMeta(SEO);

export default function ProjectsRoutePage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Projects', path: '/projects' },
          ],
        })}
      />
      <ProjectsPage />
    </>
  );
}
