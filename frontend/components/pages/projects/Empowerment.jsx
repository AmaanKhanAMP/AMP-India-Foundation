import ScrollToTop from '@/components/layout/ScrollToTop';
import { ECONOMIC_EMPOWERMENT_IMAGE } from '@/lib/projectAssets';

const Empowerment = () => {
  const title = 'Economic Empowerment';
  const subtitle = 'Financial Independence & Livelihood Support';
  const quote =
    'Helping people build stable incomes and become financially independent.';
  const badge = 'ECONOMIC EMPOWERMENT';
  const image = ECONOMIC_EMPOWERMENT_IMAGE;
  const paragraphs = [
    'A sustainable source of income can transform the future of an individual and an entire family.',
    'AIF supports initiatives that help people explore self-employment and build more secure livelihoods.',
    'Our programmes provide guidance on starting and managing small businesses, accessing early financial support and reaching customers and markets. By promoting entrepreneurship and livelihood opportunities, we help individuals build their own sources of income, become more self-reliant and create a more secure future for their families.',
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
            <img src={image} alt="Economic Empowerment" className="geo-img" />
            <div className="geo-frame-border"></div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Empowerment;