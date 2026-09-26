"use client";

import Image from 'next/image';
import { motion } from 'framer-motion';
import { fallbackByTitle, useCmsImageSrc } from '@/lib/cmsImage';

import communityRegistrationDrive from '@/src/assets/gallery/community-registration-drive.png';
import communityEventRegistration from '@/src/assets/gallery/community-event-registration.png';
import ampAhmedabadWorkshop from '@/src/assets/gallery/amp-ahmedabad-chapter-workshop.png';
import megaJobFairByculla from '@/src/assets/gallery/mega-job-fair-byculla-mumbai.png';
import megaJobFairBallari from '@/src/assets/gallery/mega-job-fair-ballari.png';
import megaJobFairThassimBeevi from '@/src/assets/gallery/mega-job-fair-thassim-beevi-college.png';

const FALLBACK_GALLERY = [
  {
    id: 1,
    src: communityRegistrationDrive,
    alt: 'Large outdoor crowd queued for a community registration and outreach drive',
    title: 'Community Outreach & Registration Drive',
    description:
      'A massive turnout of community members gathering for an organized event, showcasing large-scale engagement and participation.',
  },
  {
    id: 2,
    src: communityEventRegistration,
    alt: 'Organizers assisting participants with registration at a community event desk',
    title: 'Community Outreach and Registration',
    description:
      'A glimpse into one of our community outreach programs, where local residents receive guidance and register for essential services at a dedicated event hub.',
  },
  {
    id: 3,
    src: ampAhmedabadWorkshop,
    alt: 'Presenter leading an AMP Ahmedabad Chapter workshop for seated members',
    title: 'AMP Ahmedabad Chapter Meeting',
    description:
      'Members of the Association of Muslim Professionals (AMP) Ahmedabad Chapter attend a professional development workshop and presentation focused on community initiatives.',
  },
  {
    id: 4,
    src: megaJobFairByculla,
    alt: 'Speaker at the podium during the Mega Job Fair at Byculla, Mumbai',
    title: 'Mega Job Fair at Byculla, Mumbai',
    description:
      'Dignitaries and speakers at the Mega Job Fair held on December 8, 2018, at Saboo Siddik College, Mumbai, organized by the Association of Muslim Professionals (AMP) and World Memon Organization.',
  },
  {
    id: 5,
    src: megaJobFairBallari,
    alt: 'Audience seated under a tent at the Mega Job Fair in Ballari, Karnataka',
    title: 'Mega Job Fair — Ballari, Karnataka',
    description:
      'A large-scale recruitment event held at The English Medium High School in Ballari, where hundreds of candidates gathered to connect with employers.',
  },
  {
    id: 6,
    src: megaJobFairThassimBeevi,
    alt: 'Interview stations filled with candidates at a Mega Job Fair college auditorium',
    title: 'Mega Job Fair at Thassim Beevi Abdul Kader College',
    description:
      'A wide-angle view of the Mega Job Fair held in the college auditorium, showing numerous interview stations and attendees engaged in career opportunities.',
  },
];

const ease = [0.22, 1, 0.36, 1];

const sectionVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.06 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease },
  },
};

const imageVariants = {
  hidden: { opacity: 0, y: 28 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease },
  },
};

const GalleryCardImage = ({ item }) => {
  const fallbackSrc = fallbackByTitle(FALLBACK_GALLERY, item.title, 'src');
  const { src, onError } = useCmsImageSrc(item.src, fallbackSrc);
  return (
    <Image
      src={src}
      alt={item.alt || item.title || 'Gallery image'}
      fill
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      className="home-gallery-image"
      loading="lazy"
      onError={onError}
    />
  );
};

const PhotoGallery = ({ images }) => {
  const galleryImages = Array.isArray(images) ? images : FALLBACK_GALLERY;

  return (
    <section className="home-photo-gallery" aria-label="Photo gallery">
      <div className="home-gallery-glow" aria-hidden="true" />
      <div className="home-gallery-blob home-gallery-blob-tr" aria-hidden="true" />
      <div className="home-gallery-blob home-gallery-blob-bl" aria-hidden="true" />

      <motion.div
        className="home-gallery-container"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={sectionVariants}
      >
        <motion.header className="home-gallery-header" variants={fadeUp}>
          <p className="home-gallery-eyebrow">PHOTO GALLERY</p>
          <h2 className="home-gallery-title">
            Capturing Moments of <span className="title-accent-blue">Impact</span>
          </h2>
          <div className="decorative-line-wrapper" aria-hidden="true">
            <span className="line-segment short" />
            <span className="line-segment long" />
            <span className="line-segment short" />
          </div>
          <p className="home-gallery-subtitle">
            A glimpse into our initiatives, volunteers, and the lives transformed through
            education, healthcare, skill development, and community empowerment.
          </p>
        </motion.header>

        <div className="home-gallery-grid">
          {galleryImages.map((item) => (
            <motion.figure
              key={item.id}
              className="home-gallery-card"
              variants={imageVariants}
            >
              <div className="home-gallery-media">
                <GalleryCardImage item={item} />
              </div>
              <figcaption className="home-gallery-caption">
                <h3 className="home-gallery-item-title">{item.title}</h3>
                <p className="home-gallery-item-desc">{item.description}</p>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

export default PhotoGallery;
