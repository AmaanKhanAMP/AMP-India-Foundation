import ProjectsHero from '@/components/projects/ProjectsHero';
import ProjectsIntroSection from '@/components/projects/ProjectsIntroSection';
import ProjectsShowcaseSection from '@/components/projects/ProjectsShowcaseSection';
import '@/styles/Projects.css';

const ProjectsPage = () => {
  return (
    <div className="projects-page-canvas">
      <ProjectsHero />
      <ProjectsIntroSection />
      <ProjectsShowcaseSection />
    </div>
  );
};

export default ProjectsPage;
