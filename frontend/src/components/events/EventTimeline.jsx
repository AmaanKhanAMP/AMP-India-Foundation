import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const timelineData = [
  { month: 'January', event: 'Education Workshops' },
  { month: 'March', event: 'Career Guidance Sessions' },
  { month: 'June', event: 'Employment Drives' },
  { month: 'August', event: 'Medical Camps' },
  { month: 'October', event: 'Skill Development Programs' },
  { month: 'December', event: 'Community Outreach' },
];

const EventTimeline = () => {
  const wrapperRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: wrapperRef,
    offset: ['start 0.8', 'end 0.4'],
  });

  const lineHeight = useTransform(scrollYProgress, [0, 1], ['0%', '100%']);

  return (
    <section className="event-timeline-section" aria-label="Annual event timeline">
      <div className="ev-container">
        <header className="ev-section-header">
          <span className="ev-section-tag">Year at a Glance</span>
          <h2 className="ev-section-title">
            Event <span className="ev-accent">Calendar</span>
          </h2>
          <p className="ev-section-subtitle">
            A year-round journey of empowerment — from classrooms to communities across India.
          </p>
        </header>

        <div className="event-timeline-wrapper" ref={wrapperRef}>
          <div className="event-timeline-line" aria-hidden="true">
            <motion.div className="event-timeline-line-fill" style={{ height: lineHeight }} />
          </div>

          {timelineData.map((item, index) => (
            <motion.div
              key={item.month}
              className="event-timeline-item"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, amount: 0.5 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
            >
              <div className="event-timeline-dot" aria-hidden="true" />
              <p className="event-timeline-month">{item.month}</p>
              <h3 className="event-timeline-event">{item.event}</h3>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default EventTimeline;
