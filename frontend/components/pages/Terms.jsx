"use client";

import Link from 'next/link';
import { motion } from 'framer-motion';

const CONTACT_EMAIL = 'contact@ampindiafoundation.org';
const OFFICE_ADDRESS =
  'Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008';

const TERMS_SECTIONS = [
  {
    id: 'revision',
    title: '1. Changes to these terms',
    paragraphs: [
      'AIF may revise or replace these terms at its discretion. It may also alter, pause, or withdraw the Site and the services on it, including any feature, database, or content, at any time and for any reason. AIF may limit particular features or services, or block access to some or all of the Site, without prior notice and without liability. Please review these terms from time to time. If you keep using the Site after a change is posted, you accept that change.',
      'These terms sit alongside any further terms AIF, or an organisation affiliated with AIF, asks you to accept when you contribute or when you use a particular part of the Site.',
    ],
  },
  {
    id: 'eligibility',
    title: '2. Who may use the Site',
    intro:
      'By registering on this Site, or by browsing it, submitting a form, creating an appeal where that option is offered, making a payment, or using any other service linked to the Site, you confirm that:',
    bullets: [
      'you have authority to enter this agreement;',
      'entering this agreement and using the Site will not break any law, regulation, or ordinance that applies to you;',
      'entering this agreement and using the Site will not infringe another person’s rights;',
      'everything you submit is true, current, complete, and accurate, and you will not present yourself falsely;',
      'you will not use the Site, or any service we provide, in a way that breaks the law or another person’s legal rights;',
      'you have reached the age of majority where you live (at least 18, and in some places 19); if you are over 13 but still a minor, you may use the Site only with a parent or legal guardian’s permission and supervision;',
      'you are not using someone else’s account without that person’s permission;',
      'you will meet any other legal requirement that applies where you live; and',
      'we have not previously restricted, suspended, or ended your access.',
    ],
  },
  {
    id: 'password',
    title: '3. Passwords and account security',
    paragraphs: [
      'If you have an account, you alone are responsible for keeping the password confidential and for everything done through that account.',
    ],
    intro: 'You agree to:',
    bullets: [
      `tell us straight away at ${CONTACT_EMAIL} if you suspect unauthorised use of an account or any other security problem; and`,
      'sign out at the end of each session. AIF is not liable for loss or damage that results from your failure to do so.',
    ],
  },
  {
    id: 'external-links',
    title: '4. Links and material from others',
    paragraphs: [
      'These terms govern only this Site and the services AIF offers on it. While using the Site you may see material from other users or from outside parties, including text, files, images, audio, video, messages, or links to other websites and apps. AIF does not review, run, or control that material. We do not promise that those sites or apps will stay available, we do not endorse them, and we are not responsible for their content, advertising, products, or services, or for how they use information you give them. You use those links at your own risk. We may remove a link at any time and for any reason.',
      'We may close your account and stop your use of the Site at any time, for any reason, at our sole discretion.',
    ],
  },
  {
    id: 'social-login',
    title: '5. Signing in through another service',
    paragraphs: [
      'Where the Site offers sign-in through a social network or another third-party account, choosing that option means you allow the Site to receive the profile image and email address from that account, to open an AIF account for you, and to use that image as your profile image here. The Site will not publish other material from that outside profile unless you permit it.',
    ],
  },
  {
    id: 'prohibited',
    title: '6. Conduct that is not allowed',
    paragraphs: [
      'You may use the Site only for lawful purposes. You must not try to reach any part of the Site, any account, or any connected system or network without permission. AIF may monitor use of the Site and may remove user material at any time.',
    ],
    intro: 'In particular, you will not use the Site to:',
    bullets: [
      'post material that is unlawful, untrue, misleading, harmful, threatening, abusive, harassing, tortious, excessively violent, defamatory, vulgar, obscene, pornographic, invasive of privacy, racially or ethnically hateful, or otherwise objectionable, or that encourages a crime or civil liability;',
      'depict or promote illegal drugs;',
      'use offensive language or images;',
      'send material you have no legal, contractual, or fiduciary right to send;',
      'create a privacy or security risk for anyone;',
      'infringe intellectual property or other proprietary rights;',
      'send junk mail, spam, chain letters, pyramid schemes, or unsolicited contests, sweepstakes, or other solicitations;',
      'introduce viruses or other code meant to interrupt, damage, or limit software, hardware, or communications equipment, or do anything that, in AIF’s judgment, is objectionable, interferes with others’ use of the services, or exposes AIF or its users to harm or liability;',
      'break any law, regulation, or court order, including rules on intellectual property, the internet, technology, data, email, or privacy;',
      'use the Site from a place where doing so is illegal;',
      'promote crime or explain how to carry out illegal activity;',
      'advertise or offer goods or services for a business purpose we have not authorised;',
      'interfere with or damage the services, servers, or connected networks, or ignore the rules of those networks, including by using viruses, bots, Trojan horses, harmful code, denial-of-service attacks, spoofing, or forged routing or email information;',
      'send information about another person without that person’s permission;',
      'collect other people’s email addresses or contact details without consent;',
      'stalk or harass another user, or store information about another user for that purpose;',
      'obtain material by a method the services do not intentionally provide;',
      'open more than one account, or open an account for someone else;',
      'sell or transfer your account or username;',
      'impersonate any person or organisation, or misstate your affiliation;',
      'use robots, spiders, scripts, or similar tools to access, search, collect from, or copy the Site for a commercial purpose without our prior written permission;',
      'except for your own user material, copy, sell, or otherwise exploit the content, assemble a collection of it by hand or by automated means, or remove text, copyright notices, or other proprietary notices from it;',
      'reverse engineer or try to extract source code or underlying algorithms, except where the law forbids that restriction;',
      'modify the services or create derivative works from them; or',
      'encourage or help anyone else to do any of the above.',
    ],
  },
  {
    id: 'further-representation',
    title: '7. Further information we may ask for',
    paragraphs: [
      'If AIF asks, you will supply additional information, which may include proof of identity, bank details, your address, certificates, or other relevant documents. You authorise AIF to make background and due-diligence enquiries when that is required.',
      'You rely on material on the Site at your own risk. We make reasonable efforts to check applicants against eligibility requirements, but we do not verify, endorse, or control information on the Site other than official AIF material. AIF is not responsible for financial dealings between users, or with anyone a user mentions on the Site, except for the uses of the Site that AIF itself describes.',
    ],
  },
  {
    id: 'indemnification',
    title: '8. Indemnity',
    paragraphs: [
      'You agree to defend, indemnify, and hold harmless AMP India Foundation, its subsidiaries and affiliated organisations, and their officers, employees, directors, contractors, and agents, against claims, proceedings, losses, liabilities, damages, costs, and expenses (including advocates’ fees) and amounts paid in settlement, arising out of:',
    ],
    bullets: [
      'your access to or use of the Site, the services, or the content;',
      'your breach of this agreement;',
      'your breach of applicable law;',
      'material you submit; or',
      'your dealings with another user.',
    ],
    afterBullets: [
      'AIF may take exclusive control of the defence and settlement of a matter you have agreed to cover, and you will cooperate with that defence or settlement.',
      'AIF is not liable for indirect, special, incidental, or consequential damages, including loss of data, whether the claim is in contract, tort (including negligence), indemnity, strict liability, or otherwise.',
    ],
  },
  {
    id: 'intellectual-property',
    title: '9. Intellectual property',
    paragraphs: [
      'The Site displays trade marks, service marks, and domain names. Unless a notice says a mark belongs to someone else, AMP India Foundation owns the marks and domain names shown on the Site, whether or not they are registered. That includes the name AMP India Foundation, the abbreviation AIF, our logo, design patterns, graphics, and the overall look of the Site. You may not use that intellectual property without our prior written consent.',
      'Text, graphics, logos, icons, images, audio, downloads, data compilations, and other works on the Site, together with the software that runs the Site, belong to AIF or to third parties and are protected by copyright and related laws. This includes material AIF owns, material it licenses, and user material.',
    ],
    intro: 'You must not:',
    bullets: [
      'alter copies of material taken from the Site;',
      'separate illustrations, photographs, video, audio, or graphics from the text that accompanies them; or',
      'remove or change a copyright, trade mark, or other proprietary notice on material taken from the Site.',
    ],
    afterBullets: [
      'Any use that this agreement does not expressly allow is a breach and may also infringe copyright, trade mark, or other law. You must respect every copyright notice or restriction attached to the content.',
    ],
  },
  {
    id: 'consent-to-use-data',
    title: '10. Use and storage of data',
    paragraphs: [
      'When you use the Site, technical data and related information that does not identify you as an individual may be collected and processed. Information that does identify you is collected, processed, and used only as the law on personal data allows.',
      'We take reasonable steps to protect personal information. We cannot guarantee the security of information you send over the internet. You accept that risk and will not hold us responsible for a security breach unless it is caused by our gross negligence.',
    ],
    subsections: [
      {
        title: 'How long information is kept',
        paragraphs: [
          'The Site generates and stores user data and addresses on our servers. That information stays encrypted or password-protected. It is kept for five (5) years from the date you accept these terms, and is then removed from our database entirely.',
        ],
      },
    ],
  },
  {
    id: 'no-endorsement',
    title: '11. No agency or endorsement',
    paragraphs: [
      'AIF is not a party to agreements made between users, or between a user and a third party. These terms, and your use of the services, do not create an agency, partnership, joint venture, or employment relationship.',
    ],
  },
  {
    id: 'payments',
    title: '12. Payments',
    paragraphs: [
      'Payments are processed by one or more payment providers under their own agreements, which include a connected-account agreement and a services agreement, and any other terms those providers introduce. Where relevant, a provider may also transmit funds. By accepting these terms you also accept the provider’s terms, as they may be updated. You must give AIF accurate and complete information, and you irrevocably authorise AIF to share that information, and related transaction information, with the provider so the payment can be completed. AIF is not responsible for how a payment provider performs.',
    ],
  },
  {
    id: 'user-rights',
    title: '13. Donations and your own checks',
    paragraphs: [
      'AIF, and organisations associated with it, will try to carry out background checks and due diligence on applicants and, where the circumstances call for it, on donors. Even so, before you donate you are responsible for asking the questions and making the checks you consider necessary.',
      'Every donation is voluntary. You make it at your own discretion and risk.',
    ],
  },
  {
    id: 'accessing-services',
    title: '14. Availability of the Site',
    paragraphs: [
      'We will make reasonable efforts to keep the services available. Because we also depend on third-party providers, we do not promise uninterrupted access, particularly when a provider causes the interruption. We are not liable if the services are unavailable. Unless we have agreed otherwise, we may suspend, withdraw, or change any part of the services without prior notice.',
      'You are responsible for the equipment and connection you need to reach the Site.',
      'You are also responsible for making sure that anyone who uses the services through your connection or account knows these terms and follows them.',
    ],
  },
  {
    id: 'support-obligation',
    title: '15. Support',
    paragraphs: [
      `AIF will provide support for problems you meet while using the Site, by email at ${CONTACT_EMAIL}. A help desk or live chat applies only where AIF actually offers that channel.`,
    ],
    intro: 'You also agree to:',
    bullets: [
      `tell us at ${CONTACT_EMAIL} as soon as you know of unauthorised use of an account or any other security breach; and`,
      'sign out at the end of each session. AIF is not liable for loss or damage caused by a failure to do so.',
    ],
  },
  {
    id: 'disclaimer-of-warranties',
    title: '16. Disclaimer of warranties',
    paragraphs: [
      'ALL INFORMATION ON THE SITE IS PROVIDED ON AN “AS IS”, “WITH ALL FAULTS”, AND “AS AVAILABLE” BASIS. TO THE FULLEST EXTENT ALLOWED BY LAW, AMP INDIA FOUNDATION DISCLAIMS EVERY WARRANTY, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT, AND NON-INFRINGEMENT, AND ANY WARRANTY ARISING FROM A COURSE OF PERFORMANCE OR DEALING. YOU USE THE SITE AND THE SERVICES AT YOUR SOLE RISK. WE DO NOT WARRANT THAT THE SERVICES WILL MEET YOUR NEEDS, THAT THEY WILL BE UNINTERRUPTED OR ERROR-FREE, THAT THEY WILL REMAIN AVAILABLE OR BE OF A PARTICULAR QUALITY, THAT DEFECTS WILL BE FIXED, OR THAT THE SITE OR ITS SERVERS ARE FREE OF VIRUSES OR OTHER HARMFUL COMPONENTS, OR IMMUNE TO HACKING, TAMPERING, COMPUTER CRIME, OR THEFT. WE MAKE NO WARRANTY ABOUT THE CORRECTNESS, ACCURACY, RELIABILITY, TIMELINESS, OR COMPLETENESS OF THE SITE OR THE SERVICES. YOU BEAR THE ENTIRE COST OF ANY SERVICING, REPAIR, OR CORRECTION YOU NEED.',
    ],
  },
  {
    id: 'limitation-of-liability',
    title: '17. Limit of liability',
    paragraphs: [
      'TO THE EXTENT THE LAW ALLOWS, AMP INDIA FOUNDATION AND, FOR THIS SECTION, ITS OFFICERS, DIRECTORS, EMPLOYEES, CONSULTANTS, AGENTS, SUCCESSORS, REPRESENTATIVES, AND AFFILIATES, WILL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, PUNITIVE, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR OTHER DAMAGES CONNECTED WITH YOUR USE OF THE SITE OR THE SERVICES, OR WITH ANY DELAY OR INABILITY TO USE THEM, WHETHER IN CONTRACT, TORT, STRICT LIABILITY, OR OTHERWISE, EVEN IF WE HAVE BEEN TOLD THAT SUCH DAMAGES ARE POSSIBLE. THIS INCLUDES DAMAGE OR INJURY FROM ERROR, OMISSION, INTERRUPTION, DELETION, DEFECT, DELAY, PERSONAL-PROPERTY DAMAGE, BODILY INJURY, EMOTIONAL DISTRESS, VIRUSES, FILE CORRUPTION, COMMUNICATIONS FAILURE, OUTAGE, THEFT, DESTRUCTION, OR UNAUTHORISED ACCESS TO OR ALTERATION OF A RECORD. WE ARE NOT LIABLE FOR DEFAMATORY, OFFENSIVE, OR ILLEGAL CONDUCT BY A USER. THIS SECTION LIMITS OUR TOTAL LIABILITY TO YOU OR ANY THIRD PARTY FOR DAMAGES, LOSSES, AND CAUSES OF ACTION ARISING FROM YOUR USE OF THE SITE OR THE SERVICES, IN CONTRACT, TORT (INCLUDING NEGLIGENCE), STRICT LIABILITY, OR OTHERWISE.',
    ],
  },
  {
    id: 'warranties',
    title: '18. No warranty of fitness or local suitability',
    paragraphs: [
      'The Site is provided “as is”. To the maximum extent the law allows, AIF excludes every warranty, written or oral, express or implied, including any warranty of performance, merchantability, or fitness for a particular purpose. AIF does not warrant that information, text, graphics, or links on the Site are accurate or complete, and it gives no warranty against harm from a virus, worm, time bomb, logic bomb, or similar malicious program.',
      'We do not warrant that the Site is appropriate or available in every place. If you choose to open it, you do so on your own initiative and at your own risk, and you must comply with local law, including rules on exporting data. We may restrict the Site, in whole or in part, for any person, area, or jurisdiction, at any time. You must not access the Site from a territory where its content is illegal.',
    ],
  },
  {
    id: 'termination',
    title: '19. Stopping the services',
    paragraphs: [
      `AIF may, at its sole discretion and without liability to you or anyone else, with or without reason and with or without notice, suspend or discontinue the Site or the services, temporarily or permanently, and may deactivate or cancel your account or an appeal. You may ask us to close an account by emailing ${CONTACT_EMAIL}. Closure can mean that information linked to the account is forfeited and deleted. You may also close an account by following any instructions the service provides. We may still keep account information afterwards where our regulatory, accounting, or legal duties require it.`,
      'YOU AGREE THAT WE ARE NOT LIABLE TO YOU OR ANYONE ELSE FOR ENDING YOUR ACCESS TO THE SITE OR THE SERVICES.',
      'Provisions that by their nature should continue after this agreement ends will continue, including provisions on ownership, warranty disclaimers, indemnity, and limits of liability.',
    ],
  },
  {
    id: 'no-legal-advice',
    title: '20. No legal advice',
    paragraphs: [
      'Nothing in these terms or on the Site is legal advice. If you need advice about your rights or duties, speak to your own lawyer.',
    ],
  },
  {
    id: 'confidentiality',
    title: '21. Confidential information',
    paragraphs: [
      'In these terms, “confidential information” means information, technical data, or know-how disclosed under these terms that is marked confidential or proprietary when disclosed, or that a reasonable person would treat as confidential or proprietary.',
    ],
  },
  {
    id: 'miscellaneous',
    title: '22. General',
    subsections: [
      {
        title: 'Severability',
        paragraphs: [
          'If a provision of these terms is invalid, the rest of the terms remain in force. The invalid provision will be read down only so far as needed where the invalidity materially affects a party’s benefit or performance.',
          'These terms are the entire agreement on their subject. They replace earlier agreements, discussions, presentations, warranties, and conditions. There are no warranties or agreements between the parties except those written here. A change must be in a written document signed by the parties.',
        ],
      },
      {
        title: 'English language',
        paragraphs: [
          'If these terms conflict with a version in another language, the English text prevails. Disputes, claims, and related proceedings will be conducted in English.',
        ],
      },
      {
        title: 'Site content may change',
        paragraphs: [
          'We update the Site from time to time, but a page may be incomplete or out of date. We are not obliged to update every item of material.',
        ],
      },
      {
        title: 'Disputes, assignment, and waiver',
        paragraphs: [
          'These terms are governed by the laws of India. The courts of India have exclusive jurisdiction. If a court where the user is based finds a term invalid or unenforceable, that term will be modified only as far as necessary to make it enforceable, and the rest will be read so as to preserve the intent of this agreement as far as the law allows.',
          'You may not transfer or assign your rights or duties under these terms. AIF may do so at any time. Any other assignment is void. A waiver is effective only if it is in a written instrument signed by the party giving it. Waiving one breach is not a waiver of a later breach.',
        ],
      },
      {
        title: 'Notices and feedback',
        paragraphs: [
          `This website is operated by AMP India Foundation (AIF), ${OFFICE_ADDRESS}. Notices, feedback, and requests for technical support should be sent to ${CONTACT_EMAIL}.`,
          'Questions, comments, suggestions, ideas, and other feedback you send through the Site or to us (“submissions”) are not confidential. AIF may use and share submissions for any purpose, including a commercial purpose, without paying you or naming you.',
        ],
      },
    ],
  },
  {
    id: 'complete-agreement',
    title: '23. Whole agreement',
    paragraphs: [
      'This agreement, including the documents it refers to, and any later changes we make, is the complete agreement between you and AIF, its subsidiaries, affiliated organisations, licensors, and third parties who help operate the Site. It replaces all earlier written or oral understandings on the same subject. You cannot amend it yourself. It also replaces earlier quotations, correspondence, and other communications between you and us.',
    ],
  },
  {
    id: 'payment-details',
    title: '24. Information given with a donation',
    paragraphs: [
      'When I donate, I agree to provide my name, email address, phone number, and billing and shipping addresses. I also agree to give the Site’s authorised online payment gateway the card or other payment details it requires, or, where an offline collection is offered, an accurate address for collection of cash or a cheque. I agree that sufficient funds or credit will be available when the donation is made.',
    ],
  },
  {
    id: 'contributor-information',
    title: '25. How a donor may be identified',
    paragraphs: [
      'Where the Site shows a donor list for a project I have funded, I authorise publication of my name and, if I signed in through a social-media account, my image. If I choose to remain anonymous, the Site will not publish those details. By giving my contact details I also agree to receive updates about later fundraising appeals, including a newsletter sent about once a fortnight, unless I opt out. AIF may stop those messages at any time.',
    ],
  },
  {
    id: 'site-owner-rights',
    title: '26. Changes to the platform',
    paragraphs: [
      'AIF may change the technology that runs the Site when it considers that appropriate, and will give users due notice. The Site is not customised for individual appeal organisers or donors. Please check the Site, including any frequently asked questions, or contact AIF, so that you are aware of changes to the platform and to these policies.',
    ],
  },
];

function TermsSection({ section }) {
  return (
    <article id={section.id} className="terms-section">
      <h2>{section.title}</h2>
      {(section.paragraphs || []).map((text, index) => (
        <p key={`${section.id}-p-${index}`}>{text}</p>
      ))}
      {section.intro ? <p>{section.intro}</p> : null}
      {section.bullets?.length ? (
        <ul className="terms-list">
          {section.bullets.map((item, index) => (
            <li key={`${section.id}-li-${index}`}>{item}</li>
          ))}
        </ul>
      ) : null}
      {(section.afterBullets || []).map((text, index) => (
        <p key={`${section.id}-ap-${index}`}>{text}</p>
      ))}
      {(section.subsections || []).map((sub) => (
        <div key={sub.title} className="terms-subsection">
          <h3>{sub.title}</h3>
          {(sub.paragraphs || []).map((text, index) => (
            <p key={`${section.id}-${sub.title}-${index}`}>{text}</p>
          ))}
        </div>
      ))}
    </article>
  );
}

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
};

const Terms = () => {
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
            <span>Terms &amp; Conditions</span>
          </nav>
          <h1 className="terms-hero-title">Terms &amp; Conditions</h1>
          <p className="terms-hero-subtitle">
            Please read these Terms &amp; Conditions carefully before using the AMP India Foundation
            website.
          </p>
        </motion.div>
      </header>

      <section className="terms-content-section">
        <motion.div
          className="terms-content-card"
          initial={fadeUp.initial}
          animate={fadeUp.animate}
          transition={{ duration: 0.5, ease: 'easeOut', delay: 0.08 }}
        >
          <h2 className="terms-document-title">
            TERMS OF USE OF THE WEBSITE/SITE/ PLATFORM
          </h2>
          <p className="terms-updated">Last Updated On: 13 October 2026</p>

          <div className="terms-acceptance">
            <h2>Disclaimer for Acceptance:</h2>
            <p>
              Please read these terms before you use the website of AMP India Foundation
              (&quot;AIF&quot; or the &quot;Foundation&quot;). In these terms, that website is called
              the Site or the Platform. This agreement is legally binding. It covers every way you
              use the Site, including browsing it, sending content or information, and making a
              payment. It applies to members, volunteers, donors, and anyone else who opens the
              Site, including guests who have not registered. If you do not accept these terms, the
              related conditions, or the Privacy Policy, do not use the Site.
            </p>
          </div>

          <h2 className="terms-general-heading">General Terms of Use:</h2>

          {TERMS_SECTIONS.map((section) => (
            <TermsSection key={section.id} section={section} />
          ))}
        </motion.div>

        <motion.div
          className="terms-help-card"
          initial={fadeUp.initial}
          whileInView={fadeUp.animate}
          viewport={{ once: true, amount: 0.25 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
        >
          <h2>Need help?</h2>
          <p>
            If you have any questions regarding these Terms &amp; Conditions, please contact AMP
            India Foundation.
          </p>
          <div className="terms-help-details">
            <p>
              <span>Email</span>
              <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
            </p>
            <p>
              <span>Phone</span>
              <a href="tel:+918291101312">+91 8291101312</a>
            </p>
            <p>
              <span>Address</span>
              AMP India Foundation, {OFFICE_ADDRESS}
            </p>
          </div>
        </motion.div>
      </section>
    </div>
  );
};

export default Terms;
