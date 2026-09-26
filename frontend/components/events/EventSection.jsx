"use client";

import EventCard from './EventCard';

function TitleWithAccent({ title }) {
  const parts = String(title).trim().split(/\s+/);
  if (parts.length < 2) {
    return title;
  }
  const last = parts.pop();
  return (
    <>
      {parts.join(' ')} <span className="ev-accent">{last}</span>
    </>
  );
}

/**
 * Shared events grid section — used for Upcoming and Past listings.
 */
const EventSection = ({
  id,
  title,
  tag,
  subtitle,
  events = [],
  buttonLabel = 'Register Now',
  showButton = false,
  useDescriptionFallback = true,
  showDecorativeLine = true,
  ariaLabel,
  className = '',
}) => {
  return (
    <section
      id={id}
      className={`upcoming-events-section ${className}`.trim()}
      aria-label={ariaLabel || title}
    >
      <div className="ev-container">
        <header className="ev-section-header">
          {tag ? <span className="ev-section-tag">{tag}</span> : null}
          <h2 className="ev-section-title">
            <TitleWithAccent title={title} />
          </h2>
          {subtitle ? <p className="ev-section-subtitle">{subtitle}</p> : null}
          {showDecorativeLine ? (
            <div className="ev-decorative-line" aria-hidden="true">
              <span className="short" />
              <span className="long" />
              <span className="short" />
            </div>
          ) : null}
        </header>

        <div className="upcoming-events-grid">
          {events.map((event, index) => (
            <EventCard
              key={event.id ?? index}
              event={event}
              index={index}
              buttonLabel={buttonLabel}
              showButton={showButton}
              useDescriptionFallback={useDescriptionFallback}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default EventSection;
