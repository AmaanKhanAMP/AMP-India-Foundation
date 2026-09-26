import Link from 'next/link';
import Image from 'next/image';

import employmentSupportImage from '@/src/assets/employment-support-job-fair.jpg';
import careerGuidanceSeminar from '@/src/assets/career-guidance-seminar.png';
import educationSupportStudents from '@/src/assets/education-support-students.png';

const cardData = [
  {
    id: 1,
    href: '/projects/education',
    image: educationSupportStudents,
    title: 'Education Support',
    subtitle: 'Building Brighter Futures',
    description:
      'We help deserving students continue their education through scholarships, mentoring, career guidance and skill development, ensuring that financial hardship does not become a barrier to success.',
  },
  {
    id: 2,
    href: '/projects/employment',
    image: employmentSupportImage,
    title: 'Employment Support',
    subtitle: 'Creating Better Career Opportunities',
    description:
      'We prepare young people for successful careers through employability training, career counselling, job fairs and placement support, helping them secure meaningful employment.',
  },
  {
    id: 3,
    href: '/projects/mentorship',
    image: careerGuidanceSeminar,
    title: 'Mentorship & Guidance',
    subtitle: 'Inspiring the Next Generation',
    description:
      'Our experienced professionals mentor students and young graduates by sharing knowledge, career advice and life skills that help them achieve their personal and professional goals.',
  },
];

const Preview = () => {
  const items = cardData;
  const heading = 'WELCOME TO';
  const accent = 'AMP INDIA FOUNDATION';
  const lead = 'Together, We Create Lasting Change';
  const intro =
    'AMP India Foundation (AIF) is a registered non-profit organization working to improve the lives of underprivileged communities across India. Through education, employment, skill development, healthcare and community empowerment, we help people build better futures with dignity and confidence.';
  const extra =
    'Supported by a nationwide network of professionals, volunteers, donors and partner organizations, we strive to create opportunities that bring lasting social impact.';
  return (
    <section className="welcome-section">
      <div className="section-container">
        <div className="section-header-block">
          <h2 className="main-section-title">
            {heading} <span className="title-accent-blue">{accent}</span>
          </h2>
          <div className="decorative-line-wrapper">
            <span className="line-segment short"></span>
            <span className="line-segment long"></span>
            <span className="line-segment short"></span>
          </div>
          <p className="section-intro-text">
            <strong>{lead}</strong>
          </p>
          <p className="section-intro-text">{intro}</p>
          <p className="section-intro-text">{extra}</p>
        </div>

        <div className="cards-grid-layout">
          {items.map((card) => (
            <Link
              key={card.id}
              href={card.href}
              className="info-feature-card"
              aria-label={`${card.title} — view project details`}
              scroll
            >
              <div className="card-image-box">
                <Image
                  src={card.image}
                  alt={card.title}
                  fill
                  sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  loading="lazy"
                  className="feature-card-img"
                />
              </div>
              <div className="card-content-box">
                <h3 className="card-main-title">{card.title}</h3>
                <h4 className="card-sub-title">{card.subtitle}</h4>
                <p className="card-description-text">{card.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Preview;
