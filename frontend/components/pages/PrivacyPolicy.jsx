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

const PrivacyPolicy = () => {
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
            <span>Privacy Policy</span>
          </nav>
          <h1 className="terms-hero-title">Privacy Policy</h1>
        </motion.div>
      </header>

      <section className="terms-content-section">
        <motion.div
          className="terms-content-card"
          initial={fadeUp.initial}
          animate={fadeUp.animate}
          transition={{ duration: 0.5, ease: 'easeOut', delay: 0.08 }}
        >
          <p className="terms-updated">Last updated on: 13 October 2026</p>

          <article className="terms-section">
            <p>
              This notice describes how AMP India Foundation (&quot;AIF&quot;, &quot;we&quot;, or
              &quot;us&quot;) handles personal information and other information gathered when you
              use the AIF website (the &quot;Site&quot;). It covers only AIF. It does not cover
              organisations AIF does not own or control, and it does not cover people who are not
              employed or managed by AIF. If you do not accept these practices, please do not use
              the Site or the services offered through it.
            </p>
            <p>
              Use of the Site is also governed by our Terms &amp; Conditions. Words that are not
              defined in this notice have the meaning given in those terms.
            </p>
          </article>

          <h2 className="terms-general-heading">Information we collect</h2>

          <article className="terms-section">
            <h2>Details you give us</h2>
            <p>
              When you open an account, we collect the details you enter. Those details can include
              your full name, a username, email address, postal address, country, and age. We need
              this information to complete an online transaction you start on the Site
              (&quot;Personal Information&quot;).
            </p>
          </article>

          <article className="terms-section">
            <h2>Information that does not identify you</h2>
            <p>
              Some information does not point to you as a named person. It includes material
              collected automatically when you open the Site (&quot;Non-Personal Data&quot;). That
              material may come from cookies, pixel tags, web beacons, browser tools, and server
              logs. It may also describe the device you use, such as the operating system or phone
              model, the browser, the domain, other system settings, the language, and the country
              and time zone of the device.
            </p>
            <p>
              Server logs may record the IP address of the device that contacts the Site. If your
              browser sends it, we may also see the page you came from and the page you go to after
              leaving. Tools such as JavaScript may record how a visit behaves, including how long a
              page takes to respond, download errors, and how you leave a page. Some location
              information may also be collected as Non-Personal Data.
            </p>
          </article>

          <article className="terms-section">
            <h2>Accuracy of what you submit</h2>
            <p>
              You confirm that what you send us is genuine, accurate, and up to date, and that you
              have the rights and permissions needed to send it. Sending that information, and our
              later storage, collection, use, transfer, access, or processing of it, must not break
              any agreement with another person, any law, any constitutional document of an
              organisation, or any judgment, order, or decree. AIF, and its officers, directors,
              contractors, and agents, are not responsible for checking that the information you
              supply is authentic.
            </p>
            <p>
              If you breach this notice, you agree to indemnify and hold harmless AIF, its officers,
              directors, contractors, and agents, and any third party who relies on information you
              provided.
            </p>
          </article>

          <h2 className="terms-general-heading">Why we use this information</h2>

          <article className="terms-section">
            <h2>Running and improving the Site</h2>
            <p>To build, operate, and improve the Site and the services offered on it.</p>
          </article>

          <article className="terms-section">
            <h2>Understanding use of the Site</h2>
            <p>To study how people use the Site.</p>
          </article>

          <article className="terms-section">
            <h2>Responding to you</h2>
            <p>To answer questions and provide support.</p>
          </article>

          <article className="terms-section">
            <h2>Messages that may interest you</h2>
            <p>
              To write to you with further information that may be relevant, for example project
              updates chosen with reference to your location and how you have used the services
              before.
            </p>
          </article>

          <article className="terms-section">
            <h2>Service messages</h2>
            <p>To send reminders, technical notices, updates, security alerts, and support messages.</p>
          </article>

          <article className="terms-section">
            <h2>Ordinary administration</h2>
            <p>
              To administer the Site, analyse activity, reduce fraud, and meet legal duties.
            </p>
          </article>

          <article className="terms-section">
            <h2>Card payments</h2>
            <p>
              Card details entered while donating are handled through the secure checkout of the
              payment partners AIF uses. Those partners are established payment gateways operating
              in India. The payment is also taken through an additional cardholder check, such as
              Verified by Visa or Mastercard 3D Secure, to reduce misuse of the card.
            </p>
            <p>
              AIF and this website do not keep your card number, card password, or CVV. A certified
              payment gateway uses those details only to finish the transaction.
            </p>
          </article>

          <article className="terms-section">
            <h2>When information may be shared</h2>
            <p>
              Other than as described here, we do not show your Personal Information on the Site or
              pass it to third parties. We may do so when it is needed to provide the services, when
              the law requires it, or when we believe in good faith that disclosure is reasonably
              necessary to:
            </p>
            <ol className="terms-list terms-list-numbered">
              <li>comply with a court order, legal process, or ongoing judicial proceeding served on us;</li>
              <li>
                protect our rights, property, and interests, including by enforcing our agreements,
                policies, and Terms &amp; Conditions;
              </li>
              <li>answer a claim that material submitted through the Site infringes someone else&apos;s rights;</li>
              <li>deal with a support request you have made;</li>
              <li>protect the rights, property, or safety of AIF, people who use the Site, and the public;</li>
              <li>
                support negotiations for, or the completion of, a merger, a sale of assets, a
                financing, or the acquisition of all or part of our work by another organisation; or
              </li>
              <li>share information because you have agreed to that sharing.</li>
            </ol>
            <p>
              If you donate, we share your account name, the amount, and your payment information
              with the third-party processor that handles the payment.
            </p>
            <p>
              We may share Non-Personal Data with analytics providers so we can see how people move
              through the Site and improve it. See also &quot;Analytics providers&quot; below. We do
              not sell Personal Information or Non-Personal Data.
            </p>
          </article>

          <article className="terms-section">
            <h2>Choosing not to be named</h2>
            <p>
              Where the Site lets a donor give without being named, choosing that option means your
              name and image are not published with the donation. If you ask for a receipt so that
              you can claim a tax deduction, the Site may still pass your name, PAN, address, and
              email address to the person or project that raised the appeal, and only for that
              receipt.
            </p>
          </article>

          <article className="terms-section">
            <h2>Choices available to you</h2>
            <p>
              You may stop email from us by using the unsubscribe link in the message, or by writing
              to <ContactEmail />. If you have an account, you may change or delete Personal
              Information by signing in and updating your profile. We keep information only for as
              long as we need it to provide the services, or for as long as we need it to meet legal
              duties, settle disputes, and enforce our agreements.
            </p>
          </article>

          <article className="terms-section">
            <h2>Analytics providers</h2>
            <p>
              This notice covers only how AIF uses and discloses information. We may use analytics
              services to interpret information collected from you. Those services may use cookies,
              web beacons, and similar tools to measure traffic. What they collect commonly includes
              your IP address, your internet provider, and the browser you used to open the Site.
              Their own tools are not covered by this notice, and AIF is not responsible for them.
            </p>
          </article>

          <article className="terms-section">
            <h2>Children</h2>
            <p>
              The Site is not aimed at anyone under 18, and AIF does not knowingly collect Personal
              Information from anyone under 18. We ask that everyone who uses the services be at
              least 18 (or the age of majority where they live), or use the services with a
              parent&apos;s consent and supervision.
            </p>
          </article>

          <article className="terms-section">
            <h2>Your agreement</h2>
            <p>
              By using the Site, or by sending us information, you agree that we may collect and use
              what you disclose, as described in this notice, including the sharing described above.
            </p>
          </article>

          <article className="terms-section">
            <h2>Changes to this notice</h2>
            <p>
              We may revise this notice from time to time. A revision takes effect when it is posted
              on the Site. The date at the top of this page shows when it was last revised. If you
              keep using the Site after a revision is posted, you accept the revised notice. We may
              also change, limit, suspend, or stop the Site or the services, or any part of them, at
              any time.
            </p>
          </article>

          <article className="terms-section">
            <h2>Safeguards</h2>
            <p>
              AIF uses reasonable security practices and procedures for the personal information it
              collects. That information is kept on secure servers. By registering or creating an
              account, you accept that these measures are reasonable and adequate. We take
              appropriate steps to protect information we hold and to limit unauthorised access, but
              the internet is not fully secure and we cannot promise absolute security. AIF is not
              liable for a security breach, or for an unintended loss or disclosure of your personal
              information, arising in connection with that information.
            </p>
            <p>
              AIF is also not responsible for loss, damage, or misuse of your personal information
              when that loss, damage, or misuse is caused by a force majeure event. A force majeure
              event is something beyond our reasonable control. It includes sabotage, fire, flood,
              explosion, acts of God, civil commotion, strikes or other industrial action, riots,
              insurrection, war, acts of government, hacking, unauthorised access to a computer,
              system, or network, computer crashes, a failure of security or encryption that is
              beyond our reasonable control, and a failure or shortage of power.
            </p>
          </article>

          <article className="terms-section">
            <h2>Questions</h2>
            <p>
              Questions about this notice can be sent to <ContactEmail />.
            </p>
          </article>
        </motion.div>
      </section>
    </div>
  );
};

export default PrivacyPolicy;
