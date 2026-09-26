"use client";

import { motion } from 'framer-motion';
import {
  Briefcase,
  GraduationCap,
  HeartPulse,
  UserRound,
  Users,
  Wrench,
} from 'lucide-react';

const ease = [0.16, 1, 0.3, 1];

const FOCUS_AREAS = [
  { id: 'education', label: 'Education', icon: GraduationCap },
  { id: 'medical-relief', label: 'Medical Relief', icon: HeartPulse },
  { id: 'employment-support', label: 'Employment Support', icon: Briefcase },
  { id: 'economic-empowerment', label: 'Economic Empowerment', icon: Users },
  { id: 'student-mentorship', label: 'Student Mentorship', icon: UserRound },
  { id: 'employment-training', label: 'Employment Training', icon: Wrench },
];

const ProjectsIntroSection = () => {
  return (
    <section className="projects-intro-section" aria-label="Projects introduction">
      <div className="projects-intro-inner">
        <div className="projects-intro-copy">
          <motion.span
            className="projects-intro-eyebrow"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.5, ease }}
          >
            OUR PROJECTS
          </motion.span>

          <motion.h2
            className="projects-intro-title"
            initial={{ opacity: 0, y: 22 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.6, ease, delay: 0.06 }}
          >
            <span className="projects-intro-title-line">Empowering Communities Through</span>
            <span className="projects-intro-title-line title-accent-blue">Sustainable Development</span>
          </motion.h2>

          <motion.div
            className="projects-intro-divider decorative-line-wrapper"
            aria-hidden="true"
            initial={{ scaleX: 0, opacity: 0 }}
            whileInView={{ scaleX: 1, opacity: 1 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.6, ease, delay: 0.12 }}
          >
            <span className="line-segment short" />
            <span className="line-segment long" />
            <span className="line-segment short" />
          </motion.div>

          <motion.p
            className="projects-intro-text"
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.6, ease, delay: 0.18 }}
          >
            At AMP India Foundation, we believe that lasting change begins with opportunity. Our
            programmes address the most pressing needs of underprivileged communities by improving
            access to education, employment, healthcare, skill development and sustainable
            livelihoods.
          </motion.p>

          <motion.p
            className="projects-intro-text"
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.6, ease, delay: 0.28 }}
          >
            Together with our volunteers, donors and partners, we are creating opportunities that
            transform lives across India.
          </motion.p>
        </div>

        <aside className="projects-intro-aside" aria-label="Project focus areas">
          <motion.ul
            className="projects-intro-areas"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.25 }}
            variants={{
              hidden: {},
              visible: { transition: { staggerChildren: 0.08, delayChildren: 0.22 } },
            }}
          >
            {FOCUS_AREAS.map(({ id, label, icon: Icon }) => (
              <motion.li
                key={id}
                className="projects-intro-area"
                variants={{
                  hidden: { opacity: 0, y: 14 },
                  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } },
                }}
                whileHover={{ x: 4, scale: 1.015 }}
                transition={{ duration: 0.22, ease: 'easeOut' }}
              >
                <span className="projects-intro-area-accent" aria-hidden="true" />
                <span className="projects-intro-area-icon" aria-hidden="true">
                  <Icon size={17} strokeWidth={2} />
                </span>
                <span className="projects-intro-area-label">{label}</span>
              </motion.li>
            ))}
          </motion.ul>
        </aside>
      </div>
    </section>
  );
};

export default ProjectsIntroSection;
