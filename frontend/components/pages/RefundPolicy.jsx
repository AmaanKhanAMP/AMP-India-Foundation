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
          <p className="terms-updated">Last Updated On: 13 October 2026</p>

          <article className="terms-section">
            <p>
              AMP India Foundation (&quot;AIF&quot;, &quot;we&quot;, or &quot;us&quot;) applies donations
              in line with the purpose the donor has indicated. A gift to AIF is complete when it is
              received. It is not refundable as a matter of course. A refund is considered only where
              the donor has a genuine reason and the Directors of AIF approve the request.
            </p>
          </article>

          <h2 className="terms-general-heading">How refund requests are handled</h2>

          <article className="terms-section">
            <h2>A clear process</h2>
            <p>
              This policy sets out how AIF reviews a request to return a donation, so that each
              request is dealt with in an open and even-handed way.
            </p>
          </article>

          <article className="terms-section">
            <h2>Care expected from donors</h2>
            <p>
              Before transferring money, donors are expected to check the amount, the beneficiary,
              and the payment details with reasonable care.
            </p>
          </article>

          <article className="terms-section">
            <h2>Mistakes and a later change of mind</h2>
            <p>
              AIF accepts that a transfer can be made by mistake, and that a donor may decide
              differently after the money has already been sent.
            </p>
          </article>

          <article className="terms-section">
            <h2>Approval is not guaranteed</h2>
            <p>
              AIF is under no duty to return a donation. A request may be refused. Any return that
              is made depends on approval by the Directors.
            </p>
          </article>

          <article className="terms-section">
            <h2>How to ask for a refund</h2>
            <p>
              Write to <ContactEmail /> if you want a donation to AMP India Foundation returned.
              The message must state why you are asking and must include the transaction details
              needed to identify the payment. The request has to reach AIF within 15 days of the
              date of the donation.
            </p>
            <p>
              AIF will look at the request and will try to return the amount where the request is
              accepted. AIF may ask for further information or documents. The donor is expected to
              provide what is reasonably asked for so the request can be considered.
            </p>
          </article>
        </motion.div>
      </section>
    </div>
  );
};

export default RefundPolicy;
