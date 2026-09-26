'use client';

import { motion } from 'framer-motion';

function stripTrailingPunct(raw) {
  const text = String(raw || '');
  const match = text.match(/^(.*?)([),.;!?]+)$/);
  if (!match) return { display: text, extra: '' };
  return { display: match[1], extra: match[2] };
}

function hrefFor(raw) {
  const { display } = stripTrailingPunct(raw);
  if (/^https?:\/\//i.test(display)) return display;
  if (/^www\./i.test(display)) return `https://${display}`;
  if (display.startsWith('/')) return display;
  return display;
}

function isSafeHref(href) {
  const value = String(href || '').trim();
  if (!value) return false;
  const lower = value.toLowerCase();
  if (lower.startsWith('javascript:') || lower.startsWith('data:') || lower.startsWith('vbscript:')) {
    return false;
  }
  return /^(https?:\/\/|\/)/i.test(value);
}

function renderContent(content) {
  const text = String(content || '');
  const tokenRe =
    /(\*\*[^*]+\*\*|https?:\/\/[^\s<>"'`]+|www\.[^\s<>"'`]+|\/(?:support-us|volunteer|projects\/[a-z0-9/-]+|events|contact|about)(?:\/[^\s<>"'`]*)?)/gi;
  const parts = text.split(tokenRe);
  return parts.map((part, index) => {
    if (!part) return null;
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (
      /^https?:\/\//i.test(part) ||
      /^www\./i.test(part) ||
      /^\/(?:support-us|volunteer|projects\/|events|contact|about)/i.test(part)
    ) {
      const { display, extra } = stripTrailingPunct(part);
      const href = hrefFor(part);
      if (!isSafeHref(href)) {
        return <span key={index}>{part}</span>;
      }
      return (
        <span key={index}>
          <a
            href={href}
            className="aif-chat-link"
            target={href.startsWith('/') ? undefined : '_blank'}
            rel={href.startsWith('/') ? undefined : 'noopener noreferrer'}
          >
            {display}
          </a>
          {extra}
        </span>
      );
    }
    return <span key={index}>{part}</span>;
  });
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      className={`aif-chat-message ${isUser ? 'aif-chat-message--user' : 'aif-chat-message--assistant'}`}
      initial={{ opacity: 0, y: 14, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="aif-chat-bubble" role="article">
        <p className="aif-chat-bubble-text">{renderContent(message.content)}</p>
      </div>
      <time className="aif-chat-timestamp">{message.timestamp}</time>
    </motion.div>
  );
}
