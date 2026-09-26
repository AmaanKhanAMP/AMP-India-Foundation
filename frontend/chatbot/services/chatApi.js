/**
 * Phase 3 chatbot API client — FastAPI + OpenAI RAG.
 *
 * Prefer streaming (SSE) when available; fall back to JSON POST.
 * Contract kept compatible with useChat: returns { reply, sessionId, ... }.
 *
 * Env:
 *   NEXT_PUBLIC_CHAT_API_URL  → FastAPI chatbot base (default http://localhost:8000)
 *   NEXT_PUBLIC_API_URL       → Flask API fallback (via shared lib/api)
 */

import { API_URL } from '@/lib/api';

const CHAT_API_BASE = (
  process.env.NEXT_PUBLIC_CHAT_API_URL ||
  API_URL ||
  'http://localhost:8000'
).replace(/\/$/, '');

const SESSION_STORAGE_KEY = 'aif_chat_session_id';

const CONNECTION_ERROR =
  "I couldn't find verified information about that in the current AMP India Foundation knowledge base. Please try again in a moment.";

/**
 * Clear stored chat session id (used by New Chat).
 */
export function clearChatSessionId() {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
  } catch {
    // ignore
  }
}

/**
 * @returns {string}
 */
export function getChatSessionId() {
  if (typeof window === 'undefined') {
    return `srv_${Date.now()}`;
  }

  try {
    const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (existing && existing.trim()) return existing.trim();

    const id =
      typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
        ? crypto.randomUUID()
        : `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

    window.localStorage.setItem(SESSION_STORAGE_KEY, id);
    return id;
  } catch {
    return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  }
}

/**
 * @param {string} [sessionId]
 */
export function persistChatSessionId(sessionId) {
  if (typeof window === 'undefined' || !sessionId) return;
  try {
    window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  } catch {
    // ignore
  }
}

/**
 * Send a message via SSE streaming when possible.
 *
 * @param {string} message
 * @param {{
 *   page?: string,
 *   sessionId?: string,
 *   onToken?: (token: string, fullText: string) => void,
 *   preferStream?: boolean,
 * }} [options]
 * @returns {Promise<{ reply: string, intent?: string, confidence?: number, sessionId?: string, success?: boolean }>}
 */
export async function sendChatMessage(message, options = {}) {
  const sessionId = options.sessionId || getChatSessionId();
  const preferStream = options.preferStream !== false;

  if (preferStream) {
    try {
      return await sendChatMessageStream(message, {
        ...options,
        sessionId,
      });
    } catch {
      // Fall through to non-streaming JSON
    }
  }

  return sendChatMessageJson(message, { ...options, sessionId });
}

/**
 * Non-streaming POST /api/chat
 */
export async function sendChatMessageJson(message, options = {}) {
  const sessionId = options.sessionId || getChatSessionId();

  let response;
  try {
    response = await fetch(`${CHAT_API_BASE}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        page: options.page || undefined,
      }),
    });
  } catch {
    const err = new Error(CONNECTION_ERROR);
    err.code = 'NETWORK';
    throw err;
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const apiMessage =
      (data && (data.response || data.message || data.reply)) || CONNECTION_ERROR;
    const err = new Error(apiMessage);
    err.code = 'HTTP';
    err.status = response.status;
    throw err;
  }

  const reply =
    (data && (data.response || data.reply)) ||
    "I couldn't find that information yet. Please contact AMP India Foundation or ask another question.";

  if (data?.session_id) {
    persistChatSessionId(data.session_id);
  }

  return {
    reply,
    intent: data?.intent,
    confidence: data?.confidence,
    sessionId: data?.session_id || sessionId,
    success: data?.success !== false,
  };
}

/**
 * Streaming POST /api/chat/stream (SSE)
 */
export async function sendChatMessageStream(message, options = {}) {
  const sessionId = options.sessionId || getChatSessionId();
  const onToken = typeof options.onToken === 'function' ? options.onToken : null;

  let response;
  try {
    response = await fetch(`${CHAT_API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        page: options.page || undefined,
      }),
    });
  } catch {
    const err = new Error(CONNECTION_ERROR);
    err.code = 'NETWORK';
    throw err;
  }

  if (!response.ok || !response.body) {
    throw new Error(CONNECTION_ERROR);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let fullText = '';
  let resolvedSession = sessionId;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split('\n\n');
    buffer = parts.pop() || '';

    for (const block of parts) {
      const lines = block.split('\n');
      let event = 'message';
      let dataLine = '';
      for (const line of lines) {
        if (line.startsWith('event:')) event = line.slice(6).trim();
        if (line.startsWith('data:')) dataLine += line.slice(5).trim();
      }
      if (!dataLine) continue;

      let payload = {};
      try {
        payload = JSON.parse(dataLine);
      } catch {
        continue;
      }

      if (event === 'meta' && payload.session_id) {
        resolvedSession = payload.session_id;
        persistChatSessionId(resolvedSession);
      }

      if (event === 'token' && typeof payload.token === 'string') {
        fullText += payload.token;
        if (onToken) onToken(payload.token, fullText);
      }
    }
  }

  if (!fullText.trim()) {
    throw new Error(CONNECTION_ERROR);
  }

  persistChatSessionId(resolvedSession);

  return {
    reply: fullText,
    sessionId: resolvedSession,
    success: true,
  };
}

/**
 * Optional quick-actions helper (unchanged UI chips).
 */
export async function fetchQuickActions() {
  return {
    primary: [],
    more: [],
    all: [],
  };
}
