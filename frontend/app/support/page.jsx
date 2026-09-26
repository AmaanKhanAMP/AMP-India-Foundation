import Support from '@/components/pages/Support';
import { pageMeta } from '@/lib/pageMetadata';

export const metadata = pageMeta({
  title: 'Support',
  description:
    'Find donation options for AMP India Foundation, including bank transfer and cheque details, to support education, employment, healthcare, and community programmes.',
  canonical: '/support-us',
});

export default function SupportPage() {
  return <Support />;
}
