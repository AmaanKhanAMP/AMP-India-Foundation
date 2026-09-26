'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FiSend } from 'react-icons/fi';

export default function ChatInput({ value, onChange, onSend, disabled, autoFocus }) {
  const textareaRef = useRef(null);
  const canSend = Boolean(value.trim()) && !disabled;

  useEffect(() => {
    if (autoFocus && textareaRef.current) textareaRef.current.focus();
  }, [autoFocus]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 96)}px`;
  }, [value]);

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (canSend) onSend();
    }
  };

  return (
    <form
      className="aif-chat-input-area"
      onSubmit={(event) => {
        event.preventDefault();
        if (canSend) onSend();
      }}
    >
      <label className="aif-chat-sr-only" htmlFor="aif-chat-input">
        Message
      </label>
      <div className={`aif-chat-input-shell ${disabled ? 'is-disabled' : ''}`}>
        <textarea
          id="aif-chat-input"
          ref={textareaRef}
          className="aif-chat-input"
          rows={1}
          placeholder="Ask me anything..."
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          aria-label="Ask me anything"
        />
        <motion.button
          type="submit"
          className="aif-chat-send"
          disabled={!canSend}
          aria-label="Send message"
          whileHover={canSend ? { scale: 1.08, rotate: 12 } : undefined}
          whileTap={canSend ? { scale: 0.9 } : undefined}
        >
          {disabled ? <span className="aif-chat-send-spinner" aria-hidden="true" /> : <FiSend size={17} />}
        </motion.button>
      </div>
    </form>
  );
}
