'use client';

import { AnimatePresence, motion } from 'framer-motion';
import ChatHeader from './ChatHeader';
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';

export default function ChatWindow({
  isOpen,
  messages,
  isTyping,
  welcomeText,
  inputValue,
  onInputChange,
  onSend,
  onClose,
  onNewChat,
  onSuggestionSelect,
}) {
  const showWelcome = messages.length === 0 && !isTyping;
  const conversationStarted = messages.length > 0;

  return (
    <AnimatePresence>
      {isOpen ? (
        <motion.div
          id="aif-chat-panel"
          className="aif-chat-window"
          role="dialog"
          aria-modal="true"
          aria-label="AMP AI Assistant"
          initial={{ opacity: 0, y: 32, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.94 }}
          transition={{ type: 'spring', stiffness: 320, damping: 28 }}
        >
          <div className="aif-chat-window-aura" aria-hidden="true" />

          <ChatHeader onClose={onClose} onNewChat={onNewChat} />

          <ChatMessages
            messages={messages}
            isTyping={isTyping}
            welcomeText={welcomeText}
            showWelcome={showWelcome}
          />

          {!conversationStarted ? (
            <SuggestedQuestions onSelect={onSuggestionSelect} />
          ) : null}

          <ChatInput
            value={inputValue}
            onChange={onInputChange}
            onSend={onSend}
            disabled={isTyping}
            autoFocus={isOpen}
          />
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
