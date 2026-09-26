"use client";

import { useEffect, useRef, useState } from 'react';
import Hero from '@/components/home/Hero';
import Impact from '@/components/home/Impact';
import Preview from '@/components/home/Preview';
import Projects from '@/components/home/Projects';
import PhotoGallery from '@/components/home/PhotoGallery';
import Testimonial from '@/components/home/Testimonial';
import Event from '@/components/home/Event';
import { loadHomeCmsClient } from '@/lib/contentApi';
import {
  cmsSnapshotEqual,
  hasCmsList,
  holdRenderableEvents,
  mergeHomeCms,
  peekHomeCms,
  rememberHomeCms,
} from '@/lib/cmsClientCache';

const EMPTY_HOME_CMS = {
  heroBanners: null,
  homeProjects: null,
  homeEvents: null,
  homeGallery: null,
  testimonials: null,
  homeEventsVisible: null,
};

function seedHomeCms(initialCms) {
  const peek = typeof window !== 'undefined' ? peekHomeCms() : null;
  const next = mergeHomeCms(peek, initialCms && typeof initialCms === 'object' ? initialCms : null);
  if (typeof window !== 'undefined') rememberHomeCms(next);
  return next.heroBanners !== undefined ? next : EMPTY_HOME_CMS;
}

/**
 * ISR seeds first paint. Client fetch only runs when no snapshot exists.
 * Upcoming Events stays mounted from the last valid list unless CMS
 * explicitly sets visible false.
 */
const Home = ({ initialCms = null }) => {
  const [cms, setCms] = useState(() => seedHomeCms(initialCms));
  const heldEventsRef = useRef(null);
  heldEventsRef.current = holdRenderableEvents(
    heldEventsRef.current,
    cms.homeEventsVisible,
    cms.homeEvents
  );
  const heldEvents = heldEventsRef.current;
  const showUpcoming = heldEvents.visible !== false && Array.isArray(heldEvents.events);

  useEffect(() => {
    if (initialCms && typeof initialCms === 'object') {
      setCms((prev) => {
        const next = mergeHomeCms(prev, initialCms);
        if (cmsSnapshotEqual(prev, next)) return prev;
        rememberHomeCms(next);
        return next;
      });
    }
  }, [initialCms]);

  useEffect(() => {
    const peeked = peekHomeCms();
    if (!peeked) return;
    setCms((prev) => {
      const next = mergeHomeCms(peeked, prev);
      if (cmsSnapshotEqual(prev, next)) return prev;
      rememberHomeCms(next);
      return next;
    });
  }, []);

  useEffect(() => {
    if (hasCmsList(initialCms) || hasCmsList(peekHomeCms())) return undefined;
    let cancelled = false;
    (async () => {
      const data = await loadHomeCmsClient();
      if (cancelled) return;
      setCms((prev) => {
        const next = mergeHomeCms(prev, data);
        if (cmsSnapshotEqual(prev, next)) return prev;
        rememberHomeCms(next);
        return next;
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [initialCms]);

  return (
    <>
      <Hero slides={cms.heroBanners} />
      <Preview />
      <Impact />
      <Projects projects={cms.homeProjects} />
      {showUpcoming ? (
        <Event events={heldEvents.events} isVisible={heldEvents.visible !== false} />
      ) : null}
      <PhotoGallery images={cms.homeGallery} />
      <Testimonial testimonials={cms.testimonials} />
    </>
  );
};

export default Home;
