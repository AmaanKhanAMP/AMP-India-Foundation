'use client';

import { motion } from 'framer-motion';
import { HiOutlineSparkles, HiPlus, HiXMark } from 'react-icons/hi2';
import { LOGO_SRC } from '../utils/constants';

export default function ChatHeader({ onClose, onNewChat }) {
  return (
    <motion.header
      className="aif-chat-header"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="aif-chat-header-wave" aria-hidden="true" />
      <div className="aif-chat-header-shimmer" aria-hidden="true" />
      <span className="aif-chat-header-particle aif-chat-header-particle--1" aria-hidden="true" />
      <span className="aif-chat-header-particle aif-chat-header-particle--2" aria-hidden="true" />
      <span className="aif-chat-header-particle aif-chat-header-particle--3" aria-hidden="true" />

      <div className="aif-chat-header-brand">
        <motion.div
          className="aif-chat-logo-wrap"
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.08, type: 'spring', stiffness: 320, damping: 20 }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={LOGO_SRC} alt="AMP India Foundation" className="aif-chat-logo" />
        </motion.div>

        <div className="aif-chat-header-text">
          <div className="aif-chat-title-row">
            <h2 className="aif-chat-title">AMP AI Assistant</h2>
            <span className="aif-chat-ai-badge">
              <HiOutlineSparkles size={10} aria-hidden="true" />
              AI
            </span>
          </div>
          <p className="aif-chat-subtitle">
            <span className="aif-chat-online-dot" aria-hidden="true" />
            Always Online
          </p>
        </div>
      </div>

      <div className="aif-chat-header-actions">
        {typeof onNewChat === 'function' ? (
          <motion.button
            type="button"
            className="aif-chat-new"
            onClick={onNewChat}
            aria-label="Start new chat"
            title="New Chat"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 420, damping: 20 }}
          >
            <HiPlus size={16} aria-hidden="true" />
            <span>New</span>
          </motion.button>
        ) : null}

        <motion.button
          type="button"
          className="aif-chat-close"
          onClick={onClose}
          aria-label="Close chat"
          whileHover={{ scale: 1.1, rotate: 90 }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 420, damping: 20 }}
        >
          <HiXMark size={18} aria-hidden="true" />
        </motion.button>
      </div>
    </motion.header>
  );
}
