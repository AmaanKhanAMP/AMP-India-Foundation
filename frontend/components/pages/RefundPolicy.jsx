"use client";

import Link from 'next/link';
import { motion } from 'framer-motion';

const CONTACT_EMAIL = 'contact@ampindiafoundation.org';

function ContactEmail() {
  return <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>;
}

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
};

const RefundPolicy = () => {
  return (
    <div className="terms-page">
      <header className="terms-hero">
        <div className="terms-hero-glow terms-hero-glow-1" aria-hidden="true" />
        <div className="terms-hero-glow terms-hero-glow-2" aria-hidden="true" />
        <div className="terms-hero-ring" aria-hidden="true" />
        <div className="terms-hero-mesh" aria-hidden="true" />

        <motion.div
          className="terms-hero-inner"
          initial={fadeUp.initial}
          animate={fadeUp.animate}
          transition={{ duration: 0.55, ease: 'easeOut' }}
        >
          <nav className="terms-breadcrumb" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span aria-hidden="true">/</span>
            <span>Refund Policy</span>
          </nav>
          <h1 className="terms-hero-title">Refund Policy</h1>
        </motion.div>
      </header>

      <section className="terms-content-section">
        <motion.div
          className="terms-content-card"
          initial={fadeUp.initial}
          animate={fadeUp.animate}
          transition={{ duration: 0.5, ease: 'easeOut', delay: 0.08 }}
        >
          <article className="terms-section">
            <p>
              AMP India Foundation takes utmost care to process and utilize donations
              as per the instructions given by our donors. Donations made to AMP India
              Foundation are final and cannot be refunded, except in certain cases
              where donors have a genuine reason for refunds and it is approved by the
              Directors.
            </p>
          </article>

          <h2 className="terms-general-heading">How AMP Treats Refund Requests</h2>

          <article className="terms-section">
            <h2>Fair and transparent</h2>
            <p>
              AMP India Foundation has created a donation refund policy to ensure fair
              and transparent processing of requests for refund of donations.
            </p>
          </article>

          <article className="terms-section">
            <h2>Due care by donors</h2>
            <p>
              AMP India Foundation expects that all donors will exercise due care and
              diligence while making donations.
            </p>
          </article>

          <article className="terms-section">
            <h2>Errors and change of mind</h2>
            <p>
              AMP India Foundation also recognizes that a donation may be made
              erroneously or the donors may change their mind after transferring the
              amount.
            </p>
          </article>

          <article className="terms-section">
            <h2>Refunds are discretionary</h2>
            <p>
              AMP India Foundation is not obliged to make refunds and may, in its
              discretion, decline any requests for refund of donations.
            </p>
          </article>

          <article className="terms-section">
            <h2>How to request a refund</h2>
            <p>
              If you would like your donation to AMP India Foundation to be refunded,
              kindly send a request mail to <ContactEmail /> with the reason for refund
              along with the transaction details. Your request must reach AMP India
              Foundation within 15 days from the date of donation.
            </p>
            <p>
              AMP India Foundation will examine each request for refund of donation
              and endeavor to make the refund. AMP India Foundation may also seek
              further information/documents and donors must co-operate in this regard.
            </p>
          </article>
        </motion.div>
      </section>
    </div>
  );
};

export default RefundPolicy;
