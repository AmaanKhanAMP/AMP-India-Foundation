import ScrollToTop from '@/components/layout/ScrollToTop';
import employmentProjectJobFair from '@/src/assets/employment-project-job-fair.png';

const employmentImageSrc =
  typeof employmentProjectJobFair === 'string'
    ? employmentProjectJobFair
    : employmentProjectJobFair?.src;

const Employment = () => {
  const title = 'Employment Support';
  const subtitle = 'Career & Job Placement Support';
  const quote =
    'Helping young people move from education to meaningful employment.';
  const badge = 'EMPLOYMENT SUPPORT';
  const image = employmentImageSrc;
  const paragraphs = [
    'Finding a suitable job can be challenging for young people, particularly when they lack practical workplace skills, confidence and access to the right opportunities.',
    'AIF helps bridge this gap through career guidance, soft-skills workshops, employability programmes, Job Drives and Mega Job Fairs. These initiatives prepare candidates for the workplace and connect them with potential employers.',
    'By bringing job seekers and employers together, we aim to help deserving youth find meaningful employment and take an important step towards a better future.',
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
            <img src={image} alt="Employment Support" className="geo-img" />
            <div className="geo-frame-border"></div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Employment;