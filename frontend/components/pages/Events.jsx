"use client";

import { useEffect, useRef, useState } from 'react';
import ScrollToTop from '@/components/layout/ScrollToTop';
import EventsHero from '@/components/events/EventsHero';
import FeaturedEvent from '@/components/events/FeaturedEvent';
import UpcomingEvents from '@/components/events/UpcomingEvents';
import EventCategories from '@/components/events/EventCategories';
import EventTimeline from '@/components/events/EventTimeline';
import PastEventsGallery from '@/components/events/PastEventsGallery';
import VolunteerCTA from '@/components/events/VolunteerCTA';
import { loadEventsCmsClient } from '@/lib/contentApi';
import {
  cmsSnapshotEqual,
  hasCmsList,
  holdRenderableEvents,
  mergeEventsCms,
  peekEventsCms,
  rememberEventsCms,
} from '@/lib/cmsClientCache';
import '@/styles/Events.css';

const EMPTY_EVENTS_CMS = {
  featuredEvents: null,
  upcomingEvents: null,
  pastEvents: null,
  upcomingVisible: null,
};

function seedEventsCms(initialCms) {
  const peek = typeof window !== 'undefined' ? peekEventsCms() : null;
  const next = mergeEventsCms(peek, initialCms && typeof initialCms === 'object' ? initialCms : null);
  if (typeof window !== 'undefined') rememberEventsCms(next);
  return next.featuredEvents !== undefined ? next : EMPTY_EVENTS_CMS;
}

/**
 * ISR seeds first paint. A previously visible Upcoming Events section is
 * held through transient null/empty revalidation and is not remounted by
 * a null Suspense fallback.
 */
const Events = ({ initialCms = null }) => {
  const [cms, setCms] = useState(() => seedEventsCms(initialCms));
  const heldUpcomingRef = useRef(null);
  heldUpcomingRef.current = holdRenderableEvents(
    heldUpcomingRef.current,
    cms.upcomingVisible,
    cms.upcomingEvents
  );
  const heldUpcoming = heldUpcomingRef.current;
  const showUpcoming =
    heldUpcoming.visible !== false && Array.isArray(heldUpcoming.events);

  useEffect(() => {
    if (initialCms && typeof initialCms === 'object') {
      setCms((prev) => {
        const next = mergeEventsCms(prev, initialCms);
        if (cmsSnapshotEqual(prev, next)) return prev;
        rememberEventsCms(next);
        return next;
      });
    }
  }, [initialCms]);

  useEffect(() => {
    const peeked = peekEventsCms();
    if (!peeked) return;
    setCms((prev) => {
      const next = mergeEventsCms(peeked, prev);
      if (cmsSnapshotEqual(prev, next)) return prev;
      rememberEventsCms(next);
      return next;
    });
  }, []);

  useEffect(() => {
    if (hasCmsList(initialCms) || hasCmsList(peekEventsCms())) return undefined;
    let cancelled = false;
    (async () => {
      const data = await loadEventsCmsClient();
      if (cancelled) return;
      setCms((prev) => {
        const next = mergeEventsCms(prev, data);
        if (cmsSnapshotEqual(prev, next)) return prev;
        rememberEventsCms(next);
        return next;
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [initialCms]);

  return (
    <div className="events-page-canvas">
      <ScrollToTop />
      <EventsHero />
      <FeaturedEvent items={cms.featuredEvents} />
      {showUpcoming ? (
        <UpcomingEvents
          events={heldUpcoming.events}
          isVisible={heldUpcoming.visible !== false}
        />
      ) : null}
      <PastEventsGallery events={cms.pastEvents} />
      <EventTimeline />
      <EventCategories />
      <VolunteerCTA
        title="Be Part of Our Next Event"
        text="Whether you are a student, volunteer, professional, institution or corporate partner, your participation helps create opportunities that transform lives. Together, we can make every event a step towards a stronger and more inclusive society."
        secondaryLabel="Partner With Us"
      />
    </div>
  );
};

export default Events;
