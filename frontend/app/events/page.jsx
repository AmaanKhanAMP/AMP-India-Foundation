import Events from '@/components/pages/Events';
import { loadEventsCms } from '@/lib/loadCms';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Events',
  description:
    'Discover AMP India Foundation events, including career guidance, job fairs, health camps, and skill development workshops that create opportunities in the community.',
  canonical: '/events',
};

export const metadata = pageMeta(SEO);

export const revalidate = 60;

/**
 * ISR page: Upcoming Events is in the static HTML. No Suspense null-seed
 * remount, so the section cannot flash away during client navigation.
 */
export default async function EventsPage() {
  const initialCms = await loadEventsCms();
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Events', path: '/events' },
          ],
        })}
      />
      <Events initialCms={initialCms} />
    </>
  );
}
