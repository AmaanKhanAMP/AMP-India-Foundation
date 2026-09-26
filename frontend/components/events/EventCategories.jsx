"use client";

import { motion } from 'framer-motion';
import {
  GraduationCap,
  Briefcase,
  HeartPulse,
  Wrench,
  Users,
  HandHeart,
} from 'lucide-react';

const categories = [
  {
    id: 1,
    icon: GraduationCap,
    title: 'Education',
    description: 'Scholarships, educational workshops and career guidance programmes.',
  },
  {
    id: 2,
    icon: Briefcase,
    title: 'Employment',
    description: 'Employability training, job fairs, placement drives and recruitment events.',
  },
  {
    id: 3,
    icon: HeartPulse,
    title: 'Healthcare',
    description: 'Medical camps, health awareness initiatives and medical assistance.',
  },
  {
    id: 4,
    icon: Wrench,
    title: 'Skill Development',
    description: 'Vocational training, entrepreneurship workshops and livelihood programmes.',
  },
  {
    id: 5,
    icon: Users,
    title: 'Mentorship',
    description: 'Career counselling, leadership development and professional mentoring.',
  },
  {
    id: 6,
    icon: HandHeart,
    title: 'Community Development',
    description: 'Outreach programmes that strengthen families and communities through sustainable support.',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
};

const EventCategories = () => {
  const categoryItems = categories;
  return (
    <section className="event-categories-section" aria-label="Event categories">
      <div className="ev-container">
        <header className="ev-section-header">
          <span className="ev-section-tag">Our Focus Areas</span>
          <h2 className="ev-section-title">
            Event <span className="ev-accent">Categories</span>
          </h2>
          <p className="ev-section-subtitle">
            Every event aligns with AMP India Foundation&apos;s core pillars of social development.
          </p>
        </header>

        <motion.div
          className="event-categories-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={containerVariants}
        >
          {categoryItems.map((cat) => {
            const Icon = cat.icon;
            return (
              <motion.div key={cat.id} className="event-category-card" variants={itemVariants}>
                <div className="event-category-icon">
                  <Icon size={26} aria-hidden="true" />
                </div>
                <h3 className="event-category-title">{cat.title}</h3>
                <p className="event-category-desc">{cat.description}</p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
};

export default EventCategories;
