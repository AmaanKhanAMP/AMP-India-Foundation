"use client";

import { useState, useEffect, useRef } from 'react';
import communityImpactBanner from '@/src/assets/hero-community-impact.png';

const assetSrc = (image) => (typeof image === 'string' ? image : image?.src);
const IMPACT_BG_FALLBACK = assetSrc(communityImpactBanner);


const impactMetrics = [
  { 
    id: 1, 
    target: 100000, 
    suffix: '+', 
    label: 'CANDIDATES PLACED', 
    // Professional SVG: Profile/User badge layout
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="8.5" cy="7" r="4" />
        <polyline points="17 11 19 13 23 9" />
      </svg>
    )
  },
  { 
    id: 2, 
    target: 625, 
    suffix: '+', 
    label: 'JOB DRIVES ORGANISED', 
    // Professional SVG: Briefcase alignment layout
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
      </svg>
    )
  },
  { 
    id: 3, 
    target: 350, 
    suffix: '+', 
    label: 'EMPLOYABILITY TRAINING PROGRAMMES', 
    // Professional SVG: Graduation mortarboard cap
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
        <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5" />
      </svg>
    )
  },
  { 
    id: 4, 
    target: 110, 
    suffix: '+', 
    label: 'MEGA JOB FAIRS CONDUCTED', 
    // Professional SVG: Global networking / Corporate architecture network
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    )
  }
];

// Reusable Counter Sub-Component
const CountUpItem = ({ target, suffix, label, icon, startTrigger }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!startTrigger) return;

    const duration = 2000;
    const frameDuration = 1000 / 60;
    const totalFrames = Math.round(duration / frameDuration);
    let frame = 0;

    const counter = setInterval(() => {
      frame++;
      const progress = frame / totalFrames;
      const easeOutProgress = 1 - Math.pow(1 - progress, 3);
      const currentCount = Math.round(target * easeOutProgress);
      
      if (frame >= totalFrames) {
        setCount(target);
        clearInterval(counter);
      } else {
        setCount(currentCount);
      }
    }, frameDuration);

    return () => clearInterval(counter);
  }, [target, startTrigger]);

  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\n))/g, ",");
  };

  return (
    <div className="impact-metric-card">
      <div className="metric-icon-box">{icon}</div>
      <h2 className="metric-number">
        {formatNumber(count)}{suffix}
      </h2>
      <p className="metric-label">{label}</p>
    </div>
  );
};

const Impact = () => {
  const [hasTriggered, setHasTriggered] = useState(false);
  const sectionRef = useRef(null);
  const metrics = impactMetrics;
  const bgImage = IMPACT_BG_FALLBACK;

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setHasTriggered(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section 
      ref={sectionRef} 
      id="impact"
      className="amp-impact-section"
      // Swapped backdrop image token to a high-end corporate workshop overlay look
      style={{ backgroundImage: `linear-gradient(rgba(11, 44, 72, 0.88), rgba(6, 24, 40, 0.93)), url('${bgImage}')` }}
    >
      <div className="impact-container">
        <div className="impact-grid-layout">
          {metrics.map((metric) => (
            <CountUpItem 
              key={metric.id}
              target={metric.target}
              suffix={metric.suffix}
              label={metric.label}
              icon={metric.icon}
              startTrigger={hasTriggered}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default Impact;