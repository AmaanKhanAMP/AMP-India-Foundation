import { motion } from 'framer-motion';
import { Calendar, MapPin } from 'lucide-react';

const EventCard = ({ event, index = 0 }) => {
  return (
    <motion.article
      className="event-card"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ delay: index * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -8 }}
    >
      <div className="event-card-image">
        <img src={event.image} alt={event.title} loading="lazy" />
        <span className="event-card-category">{event.category}</span>
      </div>

      <div className="event-card-body">
        <h3 className="event-card-title">{event.title}</h3>

        <div className="event-card-meta">
          <span>
            <Calendar aria-hidden="true" />
            {event.date}
          </span>
          <span>
            <MapPin aria-hidden="true" />
            {event.venue}
          </span>
        </div>

        <p className="event-card-desc">{event.description}</p>
      </div>
    </motion.article>
  );
};

export default EventCard;
