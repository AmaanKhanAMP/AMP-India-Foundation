"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const FeaturedInitiatives = () => {
  const pathname = usePathname();

  const projectList = [
    {
      path: '/projects/education',
      title: 'Education',
      tagline: 'Empowering BPL youth through localized technical skill frameworks.',
      image: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&q=80&w=800'
    },
    {
      path: '/projects/medical',
      title: 'Medical Relief',
      tagline: 'Breaking barriers to provide essential diagnostic and clinical relief.',
      image: "https://images.unsplash.com/photo-1584515933487-7804366f295a?auto=format&fit=crop&q=80&w=800"
    },
    {
      path: '/projects/employment',
      title: 'Employment Support',
      tagline: 'Bridging the transition from student networks to corporate ecosystems.',
      image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=800'
    },
    {
      path: '/projects/empowerment',
      title: 'Economic Empowerment',
      tagline: 'Cultivating entrepreneurial self-reliance across urban and rural chapters.',
      image: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=800'
    },
    {
      path: '/projects/mentorship',
      title: 'Student Mentorship',
      tagline: 'Connecting industry experience with first-generation student networks.',
      image: 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=800'
    },
    {
      path: '/projects/training',
      title: 'Employability Training',
      tagline: 'Polishing core foundational skills to ensure immediate employment fit.',
      image: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&q=80&w=800'
    }
  ];

  return (
    <section className="featured-tabs-section">
      <div className="section-title-banner">
         MAIN STRATEGIC INITIATIVES 
      </div>

      <div className="tabs-strip-container">
        {projectList.map((project) => {
          const isSelected =
            pathname === project.path ||
            (project.path === '/projects/medical' && pathname === '/projects/healthcare');
          return (
            <Link 
              key={project.path}
              href={project.path}
              className={`editorial-tab-card ${isSelected ? 'is-selected' : ''}`}
              scroll
            >
              <div className="tab-img-preview">
                <img src={project.image} alt={project.title} />
                <div className="tab-img-overlay"></div>
              </div>
              <div className="tab-meta-content">
                <h3 className="tab-title">{project.title}</h3>
                <p className="tab-summary-desc">{project.tagline}</p>
                <span className="tab-action-trigger">Explore Component View →</span>
              </div>
              <div className="tab-underline"></div>
            </Link>
          );
        })}
      </div>
    </section>
  );
};

export default FeaturedInitiatives;
