'use client';

import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { HiXMark } from 'react-icons/hi2';
import ChatWindow from './ChatWindow';
import ChatRobot from './ChatRobot';
import { useChat } from '../hooks/useChat';
import '../styles/chatbot.css';

function canHoverFine() {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(hover: hover) and (pointer: fine)').matches;
}

export default function ChatWidget() {
  const {
    isOpen,
    messages,
    isTyping,
    welcomeText,
    inputValue,
    setInputValue,
    close,
    toggle,
    startNewChat,
    sendMessage,
  } = useChat();

  const fabRef = useRef(null);
  const hintHideTimer = useRef(null);
  const [showHint, setShowHint] = useState(false);
  const unread = !isOpen && messages.length > 0 ? 1 : 0;

  useEffect(() => {
    if (!isOpen) return undefined;
    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        close();
        fabRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, close]);

  // Never keep the tip up while the chat panel is open
  useEffect(() => {
    if (isOpen) {
      setShowHint(false);
      if (hintHideTimer.current) {
        window.clearTimeout(hintHideTimer.current);
        hintHideTimer.current = null;
      }
    }
  }, [isOpen]);

  useEffect(
    () => () => {
      if (hintHideTimer.current) window.clearTimeout(hintHideTimer.current);
    },
    []
  );

  const clearHintTimer = () => {
    if (hintHideTimer.current) {
      window.clearTimeout(hintHideTimer.current);
      hintHideTimer.current = null;
    }
  };

  const handleWrapMouseEnter = () => {
    if (isOpen || !canHoverFine()) return;
    clearHintTimer();
    setShowHint(true);
  };

  const handleWrapMouseLeave = () => {
    if (!canHoverFine()) return;
    clearHintTimer();
    setShowHint(false);
  };

  /** Touch: briefly reveal tip; click still opens chat as before. */
  const handleFabPointerDown = (event) => {
    if (isOpen || event.pointerType !== 'touch') return;
    clearHintTimer();
    setShowHint(true);
    hintHideTimer.current = window.setTimeout(() => {
      setShowHint(false);
      hintHideTimer.current = null;
    }, 2200);
  };

  const handleFabClick = (event) => {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    ripple.className = 'aif-chat-fab-ripple';
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = `${size}px`;
    ripple.style.height = `${size}px`;
    ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
    button.appendChild(ripple);
    window.setTimeout(() => ripple.remove(), 500);
    toggle();
  };

  return (
    <div className="aif-chat-root">
      <ChatWindow
        isOpen={isOpen}
        messages={messages}
        isTyping={isTyping}
        welcomeText={welcomeText}
        inputValue={inputValue}
        onInputChange={setInputValue}
        onSend={() => sendMessage()}
        onClose={close}
        onNewChat={startNewChat}
        onSuggestionSelect={(text) => sendMessage(text)}
      />

      <div
        className={`aif-chat-fab-wrap${isOpen ? ' aif-chat-fab-wrap--open' : ''}`}
        onMouseEnter={handleWrapMouseEnter}
        onMouseLeave={handleWrapMouseLeave}
      >
        <div className="aif-chat-fab-anchor">
          {!isOpen ? (
            <div
              className={`aif-chat-fab-hint${showHint ? ' is-visible' : ''}`}
              role="status"
              aria-live="polite"
              aria-hidden={!showHint}
            >
              <span className="aif-chat-fab-hint-text">Hi! How can I help you?</span>
            </div>
          ) : null}

          {!isOpen ? <span className="aif-chat-fab-pulse" aria-hidden="true" /> : null}

          <motion.button
            ref={fabRef}
            type="button"
            className={`aif-chat-fab ${isOpen ? 'aif-chat-fab--open' : ''}`}
            onClick={handleFabClick}
            onPointerDown={handleFabPointerDown}
            aria-label={isOpen ? 'Close AMP AI Assistant' : 'Open AMP AI Assistant'}
            aria-expanded={isOpen}
            aria-controls="aif-chat-panel"
            whileHover={{ scale: 1.1, y: -4 }}
            whileTap={{ scale: 0.94 }}
            transition={{ type: 'spring', stiffness: 340, damping: 20 }}
          >
            {unread > 0 ? (
              <span className="aif-chat-fab-badge" aria-label="Unread messages">
                {unread}
              </span>
            ) : null}

            <AnimatePresence mode="wait" initial={false}>
              {isOpen ? (
                <motion.span
                  key="close"
                  className="aif-chat-fab-icon"
                  initial={{ opacity: 0, rotate: -90, scale: 0.6 }}
                  animate={{ opacity: 1, rotate: 0, scale: 1 }}
                  exit={{ opacity: 0, rotate: 90, scale: 0.6 }}
                  transition={{ duration: 0.18 }}
                >
                  <HiXMark size={26} />
                </motion.span>
              ) : (
                <motion.span
                  key="robot"
                  className="aif-chat-fab-icon aif-chat-fab-icon--robot"
                  initial={{ opacity: 0, scale: 0.6 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.6 }}
                  transition={{ duration: 0.18 }}
                >
                  <ChatRobot size="sm" />
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>
    </div>
  );
}
