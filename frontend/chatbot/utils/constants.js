export const AIF_BLUE = '#2F5FEA';
export const AIF_BLUE_DARK = '#1E4FD8';
export const AIF_BLUE_DEEP = '#173A9B';
export const AIF_BLUE_SOFT = '#E8F0FF';
export const AIF_BLUE_MIST = '#F5F8FF';

/**
 * Site-wide chatbot widget flag.
 * Set to `true` to show the AMP AI Assistant again (no other code changes needed).
 * While `false`, the widget is not rendered and no chat API calls run from the UI.
 */
export const CHATBOT_ENABLED = false;

export const LOGO_SRC = '/assets/logo.png';

export const PHASE1_REPLY =
  'The AI backend will be connected in the next phase.';

export const TYPING_DELAY_MS = 800;

export const ANIMATION_MS = 400;

/** Page-aware welcome copy (UI only — no AI). */
export const PAGE_WELCOME = {
  '/': 'Welcome to AMP India Foundation.',
  '/home': 'Welcome to AMP India Foundation.',
  '/about': 'Learn more about AMP India Foundation.',
  '/what-we-do': 'Explore what we do at AMP India Foundation.',
  '/projects': 'Need information about our projects?',
  '/events': 'Looking for upcoming events?',
  '/volunteer': 'Want to become a volunteer?',
  '/support': 'Need help making a donation?',
  '/support-us': 'Need help making a donation?',
  '/contact': 'Looking for office details?',
  '/terms-and-conditions': 'Have questions about our Terms & Conditions?',
};

export const DEFAULT_WELCOME = 'Welcome to AMP India Foundation.';

export const WELCOME_CAPABILITIES = [
  'Scholarships',
  'Projects',
  'Events',
  'Medical Programs',
  'Donations',
  'Volunteer Opportunities',
  'Contact Information',
];

export const SUGGESTED_QUESTIONS = [
  { id: 'scholarship', label: '🎓 Scholarships', text: 'Tell me about Scholarship Programs' },
  { id: 'events', label: '📅 Events', text: 'What upcoming events do you have?' },
  { id: 'donate', label: '❤️ Donate', text: 'How can I donate to AMP India Foundation?' },
  { id: 'volunteer', label: '🤝 Volunteer', text: 'How can I become a volunteer?' },
  { id: 'medical', label: '🏥 Medical', text: 'Tell me about Medical Projects' },
  { id: 'contact', label: '📞 Contact', text: 'How can I contact AMP India Foundation?' },
];

/**
 * Resolve a pathname (including nested routes) to page-aware welcome text.
 */
export function getPageWelcome(pathname = '/') {
  if (!pathname) return DEFAULT_WELCOME;

  const exact = PAGE_WELCOME[pathname];
  if (exact) return exact;

  if (pathname.startsWith('/projects')) return PAGE_WELCOME['/projects'];
  if (pathname.startsWith('/events')) return PAGE_WELCOME['/events'];
  if (pathname.startsWith('/volunteer')) return PAGE_WELCOME['/volunteer'];
  if (pathname.startsWith('/support')) return PAGE_WELCOME['/support-us'];
  if (pathname.startsWith('/contact')) return PAGE_WELCOME['/contact'];
  if (pathname.startsWith('/about')) return PAGE_WELCOME['/about'];
  if (pathname.startsWith('/what-we-do')) return PAGE_WELCOME['/what-we-do'];
  if (pathname.startsWith('/terms')) return PAGE_WELCOME['/terms-and-conditions'];

  return DEFAULT_WELCOME;
}

export function createMessageId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export function formatTimestamp(date = new Date()) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
