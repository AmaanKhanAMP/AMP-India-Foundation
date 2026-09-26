"use client";

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';
import Image from 'next/image';
import eventsHeroBanner from '@/src/assets/events-hero.png';

const EventsHero = () => {
  const scrollToEvents = () => {
    document.getElementById('upcoming-events')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="events-hero" aria-label="Events hero">
      <Image
        src={eventsHeroBanner}
        alt=""
        fill
        priority
        sizes="100vw"
        quality={80}
        className="events-hero-bg"
        aria-hidden="true"
      />
      <div className="events-hero-mesh" aria-hidden="true" />
      <div className="events-hero-blob events-hero-blob-1" aria-hidden="true" />
      <div className="events-hero-blob events-hero-blob-2" aria-hidden="true" />
      <div className="events-hero-blob events-hero-blob-3" aria-hidden="true" />

      <motion.div
        className="events-hero-content"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <motion.span
          className="events-hero-badge"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <Sparkles size={14} aria-hidden="true" />
          AMP India Foundation Events
        </motion.span>

        <motion.h1
          className="events-hero-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.7 }}
        >
          Creating Opportunities. <span>Inspiring Change.</span>
        </motion.h1>

        <motion.p
          className="events-hero-subtitle"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45, duration: 0.7 }}
        >
          Every event at AMP India Foundation is a step towards building stronger communities. From career guidance and job fairs to health camps and skill development workshops, our events create opportunities that transform lives.
        </motion.p>

        <motion.div
          className="events-hero-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.7 }}
        >
          <button type="button" className="events-btn-primary" onClick={scrollToEvents}>
            Explore Upcoming Events
          </button>
          <Link href="/volunteer" className="events-btn-outline">
            Become a Volunteer
          </Link>
        </motion.div>
      </motion.div>
    </section>
  );
};

export default EventsHero;
