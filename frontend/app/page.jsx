import Home from '@/components/pages/Home';
import { loadHomeCms } from '@/lib/loadCms';
import { homeMetadata } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

export const metadata = homeMetadata;

export const revalidate = 60;

/**
 * ISR page: CMS is baked into the static HTML. Client navigations reuse that
 * payload and do not remount Home with a null seed (that flicker was caused
 * by a Suspense fallback of <Home initialCms={null} />).
 */
export default async function HomePage() {
  const initialCms = await loadHomeCms();
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          absoluteTitle: 'AMP India Foundation',
          description: homeMetadata.description,
          canonical: '/',
        })}
      />
      <Home initialCms={initialCms} />
    </>
  );
}
