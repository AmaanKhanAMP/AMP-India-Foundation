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
          <p className="terms-updated">Last updated on: 18.05.2021</p>

          <article className="terms-section">
            <p>
              This Privacy Policy explains how AMP India Foundation or “we” use personal
              and other types of information collected from you when you visit the AMP
              India Foundation website (the “Site”). This policy does not apply to the
              practices of companies not owned or controlled by AMP India Foundation or
              to people whom AMP India Foundation does not employ or manage. If you do
              not agree with our practices, please do not use our Site and the Services.
            </p>
            <p>
              Your access for using the Site and Services is also subject to the Terms
              of Use. Anything that is not defined here can be found in our Terms of Use
              Policy.
            </p>
          </article>

          <h2 className="terms-general-heading">Types of Information We Collect</h2>

          <article className="terms-section">
            <h2>Personal Information</h2>
            <p>
              We collect the personal information that you provide us when you create
              your user account. This includes your full name, username, email address,
              your address, country of residence, and age. This is required for any
              online transactions you make from the Site (“Personal Information”).
            </p>
          </article>

          <article className="terms-section">
            <h2>Aggregate and Anonymous Data</h2>
            <p>
              Aggregate and anonymous data is information that does not identify you
              specifically, including data collected automatically when you enter our
              Site (“Non-Personal Data”). This may include cookies, pixel tags, web
              beacons, browser analysis tools, and web server logs. This also includes
              information from the devices you use to access our Site or mobile
              platform, your operating system type or mobile device model, browser type,
              domain, and other system settings, as well as the language your system
              uses and the country and time zone of your device. Our server logs may
              also record the IP addresses of the devices you use to interact with the
              Site. We may also collect information about a website you were visiting
              before you came to our Site and any website you visit after you leave our
              Site, if this information is supplied to us by your browser. We may also
              use software tools, such as JavaScript, to measure and collect session
              information, including page response times, download errors, and methods
              used to browse away from the page. Non-Personal Data also includes some
              data collected by location services.
            </p>
          </article>

          <article className="terms-section">
            <h2>Authenticity of Information provided</h2>
            <p>
              You hereby represent to us that the information you provide is and shall
              be authentic, correct, current, and you have all the rights, permissions
              and consents as may be required to provide such information to us.
              Further, you providing the information to us and our consequent storage,
              collection, usage, transfer, access, or processing of the same, shall not
              be in violation of any third party agreement, laws, charter documents,
              judgments, orders, and decrees. We and each of our entity&apos;s officers,
              directors, contractors, or agents shall not be responsible for the
              authenticity of the information that you provide to us.
            </p>
            <p>
              You shall indemnify and hold harmless us and each of our entity&apos;s
              officers, directors, contractors or agents, and any third party relying
              on the information provided by you in the event you are in breach of this
              Privacy Policy.
            </p>
          </article>

          <h2 className="terms-general-heading">How We Use Personal Information and Non-Personal Data</h2>

          <article className="terms-section">
            <h2>Build and improve</h2>
            <p>Build, operate and improve our Site and the Services.</p>
          </article>

          <article className="terms-section">
            <h2>User analytics</h2>
            <p>Perform user analytics.</p>
          </article>

          <article className="terms-section">
            <h2>Customer support</h2>
            <p>Provide customer support.</p>
          </article>

          <article className="terms-section">
            <h2>Communicate with you</h2>
            <p>
              Communicate with you and provide additional information that may be of
              interest to you such as, for example, sending project information that we
              believe may be of interest to you based on your geographic location and
              previous use of the Service.
            </p>
          </article>

          <article className="terms-section">
            <h2>Notices and support</h2>
            <p>Send you reminders, technical notices, updates, security alerts and support.</p>
          </article>

          <article className="terms-section">
            <h2>Everyday business needs</h2>
            <p>
              Manage our everyday business needs such as Site administration, analytics,
              fraud prevention, or to comply with the law.
            </p>
          </article>

          <article className="terms-section">
            <h2>Use of your Credit/Debit Card Details</h2>
            <p>
              Your credit and debit card details submitted while making a donation on
              the Site goes through the safe and secure transaction process provided by
              our payment gateway partners, which only include the most trusted payment
              gateways in India. Furthermore, you will also be taken through a 3D
              secure verification such as &quot;Verified by Visa&quot; or “Master Card
              3D Secure” password protected process to prevent any misuse of your
              debit/credit cards. Your credit/debit card details (card numbers,
              passwords, CVV numbers, etc.) are not stored by AMP India Foundation or
              the website. Such information is only used by a certified payment gateway
              to complete the payment transaction.
            </p>
          </article>

          <article className="terms-section">
            <h2>When and Why We Disclose Personal Information and Non-Personal Data</h2>
            <p>
              Except as provided herein, we will not display on the Site, or otherwise
              disclose your Personal Information to any third parties unless it is
              necessary to provide the Services when required by law, or if we have
              good faith belief that such action is reasonably necessary to:
            </p>
            <ol className="terms-list terms-list-numbered">
              <li>
                comply with current judicial proceedings, a court order or legal process
                served on us;
              </li>
              <li>
                protect and defend our rights, property and interests, including by
                enforcing our agreements, policies and Terms of Use;
              </li>
              <li>
                respond to claims that any submitted content violates the rights of
                third parties;
              </li>
              <li>respond to your requests for customer service;</li>
              <li>
                protect the rights, property or personal safety of AMP India Foundation,
                its users and the public;
              </li>
              <li>
                in connection with, or during negotiations of, any merger, sale of
                company assets, financing or acquisition of all or a portion of our
                business by another company, or
              </li>
              <li>with your consent to share the information.</li>
            </ol>
            <p>
              If you are a Donor, we will share your account name and the amount of
              your donation and your payment information with our third-party payment
              processor.
            </p>
            <p>
              We may share Non-Personal Data with analytics companies to learn
              information about how our users interact with the Site. This enables us
              to optimize the Service and improve our efforts. See also “Third Party
              Analytics” below. We will never sell your Personal Information or
              Non-Personal Data.
            </p>
          </article>

          <article className="terms-section">
            <h2>Anonymity</h2>
            <p>
              The Site allows any Donor to make an &quot;anonymous&quot; donation to a
              Cause. By choosing to be anonymous, the Site does not publish your name
              or image in the cause donor information. The Site would however provide
              your name, Pan Card details, address and email address to the Cause
              Raiser, only in case you opt for a receipt for the purpose of tax
              deduction.
            </p>
          </article>

          <article className="terms-section">
            <h2>Your Choices</h2>
            <p>
              You can opt-out of receiving our emails by following the unsubscribe
              instructions included in each such email or by contacting us at{' '}
              <ContactEmail />. You can modify or delete the Personal Information you
              have provided to us by logging in and updating your profile. We will
              retain your information only for as long as needed to provide you the
              Services or as long as necessary to comply with our legal obligations,
              resolve disputes, and enforce our agreements.
            </p>
          </article>

          <article className="terms-section">
            <h2>Third-Party Analytics</h2>
            <p>
              This Privacy Policy only addresses the use and disclosure of information
              by AMP India Foundation. We may use analytics services to help us analyze
              the information we have collected from you. These analytics services may
              use cookies, web beacons and other devices and technologies to track
              traffic data. Data that they collect typically includes, but is not
              limited to, your IP address, your ISP, the browser you use to visit our
              Site. This Privacy Policy does not apply to, and we are not responsible
              for, such technologies placed by third party analytics services.
            </p>
          </article>

          <article className="terms-section">
            <h2>Children</h2>
            <p>
              The Site is not directed at children under the age of 18, and does not
              consciously collect any Personal Information from children under the age
              of 18. We request that all users be at least 18 years old (or legal age
              in the respective jurisdiction) or have received parental consent and
              supervision when using the Service.
            </p>
          </article>

          <article className="terms-section">
            <h2>Consent</h2>
            <p>
              By using the Site and/ or by providing your information, you consent to
              the collection and use of the information you disclose on the Site in
              accordance with this Privacy Policy, including but not limited to your
              consent for sharing your information as per this Privacy Policy.
            </p>
          </article>

          <article className="terms-section">
            <h2>Modifications</h2>
            <p>
              We may occasionally modify the Privacy Policy. All changes will be
              effective upon posting on the Site. You can determine when the Privacy
              Policy was last revised by referring to the “Last Updated” legend at the
              top of the page. You agree to be bound by any such changes if you
              continue to use the Site after such changes have been posted. We may
              change, restrict access to, suspend or discontinue the Site or the
              Service, or any portion thereof, at any time.
            </p>
          </article>

          <article className="terms-section">
            <h2>Security</h2>
            <p>
              The Site has adopted reasonable security practices and procedures to
              ensure that the personal information collected is secure. Your personal
              information is held on secure servers. You agree that such measures are
              secured and adequate when you register with us/create an account. While
              it is our endeavor to take all reasonable and appropriate steps to keep
              secure any information which we hold about you and prevent unauthorized
              access, you acknowledge that the internet is not 100% secure and that we
              cannot provide any absolute assurance regarding the security of your
              personal information. We will not be liable in any way in relation to
              any breach of security or unintended loss or disclosure of information
              caused by us in relation to your personal information.
            </p>
            <p>
              Notwithstanding anything contained in this Privacy Policy or elsewhere,
              we shall not be held responsible for any loss, damage or misuse of your
              personal information, if such loss, damage, or misuse is attributable to
              a Force Majeure Event. “Force Majeure Event” shall mean any event that
              is beyond the reasonable control of us and shall include, without
              limitation, sabotage, fire, flood, explosion, acts of God, civil
              commotion, strikes or industrial action of any kind, riots, insurrection,
              war, acts of government, computer hacking, unauthorized access to a
              computer, computer system or computer network, computer crashes, breach
              of security and encryption (provided beyond the reasonable control of
              us), power or electricity failure or unavailability of adequate power or
              electricity.
            </p>
          </article>

          <article className="terms-section">
            <h2>Questions about Our Privacy Policy</h2>
            <p>
              If you have any questions or concerns regarding this Privacy Policy, you
              may contact us by e-mail at <ContactEmail />
            </p>
          </article>
        </motion.div>
      </section>
    </div>
  );
};

export default PrivacyPolicy;
