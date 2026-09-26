import ScrollToTop from '@/components/layout/ScrollToTop';
import educationProjectSeminar from '@/src/assets/education-project-seminar.png';

const educationImageSrc =
  typeof educationProjectSeminar === 'string'
    ? educationProjectSeminar
    : educationProjectSeminar?.src;

const Education = () => {
  const title = 'Education';
  const subtitle = 'Building Brighter Futures Through Education';
  const quote =
    'Every child deserves the opportunity to learn, grow and build a better future.';
  const badge = 'EDUCATION';
  const image = educationImageSrc;
  const paragraphs = [
    'For many children and young people from underprivileged families, financial hardship and limited access to quality educational support can become major barriers to achieving their potential.',
    'AIF works to address these challenges by creating opportunities for students to learn, develop and make informed choices about their future.',
    'Our education initiatives include scholarships, school development programmes, teacher training, career guidance seminars and skill development, helping students access better learning opportunities and supporting schools and teachers in creating stronger educational environments. Through these initiatives and partnerships with institutions, professionals and donors, AIF strives to make quality education more accessible and help students build the knowledge, skills and confidence they need for a brighter future.',
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
            <img src={image} alt="Education" className="geo-img" />
            <div className="geo-frame-border"></div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Education;