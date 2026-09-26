import Medical from '@/components/pages/projects/Medical';
import { pageMeta } from '@/lib/pageMetadata';

export const metadata = pageMeta({
  title: 'Healthcare',
  description:
    'Healthcare support and outreach from AMP India Foundation, including health check-up camps, medicine distribution, and medical assistance for people in need.',
  canonical: '/projects/medical',
});

export default function HealthcarePage() {
  return <Medical />;
}
