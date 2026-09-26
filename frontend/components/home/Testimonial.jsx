"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import CmsMediaImage from '@/components/media/CmsMediaImage';

const AUTO_SCROLL_MS = 5000;
const SWIPE_THRESHOLD_PX = 48;
const EASE = [0.45, 0, 0.2, 1];

/**
 * Local fallbacks use public/assets paths (same pattern as Medical, Contact, Navbar).
 * Do not ES-import from src/assets for site images — this project serves them from public/.
 */
const DEFAULT_AVATAR = '/assets/logo.png';

const LOCAL_AVATARS_BY_NAME = {
  'mrinal kanti debnath': '/assets/testimonials/aamir-malik.png',
  'yawar ihsan': '/assets/testimonials/imran-shaikh.png',
  'chandrakant khade': '/assets/testimonials/rahul-sharma.png',
  'mohammed farrok gheewala': '/assets/testimonials/imran-siddiqui.png',
  'vikram singh': '/assets/testimonials/mohammed-arif.png',
  'mohammed ekramuddin shaikh': '/assets/testimonials/mohammed-ekramuddin-shaikh.png',
};

function normalizeName(name) {
  return String(name || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

/**
 * True when avatar looks like a real CMS/media upload (not empty, not stock Unsplash,
 * not a local public fallback under /assets/).
 * Priority: CMS upload → local fallback → default placeholder.
 */
function isCmsUploadedAvatar(url) {
  if (!url || typeof url !== 'string') return false;
  const value = url.trim();
  if (!value) return false;
  if (/unsplash\.com/i.test(value)) return false;
  if (/^https?:\/\/images\.unsplash\.com/i.test(value)) return false;
  // Local public assets are fallbacks, not CMS uploads
  if (value.startsWith('/assets/')) return false;
  return true;
}

function localAvatarForName(name) {
  return LOCAL_AVATARS_BY_NAME[normalizeName(name)] || null;
}

function resolveTestimonialAvatar(item) {
  if (isCmsUploadedAvatar(item?.avatar)) {
    return item.avatar;
  }
  return localAvatarForName(item?.name) || DEFAULT_AVATAR;
}

const FALLBACK_TESTIMONIALS = [
  {
    id: 1,
    name: 'Mrinal Kanti Debnath',
    role: 'HR Recruiter, Godrej Appliances',
    location: '',
    avatar: '/assets/testimonials/aamir-malik.png',
    quote:
      '"We have been associated with AMP India Foundation\'s employment initiatives for several years. Their job fairs are well-organized and help us connect with quality candidates. We look forward to continuing this valuable partnership in the years ahead."',
  },
  {
    id: 2,
    name: 'Yawar Ihsan',
    role: 'Operations Officer, G4S Secure',
    location: '',
    avatar: '/assets/testimonials/imran-shaikh.png',
    quote:
      '"Participating in the employment drive was a rewarding experience. It gave me the opportunity to interact with talented candidates from diverse backgrounds while witnessing the Foundation\'s commitment to creating meaningful career opportunities for job seekers."',
  },
  {
    id: 3,
    name: 'Chandrakant Khade',
    role: 'Apprentice Recruitment Officer, Allied Resource Management Services Pvt. Ltd.',
    location: '',
    avatar: '/assets/testimonials/rahul-sharma.png',
    quote:
      '"It was a wonderful experience participating in the event. The programme was professionally managed and provided an excellent platform for connecting deserving candidates with employment opportunities."',
  },
  {
    id: 4,
    name: 'Mohammed Farrok Gheewala',
    role: 'Chairman, F. Gheewala HR Consultants',
    location: '',
    avatar: '/assets/testimonials/imran-siddiqui.png',
    quote:
      '"The Mumbai Job Fair was a well-coordinated initiative, and we appreciate the dedication and professionalism of the AMP India Foundation team. We value our association and look forward to participating in many more such impactful programmes."',
  },
  {
    id: 5,
    name: 'Vikram Singh',
    role: 'Lead Recruiter, PVK HR Solutions Pvt. Ltd.',
    location: '',
    avatar: '/assets/testimonials/mohammed-arif.png',
    quote:
      '"AMP India Foundation is creating meaningful social impact by connecting underprivileged youth with employment opportunities. Their commitment, transparency and nationwide outreach make them a trusted partner in community development."',
  },
  {
    id: 6,
    name: 'Mohammed Ekramuddin Shaikh',
    role: 'Co-Founder & Managing Partner, Nutra Essenza Wellness LLP',
    location: '',
    avatar: '/assets/testimonials/mohammed-ekramuddin-shaikh.png',
    quote:
      '"My association with AMP India Foundation\'s Employment Assistance Cell has been truly inspiring. Their dedication to career guidance, mentoring and skill development is empowering thousands of young people and helping build a stronger and more confident society."',
  },
];

const Testimonial = ({ testimonials }) => {
  const rawTestimonials = Array.isArray(testimonials)
    ? testimonials
    : FALLBACK_TESTIMONIALS;

  const testimonialsData = rawTestimonials.map((item) => ({
    ...item,
    avatar: resolveTestimonialAvatar(item),
  }));
  const total = testimonialsData.length;

  const [activeIndex, setActiveIndex] = useState(1);
  const [direction, setDirection] = useState(1);
  const [isPaused, setIsPaused] = useState(false);
  const pointerRef = useRef({ tracking: false, startX: 0, startY: 0 });
  const resumeTimerRef = useRef(null);

  const clearResumeTimer = useCallback(() => {
    if (resumeTimerRef.current != null) {
      window.clearTimeout(resumeTimerRef.current);
      resumeTimerRef.current = null;
    }
  }, []);

  const pauseAutoplay = useCallback(() => {
    clearResumeTimer();
    setIsPaused(true);
  }, [clearResumeTimer]);

  const resumeAutoplay = useCallback(
    (delayMs = 0) => {
      clearResumeTimer();
      if (delayMs > 0) {
        resumeTimerRef.current = window.setTimeout(() => {
          setIsPaused(false);
          resumeTimerRef.current = null;
        }, delayMs);
        return;
      }
      setIsPaused(false);
    },
    [clearResumeTimer]
  );

  const goTo = useCallback(
    (index, dir = 1) => {
      if (total <= 0) return;
      const next = ((index % total) + total) % total;
      setDirection(dir);
      setActiveIndex(next);
    },
    [total]
  );

  const handlePrev = useCallback(() => {
    goTo(activeIndex - 1, -1);
  }, [activeIndex, goTo]);

  const handleNext = useCallback(() => {
    goTo(activeIndex + 1, 1);
  }, [activeIndex, goTo]);

  useEffect(() => {
    if (isPaused || total <= 1) return undefined;

    const id = window.setInterval(() => {
      setDirection(1);
      setActiveIndex((prev) => (prev === total - 1 ? 0 : prev + 1));
    }, AUTO_SCROLL_MS);

    return () => window.clearInterval(id);
  }, [isPaused, total, activeIndex]);

  useEffect(() => () => clearResumeTimer(), [clearResumeTimer]);

  const getCardPositionClass = (index) => {
    const raw = ((index - activeIndex) % total + total) % total;
    const offset = raw <= Math.floor(total / 2) ? raw : raw - total;

    switch (offset) {
      case 0:
        return 'position-center';
      case -1:
        return 'position-left-1';
      case -2:
        return 'position-left-2';
      case 1:
        return 'position-right-1';
      case 2:
        return 'position-right-2';
      default:
        return 'position-hidden';
    }
  };

  const onPointerDown = (event) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    pointerRef.current = {
      tracking: true,
      startX: event.clientX,
      startY: event.clientY,
    };
    if (event.pointerType !== 'mouse') {
      pauseAutoplay();
    }
  };

  const onPointerUp = (event) => {
    if (!pointerRef.current.tracking) return;

    const dx = event.clientX - pointerRef.current.startX;
    const dy = event.clientY - pointerRef.current.startY;
    const isSwipe =
      Math.abs(dx) >= SWIPE_THRESHOLD_PX && Math.abs(dx) > Math.abs(dy);

    pointerRef.current.tracking = false;

    if (isSwipe) {
      if (dx < 0) handleNext();
      else handlePrev();
    }

    if (event.pointerType !== 'mouse') {
      resumeAutoplay(900);
    }
  };

  const onPointerCancel = () => {
    pointerRef.current.tracking = false;
    resumeAutoplay(600);
  };

  const active = testimonialsData[activeIndex];
  if (!active) return null;

  return (
    <section className="testimonials-section">
      <div className="testimonials-container">
        <header className="testimonials-header">
          <h2>
            SUCCESS <span className="text-blue-accent">STORIES</span>
          </h2>
          <div className="decorative-line-wrapper" aria-hidden="true">
            <span className="line-segment short" />
            <span className="line-segment long" />
            <span className="line-segment short" />
          </div>
          <p className="section-intro-text">
            Hear inspiring stories from students, job seekers, volunteers and beneficiaries whose
            lives have been transformed through AMP India Foundation&apos;s initiatives.
          </p>
        </header>

        <div
          className="testimonial-slider-window"
          onMouseEnter={pauseAutoplay}
          onMouseLeave={() => resumeAutoplay(0)}
          onPointerDown={onPointerDown}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerCancel}
        >
          <div className="testimonial-avatar-band">
            <button
              type="button"
              className="slider-arrow left-arrow is-desktop-arrow"
              onClick={() => {
                pauseAutoplay();
                handlePrev();
                resumeAutoplay(1400);
              }}
              aria-label="Previous testimonial"
            >
              <span aria-hidden="true">‹</span>
            </button>

            <div className="avatar-stage-row">
              {testimonialsData.map((item, index) => {
                const positionClass = getCardPositionClass(index);
                const loadAvatar = positionClass !== 'position-hidden';
                return (
                <button
                  type="button"
                  key={item.id}
                  className={`avatar-card-node ${positionClass}`}
                  onClick={() => {
                    pauseAutoplay();
                    const raw = ((index - activeIndex) % total + total) % total;
                    const offset = raw <= Math.floor(total / 2) ? raw : raw - total;
                    goTo(index, offset >= 0 ? 1 : -1);
                    resumeAutoplay(1400);
                  }}
                  aria-label={`Show testimonial from ${item.name}`}
                  aria-current={index === activeIndex ? 'true' : undefined}
                >
                  {loadAvatar ? (
                    <CmsMediaImage
                      cmsSrc={item.avatar}
                      fallbackSrc={localAvatarForName(item.name) || DEFAULT_AVATAR}
                      alt=""
                      width={180}
                      height={180}
                      sizes="180px"
                      loading="lazy"
                      className="testimonial-avatar"
                    />
                  ) : null}
                </button>
                );
              })}
            </div>

            <button
              type="button"
              className="slider-arrow right-arrow is-desktop-arrow"
              onClick={() => {
                pauseAutoplay();
                handleNext();
                resumeAutoplay(1400);
              }}
              aria-label="Next testimonial"
            >
              <span aria-hidden="true">›</span>
            </button>
          </div>

          <div className="testimonial-text-viewport">
            <AnimatePresence mode="wait" initial={false} custom={direction}>
              <motion.div
                key={active.id}
                className="testimonial-text-block"
                custom={direction}
                variants={{
                  enter: (dir) => ({ opacity: 0, x: 28 * dir }),
                  center: { opacity: 1, x: 0 },
                  exit: (dir) => ({ opacity: 0, x: -28 * dir }),
                }}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{ duration: 0.7, ease: EASE }}
              >
                <p className="testimonial-quote">{active.quote}</p>
                <h3 className="testimonial-author-name">{active.name}</h3>
                <p className="testimonial-author-meta">
                  {active.role} &bull;{' '}
                  <span className="meta-location">{active.location}</span>
                </p>
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="testimonial-mobile-nav">
            <button
              type="button"
              className="slider-arrow left-arrow"
              onClick={() => {
                pauseAutoplay();
                handlePrev();
                resumeAutoplay(1400);
              }}
              aria-label="Previous testimonial"
            >
              <span aria-hidden="true">‹</span>
            </button>
            <button
              type="button"
              className="slider-arrow right-arrow"
              onClick={() => {
                pauseAutoplay();
                handleNext();
                resumeAutoplay(1400);
              }}
              aria-label="Next testimonial"
            >
              <span aria-hidden="true">›</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonial;
