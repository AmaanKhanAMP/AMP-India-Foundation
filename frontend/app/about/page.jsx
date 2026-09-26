import About from '@/components/pages/About';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'About',
  description:
    'Learn about AMP India Foundation, a registered non-profit creating opportunities through education, employment, healthcare, skill development, and community empowerment.',
  canonical: '/about',
};

export const metadata = pageMeta(SEO);

export default function AboutPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'About', path: '/about' },
          ],
        })}
      />
      <About />
    </>
  );
}
