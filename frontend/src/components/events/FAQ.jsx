import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const faqData = [
  {
    id: 1,
    q: 'How do I register for an event?',
    a: 'You can register for upcoming events by clicking the "Register Now" or "Learn More" buttons on this page. For flagship events like job fairs and employment drives, registration links are shared via our website and social channels. Walk-in registrations may be available for select community events.',
  },
  {
    id: 2,
    q: 'Are events free to attend?',
    a: 'Yes. The vast majority of AMP India Foundation events — including job fairs, medical camps, education workshops, and skill training programs — are completely free for eligible participants. Our mission is to remove financial barriers to opportunity.',
  },
  {
    id: 3,
    q: 'Can students attend these events?',
    a: 'Absolutely. Many of our events are specifically designed for students and young graduates — including scholarship awareness workshops, career guidance sessions, mentorship summits, and Centres of Excellence programs. Students from underprivileged backgrounds are especially encouraged to participate.',
  },
  {
    id: 4,
    q: 'Can organizations collaborate on events?',
    a: 'Yes. Corporate partners, educational institutions, and NGOs can collaborate with AIF on employment drives, training programs, and community outreach initiatives. Please reach out through our Contact page to discuss partnership opportunities.',
  },
  {
    id: 5,
    q: 'How do I volunteer at events?',
    a: 'Professionals and student mentors can register as volunteers through our Volunteer page. You can contribute your skills in event coordination, career counselling, medical support, training delivery, or on-ground logistics based on your expertise.',
  },
];

const FAQ = () => {
  const [openId, setOpenId] = useState(null);

  const toggle = (id) => setOpenId(openId === id ? null : id);

  return (
    <section className="events-faq-section" aria-label="Frequently asked questions">
      <div className="ev-container">
        <header className="ev-section-header">
          <span className="ev-section-tag">Got Questions?</span>
          <h2 className="ev-section-title">
            Frequently Asked <span className="ev-accent">Questions</span>
          </h2>
          <p className="ev-section-subtitle">
            Everything you need to know about participating in AMP India Foundation events.
          </p>
        </header>

        <div className="events-faq-list">
          {faqData.map((faq) => {
            const isOpen = openId === faq.id;
            return (
              <motion.div
                key={faq.id}
                className={`events-faq-item ${isOpen ? 'expanded' : ''}`}
                layout
              >
                <button
                  type="button"
                  className="events-faq-trigger"
                  onClick={() => toggle(faq.id)}
                  aria-expanded={isOpen}
                >
                  <span className="events-faq-question">{faq.q}</span>
                  <motion.div
                    className="events-faq-icon"
                    animate={{ rotate: isOpen ? 135 : 0 }}
                    transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                      <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                  </motion.div>
                </button>

                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      className="events-faq-answer"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.24, ease: 'easeInOut' }}
                    >
                      <p>{faq.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FAQ;
