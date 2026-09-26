"use client";

import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin } from 'lucide-react';
import { fallbackByTitle } from '@/lib/cmsImage';
import CmsMediaImage from '@/components/media/CmsMediaImage';

const FALLBACK_FEATURED = {
  title: 'Kupwara Mega Job Fair',
  date: '22 August 2026',
  venue: 'Kupwara, Jammu & Kashmir',
  description:
    'A Mega Job Fair connecting job seekers with employers across multiple industries and creating opportunities for meaningful employment.',
  image: '/assets/kupwara-mega-job-fair.jpeg',
  imageFit: 'contain',
};

const FeaturedEventCard = ({ featuredEvent }) => {
  const fallbackSrc = fallbackByTitle([FALLBACK_FEATURED], featuredEvent.title);
  const imageContain = featuredEvent.imageFit === 'contain';

  return (
    <section className="featured-event-section" aria-label="Featured event">
      <motion.article
        className="featured-event-card"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      >
        <div
          className={`featured-event-image-wrap${imageContain ? ' featured-event-image-wrap--contain' : ''}`}
        >
          <CmsMediaImage
            cmsSrc={featuredEvent.image}
            fallbackSrc={fallbackSrc}
            alt={featuredEvent.title}
            fill
            sizes="(max-width: 768px) 100vw, 50vw"
            loading="lazy"
            className="featured-event-photo"
            style={
              imageContain
                ? { objectFit: 'contain', objectPosition: 'center' }
                : { objectFit: 'cover', objectPosition: 'center' }
            }
          />
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
            {featuredEvent.time ? (
              <span className="featured-meta-item">
                <Clock size={16} aria-hidden="true" />
                {featuredEvent.time}
              </span>
            ) : null}
            <span className="featured-meta-item">
              <MapPin size={16} aria-hidden="true" />
              {featuredEvent.venue}
            </span>
          </div>
        </div>
      </motion.article>
    </section>
  );
};

const FeaturedEvent = ({ items: itemsProp }) => {
  const items = Array.isArray(itemsProp) ? itemsProp : [FALLBACK_FEATURED];
  const featuredEvent = items[0];

  // No published featured event — do not resurrect hardcoded fallback
  if (!featuredEvent) return null;

  return <FeaturedEventCard featuredEvent={featuredEvent} />;
};

export default FeaturedEvent;
