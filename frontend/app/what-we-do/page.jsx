import About from '@/components/pages/About';
import { pageMeta } from '@/lib/pageMetadata';

export const metadata = pageMeta({
  title: 'What We Do',
  description:
    'See how AMP India Foundation supports education, employment, skill development, healthcare, and empowerment programmes for underprivileged communities.',
  canonical: '/about',
});

export default function WhatWeDoPage() {
  return <About />;
}
