"use client";

import { useState, useRef } from 'react';

import { fallbackByTitle } from '@/lib/cmsImage';
import CmsMediaImage from '@/components/media/CmsMediaImage';

import etpImage from '@/src/assets/home-project-etp.png';
import megaJobFairImage from '@/src/assets/home-project-mega-job-fair.png';
import careerGuidanceImage from '@/src/assets/home-project-career-guidance.png';
import educationSupportImage from '@/src/assets/home-project-education-support.png';

const assetSrc = (image) => (typeof image === 'string' ? image : image?.src);

const FALLBACK_PROJECTS = [
  {
    id: 1,
    image: assetSrc(etpImage),
    title: 'Employability Training Program (ETP)',
  },
  {
    id: 2,
    image: assetSrc(megaJobFairImage),
    title: 'Mega Job Fair',
  },
  {
    id: 3,
    image: assetSrc(careerGuidanceImage),
    title: 'Career Guidance & Mentorship',
  },
  {
    id: 4,
    image: assetSrc(educationSupportImage),
    title: 'Education Support',
  },
];

const ProjectCardImage = ({ project }) => {
  const fallbackSrc = fallbackByTitle(FALLBACK_PROJECTS, project.title);
  return (
    <CmsMediaImage
      cmsSrc={project.image}
      fallbackSrc={fallbackSrc}
      alt={project.title}
      fill
      sizes="(max-width: 768px) 290px, 360px"
      loading="lazy"
      className="project-img"
    />
  );
};

const Projects = ({ projects }) => {
  const projectsData = Array.isArray(projects) ? projects : FALLBACK_PROJECTS;
  const [isPaused, setIsPaused] = useState(false);
  const sliderTrackRef = useRef(null);

  const duplicatedProjects = [...projectsData, ...projectsData];

  return (
    <section className="latest-projects-section">
      <div className="projects-container">
        <div className="projects-header">
          <h2>
            OUR <span className="text-blue-accent">PROJECTS</span>
          </h2>
          <div className="decorative-line-wrapper">
            <span className="line-segment short"></span>
            <span className="line-segment long"></span>
            <span className="line-segment short"></span>
          </div>
          <p className="section-intro-text">
            Through our various initiatives, we work towards creating opportunities in education,
            employment, healthcare, skill development and community empowerment.
          </p>
        </div>

        <div className="projects-carousel-window">
          <div
            ref={sliderTrackRef}
            className={`projects-slider-track ${isPaused ? 'paused' : ''}`}
          >
            {duplicatedProjects.map((project, index) => (
              <div
                key={`${project.id}-${index}`}
                className="project-card"
                onMouseEnter={() => setIsPaused(true)}
                onMouseLeave={() => setIsPaused(false)}
              >
                <ProjectCardImage project={project} />
                <div className="project-hover-overlay">
                  <div className="overlay-content">
                    <p className="project-description-text">{project.title}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Projects;
