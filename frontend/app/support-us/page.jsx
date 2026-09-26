import Support from '@/components/pages/Support';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Support Us',
  description:
    'Support AMP India Foundation with a donation that helps create opportunities in education, employment, healthcare, and community development.',
  canonical: '/support-us',
};

export const metadata = pageMeta(SEO);

export default function SupportUsPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Support Us', path: '/support-us' },
          ],
        })}
      />
      <Support />
    </>
  );
}
