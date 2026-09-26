import PrivacyPolicy from '@/components/pages/PrivacyPolicy';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Privacy Policy',
  description:
    'Read how AMP India Foundation collects, uses, and protects personal information when you visit our website or make a donation.',
  canonical: '/privacy-policy',
};

export const metadata = pageMeta(SEO);

export default function PrivacyPolicyPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Privacy Policy', path: '/privacy-policy' },
          ],
        })}
      />
      <PrivacyPolicy />
    </>
  );
}
