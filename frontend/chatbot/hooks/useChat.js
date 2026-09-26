'use client';

import { useCallback, useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import {
  clearChatSessionId,
  getChatSessionId,
  persistChatSessionId,
  sendChatMessage,
} from '../services/chatApi';
import {
  createMessageId,
  formatTimestamp,
  getPageWelcome,
} from '../utils/constants';

const MESSAGES_STORAGE_KEY = 'aif_chat_messages';

function loadStoredMessages() {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(MESSAGES_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistMessages(messages) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(messages));
  } catch {
    // ignore quota / private mode
  }
}

/**
 * Chat state for the AMP AI Assistant.
 * Persists messages + session in localStorage. Closing does NOT clear history.
 * Only "New Chat" clears history.
 */
export function useChat() {
  const pathname = usePathname() || '/';
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [hydrated, setHydrated] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [currentPage, setCurrentPage] = useState(pathname);

  useEffect(() => {
    setCurrentPage(pathname);
  }, [pathname]);

  useEffect(() => {
    setMessages(loadStoredMessages());
    getChatSessionId();
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    persistMessages(messages);
  }, [messages, hydrated]);

  const open = useCallback(() => setIsOpen(true), []);

  const close = useCallback(() => {
    // Keep messages + session — only hide the panel
    setIsOpen(false);
    setInputValue('');
    setIsTyping(false);
  }, []);

  const toggle = useCallback(() => {
    setIsOpen((prev) => {
      if (prev) {
        setInputValue('');
        setIsTyping(false);
        return false;
      }
      return true;
    });
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setInputValue('');
    setIsTyping(false);
    try {
      window.localStorage.removeItem(MESSAGES_STORAGE_KEY);
    } catch {
      // ignore
    }
    clearChatSessionId();
    const freshId = getChatSessionId();
    persistChatSessionId(freshId);
  }, []);

  const welcomeText = getPageWelcome(currentPage);

  const sendMessage = useCallback(
    async (rawText) => {
      const text = (rawText ?? inputValue).trim();
      if (!text || isTyping) return;

      const userMessage = {
        id: createMessageId(),
        role: 'user',
        content: text,
        timestamp: formatTimestamp(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInputValue('');
      setIsTyping(true);

      const assistantId = createMessageId();
      let startedStream = false;

      try {
        await sendChatMessage(text, {
          page: currentPage,
          onToken: (_token, fullText) => {
            if (!startedStream) {
              startedStream = true;
              setIsTyping(false);
              setMessages((prev) => [
                ...prev,
                {
                  id: assistantId,
                  role: 'assistant',
                  content: fullText,
                  timestamp: formatTimestamp(),
                },
              ]);
              return;
            }
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId ? { ...msg, content: fullText } : msg
              )
            );
          },
        }).then(({ reply }) => {
          if (!startedStream) {
            setMessages((prev) => [
              ...prev,
              {
                id: assistantId,
                role: 'assistant',
                content: reply,
                timestamp: formatTimestamp(),
              },
            ]);
          } else {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId ? { ...msg, content: reply } : msg
              )
            );
          }
        });
      } catch (error) {
        const errorMessage = {
          id: createMessageId(),
          role: 'assistant',
          content:
            error?.message ||
            "I couldn't find verified information about that in the current AMP India Foundation knowledge base.",
          timestamp: formatTimestamp(),
        };
        setMessages((prev) => {
          const withoutPartial = prev.filter((msg) => msg.id !== assistantId);
          return [...withoutPartial, errorMessage];
        });
      } finally {
        setIsTyping(false);
      }
    },
    [currentPage, inputValue, isTyping]
  );

  const applySuggestion = useCallback((text) => {
    setInputValue(text);
  }, []);

  return {
    isOpen,
    messages,
    isTyping,
    currentPage,
    welcomeText,
    inputValue,
    setInputValue,
    open,
    close,
    toggle,
    startNewChat,
    sendMessage,
    applySuggestion,
  };
}

export default useChat;
