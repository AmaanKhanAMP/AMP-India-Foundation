import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import BackToTop from '@/components/layout/BackToTop';
import { ChatWidget, CHATBOT_ENABLED } from '@/chatbot';
import { loadSiteShellCms } from '@/lib/loadCms';
import { siteGraphJsonLd } from '@/lib/jsonLd';
import JsonLd from '@/components/seo/JsonLd';
import './globals.css';
import { GoogleAnalytics } from '@next/third-parties/google';

const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL || '').replace(/\/$/, '');
const SITE_NAME = 'AMP India Foundation';
const SITE_DESCRIPTION =
  'AMP India Foundation — empowering communities through education, employment, mentorship, healthcare, and skill development.';

export const metadata = {
  metadataBase: SITE_URL ? new URL(SITE_URL) : undefined,
  title: {
    default: SITE_NAME,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: SITE_URL || undefined,
    siteName: SITE_NAME,
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    images: [
      {
        url: '/assets/logo.png',
        alt: SITE_NAME,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    images: ['/assets/logo.png'],
  },
};

/** ISR so the shell is prerendered and client navigations do not wait on Render. */
export const revalidate = 60;

export default async function RootLayout({ children }) {
  const shell = await loadSiteShellCms();

  return (
    <html lang="en">
      <body>
        <JsonLd data={siteGraphJsonLd()} />
        <Navbar
          settings={shell.navbarSettings}
          items={shell.navbarItems}
        />
        <main style={{ minHeight: '80vh' }}>{children}</main>
        <Footer
          settings={shell.footerSettings}
          links={shell.footerLinks}
          focusItems={shell.footerFocus}
        />
        {CHATBOT_ENABLED ? <ChatWidget /> : null}
        <BackToTop />
        <GoogleAnalytics gaId="G-ZP1NZH34Y5" />
      </body>
    </html>
  );
}
