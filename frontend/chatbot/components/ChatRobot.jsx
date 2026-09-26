'use client';

import { motion } from 'framer-motion';

/**
 * Friendly AMP AI robot mascot (pure SVG — no external assets).
 */
export default function ChatRobot({ size = 'md', className = '' }) {
  const dim = size === 'lg' ? 148 : size === 'sm' ? 56 : 120;

  return (
    <div
      className={`aif-chat-robot ${className}`}
      style={{ width: dim, height: dim }}
      aria-hidden="true"
    >
      <span className="aif-chat-robot-glow" />
      <span className="aif-chat-robot-orbit" />
      <span className="aif-chat-robot-orbit aif-chat-robot-orbit--2" />
      <span className="aif-chat-robot-spark aif-chat-robot-spark--1" />
      <span className="aif-chat-robot-spark aif-chat-robot-spark--2" />
      <span className="aif-chat-robot-spark aif-chat-robot-spark--3" />

      <motion.div
        className="aif-chat-robot-body"
        animate={{ y: [0, -7, 0] }}
        transition={{ duration: 3.2, repeat: Infinity, ease: 'easeInOut' }}
      >
        <svg viewBox="0 0 160 160" width="100%" height="100%" fill="none">
          {/* Antenna */}
          <motion.g
            animate={{ rotate: [-6, 6, -6] }}
            transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
            style={{ transformOrigin: '80px 22px' }}
          >
            <line x1="80" y1="28" x2="80" y2="14" stroke="#2563EB" strokeWidth="3" strokeLinecap="round" />
            <circle cx="80" cy="10" r="5" fill="#60A5FA" />
            <circle cx="80" cy="10" r="2.5" fill="#ffffff" />
          </motion.g>

          {/* Head */}
          <rect x="42" y="30" width="76" height="58" rx="22" fill="#ffffff" stroke="#2563EB" strokeWidth="3" />
          <rect x="50" y="40" width="60" height="34" rx="14" fill="#EFF6FF" />

          {/* Eyes (blink) */}
          <motion.g
            animate={{ scaleY: [1, 1, 0.12, 1, 1] }}
            transition={{ duration: 4, times: [0, 0.42, 0.46, 0.5, 1], repeat: Infinity }}
            style={{ transformOrigin: '80px 56px' }}
          >
            <circle cx="64" cy="56" r="7" fill="#0B5ED7" />
            <circle cx="96" cy="56" r="7" fill="#0B5ED7" />
            <circle cx="66" cy="54" r="2.2" fill="#ffffff" />
            <circle cx="98" cy="54" r="2.2" fill="#ffffff" />
          </motion.g>

          {/* Smile */}
          <path d="M68 70c4 6 20 6 24 0" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round" />

          {/* Body */}
          <rect x="50" y="92" width="60" height="42" rx="16" fill="#ffffff" stroke="#2563EB" strokeWidth="3" />
          <rect x="62" y="102" width="36" height="18" rx="8" fill="#DBEAFE" />
          <circle cx="80" cy="111" r="4" fill="#0B5ED7" />

          {/* Left arm */}
          <rect x="28" y="98" width="18" height="28" rx="9" fill="#ffffff" stroke="#2563EB" strokeWidth="2.5" />

          {/* Right arm (wave) */}
          <motion.g
            animate={{ rotate: [0, -28, 8, -22, 0] }}
            transition={{ duration: 2.6, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
            style={{ transformOrigin: '122px 104px' }}
          >
            <rect x="114" y="90" width="18" height="28" rx="9" fill="#ffffff" stroke="#2563EB" strokeWidth="2.5" />
            <circle cx="123" cy="88" r="7" fill="#EFF6FF" stroke="#2563EB" strokeWidth="2" />
          </motion.g>

          {/* Feet */}
          <rect x="56" y="136" width="18" height="12" rx="6" fill="#DBEAFE" stroke="#2563EB" strokeWidth="2" />
          <rect x="86" y="136" width="18" height="12" rx="6" fill="#DBEAFE" stroke="#2563EB" strokeWidth="2" />
        </svg>
      </motion.div>
    </div>
  );
}
