"use client";

import  { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { Eye, Rocket } from 'lucide-react';

import aboutOpportunitySeminar from '@/src/assets/about-opportunity-seminar.png';
import aboutOpportunityCareerChart from '@/src/assets/about-opportunity-career-chart.png';
import aboutHeroBanner from '@/src/assets/about-hero.png';

const MotionLink = motion.create(Link);

const assetSrc = (image) => (typeof image === 'string' ? image : image?.src);
const aboutSeminarSrc = assetSrc(aboutOpportunitySeminar);
const aboutCareerChartSrc = assetSrc(aboutOpportunityCareerChart);
const aboutHeroSrc = assetSrc(aboutHeroBanner);


const About = () => {
  const [activeBadge, setActiveBadge] = useState(null);
  const [openFaq, setOpenFaq] = useState(null);

  /* Focus Areas → existing 5 capsules (same count) */
  const avenues = [
    {
      id: 1,
      title: 'Education',
      desc: 'Supporting deserving students through scholarships, career guidance, mentoring, digital learning and skill development to help them achieve their educational goals.',
    },
    {
      id: 2,
      title: 'Employment',
      desc: 'Preparing youth for successful careers through employability training, job fairs, placement support and industry partnerships.',
    },
    {
      id: 3,
      title: 'Skill Development',
      desc: 'Providing vocational and technical training that improves employability and creates opportunities for self-employment.',
    },
    {
      id: 4,
      title: 'Healthcare',
      desc: 'Extending medical assistance, health awareness programmes, medical camps and emergency support to individuals and families in need.',
    },
    {
      id: 5,
      title: 'Empowerment',
      desc: 'Promoting sustainable livelihoods, financial inclusion, entrepreneurship and social development initiatives that strengthen communities.',
    },
  ];

  /* Core Values → existing 3 cards only (Inclusiveness & Collaboration ignored — no extra cards) */
  const features = [
    {
      id: "feat-1",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M12 8v4l3 3" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      title: "Compassion",
      desc: "We serve every individual with empathy, dignity and respect."
    },
    {
      id: "feat-2",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" strokeLinecap="round"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" strokeLinecap="round"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75" strokeLinecap="round"/>
        </svg>
      ),
      title: "Integrity",
      desc: "We maintain the highest standards of honesty, transparency and accountability in everything we do."
    },
    {
      id: "feat-3",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="8" r="7" />
          <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" strokeLinejoin="round"/>
        </svg>
      ),
      title: "Excellence",
      desc: "We continuously strive to deliver impactful programmes with professionalism and quality."
    }
  ];

  /* What We Do → existing 5 numbered rows */
  const objectives = [
    {
      num: "01",
      title: "Education & Scholarships",
      desc: "Helping deserving students continue their education through scholarships, educational support, mentoring and career guidance.",
      highlighted: false
    },
    {
      num: "02",
      title: "Employability & Career Development",
      desc: "Organising employability training programmes, career counselling sessions, job drives and Mega Job Fairs to connect youth with employment opportunities.",
      highlighted: true 
    },
    {
      num: "03",
      title: "Skill Development",
      desc: "Providing vocational and technical training that prepares individuals for today's job market and encourages entrepreneurship.",
      highlighted: false
    },
    {
      num: "04",
      title: "Healthcare & Medical Support",
      desc: "Supporting health camps, emergency medical assistance and healthcare initiatives for underprivileged individuals and families.",
      highlighted: true
    },
    {
      num: "05",
      title: "Community Development",
      desc: "Implementing programmes that promote self-reliance, financial empowerment and the overall well-being of underserved communities.",
      highlighted: false
    }
  ];

  /* FAQ → existing accordion; 5 approved Q&As (6th dummy removed — no invented content) */
  const faqData = [
    {
      id: 1,
      q: "What does AMP India Foundation do?",
      a: "AMP India Foundation works in the areas of education, employment, skill development, healthcare and community empowerment to improve the lives of underprivileged individuals across India."
    },
    {
      id: 2,
      q: "Who can benefit from your programmes?",
      a: "Students, job seekers, women, youth, families and disadvantaged communities from across India can benefit from our various initiatives, subject to the eligibility criteria of each programme."
    },
    {
      id: 3,
      q: "How can I support the Foundation?",
      a: "You can support our mission by making a donation, volunteering your time and skills, mentoring students, partnering with us, or helping spread awareness about our work."
    },
    {
      id: 4,
      q: "Can I volunteer with AMP India Foundation?",
      a: "Yes. We welcome students, professionals, entrepreneurs and retirees who wish to contribute their time, expertise and experience towards social development."
    },
    {
      id: 5,
      q: "Are your programmes open to everyone?",
      a: "Yes. Our initiatives are implemented without discrimination based on caste, community, creed, gender or religion."
    }
  ];

  const toggleFaq = (id) => {
    setOpenFaq(openFaq === id ? null : id);
  };

  const resolvedHero = aboutHeroSrc;
  const resolvedSeminar = aboutSeminarSrc;
  const resolvedChart = aboutCareerChartSrc;
  const resolvedAvenues = avenues;
  const resolvedFeatures = features;
  const resolvedObjectives = objectives;
  const resolvedFaqs = faqData;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 60, damping: 16 } }
  };

  const leftPanelVariants = {
    hidden: { opacity: 0, x: -40 },
    visible: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 50, damping: 15 } }
  };

  return (
    <div className="about-page-canvas">
      {/* ================= HERO BANNER ================= */}
      <header
        className="about-hero-banner"
        style={{ backgroundImage: `url(${resolvedHero})` }}
      >
        <div className="about-hero-gradient" aria-hidden="true" />
        <div className="hero-overlay-mesh"></div>
        <div className="hero-content-wrapper">  
         
          <h1 className="hero-title">
            Empowering Lives.{' '}
            <span className="hero-gradient-text">Transforming Communities.</span>
          </h1>
          <div className="hero-description"><p>At AMP India Foundation, we believe that every individual deserves an opportunity to learn, earn and live with dignity. Through education, employment, healthcare, skill development and community empowerment, we work to create lasting change for underprivileged communities across India.</p>
          </div>
          <div className="hero-divider"></div>
        </div>
      </header>

      {/* ================= MAIN CONTENT SECTION ================= */}
      <motion.section 
        className="about-content-sec"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={containerVariants}
      >
        <div className="about-max-wrapper">
          <motion.div className="image-canvas-column" variants={itemVariants}>
            <div className="image-base-accent-box" />
            <div className="overlap-frame-card frame-top-left">
              <img src={resolvedSeminar} alt="Career guidance seminar" />
              <div className="image-overlay-gradient"></div>
            </div>
            <div className="overlap-frame-card frame-bottom-right">
              <img src={resolvedChart} alt="Career guidance workshop" />
              <div className="image-overlay-gradient"></div>
            </div>
          </motion.div>

          <motion.div className="text-editorial-column" variants={itemVariants}>
            <span className="editorial-tag">Who We Are</span>
            <h2 className="editorial-heading">
              Creating Opportunities for a <span className="gradient-text">Better Tomorrow</span>
            </h2>

            <div className="editorial-stats-bar">
              <div className="stat-item">
                <span className="stat-value">5+</span>
                <span className="stat-label">Core Initiatives</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">Pan-India</span>
                <span className="stat-label">Program Scope</span>
              </div>
            </div>

            <div className="editorial-description-wrapper">
              <p className="paragraph-lead">
                <strong>AMP India Foundation (AIF)</strong> is a registered non-profit organization committed to empowering underprivileged individuals and communities through sustainable development initiatives.
              </p>
              <p className="paragraph-body">
                Established by a network of committed professionals and social leaders, AIF works across India to improve access to quality education, meaningful employment, healthcare, skill development and economic opportunities.
              </p>

              <div className="about-vm-grid">
                <motion.article
                  className="about-vm-card"
                  variants={itemVariants}
                  whileHover={{ y: -3 }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                >
                  <div className="about-vm-card-overlay" aria-hidden="true" />
                  <div className="about-vm-card-inner">
                    <div className="about-vm-card-heading">
                      <div className="about-vm-icon-wrap" aria-hidden="true">
                        <Eye size={16} strokeWidth={2} />
                      </div>
                      <h3 className="about-vm-card-title">Our Vision</h3>
                    </div>
                    <p className="about-vm-card-body">
                      To build an inclusive India where every individual has equal opportunities to
                      learn, earn and live with dignity.
                    </p>
                  </div>
                </motion.article>

                <motion.article
                  className="about-vm-card"
                  variants={itemVariants}
                  whileHover={{ y: -3 }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                >
                  <div className="about-vm-card-overlay" aria-hidden="true" />
                  <div className="about-vm-card-inner">
                    <div className="about-vm-card-heading">
                      <div className="about-vm-icon-wrap" aria-hidden="true">
                        <Rocket size={16} strokeWidth={2} />
                      </div>
                      <h3 className="about-vm-card-title">Our Mission</h3>
                    </div>
                    <p className="about-vm-card-body">
                      To empower underprivileged communities through education, employment,
                      healthcare, skill development, mentorship and sustainable livelihood
                      initiatives by connecting professionals, volunteers, donors and institutions
                      for lasting social impact.
                    </p>
                  </div>
                </motion.article>
              </div><br />

              <div className="capsule-container">
                <p className="capsule-instruction">Click an initiative to explore our scope:</p>
                <div className="capsule-row">
                  {resolvedAvenues.map((item) => (
                    <button
                      key={item.id}
                      className={`capsule-badge ${activeBadge?.id === item.id ? 'active' : ''}`}
                      onClick={() => setActiveBadge(activeBadge?.id === item.id ? null : item)}
                    >
                      {item.title}
                    </button>
                  ))}
                </div>
                <div className={`badge-description-panel ${activeBadge ? 'visible' : ''}`}>
                  {activeBadge && <p><strong>{activeBadge.title}:</strong> {activeBadge.desc}</p>}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* ================= 3-COLUMN BANNER: WHY CHOOSE AIF ================= */}
      <motion.section 
        className="why-choose-banner-section"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={containerVariants}
      >
        <div className="banner-container">
          <motion.div className="banner-intro-header" variants={itemVariants}>
            <span className="section-mini-tag text-center">Our Core Values</span>
            <h2 className="section-main-heading text-center">Our Core Values</h2>
          </motion.div>

          <div className="banner-features-grid">
            {resolvedFeatures.map((feat, index) => (
              <motion.div 
                key={feat.id} 
                className="banner-feature-item"
                variants={itemVariants}
                style={{ '--card-idx': index }}
                whileHover={{ y: -5 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <div className="banner-item-icon-box">
                  {feat.icon}
                </div>
                <h3 className="banner-item-title">{feat.title}</h3>
                <p className="banner-item-desc">{feat.desc}</p>
                <div className="banner-item-animated-underline"></div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* ================= ASYMMETRIC SPLIT: WHAT WE DO SECTION ================= */}
      <section className="wwd-canvas">
        <motion.div 
          className="wwd-max-container"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.15 }}
          variants={containerVariants}
        >
          {/* LEFT SIDEBAR PANEL */}
          <motion.div className="wwd-left-sidebar" variants={leftPanelVariants}>
            <div className="wwd-sticky-box">
              <span className="wwd-mini-tag">Overview</span>
              <h2 className="wwd-main-heading">What We Do</h2>
              <p className="wwd-intro-text">
                AMP India Foundation works across multiple areas of social development to create opportunities and improve lives.
              </p>
              <div className="wwd-badge-row">
                <span className="wwd-line-accent"></span>
                <span className="wwd-badge-text">Non-profit organization</span>
              </div>
            </div>
          </motion.div>

          {/* RIGHT SIDE ALTERNATING STRIPS */}
          <div className="wwd-right-content">
            {resolvedObjectives.map((item) => (
              <motion.div 
                key={item.num} 
                className={`wwd-item-row ${item.highlighted ? 'shaded-bg' : ''}`}
                variants={itemVariants}
                whileHover={{ x: 12 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
              >
                <div className="wwd-num-col">
                  <span>{item.num}</span>
                </div>
                <div className="wwd-text-col">
                  <h3>{item.title}</h3>
                  <p>{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* <div className="wwd-blueprint-footer">
          <span className="wwd-copyright">© AMP INDIA FOUNDATION</span>
          <div className="wwd-deco-dots">
            <span></span><span></span><span></span><span></span>
          </div>
        </div> */}
      </section>

      {/* ================= FAQ SECTION ================= */}
      <motion.section 
        className="faq-section-canvas"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.15 }}
        variants={containerVariants}
      >
        <div className="faq-main-wrapper">
          
          <div className="faq-header-split-block">
            <div className="faq-header-left">
              <span className="faq-pill-tag">Frequently Asked Questions</span>
              <h2 className="faq-section-title">Helping you Understand Our Work Better</h2>
            </div>
            <div className="faq-header-right">
              <p className="faq-header-intro">
                We've gathered answers to the questions we hear most, making it easy for you to learn about our work, values, and the structural impact we create together.
              </p>
              <MotionLink
                href="/contact"
                className="faq-cta-btn"
                whileHover={{ y: -2, boxShadow: "0 6px 20px rgba(30, 74, 138, 0.25)" }}
                whileTap={{ scale: 0.98 }}
              >
                Contact Us Now ↗
              </MotionLink>
            </div>
          </div>

          <div className="faq-accordion-grid">
            {resolvedFaqs.map((faq) => {
              const isOpen = openFaq === faq.id;
              return (
                <motion.div 
                  key={faq.id} 
                  className={`faq-accordion-card ${isOpen ? 'card-expanded' : ''}`}
                  variants={itemVariants}
                  layout
                >
                  <button 
                    className="faq-trigger-bar" 
                    onClick={() => toggleFaq(faq.id)}
                    aria-expanded={isOpen}
                  >
                    <span className="faq-question-text">
                      <span className="faq-q-prefix">Q{faq.id}.</span> {faq.q}
                    </span>
                    <motion.div 
                      className="faq-icon-circle"
                      animate={{ rotate: isOpen ? 135 : 0 }}
                      transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    >
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      </svg>
                    </motion.div>
                  </button>

                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div 
                        className="faq-answer-dropdown"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.24, ease: "easeInOut" }}
                      >
                        <p className="faq-answer-text">{faq.a}</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>

        </div>
      </motion.section>
    </div>
  );
};

export default About;
