"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';

import { fallbackByTitle } from '@/lib/cmsImage';
import { toCanonicalPath } from '@/lib/pageMetadata';
import CmsMediaImage from '@/components/media/CmsMediaImage';

import communityImpactBanner from '@/src/assets/hero-community-impact.png';
import educationBanner from '@/src/assets/hero-education.png';
import employmentBanner from '@/src/assets/hero-employment.png';

const assetSrc = (image) => (typeof image === 'string' ? image : image?.src);

const communityImpactImage = assetSrc(communityImpactBanner);
const educationBannerImage = assetSrc(educationBanner);
const employmentBannerImage = assetSrc(employmentBanner);

const FALLBACK_SLIDES = [
  {
    id: 1,
    image: educationBannerImage,
    titleStart: 'Empowering Lives Through',
    titleAccent: 'Education',
    subtitle:
      'Every child deserves the opportunity to learn, grow and succeed. We support underprivileged students through scholarships, mentoring, career guidance and skill development to help them build a brighter future.',
    primaryBtnText: 'Learn More',
    secondaryBtnText: 'Our Projects',
    primaryLink: '/about',
    secondaryLink: '/projects',
  },
  {
    id: 2,
    image: employmentBannerImage,
    titleStart: 'Creating Opportunities Through',
    titleAccent: 'Employment',
    subtitle:
      "A good job can transform a family's future. Through employability training, career guidance, job fairs and placement support, we help young people become job-ready and connect them with meaningful employment opportunities.",
    primaryBtnText: 'Join Us',
    secondaryBtnText: 'Our Impact',
    primaryLink: '/volunteer',
    secondaryLink: '/#impact',
  },
  {
    id: 3,
    image: communityImpactImage,
    titleStart: 'Building Stronger',
    titleAccent: 'Communities',
    subtitle:
      'We empower individuals and families through skill development, entrepreneurship support, healthcare initiatives and community development programs, enabling them to become self-reliant and lead dignified lives.',
    primaryBtnText: 'Support Us',
    secondaryBtnText: 'Our Mission',
    primaryLink: '/support-us',
    secondaryLink: '/about',
  },
];

const HeroSlide = ({ slide, isActive, shouldLoadImage, priority, onImageLoad }) => {
  const fallbackSrc = fallbackByTitle(FALLBACK_SLIDES, slide.titleStart);
  const photoSrc = slide.image || fallbackSrc;
  const isEducationSlide =
    (typeof photoSrc === 'string' && photoSrc.includes('hero-education')) ||
    photoSrc === educationBannerImage;
  const isEmploymentSlide =
    (typeof photoSrc === 'string' && photoSrc.includes('hero-employment')) ||
    photoSrc === employmentBannerImage;

  return (
    <div
      className={`carousel-slide ${isActive ? 'active' : ''} ${isEducationSlide ? 'carousel-slide-education' : ''} ${isEmploymentSlide ? 'carousel-slide-employment' : ''}`}
    >
      {shouldLoadImage ? (
        <div className="carousel-slide-media" aria-hidden="true">
          <CmsMediaImage
            cmsSrc={slide.image}
            fallbackSrc={fallbackSrc}
            alt=""
            fill
            sizes="100vw"
            quality={80}
            priority={priority}
            onLoad={priority ? onImageLoad : undefined}
            className="carousel-slide-photo"
          />
        </div>
      ) : null}
      <div className="carousel-slide-overlay" aria-hidden="true" />
      <div className="carousel-content-container">
        <div className="carousel-text-block">
          <h1 className="carousel-title">
            {slide.titleStart?.endsWith(' Through') ? (
              <>
                {slide.titleStart.slice(0, -8)}
                <br aria-hidden="true" />
                {' Through '}
                <span className="title-blue-accent">{slide.titleAccent}</span>
              </>
            ) : (
              <>
                {slide.titleStart}{' '}
                <span className="title-blue-accent">{slide.titleAccent}</span>
              </>
            )}
          </h1>
          <p className="carousel-subtitle">{slide.subtitle}</p>

          <div className="carousel-btn-group">
            <Link href={toCanonicalPath(slide.primaryLink)} className="btn-primary-blue">{slide.primaryBtnText}</Link>
            <Link href={toCanonicalPath(slide.secondaryLink)} className="btn-outline-white">{slide.secondaryBtnText}</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

const HeroCarousel = ({ slides }) => {
  // Empty published list → hide hero only. null/undefined → FALLBACK only when
  // there is no CMS snapshot yet (snapshot restore avoids FALLBACK→CMS flash).
  const slidesData = Array.isArray(slides) ? slides : FALLBACK_SLIDES;
  const [currentSlide, setCurrentSlide] = useState(0);
  const [animating, setAnimating] = useState(false);
  const [nextSlideUnlocked, setNextSlideUnlocked] = useState(false);
  // Preserve slide index across CMS refresh when length is unchanged.
  const slideCount = slidesData.length;

  useEffect(() => {
    if (currentSlide >= slideCount) setCurrentSlide(0);
  }, [slideCount, currentSlide]);

  useEffect(() => {
    const id = window.setTimeout(() => setNextSlideUnlocked(true), 2500);
    return () => window.clearTimeout(id);
  }, []);

  const triggerAnimation = (callback) => {
    if (animating) return;
    setAnimating(true);
    callback();
    setTimeout(() => setAnimating(false), 800);
  };

  const handlePrev = () => {
    triggerAnimation(() => {
      setCurrentSlide((prev) => (prev === 0 ? slideCount - 1 : prev - 1));
    });
  };

  const handleNext = () => {
    triggerAnimation(() => {
      setCurrentSlide((prev) => (prev === slideCount - 1 ? 0 : prev + 1));
    });
  };

  useEffect(() => {
    if (!slideCount) return;
    const timer = setInterval(() => {
      handleNext();
    }, 6000);
    return () => clearInterval(timer);
  }, [currentSlide, animating, slideCount]);

  if (!slideCount) return null;

  return (
    <div className="hero-carousel-wrapper">
      {slidesData.map((slide, index) => {
        const isActive = index === currentSlide;
        const isNext = index === (currentSlide + 1) % slideCount;
        return (
          <HeroSlide
            key={slide.id}
            slide={slide}
            isActive={isActive}
            shouldLoadImage={isActive || (isNext && nextSlideUnlocked)}
            priority={index === 0 && isActive}
            onImageLoad={() => setNextSlideUnlocked(true)}
          />
        );
      })}

      <button className="nav-arrow arrow-left" onClick={handlePrev} aria-label="Previous slide">
        <span>‹</span>
      </button>
      <button className="nav-arrow arrow-right" onClick={handleNext} aria-label="Next slide">
        <span>›</span>
      </button>

      <div className="carousel-indicators">
        {slidesData.map((_, index) => (
          <span
            key={index}
            className={`indicator-dot ${index === currentSlide ? 'active' : ''}`}
            onClick={() => triggerAnimation(() => setCurrentSlide(index))}
          />
        ))}
      </div>
    </div>
  );
};

export default HeroCarousel;
