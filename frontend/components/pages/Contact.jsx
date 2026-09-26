"use client";

import { useState } from 'react';
import { API_URL } from '@/lib/api';
const contact = '/assets/contact.jpeg';

const Contact = () => {
  const [formData, setFormData] = useState({ 
    firstName: '', 
    lastName: '', 
    email: '', 
    phone: '', 
    message: '' 
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formFeedback, setFormFeedback] = useState({ type: '', text: '' });

  const address =
    'Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008';
  const phone = '+91 8291101312';
  const email = 'contact@ampindiafoundation.org';
  const heroImage = contact;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (formFeedback.text) {
      setFormFeedback({ type: '', text: '' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormFeedback({ type: '', text: '' });
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          phone: formData.phone,
          message: formData.message,
        }),
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.success) {
        const validationErrors = result.errors
          ? Object.values(result.errors).join(' ')
          : '';
        setFormFeedback({
          type: 'error',
          text:
            validationErrors ||
            result.message ||
            'Unable to send your message. Please try again.',
        });
        return;
      }

      setFormFeedback({
        type: 'success',
        text: result.message || 'Your message has been submitted successfully.',
      });
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        message: '',
      });
    } catch (_error) {
      setFormFeedback({
        type: 'error',
        text: 'Network error. Please check your connection and try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="contact-page">

      {/* Dynamic Immersive Background Image Banner */}
      <header 
        className="hero-section full-bleed-bg" 
        style={{ backgroundImage: `linear-gradient(to right, rgba(0, 31, 71, 0.41) 30%, rgba(0, 21, 51, 0.85) 60%, rgba(2, 6, 23, 0.4) 100%), url(${heroImage})` }}
      >
        <div className="hero-ambient-glow-1"></div>
        <div className="hero-content full-bleed-layout">
          <div className="hero-text animate-slide-up">
            <div className="hero-tagline-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
              <span>Communication Hub</span>
            </div>
            <h1 className="hero-heading">
              Let's start a <br/>
              <span className="hero-heading-gradient-wrapper">
                <span className="hero-heading-gradient font-extrabold">meaningful</span>
                <span className="heading-geometric-underline"></span>
              </span> 
              <br/>conversation
            </h1>
            <p className="hero-subtext">
              Have questions, partnership ideas, or want to support our initiatives? Reach out to our team and we will guide you with clarity, care, and purpose.
            </p>
            <div className="hero-action-ctas">
              <a href="#contact-form-section" className="hero-primary-btn">
                <span>Drop a Message</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              </a>
            </div>
          </div>
          
         
        </div>
      </header>

      {/* Overlapping Professional Cards Section */}
      <section className="info-cards-section animate-staggered-fade">
        <div className="cards-grid-layout">
          
          {/* Card: Address */}
          <div className="premium-info-card" style={{ '--card-index': 1 }}>
            <div className="card-icon-frame">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
            </div>
            <h3 className="card-title text-heading">Our Address</h3>
            <p className="card-desc-text">
              {address}
            </p>
          </div>

          {/* Card: Call */}
          <div className="premium-info-card" style={{ '--card-index': 2 }}>
            <div className="card-icon-frame">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
            </div>
            <h3 className="card-title text-heading">Call Us</h3>
            <p style={{ margin: 0 }}>
              <a href={`tel:${phone.replace(/\s/g, '')}`} className="card-anchor-link">{phone}</a>
            </p>
            <span className="card-sub-meta">11:00 am to 7:00 pm IST</span>
          </div>

          {/* Card: Email */}
          <div className="premium-info-card" style={{ '--card-index': 3 }}>
            <div className="card-icon-frame">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
            </div>
            <h3 className="card-title text-heading">Email Us</h3>
            <p style={{ margin: 0 }}>
              <a href={`mailto:${email}`} className="card-anchor-link">{email}</a>
            </p>
          </div>

        </div>
      </section>
       {/* Isolated Section 2: Full Width Interactive Map Section */}
       <section id="map-section" className="map-visual-section scroll-triggered-reveal">
        <div className="map-section-container">
          <div className="map-layout-header">
            <div className="map-header-split-row">
              <div className="map-intro-text-block">
                <p className="section-tagline">Location map</p>
                <h2 className="section-main-title text-heading">Visit our main office</h2>
                <p className="section-explanatory-text">
                  Our regional operations are anchored dynamically in Mumbai. View the high-fidelity structural vector details below or seamlessly shift to external routing maps.
                </p>
              </div>
              <a href="https://maps.google.com" target="_blank" rel="noopener noreferrer" className="map-external-anchor-link">
                <span>Open in Google Maps</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
              </a>
            </div>
          </div>
          
          <div className="premium-map-display-panel">
            <div className="map-panel-top-banner">
              <div>
                <h3 className="map-panel-title text-heading">AMP India Foundation</h3>
                <p className="map-panel-subtitle">Clare Road, Nagpada, Mumbai, Maharashtra</p>
              </div>
              <div className="map-status-badge">
                <span className="pulse-dot-indicator"></span>
                <span>Verified Registry Point</span>
              </div>
            </div>
            <div className="iframe-responsive-viewport">
              <iframe 
                title="AMP India Foundation Location" 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3773.141291782794!2d72.82685557492766!3d18.96936645531204!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3be7ce6871485c39%3A0x2eccfdf8278853e1!2sAMP%20India%20Foundation!5e0!3m2!1sen!2sin!4v1784187273160!5m2!1sen!2sin"
                loading="lazy" 
                className="embedded-iframe-node"
              ></iframe>
            </div>
          </div>
        </div>
      </section>

      {/* Isolated Section 1: Contact Form Layout */}
      <section id="contact-form-section" className="form-content-section scroll-triggered-reveal">
        <div className="form-split-layout">
          
          <div className="form-sticky-panel">
            <p className="section-tagline">Message form</p>
            <h2 className="section-main-title text-heading">Tell us how we can help</h2>
            <p className="section-explanatory-text">
              Fill out our explicit workspace request terminal. Your message will be securely routed directly to the regional management team for verification and scheduling.
            </p>
            <div className="form-response-metric-box">
              <div className="metric-header-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                <span>Average Response Duration</span>
              </div>
              <p className="metric-body-text">Our dedicated communication desk prioritizes inquiry processing within 1 business day.</p>
            </div>
          </div>
          
          <div className="immersive-interactive-form">
            <form className="form-fields-stack" onSubmit={handleSubmit}>
              
              {/* Row 1: First Name & Last Name */}
              <div className="form-row-duo">
                <div className="input-group-block">
                  <label htmlFor="firstName" className="form-input-label">First Name</label>
                  <input 
                    type="text" id="firstName" name="firstName" required 
                    placeholder="John" className="modular-text-input" 
                    value={formData.firstName} onChange={handleChange} 
                  />
                </div>
                <div className="input-group-block">
                  <label htmlFor="lastName" className="form-input-label">Last Name</label>
                  <input 
                    type="text" id="lastName" name="lastName" required 
                    placeholder="Doe" className="modular-text-input" 
                    value={formData.lastName} onChange={handleChange} 
                  />
                </div>
              </div>

              {/* Row 2: Email & Phone Number */}
              <div className="form-row-duo">
                <div className="input-group-block">
                  <label htmlFor="email" className="form-input-label">Email Address</label>
                  <input 
                    type="email" id="email" name="email" required 
                    placeholder="john.doe@corporate.com" className="modular-text-input" 
                    value={formData.email} onChange={handleChange} 
                  />
                </div>
                <div className="input-group-block">
                  <label htmlFor="phone" className="form-input-label">Phone Number</label>
                  <input 
                    type="tel" id="phone" name="phone" required 
                    placeholder="+91 XXXXX XXXXX" className="modular-text-input" 
                    value={formData.phone} onChange={handleChange} 
                  />
                </div>
              </div>

              {/* Message Block */}
              <div className="input-group-block">
                <label htmlFor="message" className="form-input-label">Message</label>
                <textarea 
                  id="message" name="message" rows="6" required 
                  placeholder="Describe your context, queries or collaboration objectives..." className="modular-textarea-input"
                  value={formData.message} onChange={handleChange}
                ></textarea>
              </div>
              
              {formFeedback.text ? (
                <p
                  role="status"
                  aria-live="polite"
                  style={{
                    margin: 0,
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    color: formFeedback.type === 'success' ? '#047857' : '#b91c1c',
                  }}
                >
                  {formFeedback.text}
                </p>
              ) : null}

              <div style={{ paddingTop: '8px' }}>
                <button
                  type="submit"
                  className="secure-submit-btn"
                  disabled={isSubmitting}
                  style={isSubmitting ? { opacity: 0.7, cursor: 'not-allowed' } : undefined}
                >
                  <span>{isSubmitting ? 'Sending...' : 'Send Secure Message'}</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
              </div>
            </form>
          </div>

        </div>
      </section>

     

    

    </div>
  );
};

export default Contact;