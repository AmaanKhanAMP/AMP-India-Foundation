import ScrollToTop from '@/components/layout/ScrollToTop';
import { MEDICAL_RELIEF_IMAGE } from '@/lib/projectAssets';

const Medical = () => {
  const title = 'Medical Relief';
  const subtitle = 'Healthcare Support & Outreach';
  const quote =
    'Making essential healthcare and medical support available to people in need.';
  const badge = 'MEDICAL RELIEF';
  const image = MEDICAL_RELIEF_IMAGE;
  const paragraphs = [
    'For many underprivileged families, the cost of healthcare can become a serious burden. Timely medical support can make a vital difference, especially when families face illness or medical emergencies.',
    'AIF supports healthcare initiatives such as health check-up camps, free medicine distribution and medical assistance for individuals who require treatment but may not be able to afford it.',
    'Our efforts aim to help vulnerable individuals and families access essential healthcare with dignity and without discrimination based on caste, community, religion or background.',
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
            <img src={image} alt="Medical Relief" className="geo-img" />
            <div className="geo-frame-border"></div>
          </div>
        </div>
      </main>
   </div>
  );
};

export default Medical;