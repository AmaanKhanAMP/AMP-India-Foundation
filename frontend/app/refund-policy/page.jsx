import RefundPolicy from '@/components/pages/RefundPolicy';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Refund Policy',
  description:
    'Learn about AMP India Foundation donation refunds, including how to request a refund and the conditions that apply.',
  canonical: '/refund-policy',
};

export const metadata = pageMeta(SEO);

export default function RefundPolicyPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Refund Policy', path: '/refund-policy' },
          ],
        })}
      />
      <RefundPolicy />
    </>
  );
}
