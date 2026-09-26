import Home from '@/components/pages/Home';
import { loadHomeCms } from '@/lib/loadCms';
import { homeMetadata } from '@/lib/pageMetadata';

export const metadata = homeMetadata;

/** Alias of `/` — same ISR seed as the root page. */
export const revalidate = 60;

export default async function HomeAliasPage() {
  const initialCms = await loadHomeCms();
  return <Home initialCms={initialCms} />;
}
