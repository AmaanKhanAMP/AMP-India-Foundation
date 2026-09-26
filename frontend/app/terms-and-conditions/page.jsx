import Terms from '@/components/pages/Terms';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Terms & Conditions',
  description:
    'Read the AMP India Foundation website terms of use, including eligibility, account security, prohibited activities, and conditions for members, volunteers, and donors.',
  canonical: '/terms-and-conditions',
};

export const metadata = pageMeta(SEO);

export default function TermsPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Terms & Conditions', path: '/terms-and-conditions' },
          ],
        })}
      />
      <Terms />
    </>
  );
}
