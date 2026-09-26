import EventCard from './EventCard';

const upcomingEvents = [
  {
    id: 1,
    title: 'Scholarship Awareness & Education Workshop',
    category: 'Education',
    date: '18 Jan 2026',
    venue: 'Delhi NCR',
    description:
      'Guiding meritorious underprivileged students on scholarship applications, higher education pathways, and Centres of Excellence programs.',
    image:
      'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 2,
    title: 'National Mega Job Fair & Placement Drive',
    category: 'Employment',
    date: '12 Aug 2026',
    venue: 'Mumbai',
    description:
      'Bridging skilled youth with top-tier corporate employers across multiple industrial sectors with on-spot interviews and hiring.',
    image:
      'https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 3,
    title: 'Free Medical Camp & Health Screening',
    category: 'Medical Camp',
    date: '22 Aug 2026',
    venue: 'Hyderabad',
    description:
      'Providing free health check-ups, critical illness screenings, and medical relief support for underserved communities.',
    image:
      'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 4,
    title: 'Vocational Skill Development Bootcamp',
    category: 'Skill Development',
    date: '05 Sep 2026',
    venue: 'Bengaluru',
    description:
      'Intensive vocational training in digital skills, tailoring, and small-scale entrepreneurship for sustainable livelihoods.',
    image:
      'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 5,
    title: 'Student Mentorship & Career Guidance Summit',
    category: 'Career Guidance',
    date: '14 Oct 2026',
    venue: 'Pune',
    description:
      'One-on-one mentoring sessions with industry professionals to guide students through academic and career decision-making.',
    image:
      'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 6,
    title: 'Community Outreach & Upliftment Drive',
    category: 'Community Outreach',
    date: '12 Dec 2026',
    venue: 'Kolkata',
    description:
      'Grassroots community development initiative distributing essential supplies, financial literacy workshops, and self-help group setups.',
    image:
      'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=600&q=80',
  },
];

const UpcomingEvents = () => {
  return (
    <section id="upcoming-events" className="upcoming-events-section" aria-label="Upcoming events">
      <div className="ev-container">
        <header className="ev-section-header">
          <span className="ev-section-tag">What&apos;s Next</span>
          <h2 className="ev-section-title">
            Upcoming <span className="ev-accent">Events</span>
          </h2>
          <p className="ev-section-subtitle">
            Discover transformative programs across education, employment, healthcare, and community development.
          </p>
          <div className="ev-decorative-line" aria-hidden="true">
            <span className="short" />
            <span className="long" />
            <span className="short" />
          </div>
        </header>

        <div className="upcoming-events-grid">
          {upcomingEvents.map((event, index) => (
            <EventCard key={event.id} event={event} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default UpcomingEvents;
