"use client";

import EventSection from './EventSection';
import { fallbackByTitle } from '@/lib/cmsImage';
import medicalCamp from '@/src/assets/medical-relief-camp.png';
import trainingWorkshop from '@/src/assets/employment-training-workshop.png';
import mentorshipAgra from '@/src/assets/mentorship-agra-chapter.png';
import communityDrive from '@/src/assets/gallery/community-registration-drive.png';

function assetSrc(image) {
  return typeof image === 'string' ? image : image?.src;
}

const FALLBACK_UPCOMING = [
  {
    id: 1,
    title: 'Kupwara Mega Job Fair',
    date: '22 August 2026',
    venue: 'Kupwara, Jammu & Kashmir',
    description:
      'A Mega Job Fair connecting job seekers with employers across multiple industries and creating opportunities for meaningful employment.',
    image: '/assets/kupwara-mega-job-fair.jpeg',
    imagePosition: 'center top',
  },
  {
    id: 2,
    title: 'National Mega Job Fair & Placement Drive',
    date: '12 Aug 2026',
    venue: 'Mumbai',
    description:
      'Bridging skilled youth with top-tier corporate employers across multiple industrial sectors with on-spot interviews and hiring.',
    image: '/assets/kupwara-mega-job-fair.jpeg',
  },
  {
    id: 3,
    title: 'Free Medical Camp & Health Screening',
    date: '22 Aug 2026',
    venue: 'Hyderabad',
    description:
      'Providing free health check-ups, critical illness screenings, and medical relief support for underserved communities.',
    image: assetSrc(medicalCamp),
  },
  {
    id: 4,
    title: 'Vocational Skill Development Bootcamp',
    date: '05 Sep 2026',
    venue: 'Bengaluru',
    description:
      'Intensive vocational training in digital skills, tailoring, and small-scale entrepreneurship for sustainable livelihoods.',
    image: assetSrc(trainingWorkshop),
  },
  {
    id: 5,
    title: 'Student Mentorship & Career Guidance Summit',
    date: '14 Oct 2026',
    venue: 'Pune',
    description:
      'One-on-one mentoring sessions with industry professionals to guide students through academic and career decision-making.',
    image: assetSrc(mentorshipAgra),
  },
  {
    id: 6,
    title: 'Community Outreach & Upliftment Drive',
    date: '12 Dec 2026',
    venue: 'Kolkata',
    description:
      'Grassroots community development initiative distributing essential supplies, financial literacy workshops, and self-help group setups.',
    image: assetSrc(communityDrive),
  },
];

const UpcomingEvents = ({ events, isVisible = null }) => {
  // Hide only when CMS/backend explicitly says hidden.
  if (isVisible === false) return null;

  // CMS list must be known — never paint FALLBACK_UPCOMING (can match drafts).
  if (!Array.isArray(events)) return null;

  const upcomingEvents = events.map((event) => ({
    ...event,
    fallbackImage: fallbackByTitle(FALLBACK_UPCOMING, event.title),
  }));

  return (
    <EventSection
      id="upcoming-events"
      tag="What's Next"
      title="Upcoming Events"
      subtitle="Discover transformative programs across education, employment, healthcare, and community development."
      events={upcomingEvents}
      ariaLabel="Upcoming events"
    />
  );
};

export default UpcomingEvents;
