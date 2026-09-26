"use client";

import { useState, useEffect } from 'react';
const volunteer = '/assets/download.jpg'; // Ensure the path is correct based on your project structure

// Custom lightweight counter hook for smooth UI performance
const useCounter = (endValue, duration = 2000, suffix = '') => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime = null;
    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // Easing function for smooth slowing down at the end (easeOutQuad)
      const easeProgress = progress * (2 - progress);
      
      setCount(Math.floor(easeProgress * endValue));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
  }, [endValue, duration]);

  return count.toLocaleString() + suffix;
};

const Volunteer = () => {
  // Setup automated counting states mapped to your layouts
  const liveVolunteers = useCounter(874, 1800, '+');
  const partnerOrgs = useCounter(38, 1500, '+');
  const statesReached = useCounter(16, 1200, '+');

  return (
    <div className="volunteer-page-container">
      
      {/* ---------------- SECTION 1: HERO SHOWCASE ---------------- */}
      <section className="volunteer-hero-section">
        <div className="volunteer-grid-overlay"></div>
        
        <div className="volunteer-hero-left">
          <div className="volunteer-program-badge">
            <span className="volunteer-badge-icon">✦</span> VOLUNTEER PROGRAM · 2026
          </div>
          <h1 className="volunteer-hero-title">
            Be the Change. <br />
            <span className="volunteer-italic-text">Volunteer with AMP India Foundation.</span>
          </h1>
          <p className="volunteer-hero-subtitle">
            Every skill, every hour and every act of kindness can change a life. Join our growing family of volunteers and use your time, knowledge and experience to create opportunities for those who need them most.
          </p>
          
          <div className="volunteer-hero-actions">
            <a href="#registration-form" className="volunteer-btn-white">
              Become a Volunteer 
              <span className="volunteer-arrow-circle">➔</span>
            </a>
            <button
              type="button"
              className="volunteer-btn-text"
              onClick={() =>
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
              }
            >
              How It Works
            </button>
          </div>
        </div>

        <div className="volunteer-hero-right">
          <div className="volunteer-floating-impact">
            <span className="volunteer-mini-tag">IMPACT</span>
            <div className="volunteer-stat-large">Thousands</div>
            <span className="volunteer-stat-sublabel">Lives Impacted Every Year</span>
          </div>

          <div className="volunteer-image-card">
            <img 
              src={volunteer}
              alt="AIF Volunteer Cohort Team" 
              className="volunteer-main-photo"
              loading="lazy"
            />
          </div>

          <div className="volunteer-floating-cohort">
            <div>
              <span className="volunteer-mini-tag">LIVE COHORT</span>
              <div className="volunteer-cohort-count">{liveVolunteers} volunteers</div>
            </div>
            <div className="volunteer-avatar-row">
              <div className="volunteer-avatar avatar-blue-1"></div>
              <div className="volunteer-avatar avatar-blue-2"></div>
              <div className="volunteer-avatar avatar-blue-3"></div>
              <div className="volunteer-avatar avatar-blue-4"></div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 2: WHY VOLUNTEER + IMPACT ---------------- */}
      <section className="volunteer-mission-section">
        <div className="volunteer-mission-left">
          <div className="volunteer-section-line-tag">— WHY VOLUNTEER WITH US?</div>
          <h2 className="volunteer-mission-title">
            Make Your <br />
            Time <br />
            <span className="volunteer-italic-blue">Count</span>
          </h2>
          
          <p className="volunteer-mission-callout">
            Volunteering with AMP India Foundation is more than giving your time—it&apos;s about making a meaningful difference.
          </p>
        </div>

        <div className="volunteer-mission-right">
          <div className="volunteer-mission-desc-container">
            <p className="volunteer-mission-desc">
              Whether you&apos;re a student, working professional, entrepreneur, teacher or retiree, your skills can help educate a child, guide a student, support a family or empower a community. Together, we are building a stronger, more inclusive India.
            </p>
            <p className="volunteer-mission-desc volunteer-mission-desc-muted">
              Everyone has something valuable to offer. Choose a role that matches your interests, skills and availability: Mentor Students, Support Education Programmes, Career &amp; Employability Support, Organise Events, Digital &amp; Creative Volunteering, and Community Outreach.
            </p>
          </div>

          <div className="volunteer-metric-grid">
            <div className="volunteer-metric-card">
              <div className="volunteer-metric-value">{liveVolunteers}</div>
              <div className="volunteer-metric-label">ACTIVE VOLUNTEERS</div>
            </div>
            <div className="volunteer-metric-card metric-border-sides">
              <div className="volunteer-metric-value">{partnerOrgs}</div>
              <div className="volunteer-metric-label">PARTNER ORGANIZATIONS</div>
            </div>
            <div className="volunteer-metric-card">
              <div className="volunteer-metric-value">{statesReached}</div>
              <div className="volunteer-metric-label">STATES REACHED</div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 3: HOW TO JOIN / FINAL CTA ---------------- */}
      <section id="registration-form" className="volunteer-portal-section">
        <div className="volunteer-portal-left">
          <div id="how-it-works" className="volunteer-line-tag-white">— READY TO MAKE A DIFFERENCE?</div>
          <h2 className="volunteer-portal-title">
            Joining is <br />
            <span className="volunteer-italic-blue-light">simple.</span>
          </h2>
          <p className="volunteer-portal-desc">
            Step 1: Complete the online volunteer registration form. Step 2: Our team will review your application and contact you. Step 3: Attend a short orientation session to understand our programmes and volunteer opportunities. Step 4: Start contributing to projects that match your interests, skills and availability. Together, let&apos;s build a brighter future for all.
          </p>
          
          <div className="volunteer-portal-meta">
            <span className="volunteer-meta-item">
              <span style={{ marginRight: '6px' }}>🔒</span> VERIFIED PORTAL
            </span>
            <span className="volunteer-meta-item">~2 MIN</span>
            <span className="volunteer-meta-item">REPLY IN 5 DAYS</span>
          </div>
        </div>

        <div className="volunteer-portal-right">
          <a 
            href="https://tinyurl.com/AIFVolunteerRegn" 
            target="_blank" 
            rel="noreferrer"
            className="volunteer-white-card"
          >
            <div className="volunteer-card-meta">REGISTRATION FORM</div>
            
            <div className="volunteer-card-body">
              <div className="volunteer-card-heading">
                Register <br />
                Now
              </div>
              <div className="volunteer-blue-action-circle">
                <span className="volunteer-arrow-diagonal">➔</span>
              </div>
            </div>
            
            <div className="volunteer-card-divider"></div>
            
            <div className="volunteer-card-url">
              TINYURL.COM/AIFVOLUNTEERREGN
            </div>
          </a>
        </div>
      </section>

    </div>
  );
};

export default Volunteer;
