"use client";

import { useLayoutEffect, useRef } from 'react';
import { motion, useAnimationControls, useInView } from 'framer-motion';

export const easeOut = 'easeOut';

export const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: easeOut }
  }
};

export const heroLeft = {
  hidden: { opacity: 0, x: -60 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.7,
      ease: easeOut,
      staggerChildren: 0.12,
      delayChildren: 0.04
    }
  }
};

export const heroBadge = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: easeOut }
  }
};

export const heroHeading = {
  hidden: { opacity: 0, x: -50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.7, ease: easeOut }
  }
};

export const heroParagraph = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.65, ease: easeOut }
  }
};

export const heroButton = {
  hidden: { opacity: 0, y: 28 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.65, ease: easeOut }
  }
};

export const heroRight = {
  hidden: { opacity: 0, x: 60 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.8, ease: easeOut, delay: 0.15 }
  }
};

export const timelineIconVariants = {
  hidden: { opacity: 0, scale: 0.6 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { type: 'spring', stiffness: 420, damping: 22 }
  }
};

export const timelineLineVariants = {
  hidden: { scaleY: 0, opacity: 0 },
  visible: {
    scaleY: 1,
    opacity: 1,
    transition: { duration: 0.65, ease: easeOut }
  }
};

/**
 * Scroll reveal — SSR-safe (initial={false}).
 * After hydrate, plays hidden → visible once when in view.
 */
export default function Reveal({
  children,
  className,
  delay = 0,
  amount = 0.2,
  as = 'div',
  variants: variantsProp,
  style,
  ...rest
}) {
  const ref = useRef(null);
  const controls = useAnimationControls();
  const played = useRef(false);
  const inView = useInView(ref, { once: true, amount });
  const Tag = motion[as] || motion.div;

  const base = variantsProp || fadeUp;
  const variants = delay
    ? {
        hidden: base.hidden,
        visible: {
          ...base.visible,
          transition: {
            ...(base.visible?.transition || {}),
            delay
          }
        }
      }
    : base;

  useLayoutEffect(() => {
    if (played.current) return;

    if (inView) {
      played.current = true;
      controls.set('hidden');
      controls.start('visible');
      return;
    }

    controls.set('hidden');
  }, [inView, controls]);

  return (
    <Tag
      ref={ref}
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      initial={false}
      animate={controls}
      variants={variants}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export function RevealGroup({
  children,
  className,
  stagger = 0.12,
  delayChildren = 0.04,
  amount = 0.2,
  as = 'div',
  style,
  ...rest
}) {
  const ref = useRef(null);
  const controls = useAnimationControls();
  const played = useRef(false);
  const inView = useInView(ref, { once: true, amount });
  const Tag = motion[as] || motion.div;

  useLayoutEffect(() => {
    if (played.current) return;

    if (inView) {
      played.current = true;
      controls.set('hidden');
      controls.start('visible');
      return;
    }

    controls.set('hidden');
  }, [inView, controls]);

  return (
    <Tag
      ref={ref}
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      initial={false}
      animate={controls}
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: stagger,
            delayChildren
          }
        }
      }}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export function RevealItem({
  children,
  className,
  as = 'div',
  y = 30,
  x = 0,
  duration = 0.6,
  style,
  variants,
  ...rest
}) {
  const Tag = motion[as] || motion.div;

  return (
    <Tag
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      variants={
        variants || {
          hidden: { opacity: 0, x, y },
          visible: {
            opacity: 1,
            x: 0,
            y: 0,
            transition: { duration, ease: easeOut }
          }
        }
      }
      {...rest}
    >
      {children}
    </Tag>
  );
}

/** Page-load hero motion — plays once after mount. */
export function HeroMotion({
  children,
  className,
  variants,
  as = 'div',
  style,
  ...rest
}) {
  const controls = useAnimationControls();
  const Tag = motion[as] || motion.div;

  useLayoutEffect(() => {
    controls.set('hidden');
    controls.start('visible');
  }, [controls]);

  return (
    <Tag
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      initial={false}
      animate={controls}
      variants={variants}
      {...rest}
    >
      {children}
    </Tag>
  );
}
