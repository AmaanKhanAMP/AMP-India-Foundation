import Contact from '@/components/pages/Contact';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Contact Us',
  description:
    'Contact AMP India Foundation in Mumbai with questions, partnership ideas, or requests for support. Reach the team by form, phone, or email.',
  canonical: '/contact',
};

export const metadata = pageMeta(SEO);

export default function ContactPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Contact Us', path: '/contact' },
          ],
        })}
      />
      <Contact />
    </>
  );
}
