'use client';

import { motion } from 'framer-motion';

export default function TypingIndicator() {
  return (
    <motion.div
      className="aif-chat-typing"
      role="status"
      aria-live="polite"
      aria-label="Assistant is typing"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
    >
      <div className="aif-chat-typing-bubble">
        <span className="aif-chat-typing-dot" />
        <span className="aif-chat-typing-dot" />
        <span className="aif-chat-typing-dot" />
      </div>
    </motion.div>
  );
}
