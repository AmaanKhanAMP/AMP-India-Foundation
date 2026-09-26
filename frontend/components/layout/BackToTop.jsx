"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { HiChevronUp } from 'react-icons/hi2';

const SHOW_AFTER_PX = 400;
/** Visual gap between Back to Top and chatbot FAB (when chatbot is enabled) */
const GAP_FROM_FAB_PX = 26;
const FALLBACK_FAB_SIZE = 68;
const FALLBACK_RIGHT_PX = 24;
/** Corner inset when the chatbot FAB is not in the DOM */
const FALLBACK_BOTTOM_PX = 24;

/**
 * Global Back to Top control.
 * Shares the chatbot wrap's `right` inset so both FAB centers stack perfectly.
 */
export default function BackToTop() {
  const [visible, setVisible] = useState(false);
  const buttonRef = useRef(null);
  const rafScrollRef = useRef(0);
  const rafPosRef = useRef(0);

  const updateVisibility = useCallback(() => {
    const y = window.scrollY || document.documentElement.scrollTop || 0;
    setVisible(y > SHOW_AFTER_PX);
  }, []);

  const updatePosition = useCallback(() => {
    const button = buttonRef.current;
    if (!button) return;

    const fab = document.querySelector('.aif-chat-fab');
    const wrap = document.querySelector('.aif-chat-fab-wrap');

    if (!fab) {
      button.style.width = `${FALLBACK_FAB_SIZE}px`;
      button.style.height = `${FALLBACK_FAB_SIZE}px`;
      button.style.right = `${FALLBACK_RIGHT_PX}px`;
      button.style.bottom = `${FALLBACK_BOTTOM_PX}px`;
      return;
    }

    const fabRect = fab.getBoundingClientRect();
    const size = Math.round(fabRect.width) || FALLBACK_FAB_SIZE;

    let rightPx = FALLBACK_RIGHT_PX;
    if (wrap) {
      const computedRight = window.getComputedStyle(wrap).right;
      const parsed = Number.parseFloat(computedRight);
      if (Number.isFinite(parsed)) {
        rightPx = parsed;
      } else {
        rightPx = Math.max(0, window.innerWidth - wrap.getBoundingClientRect().right);
      }
    } else {
      rightPx = Math.max(0, window.innerWidth - fabRect.right);
    }

    const clearance = Math.max(0, window.innerHeight - fabRect.top) + GAP_FROM_FAB_PX;

    button.style.width = `${size}px`;
    button.style.height = `${size}px`;
    button.style.right = `${Math.round(rightPx)}px`;
    button.style.bottom = `${Math.round(clearance)}px`;
  }, []);

  useEffect(() => {
    const onScroll = () => {
      if (rafScrollRef.current) return;
      rafScrollRef.current = window.requestAnimationFrame(() => {
        rafScrollRef.current = 0;
        updateVisibility();
      });
    };

    const schedulePosition = () => {
      if (rafPosRef.current) return;
      rafPosRef.current = window.requestAnimationFrame(() => {
        rafPosRef.current = 0;
        updatePosition();
      });
    };

    updateVisibility();
    updatePosition();

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', schedulePosition, { passive: true });
    window.addEventListener('orientationchange', schedulePosition, { passive: true });

    let resizeObserver;
    const fab = document.querySelector('.aif-chat-fab');
    const wrap = document.querySelector('.aif-chat-fab-wrap');
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(schedulePosition);
      if (fab) resizeObserver.observe(fab);
      if (wrap) resizeObserver.observe(wrap);
    }

    const bootTimers = [80, 300, 800, 1600].map((ms) =>
      window.setTimeout(schedulePosition, ms)
    );

    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', schedulePosition);
      window.removeEventListener('orientationchange', schedulePosition);
      if (rafScrollRef.current) window.cancelAnimationFrame(rafScrollRef.current);
      if (rafPosRef.current) window.cancelAnimationFrame(rafPosRef.current);
      resizeObserver?.disconnect();
      bootTimers.forEach((id) => window.clearTimeout(id));
    };
  }, [updatePosition, updateVisibility]);

  const handleClick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <button
      ref={buttonRef}
      type="button"
      className={`back-to-top${visible ? ' is-visible' : ''}`}
      aria-label="Back to Top"
      title="Back to Top"
      onClick={handleClick}
    >
      <HiChevronUp className="back-to-top-icon" size={28} aria-hidden="true" />
    </button>
  );
}
