"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  CalendarDays,
  ChevronDown,
  GalleryHorizontalEnd,
  Home,
  Image as ImageIcon,
  LayoutDashboard,
  Link2,
  LogOut,
  Mail,
  Menu,
  MessageSquareQuote,
  PanelBottom,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  Sparkles,
  Star,
  Trash2,
  User,
  X,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/utils/cn";
import BrandLogo from "./BrandLogo";

const NAV = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Website Management",
    icon: Home,
    children: [
      {
        label: "Site Layout",
        children: [
          { label: "Navbar", href: "/site/navbar", icon: Menu },
          { label: "Footer", href: "/site/footer", icon: PanelBottom },
          { label: "Useful Links", href: "/site/footer/links", icon: Link2 },
          { label: "Recent Focus", href: "/site/footer/focus", icon: Sparkles },
        ],
      },
      {
        label: "Home Page",
        children: [
          { label: "Hero Banners", href: "/home/hero-banners", icon: Sparkles },
          { label: "Latest Projects", href: "/home/projects", icon: GalleryHorizontalEnd },
          { label: "Photo Gallery", href: "/home/gallery", icon: ImageIcon },
          { label: "Upcoming Events", href: "/home/events", icon: CalendarDays },
          { label: "Testimonials", href: "/home/testimonials", icon: MessageSquareQuote },
        ],
      },
      {
        label: "Events Page",
        children: [
          { label: "Featured Events", href: "/events/featured", icon: Star },
          { label: "Upcoming Events", href: "/events/upcoming", icon: CalendarDays },
          { label: "Past Events", href: "/events/gallery", icon: ImageIcon },
        ],
      },
    ],
  },
  {
    label: "Trash",
    href: "/trash",
    icon: Trash2,
  },
  {
    label: "Messages",
    icon: Mail,
    children: [{ label: "Contact Messages", href: "/messages/contact", icon: Mail }],
  },
  {
    label: "Settings",
    icon: Settings,
    children: [
      { label: "Profile", href: "/settings/profile", icon: User },
      { label: "Change Password", href: "/settings/password", icon: Settings },
    ],
  },
];

function flattenNav(items) {
  const leaves = [];
  items.forEach((item) => {
    if (item.href && !item.children) {
      leaves.push({ label: item.label, href: item.href, icon: item.icon });
      return;
    }
    (item.children || []).forEach((child) => {
      if (child.href && !child.children) {
        leaves.push({
          label: child.label,
          href: child.href,
          icon: child.icon || item.icon,
        });
        return;
      }
      (child.children || []).forEach((leaf) => {
        if (leaf.href) {
          leaves.push({
            label: leaf.label,
            href: leaf.href,
            icon: leaf.icon || child.icon || item.icon,
          });
        }
      });
    });
  });
  return leaves;
}

function isActivePath(pathname, href) {
  if (!href) return false;
  return pathname === href || pathname.startsWith(`${href}/`);
}

function NavLink({ href, active, icon: Icon, label, collapsed, onNavigate }) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      title={collapsed ? label : undefined}
      aria-label={label}
      className={cn(
        "group relative flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200",
        collapsed ? "justify-center px-2 py-2.5" : "px-3 py-2.5",
        active
          ? "cms-nav-active"
          : "text-[#64748B] hover:bg-[var(--primary-soft)] hover:text-[#2563EB]"
      )}
    >
      {!active && !collapsed ? (
        <span className="absolute left-0 top-1/2 h-0 w-[3px] -translate-y-1/2 rounded-r-full bg-[#2563EB] opacity-0 transition-all group-hover:h-4 group-hover:opacity-40" />
      ) : null}
      {active && !collapsed ? (
        <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-white/90" />
      ) : null}
      <Icon
        className={cn(
          "h-[18px] w-[18px] shrink-0 transition-colors",
          active ? "text-white" : "text-slate-400 group-hover:text-[#2563EB]"
        )}
      />
      {!collapsed ? <span className="truncate tracking-tight">{label}</span> : null}
    </Link>
  );
}

function SidebarNav({ collapsed, onNavigate }) {
  const pathname = usePathname();
  const { logout, user } = useAuth();
  const [openGroups, setOpenGroups] = useState({
    "Website Management": true,
    "Site Layout": true,
    "Home Page": true,
    "Events Page": true,
    Messages: true,
    Settings: false,
  });

  const toggleGroup = (key) => {
    setOpenGroups((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const flatActive = useMemo(() => pathname, [pathname]);
  const collapsedLinks = useMemo(() => flattenNav(NAV), []);

  if (collapsed) {
    return (
      <>
        <nav className="flex-1 overflow-y-auto px-2.5 py-4">
          <ul className="space-y-1">
            {collapsedLinks.map((item) => {
              const active = isActivePath(flatActive, item.href);
              const Icon = item.icon || LayoutDashboard;
              return (
                <li key={item.href}>
                  <NavLink
                    href={item.href}
                    active={active}
                    icon={Icon}
                    label={item.label}
                    collapsed
                    onNavigate={onNavigate}
                  />
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="border-t border-slate-200/70 p-2.5">
          <button
            type="button"
            onClick={() => logout()}
            title="Logout"
            aria-label="Logout"
            className="flex w-full items-center justify-center rounded-xl px-2 py-2.5 text-[var(--danger)] transition hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </>
    );
  }

  return (
    <>
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-1">
          {NAV.map((item) => {
            if (!item.children) {
              const active = isActivePath(flatActive, item.href);
              return (
                <li key={item.label}>
                  <NavLink
                    href={item.href}
                    active={active}
                    icon={item.icon}
                    label={item.label}
                    onNavigate={onNavigate}
                  />
                </li>
              );
            }

            return (
              <li key={item.label} className="pt-4 first:pt-0">
                <button
                  type="button"
                  onClick={() => toggleGroup(item.label)}
                  className="mb-1 flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left transition hover:bg-slate-50"
                >
                  <item.icon className="h-4 w-4 shrink-0 text-slate-400" />
                  <span className="flex-1 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-400">
                    {item.label}
                  </span>
                  <ChevronDown
                    className={cn(
                      "h-3.5 w-3.5 text-slate-400 transition-transform duration-200",
                      openGroups[item.label] ? "rotate-0" : "-rotate-90"
                    )}
                  />
                </button>

                <AnimatePresence initial={false}>
                  {openGroups[item.label] ? (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.22, ease: "easeOut" }}
                      className="overflow-hidden"
                    >
                      {item.children.map((child) => {
                        if (child.children) {
                          return (
                            <div key={child.label} className="ml-2 mt-1 border-l border-slate-200/80 pl-2">
                              <button
                                type="button"
                                onClick={() => toggleGroup(child.label)}
                                className="flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-400 hover:text-slate-600"
                              >
                                {child.label}
                                <ChevronDown
                                  className={cn(
                                    "h-3.5 w-3.5 transition-transform duration-200",
                                    openGroups[child.label] ? "rotate-0" : "-rotate-90"
                                  )}
                                />
                              </button>
                              <AnimatePresence initial={false}>
                                {openGroups[child.label] ? (
                                  <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden"
                                  >
                                    {child.children.map((leaf) => {
                                      const active = isActivePath(flatActive, leaf.href);
                                      return (
                                        <div key={leaf.href} className="mt-0.5">
                                          <NavLink
                                            href={leaf.href}
                                            active={active}
                                            icon={leaf.icon}
                                            label={leaf.label}
                                            onNavigate={onNavigate}
                                          />
                                        </div>
                                      );
                                    })}
                                  </motion.div>
                                ) : null}
                              </AnimatePresence>
                            </div>
                          );
                        }

                        const active = isActivePath(flatActive, child.href);
                        return (
                          <div key={child.href || child.label} className="mt-0.5">
                            <NavLink
                              href={child.href}
                              active={active}
                              icon={child.icon}
                              label={child.label}
                              onNavigate={onNavigate}
                            />
                          </div>
                        );
                      })}
                    </motion.div>
                  ) : null}
                </AnimatePresence>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="space-y-2 border-t border-slate-200/70 p-3">
        {user ? (
          <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-[var(--primary-soft)] px-3 py-2.5">
            <p className="truncate text-xs font-bold text-slate-800">{user.name}</p>
            <p className="truncate text-[11px] text-slate-500">{user.email}</p>
          </div>
        ) : null}
        <button
          type="button"
          onClick={() => logout()}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold text-[var(--danger)] transition hover:bg-red-50"
        >
          <LogOut className="h-4 w-4" />
          <span>Logout</span>
        </button>
      </div>
    </>
  );
}

export default function Sidebar({ collapsed, onToggle, mobileOpen, onMobileClose }) {
  const pathname = usePathname();

  useEffect(() => {
    onMobileClose?.();
  }, [pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  const header = (
    <div
      className={cn(
        "flex h-24 w-full shrink-0 items-center justify-between overflow-hidden border-b border-[#E5E7EB] bg-white",
        collapsed ? "px-3" : "px-5"
      )}
    >
      {/* Left: logo + divider + Admin CMS */}
      <div className="flex min-w-0 flex-1 items-center overflow-hidden pr-3">
        <BrandLogo collapsed={collapsed} />
      </div>

      {/* Right: collapse / close — always far right */}
      <div className="flex shrink-0 items-center gap-1">
        <button
          type="button"
          onClick={onToggle}
          className="hidden h-9 w-9 items-center justify-center rounded-[10px] text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 lg:inline-flex"
          aria-label="Toggle sidebar"
        >
          {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </button>
        <button
          type="button"
          onClick={onMobileClose}
          className="inline-flex h-9 w-9 items-center justify-center rounded-[10px] text-slate-500 hover:bg-slate-100 lg:hidden"
          aria-label="Close menu"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );

  return (
    <>
      <aside
        className={cn(
          "sticky top-0 z-30 hidden h-screen flex-col overflow-hidden border-r border-[#E5E7EB] bg-white transition-[width] duration-200 ease-out lg:flex",
          collapsed ? "w-20" : "w-[300px]"
        )}
      >
        {header}
        <SidebarNav collapsed={collapsed} />
      </aside>

      <AnimatePresence>
        {mobileOpen ? (
          <>
            <motion.button
              type="button"
              aria-label="Close sidebar"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-[2px] lg:hidden"
              onClick={onMobileClose}
            />
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", stiffness: 320, damping: 32 }}
              className="fixed inset-y-0 left-0 z-50 flex w-[300px] flex-col overflow-hidden border-r border-[#E5E7EB] bg-white shadow-xl lg:hidden"
            >
              {header}
              <SidebarNav collapsed={false} onNavigate={onMobileClose} />
            </motion.aside>
          </>
        ) : null}
      </AnimatePresence>
    </>
  );
}
