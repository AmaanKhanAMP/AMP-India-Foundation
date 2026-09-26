import { motion } from 'framer-motion';

const pastEvents = [
  {
    id: 1,
    name: 'National Job Fair 2025',
    year: '2025',
    location: 'Mumbai',
    image:
       'https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=600&q=80',
    tall: true,
  },
  {
    id: 2,
    name: 'Medical Relief Camp',
    year: '2025',
    location: 'Hyderabad',
    image:
 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80',
    tall: false,
  },
  {
    id: 3,
    name: 'Scholarship Distribution',
    year: '2024',
    location: 'Delhi',
    image:
      'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=600&q=80',
    tall: false,
  },
  {
    id: 4,
    name: 'Skill Training Graduation',
    year: '2024',
    location: 'Bengaluru',
    image:
      'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80',
    tall: true,
  },
  {
    id: 5,
    name: 'Mentorship Summit',
    year: '2024',
    location: 'Pune',
    image:
      'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80',
    tall: false,
  },
  {
    id: 6,
    name: 'Community Upliftment Drive',
    year: '2023',
    location: 'Kolkata',
    image:
      'https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=600&q=80',
    tall: true,
  },
];

const PastEventsGallery = () => {
  return (
    <section className="past-events-section" aria-label="Past events gallery">
      <div className="ev-container">
        <header className="ev-section-header">
          <span className="ev-section-tag">Our Legacy</span>
          <h2 className="ev-section-title">
            Past Events <span className="ev-accent">Gallery</span>
          </h2>
          <p className="ev-section-subtitle">
            Celebrating years of transformative impact across communities throughout India.
          </p>
        </header>

        <div className="past-events-masonry">
          {pastEvents.map((event, index) => (
            <motion.figure
              key={event.id}
              className="past-event-item"
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ delay: index * 0.08, duration: 0.5 }}
            >
              <img src={event.image} alt={event.name} loading="lazy" />
              <figcaption className="past-event-overlay">
                <p className="past-event-name">{event.name}</p>
                <span className="past-event-meta">
                  {event.year} · {event.location}
                </span>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PastEventsGallery;
