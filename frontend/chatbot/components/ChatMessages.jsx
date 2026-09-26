'use client';

import { useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import ChatRobot from './ChatRobot';
import { WELCOME_CAPABILITIES } from '../utils/constants';

export default function ChatMessages({ messages, isTyping, welcomeText, showWelcome }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isTyping, showWelcome]);

  return (
    <div
      className="aif-chat-messages"
      role="log"
      aria-live="polite"
      aria-relevant="additions"
    >
      <div className="aif-chat-messages-bg" aria-hidden="true">
        <span className="aif-chat-blob aif-chat-blob--1" />
        <span className="aif-chat-blob aif-chat-blob--2" />
      </div>

      <AnimatePresence mode="popLayout">
        {showWelcome ? (
          <motion.div
            key="welcome"
            className="aif-chat-welcome"
            initial={{ opacity: 0, y: 16, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -24, scale: 0.96 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="aif-chat-welcome-grid">
              <div className="aif-chat-welcome-copy">
                <p className="aif-chat-welcome-emoji">👋</p>
                <h3 className="aif-chat-welcome-hello">Hello!</h3>
                <p className="aif-chat-welcome-name">I&apos;m AMP AI Assistant</p>
                <p className="aif-chat-welcome-ask">Need help today?</p>
                <p className="aif-chat-welcome-lead">{welcomeText}</p>
                <p className="aif-chat-welcome-help">Ask me about:</p>
                <ul className="aif-chat-welcome-list">
                  {WELCOME_CAPABILITIES.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="aif-chat-welcome-robot">
                <ChatRobot size="lg" />
              </div>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>

      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      <AnimatePresence>{isTyping ? <TypingIndicator key="typing" /> : null}</AnimatePresence>

      <div ref={endRef} />
    </div>
  );
}
