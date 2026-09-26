"use client";

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

const VolunteerCTA = ({
  title = 'Become Part of Every Success Story',
  text = 'Every event becomes impactful because of passionate volunteers and supporters like you.',
  secondaryLabel = 'Support Our Mission',
  secondaryHref = '/support-us',
}) => {
  return (
    <section className="volunteer-cta-section" aria-label="Volunteer call to action">
      <motion.div
        className="volunteer-cta-inner"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.4 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      >
        <h2 className="volunteer-cta-title">{title}</h2>
        <p className="volunteer-cta-text">{text}</p>

        <div className="volunteer-cta-actions">
          <Link href="/volunteer" className="volunteer-cta-btn-white">
            Become a Volunteer
            <ArrowRight size={16} aria-hidden="true" />
          </Link>
          <Link href={secondaryHref} className="volunteer-cta-btn-outline">
            {secondaryLabel}
          </Link>
        </div>
      </motion.div>
    </section>
  );
};

export default VolunteerCTA;
