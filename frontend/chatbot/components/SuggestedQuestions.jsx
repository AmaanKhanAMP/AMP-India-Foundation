'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

const QUICK_ACTIONS = [
  { id: 'scholarship', icon: '🎓', label: 'Scholarships', text: 'Tell me about Scholarship Programs' },
  { id: 'events', icon: '📅', label: 'Events', text: 'What upcoming events do you have?' },
  { id: 'donate', icon: '❤️', label: 'Donate', text: 'How can I donate to AMP India Foundation?' },
  { id: 'volunteer', icon: '🤝', label: 'Volunteer', text: 'How can I become a volunteer?' },
  { id: 'medical', icon: '🏥', label: 'Medical', text: 'Tell me about Medical Projects' },
  { id: 'contact', icon: '📞', label: 'Contact', text: 'How can I contact AMP India Foundation?' },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 10, scale: 0.94 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 380, damping: 24 },
  },
};

export default function SuggestedQuestions({ onSelect, hidden = false, compact = false }) {
  const [expanded, setExpanded] = useState(false);

  if (hidden) return null;

  const actions =
    compact && !expanded ? QUICK_ACTIONS.slice(0, 3) : QUICK_ACTIONS;

  return (
    <motion.div
      className={`aif-chat-suggestions ${
        compact
          ? `aif-chat-suggestions--compact${expanded ? ' is-expanded' : ''}`
          : 'aif-chat-suggestions--welcome'
      }`}
      aria-label="Quick actions"
      variants={container}
      initial="hidden"
      animate="show"
    >
      {actions.map((action) => (
        <motion.button
          key={action.id}
          type="button"
          className="aif-chat-chip"
          onClick={() => onSelect(action.text)}
          variants={item}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
        >
          <span className="aif-chat-chip-icon" aria-hidden="true">
            {action.icon}
          </span>
          <span className="aif-chat-chip-label">{action.label}</span>
        </motion.button>
      ))}

      {compact && !expanded ? (
        <motion.button
          type="button"
          className="aif-chat-chip aif-chat-chip--more"
          onClick={() => setExpanded(true)}
          variants={item}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
        >
          + More
        </motion.button>
      ) : null}

      {compact && expanded ? (
        <motion.button
          type="button"
          className="aif-chat-chip aif-chat-chip--more"
          onClick={() => setExpanded(false)}
          variants={item}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
        >
          Less
        </motion.button>
      ) : null}
    </motion.div>
  );
}
