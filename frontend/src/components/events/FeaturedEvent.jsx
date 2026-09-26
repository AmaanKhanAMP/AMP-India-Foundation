import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin } from 'lucide-react';

const featuredEvent = {
  title: 'Career Guidance & Employment Drive 2026',
  date: 'Saturday, 15 March 2026',
  time: '9:00 AM – 5:00 PM',
  venue: 'Mumbai',
  category: 'Employment',
  description:
    'A flagship employment initiative connecting skilled youth with leading corporate employers. Featuring resume clinics, mock interviews, on-spot hiring, and career counselling by industry professionals.',
  image:
    'https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=900&q=80',
};

const FeaturedEvent = () => {
  return (
    <section className="featured-event-section" aria-label="Featured event">
      <motion.article
        className="featured-event-card"
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="featured-event-image-wrap">
          <img
            src={featuredEvent.image}
            alt={featuredEvent.title}
            loading="lazy"
          />
          <span className="featured-event-badge">{featuredEvent.category}</span>
        </div>

        <div className="featured-event-body">
          <span className="featured-event-label">Featured Event</span>
          <h2 className="featured-event-title">{featuredEvent.title}</h2>
          <p className="featured-event-desc">{featuredEvent.description}</p>

          <div className="featured-event-meta">
            <span className="featured-meta-item">
              <Calendar size={16} aria-hidden="true" />
              {featuredEvent.date}
            </span>
            <span className="featured-meta-item">
              <Clock size={16} aria-hidden="true" />
              {featuredEvent.time}
            </span>
            <span className="featured-meta-item">
              <MapPin size={16} aria-hidden="true" />
              {featuredEvent.venue}
            </span>
          </div>

          {/* <a href="#upcoming-events" className="events-btn-primary">
            Register Now
          </a> */}
        </div>
      </motion.article>
    </section>
  );
};

export default FeaturedEvent;
