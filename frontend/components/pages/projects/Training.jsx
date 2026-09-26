import ScrollToTop from '@/components/layout/ScrollToTop';
import { EMPLOYMENT_TRAINING_IMAGE } from '@/lib/projectAssets';

const Training = () => {
  const title = 'Employment Training';
  const subtitle = 'Job Preparation & Professional Skills';
  const quote =
    'Helping young people become confident and ready for the workplace.';
  const badge = 'EMPLOYMENT TRAINING';
  const image = EMPLOYMENT_TRAINING_IMAGE;
  const paragraphs = [
    'Having a qualification is important, but young people also need practical skills and confidence to successfully enter today’s job market.',
    'AIF’s Employability Training Programme (ETP) helps bridge this gap.',
    'Led by experienced trainers, ETP focuses on practical job-preparation skills such as finding suitable opportunities, writing an effective resume, preparing for interviews, professional grooming, workplace behaviour and communication.',
    'The programme helps job seekers become better prepared, more confident and ready to make the most of the employment opportunities available to them.',
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
            <img src={image} alt="Employability Training" className="geo-img" />
            <div className="geo-frame-border"></div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Training;