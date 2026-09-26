import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Users, GraduationCap, Building2, HeartPulse } from 'lucide-react';

const stats = [
  { id: 1, target: 80, suffix: '+', label: 'Job Fairs', icon: Building2 },
  { id: 2, target: 625, suffix: '+', label: 'Employment Drives', icon: Briefcase },
  { id: 3, target: 39000, suffix: '+', label: 'Candidates Placed', icon: Users },
  { id: 4, target: 350, suffix: '+', label: 'Training Programs', icon: GraduationCap },
  { id: 5, target: 25, suffix: '+', label: 'Medical Camps', icon: HeartPulse },
];

const CountUp = ({ target, suffix, startTrigger }) => {
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
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(target * easeOut);

      if (frame >= totalFrames) {
        setCount(target);
        clearInterval(counter);
      } else {
        setCount(current);
      }
    }, frameDuration);

    return () => clearInterval(counter);
  }, [target, startTrigger]);

  const formatted = count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');

  return (
    <>
      {formatted}
      {suffix}
    </>
  );
};

const ImpactStats = () => {
  const [triggered, setTriggered] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTriggered(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="impact-stats-section"
      aria-label="Impact through events"
    >
      <div className="ev-container">
        <header className="ev-section-header" style={{ marginBottom: 48 }}>
          <span
            className="ev-section-tag"
            style={{ background: 'rgba(255,255,255,0.1)', color: '#93c5fd', borderColor: 'rgba(255,255,255,0.15)' }}
          >
            Measurable Impact
          </span>
          <h2 className="ev-section-title" style={{ color: '#ffffff' }}>
            Impact Through <span className="ev-accent" style={{ color: '#93c5fd' }}>Events</span>
          </h2>
          <p className="ev-section-subtitle" style={{ color: '#94a3b8' }}>
            Every gathering creates ripples of change — empowering lives across India.
          </p>
        </header>

        <div className="impact-stats-grid">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.id}
                className="impact-stat-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
              >
                <div className="impact-stat-icon">
                  <Icon size={22} aria-hidden="true" />
                </div>
                <p className="impact-stat-number">
                  <CountUp target={stat.target} suffix={stat.suffix} startTrigger={triggered} />
                </p>
                <p className="impact-stat-label">{stat.label}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default ImpactStats;
