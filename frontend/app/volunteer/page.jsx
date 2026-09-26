import Volunteer from '@/components/pages/Volunteer';
import { pageMeta } from '@/lib/pageMetadata';
import { pageGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';

const SEO = {
  title: 'Volunteer',
  description:
    'Volunteer with AMP India Foundation as a mentor, educator, event organiser, or community supporter. Use your time and skills to create opportunities for those who need them most.',
  canonical: '/volunteer',
};

export const metadata = pageMeta(SEO);

export default function VolunteerPage() {
  return (
    <>
      <JsonLd
        data={pageGraphJsonLd({
          ...SEO,
          breadcrumbs: [
            { name: 'Home', path: '/' },
            { name: 'Volunteer', path: '/volunteer' },
          ],
        })}
      />
      <Volunteer />
    </>
  );
}
