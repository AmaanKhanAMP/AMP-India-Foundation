"use client";

import Link from 'next/link';
import { motion } from 'framer-motion';

const TERMS_SECTIONS = [
  {
    id: 'revision',
    title: '1. REVISION/MODIFICATION OF THIS TERMS OF USE',
    paragraphs: [
      'AIF reserves the right, at its sole discretion, to modify or replace these Terms of Use, or change, suspend, or discontinue the Site and its services (including, but not limited to, the availability of any feature, database, or Content) at any time for any reason. AMP INDIA FOUNDATION (AIF) may also impose limits on certain features and services or restrict your access to parts or all the website without notice or liability. It is your responsibility to check the Terms of Use periodically for changes. Your continued use of the website following the posting of any changes to the Terms of Use constitutes acceptance of those changes.',
      'These terms and conditions apply in addition to any other terms and conditions that the Company or its affiliated organizations may ask you to sign at the time of making a contribution. The Company may ask you to sign specific terms and conditions at different point of activities on the website.',
    ],
  },
  {
    id: 'eligibility',
    title: '2. ELIGIBILITY TO USE THE SITE',
    intro:
      'Once you successfully register on www.ampindiafoundation.org or perform any activity which includes but not limited to browsing site content, filling forms, cause creation, payments or usage of any other native or third party services linked to this site, you :',
    bullets: [
      'You have the authority to enter into this agreement.',
      'Your decision to enter into this agreement and your use of the Platform will not violate any applicable law, regulation, or ordinance.',
      'Your decision to enter into this agreement and your use of the Platform will not infringe the rights of any third parties.',
      'All information you submit is truthful, current, complete and accurate and you will not misrepresent yourself to the public through your use of the Platform.',
      'You will never use the Platform, or any services we provide to you, in a manner that violates the law or the legal rights of a third party.',
      '6. You are over the age of majority in the jurisdiction in which you live (i.e. at least 18, and in some cases 19) or, if you are a minor over the age of 13, you may only use the Platform with the permission and supervision of your parent or legal guardian.',
      'You are not using another member’s account without her/his permission.',
      'Any other legal compliances that may arise from time to time in your jurisdiction.',
      'You have not been previously restricted, suspended or terminated by us.',
    ],
  },
  {
    id: 'password',
    title: '3. PASSWORD AND ACCOUNT SECURITY',
    paragraphs: [
      'You are solely responsible for maintaining the confidentiality of your password associated with your account. Accordingly, you understand and agree that you are solely responsible for any and all activities that occur under your account.',
    ],
    intro: 'You agree to:',
    bullets: [
      'immediately notify us at via contact@ampindiafoundation.org of any unauthorized use of account or any other breach of security, and',
      'ensure that you log off and exit from your account at the end of each session when accessing the Services. AMP INDIA FOUNDATION (AIF) will not be liable for any loss or damage arising from your failure to comply with this section.',
    ],
  },
  {
    id: 'external-links',
    title: '4. External Links',
    paragraphs: [
      'This Agreement applies only to the Site and the Services. In using the Services, you may be exposed to content and information, for example, data, text, files, information, usernames, graphics, images, photographs, profiles, audio, video, messages, services or links, from other users or third parties such as producers (“Third-Party Content”), either at the Site or through links to third-party websites or mobile applications. Because we do not review, monitor, operate or control any such Third-Party Content, you acknowledge and agree that we are not responsible for the availability of such websites or mobile applications and do not endorse and are not responsible or liable, directly or indirectly, for any content, advertising, products, services or other materials on or available from such websites or mobile applications. We make no guarantees, representations or warranties as to, and shall have no liability for, any content delivered by any third party, including, without limitation, the accuracy or subject matter of any content, or the use of any personal information you provide to any such website. You acknowledge and agree that use of such links is entirely at your own risk. We may discontinue links to any other website or mobile applications at any time and for any reason.',
      'We reserve the right to terminate your account, and your use of the Site at any time, for any reason whatsoever at our sole and absolute discretion.',
    ],
  },
  {
    id: 'social-login',
    title: '5. Registration with Social Media or any third-party accounts:',
    paragraphs: [
      'By choosing the social media login, you agree to give the Site, access to your Social Media account’s profile pictures and email id. You also allow our Site to create your account and use your profile picture as the profile picture on the Site account. The Site does not publish any content of your social media profile without your permission.',
    ],
  },
  {
    id: 'prohibited',
    title: '6. Prohibited Activities',
    paragraphs: [
      'By accessing and using the Site, you agree that you will not use the Site and the Service for any unlawful or prohibited purpose. You may not attempt, through any means, to gain unauthorized access to any part of the Site or the Service, other account, computer system or network connected to our server. AMP INDIA FOUNDATION (AIF) reserves the right, in its sole and absolute discretion, to monitor any and all use of the Site and remove any User Content at any time.',
    ],
    intro: 'Without limiting the foregoing, you will not use the Site and the Services to:',
    bullets: [
      'post or otherwise transmit any User Content that is unlawful, false, misleading, inaccurate, harmful, threatening, abusive, harassing, tortious, excessively violent, defamatory, vulgar, obscene, pornographic, libellous, invasive of another‘s privacy, hateful racially, ethnically or that encourages conduct that would be considered a criminal offense, give rise to civil liability, or is otherwise objectionable;',
      'depicts or advocates the use of illicit drugs;',
      'makes use of offensive language or images;',
      'you do not have a right to transmit under any law or under contractual or fiduciary relationships;',
      'poses or creates a privacy or security risk to any person;',
      'infringes any intellectual property or other proprietary rights of any party;',
      'are “junk mail,” “spam,” “chain letters,” “pyramid schemes,” “contests,” “sweepstakes,” or any other form of solicitation;',
      'contains software viruses or any other computer code, files or programs designed to interrupt, destroy or limit the functionality of any computer software or hardware or telecommunications equipment; or in the sole judgment of AMP INDIA FOUNDATION (AIF) is objectionable or which restricts or inhibits any other person from using or enjoying the Services, or which may expose AMP INDIA FOUNDATION (AIF) or its users to any harm or liability of any type;',
      'violate any applicable local, state, national, international or other law or regulation, or any order of a court, including without limitation, rules about intellectual property rights, the Internet, technology, data, email or privacy;',
      'access the Site and the Content from territories where such website and consent are illegal or strictly prohibited;',
      'further or promote any criminal activity or enterprise or provide instructional information about illegal activities;',
      'advertise or offer to sell or buy any goods or services for any business purpose that is not specifically authorized.',
      'interfere with, disrupt or damage the Services or servers or networks connected to the Services, or disobey any requirements, procedures, policies or regulations of networks connected to the Services, including, without limitation, through the use of viruses, cancel bots, Trojan horses, harmful code, flood pings, denial-of-service attacks, packet or IP spoofing, forged routing or electronic mail address information or similar methods or technology;',
      'use the Services to transmit, distribute, post or submit any information concerning any other person without their permission;',
      'harvest or collect email addresses or other contact information of other Users by electronic or other means without their consent;',
      '“stalk” or harass any other User or collect or store any information about any other User;',
      'obtain or attempt to access or otherwise obtain any materials or information through any means not intentionally made available or provided for through the Services;',
      'register for more than one user account or register for a user account on behalf of an individual other than yourself;',
      'transfer or sell your account and/or username to another party;',
      'impersonate any person or entity, or falsify or otherwise misrepresent yourself or your affiliation with any person or entity;',
      'use automated scripts to access, search collect information or otherwise interact with the Services (including without limitation robots, spiders or scripts) or use any robot, spider, other automatic device, or manual process to extract, “screen scrape,” monitor, “mine,” or copy any static or dynamic web page on the Site or the Content contained on any such web page for commercial use without our prior express written permission;',
      'other than with respect to your own User Content,',
      'use, reproduce, duplicate, copy, sell, resell or exploit the Content;',
      'compile a collection of Content, whether by manual methods, using bots, crawlers, or spiders, or otherwise; or',
      'otherwise remove any text, copyright or other proprietary notices contained in the Content;',
      'decipher, decompile, disassemble, reverse engineer, or otherwise attempt to derive any source code or underlying ideas or algorithms of any part of the Service, except to the extent applicable laws specifically prohibit such restriction;',
      'modify, translate, or otherwise create derivative works of any part of the Service; or',
      'advocate, encourage, or assist any third party in doing any of the foregoing.',
    ],
  },
  {
    id: 'further-representation',
    title: '7. FURTHER REPRESENTATION',
    paragraphs: [
      'You understand and agree that, if asked by AMP INDIA FOUNDATION (AIF), you will be required to provide supplementary information about yourself which include but not limited to your identity, Bank Account details, address, certifications or any kind of relevant documents as and when required. You authorize AMP INDIA FOUNDATION (AIF) to conduct background inquiries, due diligence as and when required.',
      'Furthermore, you agree that your use of the Service and reliance upon any of the materials available at the Site is solely at your own risk. While we take reasonable efforts to review applicants for compliance with the eligibility requirements, we do not verify, endorse or control any of the information on the Site (outside of official documentation). You also agree that AMP INDIA FOUNDATION (AIF) will not be responsible for any kind of financial transaction between users of this site or any parties mentioned on the site by any user except the intended use of the site as described on AIF.',
    ],
  },
  {
    id: 'indemnification',
    title: '8. INDEMNIFICATION',
    paragraphs: [
      'You agree to defend, indemnify and hold harmless AMP INDIA FOUNDATION (AIF) , our subsidiaries and affiliated companies, and their officers, employees, directors, contractors and agents, from and against any and all claims, causes of actions, suits or proceedings, as well as any and all losses, liabilities, damages, costs and expenses (including advocates’ fees) and all amounts paid in settlement arising out of, connected with, or accruing from:',
    ],
    bullets: [
      'your access to or/and use of the Site, the Services or the Content;',
      'your violation of this Agreement;',
      'your violation of any applicable law;',
      'your User Content, or',
      'your interaction with any User.',
    ],
    afterBullets: [
      'AMP INDIA FOUNDATION (AIF) may assume the exclusive defence and control of any matter for which you have agreed to indemnify AMP INDIA FOUNDATION (AIF) and you agree to assist and cooperate with AMP INDIA FOUNDATION (AIF) in the defence or settlement of any such matters.',
      'In no event shall AMP INDIA FOUNDATION (AIF) be liable for any indirect, special, incidental, consequential (including loss of data or information) or any other damages based on contract, tort (including negligence), indemnity, strict liability or otherwise.',
    ],
  },
  {
    id: 'intellectual-property',
    title: '9. INTELLECTUAL PROPERTY',
    paragraphs: [
      'The Site contains trademarks, service marks and domain names owned by AIF. Unless specifically noted that such trademarks, service marks or domain names belong to a third party, AMP INDIA FOUNDATION (AIF) owns all trademarks, service marks and domain names displayed on the Site, whether registered or unregistered, including but not limited to, the name AMP INDIA FOUNDATION (AIF), our logo, our design patterns and our other graphics, the website trade dress, and other indicia of origin of AMP INDIA FOUNDATION (AIF) products and services. The use of our intellectual property is strictly prohibited, unless we have granted our prior written consent.',
      'The content of the Site, including text, graphics, logos, button icons, images, audio clips, digital downloads, data compilations, and any other works of authorship, both individually and as they are compiled on the Site (the “Content”), and software used on this Site, are the property of AMP INDIA FOUNDATION (AIF) or third parties, and are protected by copyright and foreign intellectual property and related laws, rules and regulations. The Content includes both material owned and controlled by AMP INDIA FOUNDATION (AIF) or third parties, licensed to AIF, including User Content (as described below).',
    ],
    intro: 'You must not:',
    bullets: [
      'Modify copies of any materials from this site',
      'Use any illustrations, photographs, video or audio sequences, or any graphics separately from the accompanying text; or',
      'Delete or alter any copyright, trademark, or other proprietary rights notices from copies of materials from this site.',
    ],
    afterBullets: [
      'Any use of the Content not expressly permitted by this Agreement is a breach of this Agreement and may violate copyright, trademark and other laws. You agree to abide by all copyright notices, information, or restrictions contained in or attached to any of the Content.',
    ],
  },
  {
    id: 'consent-to-use-data',
    title: '10. CONSENT TO USE DATA',
    paragraphs: [
      'You logging into the website, that your data maybe collected, processed and use of technical data and related information (which for the avoidance of doubt are not user specific data), including but not limited to technical information. User specific data will only be collected, processed and used in accordance with any applicable law with respect to personal integrity.',
      'We endeavour to take all reasonable steps to protect your personal information. However, we cannot guarantee the security of any data you disclose online. You accept the inherent security risks of providing information and dealing online over the Internet and will not hold us responsible for any breach whatsoever of security unless this is due to our gross negligence.',
    ],
    subsections: [
      {
        title: '1. Storage of Information and Data',
        paragraphs: [
          'The Platform generates and stores data and addresses of Users in our servers, and the same is encrypted / password protected at all times. It shall be stored in our database for a period of five (5) years from the date the User accepts our Terms and Conditions and thereafter after the said period it shall be destroyed from our database entirely.',
        ],
      },
    ],
  },
  {
    id: 'no-endorsement',
    title: '11. NO ENDORSEMENT',
    paragraphs: [
      'AMP INDIA FOUNDATION (AIF) is not a party to any agreements between or among our users or third parties. No agency, partnership, joint venture, or employment is created as a result of the Terms or any user’s use of the Services.',
    ],
  },
  {
    id: 'payments',
    title: '12. PAYMENTS',
    paragraphs: [
      'Payment processing services for this are provided by payment provider(s) and are subject to their Account Agreement which includes the Service Agreement. Where applicable, the payment provider(s) may facilitate money transmission services. By agreeing to these Terms, you agree to be bound by their Connected Account Agreement, Services Agreement, and any other Terms and Condition introduced by them that may be modified and/or amended from time to time. As a condition of AMP INDIA FOUNDATION (AIF) enabling payment processing services through payment provider (s), you agree at all material times to provide us accurate and complete information about you and you irrevocably authorize AMP INDIA FOUNDATION (AIF) to share with payment provider(s) this information and transaction information related to the payment processing services provided by payment provider(s). AMP INDIA FOUNDATION (AIF) is not responsible for the performance of payment provider(s) at any given point of time.',
    ],
  },
  {
    id: 'user-rights',
    title: '13. USER RIGHTS',
    paragraphs: [
      'AIF and its associated NGOs will endeavour to the best of its ability to conduct background checks and due diligence on Applicants and if circumstances warrant it, on Donors as well. However, as a Member you are solely responsible for asking questions and conducting your own background check to the extent you feel is necessary before you make a Donation.',
      'You agree and understand that all Donations are made voluntarily and at your sole discretion and risk.',
    ],
  },
  {
    id: 'accessing-services',
    title: '14. ACCESSING OUR SERVICES',
    paragraphs: [
      'We will use reasonable efforts to make our Services available to you without any interruption. However, as our Services are also dependent on other third-party service providers, we do not guarantee that our Services will always be available or uninterrupted, especially when our third-party service provider is the Cause of the interruption. As such, we will not be liable to you if for any reason our Services are unavailable at any given time. Unless specified or agreed otherwise, we also reserve the right to suspend, withdraw, discontinue or change any part of our Services without prior notice.',
      'You are responsible for making all arrangements necessary for you to have access to our Services.',
      'You are also responsible for ensuring that all persons who access our Services through your internet connection or account are aware of these Terms and Conditions that they comply with them at all times.',
    ],
  },
  {
    id: 'support-obligation',
    title: '15. SUPPORT OBLIGATION',
    paragraphs: [
      'AMP INDIA FOUNDATION (AIF) INDIA FOUNDATION (AIF) shall be obliged to provide technical support services via contact@ampindiafoundation.org , pursuant to this agreement with respect to problems or issues encountered by the End User, in the form but not limited to email / help desk support and live chat.',
    ],
    intro: 'User also agrees to :',
    bullets: [
      'immediately notify team at contact@ampindiafoundation.org of any unauthorized use of account or any other breach of security, and',
      'ensure that you log off and exit from your account at the end of each session when accessing the Services. AMP INDIA FOUNDATION (AIF) will not be liable for any loss or damage arising from your failure to comply with this section.',
    ],
  },
  {
    id: 'disclaimer-of-warranties',
    title: '16. DISCLAIMER OF WARRANTIES',
    paragraphs: [
      'ALL INFORMATION AVAILABLE AT OUR SITE IS PROVIDED ON “AS IS,” “WITH ALL FAULTS” AND “AS AVAILABLE” BASIS AND, TO THE FULLEST EXTENT PERMISSIBLE PURSUANT TO APPLICABLE LAW, AMP INDIA FOUNDATION (AIF) DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT OR NON-INFRINGEMENT, AND WARRANTIES IMPLIED FROM A COURSE OF PERFORMANCE OR COURSE OF DEALING. YOU EXPRESSLY AGREE THAT YOUR USE OF OUR SITE AND THE SERVICES IS AT YOUR SOLE RISK. WE DO NOT WARRANT THAT THE SERVICES YOU OBTAIN THROUGH OUR SITE WILL MEET YOUR EXPECTATIONS AND REQUIREMENTS, BE UNINTERRUPTED OR ERROR-FREE, WILL BE AVAILABLE FOR USE, WILL BE OF A CERTAIN QUALITY, THAT DEFECTS WILL BE CORRECTED, OR THAT THE SITE OR THE SERVER ARE FREE OF VIRUSES OR OTHER HARMFUL COMPONENTS, OR THAT THE SITE OR THE TECHNOLOGY THAT MAKES IT AVAILABLE, ARE IMMUNE TO HACKER ACTIVITY, ELECTRONIC OR NON-ELECTRONIC TAMPERING, COMPUTER CRIME OR THEFT. WE DO NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OR THE RESULTS OF THE USE OF THE SITE AND SERVICES IN TERMS OF THEIR CORRECTNESS, ACCURACY, RELIABILITY, TIMELINESS, COMPLETENESS, CURRENTNESS, OR OTHERWISE. YOU (AND NOT WE) ASSUME THE ENTIRE COST OF ALL NECESSARY SERVICING, REPAIR, OR CORRECTION.',
    ],
  },
  {
    id: 'limitation-of-liability',
    title: '17. LIMITATION OF LIABILITY',
    paragraphs: [
      'IN NO EVENT SHALL AMP INDIA FOUNDATION (AIF) (FOR PURPOSES OF THIS SECTION, AMP INDIA FOUNDATION (AIF) OR “WE” INCLUDES OFFICERS, DIRECTORS, EMPLOYEES, CONSULTANTS, AGENTS, SUCCESSORS, REPRESENTATIVES OR AFFILIATES) BE LIABLE FOR ANY DIRECT, INDIRECT, PUNITIVE, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR OTHER DAMAGES ARISING OUT OF OR IN ANY WAY CONNECTED WITH YOUR USE OF THE SITE OR THE SERVICES OR WITH THE DELAY OR INABILITY TO USE THE SITE OR THE SERVICES, OR OTHERWISE ARISING OUT OF THE USE OF THE SITE AND THE SERVICES, WHETHER BASED ON CONTRACT, TORT, STRICT LIABILITY OR OTHERWISE, EVEN IF WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. THIS APPLIES, WITHOUT LIMITATION, TO ANY DAMAGES OR INJURY ARISING FROM ERROR, OMISSION, INTERRUPTION, DELETION, DEFECT, DELAY IN OPERATION OR TRANSMISSION OF INFORMATION THROUGH THE SITE, INJURY TO PERSONAL PROPERTY, BODILY INJURY OR EMOTIONAL DISTRESS, COMPUTER VIRUS, FILE CORRUPTION, COMMUNICATION-LINE FAILURE, NETWORK OR SYSTEM OUTAGE, OR THEFT, DESTRUCTION, UNAUTHORIZED ACCESS TO, ALTERATION OF, OR USE OF ANY RECORD. YOU SPECIFICALLY AGREE THAT WE WILL NOT BE LIABLE FOR ANY DEFAMATORY, OFFENSIVE OR ILLEGAL CONDUCT OF ANY USER OF THE SITE OR THE SERVICES. IN NO EVENT WILL OUR TOTAL LIABILITY TO YOU OR ANY THIRD PARTY FOR ANY DAMAGES, LOSSES, AND CAUSES OF ACTION RESULTING FROM YOUR USE OF THE SITE OR THE SERVICES, WHETHER IN CONTRACT, TORT (INCLUDING, BUT NOT LIMITED TO NEGLIGENCE), STRICT LIABILITY OR OTHERWISE.',
    ],
  },
  {
    id: 'warranties',
    title: '18. WARRANTIES',
    paragraphs: [
      'The Site is provided on an \'As Is\' basis and to the maximum extent permitted by applicable law and hereby expressly disclaims and excludes any and all warranties for the Site, whether written or oral, expressed or implied warranty of any kind, including but not limited to any warranties of performance, merchantability or fitness for a particular use or purpose. AMP INDIA FOUNDATION (AIF) does not warrant or assume responsibility for the accuracy or completeness of any information, text, graphics, links or other items contained within the Site. AMP INDIA FOUNDATION (AIF) makes no warranties with respect to any harm that may be Cause by the transmission of a computer virus, worm, time bomb, logic bomb, or other such computer malware program.',
      'We do not represent or warrant that the Site, or any part thereof, is appropriate or available for use in any particular jurisdiction. Those who choose to access the Site do so on their own initiative and at their own risk, and are responsible for complying with all local laws, rules and regulations, including laws regulating the export of data. We may limit the availability of the Site, in whole or in part, to any person, geographic area or jurisdiction that we choose, at any time and in our sole discretion. Accessing the Site is prohibited from territories where the Site’s Content is illegal.',
    ],
  },
  {
    id: 'termination',
    title: '19. RIGHT TO DISCONTINUE SERVICES; TERMINATION',
    paragraphs: [
      'AIF may, in our sole discretion and without liability to you or to any third party, with or without Cause, with or without notice, suspend or discontinue, temporarily or permanently, the Site, the and the Services (or any part thereof) and/or deactivate or cancel your account or Cause. You may also cancel your account at any time by sending us an email at contact@ampindiafoundation.org Termination may result in the forfeiture and destruction of all information associated with your account. You may terminate your account by following the instructions on the Service, but we may retain your account information after you terminate in accordance with our regulatory, accounting, and legal compliance procedures.',
      'YOU AGREE THAT WE WILL NOT BE LIABLE TO YOU OR ANY OTHER PARTY FOR TERMINATION OF YOUR ACCESS TO THE SITE OR THE SERVICES.',
      'All provisions of this Agreement that by their nature should survive termination shall survive termination, including, without limitation, ownership provisions, warranty disclaimers, indemnity and limitations of liability.',
    ],
    subsections: [
      {
        title: 'NO LEGAL ADVICE',
        paragraphs: [
          'Nothing contained in this Agreement or the Service constitutes legal advice. If you have any questions regarding your legal rights and legal obligations, you should consult with your lawyer.',
        ],
      },
      {
        title: '1. CONFIDENTIALITY',
        paragraphs: [
          'For purposes of this Terms of Use, the term “Confidential Information” means any information, technical data or know-how, including, without limitation, that is disclosed under this Terms of Use which is identified as confidential or proprietary at the time of disclosure, or which by its nature is reasonably to be considered as confidential or proprietary.',
        ],
      },
    ],
  },
  {
    id: 'miscellaneous',
    title: '21. MISCELLANEOUS',
    subsections: [
      {
        title: '24.1 Severability',
        paragraphs: [
          'If any provision of this Terms of Use or part thereof is invalid, this shall not Cause the entire Terms of Use to be invalid, instead, the Terms of Use or relevant provision, shall be reconciled, to the extent the invalidity materially affects any Party’s benefit or performance under the Terms of Use.',
          'This Agreement constitutes the entire agreement between the parties with respect to the subject matter of this Contract. All previous agreements, discussions, presentations, warranties, and conditions are combined in this document. There are no warranties, representations, conditions, or agreements, express or implied, between the parties, except those explicitly stated in this Agreement. This Agreement may be changed or amended only by a written document duly executed by the parties.',
        ],
      },
      {
        title: '24.2 English Language',
        paragraphs: [
          'In the event of a conflict between these Terms and a regional language version of our Terms of Use, the English language version of these Terms govern. All disputes, claims and Causes of action (and related proceedings) will be communicated in English.',
        ],
      },
      {
        title: '24.3 Update of Content:',
        paragraphs: [
          'We update the content on this Website from time to time, but its content is not necessarily always complete or up-to date. Any of the material on the Website may be out of date at any given time, and we are under no obligation to update such material.',
        ],
      },
      {
        title: '24.4 Dispute resolution',
        paragraphs: [
          'This Agreement shall be governed by and construed in accordance with the laws of India. In the event of a dispute, the courts of India shall have absolute and exclusive jurisdiction. If any term or provision of this Agreement where the User originates from is found by a court of competent jurisdiction to be invalid, illegal, or otherwise unenforceable, that term or provision will be deemed modified to the extent necessary to render such term or provision enforceable, and the terms and conditions hereunder will be construed and enforced accordingly, preserving to the fullest permissible extent the intent of this Agreement.',
          'Assignment; Waiver. You may not transfer, assign or delegate any of your rights, obligations or privileges hereunder; we may do so at any time. Any assignment of the foregoing other than as provided for in this section shall be null and void. No waiver of any provision or any right granted hereunder will be effective unless set forth in a written instrument signed by the waiving party. No waiver by either party of any breach or default hereunder shall be deemed a waiver of any subsequent breach or default.',
        ],
      },
      {
        title: '24.5 Your Comments and Concerns',
        paragraphs: [
          'This Website is operated by AMP INDIA FOUNDATION (AIF) Ground Floor, Plot 2, New Police Line, R. B. Chandorkar Marg, Near Jacob Circle Mumbai, Maharashtra, India, 400011, India. All notices should be sent to: contact@ampindiafoundation.org via email. All other feedback, comments, requests for technical support, and other communications relating to the Website should be directed to: contact@ampindiafoundation.org',
          'Note that questions, comments, suggestions, ideas, feedback or other information shared on this Website or to use (collectively “Submissions”) are not confidential and AMP INDIA FOUNDATION (AIF) is entitled to the unrestricted use and dissemination of Submissions for any purpose, commercial or otherwise, without acknowledgment or compensation to you.',
        ],
      },
    ],
  },
  {
    id: 'complete-agreement',
    title: '22. COMPLETE AGREEMENT',
    paragraphs: [
      'This Agreement, including any references mentioned and incorporated herein, together with such changes as may be subsequently made by us, constitutes the complete agreement between you and us, our subsidiaries, affiliated companies, licensors, and those third parties assisting in the operation of the Site with respect to the subject matter of this Agreement and supersedes all prior agreements and understandings, written or oral. This Agreement may not be amended by the user. This Agreement supersedes any previous quotations, correspondence, or other communications, written or oral, between you and us.',
    ],
  },
  {
    id: 'payment-details',
    title: 'Payment details',
    paragraphs: [
      'By providing a Donation, I agree to provide my name, email address, phone number, billing, and shipping addresses. I also agree to provide the authorized online payment gateway of the Site, necessary & required details of their credit and debit cards for making an online contribution, or the accurate address for cash/cheque pick up to the Site’s offline collection vendors. I agree to have enough funds or credit during making a donation.',
    ],
  },
  {
    id: 'contributor-information',
    title: 'Other contributor information',
    paragraphs: [
      'I also authorize the Site to publish my name and image (if logged in through Social Media) on the ‘Donors section of the project that is funded by me. However, if I choose to be “anonymous”, then none of my details shall be made public by the Site. Furthermore, by providing the Site my contact details, I agree to receive regular updates about the future crowdfunding campaigns on the Site through fortnightly newsletters. The Site can always choose to deactivate reception of the Site’s newsletter and other notifications.',
    ],
  },
  {
    id: 'site-owner-rights',
    title: 'Site Owner Rights',
    paragraphs: [
      'Site owner reserves the right to make changes in its technology platform at any time as it sees fit with due notification to users. www.aifindiafoundation.org will not tailor it’s offering to various cause creators or donors. Users are requested to keep themselves updated with all changes on platform and policies by regularly checking its FAQs or with the AMP INDIA FOUNDATION (AIF) directly.',
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
          <p className="terms-updated">Last Updated On: 9/12/2020</p>

          <div className="terms-acceptance">
            <h2>Disclaimer for Acceptance:</h2>
            <p>
              Please read these Terms of Use of website and Terms and Conditions carefully before
              using www.ampindiafoundation.org (hereafter referred as ‘website’ or the ‘Site’ or the
              ‘Platform’), owned by organisation AMP INDIA FOUNDATION (AIF) (hereafter referred as
              ‘AIF or ‘Company’) and its affiliated organisations/companies. This agreement sets
              forth the legally binding terms and conditions for your use of the site
              ampindiafoundation.org. By using the service/services in any manner, including, but not
              limited to, visiting or browsing the site or contributing content, information, or other
              materials or services to the site, payments, you agree to be bound by this agreement.
              These Terms of Use and associated Terms and Conditions apply to all who access this
              website, including but not limited to, Members, Volunteers and Donors. These Terms of
              Use apply to you even if you are a guest and not a registered user of the Website. If you
              do not agree to these Terms of Use or Terms and Conditions or the Privacy Policy, you
              must not access or use the Website.
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
              <a href="mailto:contact@ampindiafoundation.org">contact@ampindiafoundation.org</a>
            </p>
            <p>
              <span>Phone</span>
              <a href="tel:+918291101312">+91 8291101312</a>
            </p>
            <p>
              <span>Address</span>
              AMP India Foundation, 72, Clare Road, Byculla, Mumbai – 400008, Maharashtra, India
            </p>
          </div>
        </motion.div>
      </section>
    </div>
  );
};

export default Terms;
