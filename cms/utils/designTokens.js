/**
 * Shared CMS design tokens.
 * Prefer CSS variables in globals.css for styling; use these in JS when needed.
 * All UI components under components/ui and components/common consume this system.
 */
export const colors = {
  primary: "#2563EB",
  primaryDark: "#1E3A8A",
  primarySoft: "#EFF6FF",
  background: "#F8FAFC",
  card: "#FFFFFF",
  foreground: "#111827",
  muted: "#64748B",
  border: "#E2E8F0",
  success: "#22C55E",
  warning: "#F59E0B",
  danger: "#EF4444",
};

export const radii = {
  sm: 12,
  md: 14,
  lg: 20,
  full: 9999,
};

export const shadows = {
  sm: "var(--shadow-sm)",
  md: "var(--shadow-md)",
  lg: "var(--shadow-lg)",
  glow: "var(--shadow-glow)",
};

export const spacing = {
  pageX: "1.5rem",
  pageY: "2rem",
  section: "2rem",
  card: "1.25rem",
};

/** Map of reusable building blocks for new CMS modules */
export const designSystemComponents = {
  layout: ["AdminLayout", "PageHeader", "Breadcrumbs", "Sidebar", "Topbar"],
  ui: ["Button", "Input", "Select", "Textarea", "SearchInput", "StatusBadge", "Modal", "ImageUpload"],
  common: [
    "BannerCard",
    "ContentCard",
    "StatCard",
    "DataTable",
    "FormShell",
    "EmptyState",
    "LoadingSkeleton",
    "Surface",
  ],
  content: ["ContentListPage", "ContentFormPage"],
};
