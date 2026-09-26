import ScrollToTop from '@/components/layout/ScrollToTop';
import { MENTORSHIP_IMAGE } from '@/lib/projectAssets';

const Mentorship = () => {
  const title = 'Student Mentorship';
  const subtitle = 'Professional Guidance & Mentorship';
  const quote =
    'Connecting students with experienced professionals who can guide their future.';
  const badge = 'STUDENT MENTORSHIP';
  const image = MENTORSHIP_IMAGE;
  const paragraphs = [
    'Many students, especially those from financially weaker backgrounds, have the ability and ambition to succeed but may not have access to experienced people who can guide them in making the right choices.',
    'AIF connects students with experienced professionals who share their knowledge, skills and work experience. Mentors help students understand their options and make informed decisions about education and careers.',
    'Through guidance on career choices, higher education, internships, professional skills and personal development, the programme helps students build confidence and prepare for successful futures.',
  ];
  return (
    <div className="editorial-portfolio-page">
      <ScrollToTop />

      <main className="hero-editorial-block">
        <div className="hero-typography-pane">
          <h1 className="premium-hero-heading">{title}</h1>
          <p className="hero-project-subtitle">{subtitle}</p>
          <div className="editorial-divider-line"></div>
          <div className="editorial-quote-card">
            <p className="quote-text">&quot;{quote.replace(/^"|"$/g, '')}&quot;</p>
          </div>
          <div className="editorial-paragraphs">
            {paragraphs.map((para) => (
              <p key={para.slice(0, 24)} className="body-para">{para}</p>
            ))}
          </div>
        </div>
        <div className="hero-graphic-pane">
          <div className="geometric-image-frame">
            <div className="geo-badge-tag">{badge}</div>
            <img src={image} alt="Student Mentorship" className="geo-img" />
            <div className="geo-frame-border"></div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Mentorship;