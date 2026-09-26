"use client";

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

import { PROJECT_CATEGORIES } from '@/lib/projectAssets';

const ease = [0.16, 1, 0.3, 1];

const ProjectsShowcaseSection = () => {
  const projects = PROJECT_CATEGORIES;
  return (
    <section
      id="our-projects"
      className="welcome-section projects-cards-band"
      aria-label="Our projects"
    >
      <div className="section-container">
        <motion.header
          className="section-header-block"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.55, ease }}
        >
          <h2 className="main-section-title">
            OUR <span className="title-accent-blue">PROJECTS</span>
          </h2>
          <div className="decorative-line-wrapper" aria-hidden="true">
            <span className="line-segment short" />
            <span className="line-segment long" />
            <span className="line-segment short" />
          </div>
        </motion.header>

        <div className="cards-grid-layout">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.12 }}
              transition={{ duration: 0.5, ease, delay: index * 0.06 }}
            >
              <Link
                href={project.href}
                className="info-feature-card"
                aria-label={`${project.title} — ${project.subtitle}`}
                scroll
              >
                <div className="card-image-box">
                  <img
                    src={project.image}
                    alt={project.title}
                    className="feature-card-img"
                    loading="lazy"
                  />
                </div>
                <div className="card-content-box">
                  <span className="projects-card-category">{project.title}</span>
                  <h3 className="card-main-title">{project.subtitle}</h3>
                  <p className="projects-card-initiatives-label">Key Initiatives:</p>
                  <ul className="projects-card-initiatives">
                    {project.initiatives.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  <span className="projects-card-explore">
                    Explore Project
                    <ArrowRight size={15} aria-hidden="true" />
                  </span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProjectsShowcaseSection;
