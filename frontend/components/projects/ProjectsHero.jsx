"use client";

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';

import { PROJECT_HERO_BG } from '@/lib/projectAssets';

const ProjectsHero = () => {
  const scrollToProjects = () => {
    document.getElementById('our-projects')?.scrollIntoView({ behavior: 'smooth' });
  };

  const heroBackground = `linear-gradient(rgba(11, 44, 72, 0.75), rgba(6, 24, 40, 0.88)), url(${PROJECT_HERO_BG})`;

  return (
    <section
      className="projects-hero"
      aria-label="Projects hero"
      style={{ backgroundImage: heroBackground }}
    >
      <div className="projects-hero-mesh" aria-hidden="true" />
      <div className="projects-hero-blob projects-hero-blob-1" aria-hidden="true" />
      <div className="projects-hero-blob projects-hero-blob-2" aria-hidden="true" />
      <div className="projects-hero-blob projects-hero-blob-3" aria-hidden="true" />

      <motion.div
        className="projects-hero-content"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <motion.span
          className="projects-hero-badge"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <Sparkles size={14} aria-hidden="true" />
          AMP India Foundation Projects
        </motion.span>

        <motion.h1
          className="projects-hero-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.7 }}
        >
          Creating Opportunities. <span>Transforming Lives.</span>
        </motion.h1>

        <motion.p
          className="projects-hero-subtitle"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45, duration: 0.7 }}
        >
          Every project at AMP India Foundation is designed to empower individuals and strengthen
          communities. From education and employment to healthcare and livelihood support, our
          initiatives help people build brighter, more self-reliant futures.
        </motion.p>

        <motion.div
          className="projects-hero-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.7 }}
        >
          <button type="button" className="projects-btn-primary" onClick={scrollToProjects}>
            Explore Our Projects
          </button>
          <Link href="/support-us" className="projects-btn-outline">
            Support Our Mission
          </Link>
        </motion.div>
      </motion.div>
    </section>
  );
};

export default ProjectsHero;
