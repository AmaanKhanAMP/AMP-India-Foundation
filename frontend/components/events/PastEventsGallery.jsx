"use client";
import EventSection from './EventSection';
import { fallbackByTitle } from '@/lib/cmsImage';
import srinagarJobFair from '@/src/assets/past-events/srinagar-job-fair.jpg';
import kolkataJobFair from '@/src/assets/past-events/kolkata-job-fair.jpg';
import doddaballapurJobFair from '@/src/assets/past-events/doddaballapur-job-fair.jpg';
import nandedJobFair from '@/src/assets/past-events/nanded-job-fair.jpg';
import ntsExam from '@/src/assets/past-events/nts-2025.jpg';
import mumbaiUnityJobFair from '@/src/assets/past-events/mumbai-unity-job-fair-2024.jpg';

function assetSrc(image) {
  return typeof image === 'string' ? image : image?.src;
}

/**
 * Past Events grid — CMS data is loaded on the server and passed as props.
 * When loadPublished fails (null), use local fallback — same pattern as Hero / Gallery / Testimonials.
 * Empty CMS arrays are kept as-is (no fallback restore).
 */
const FALLBACK_PAST_EVENTS = [
  {
    id: 1,
    title: "AMP's 2nd Srinagar, Kashmir Job Fair",
    date: '30 August 2025',
    venue: 'Srinagar, Jammu & Kashmir',
    description:
      'AMP, in partnership with Hamdard Learning & Welfare Society, organised a mega Job Fair at IITM campus, Hyderpora, Srinagar. The event registered 2,769 candidates, with 1,606 interviewed and 404 candidates shortlisted and selected.',
    image: assetSrc(srinagarJobFair),
  },
  {
    id: 2,
    title: 'AMP Kolkata Job Fair',
    date: '23 August 2025',
    venue: 'Kolkata, West Bengal',
    description:
      "AMP, in partnership with Govt. Girls' General Degree College, organised a Job Fair in Kolkata with 492 registered candidates and 18 participating companies offering 2,800+ job vacancies. 288 candidates were shortlisted and selected.",
    image: assetSrc(kolkataJobFair),
  },
  {
    id: 3,
    title: 'AMP Mega Job Fair in Doddaballapur',
    date: '12 April 2025',
    venue: 'Doddaballapur, Karnataka',
    description:
      'AMP organised a Mega Job Fair at Lavanya Degree College, Doddaballapur, in partnership with Lavanya Group of Institutions. The event attracted 215 candidates, with 9 companies offering 1,972+ vacancies and 113 candidates shortlisted and selected.',
    image: assetSrc(doddaballapurJobFair),
  },
  {
    id: 4,
    title: 'AMP Mega Job Fair in Nanded',
    date: '11 January 2025',
    venue: 'Nanded, Maharashtra',
    description:
      'AMP, in association with World Memon Organisation and Memon Community Trust, organised a Mega Job Fair at ITM College, Nanded. Around 1,000 candidates were interviewed, with 450+ selected and shortlisted and 33 corporates and recruiters participating.',
    image: assetSrc(nandedJobFair),
  },
  {
    id: 5,
    title: 'AMP National Talent Search 2025 – Grand Launch',
    date: '7 December 2024',
    venue: 'Pan India',
    description:
      'AIF/AMP launched the National Talent Search 2025 programme and felicitated the National Awardees, bringing together distinguished guests, professionals and community leaders to celebrate talent, education and achievement.',
    image: assetSrc(ntsExam),
  },
  {
    id: 6,
    title: 'AMP Unity Job Fair at Mumbai 2024',
    date: '17 August 2024',
    venue: 'Mumbai, Maharashtra',
    description:
      'AMP, along with Pir Makhdum Saheb Charitable Trust and Bombay Catholic Sabha, organised a Free Mega Job Fair at Sacred Heart Boys School, Santacruz, Mumbai. The event had 1,768 candidates interviewed, with 80 selected and 554 shortlisted for the next round.',
    image: assetSrc(mumbaiUnityJobFair),
  },
];

const PastEventsGallery = ({ events }) => {
  const rawEvents = Array.isArray(events) ? events : FALLBACK_PAST_EVENTS;
  const pastEvents = rawEvents.map((event) => ({
    ...event,
    fallbackImage: fallbackByTitle(FALLBACK_PAST_EVENTS, event.title),
  }));

  return (
    <EventSection
      id="past-events"
      tag="Our Legacy"
      title="Our Journey So Far"
      subtitle="Over the years, AMP India Foundation has organised hundreds of impactful programmes across India, helping students pursue higher education, enabling youth to find meaningful employment and supporting communities through healthcare and livelihood initiatives."
      events={pastEvents}
      ariaLabel="Past events"
      className="past-events-listing"
      useDescriptionFallback
    />
  );
};

export default PastEventsGallery;
