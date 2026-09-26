"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { LogOut, Menu, Settings, User } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import Breadcrumbs from "./Breadcrumbs";
import SearchInput from "@/components/ui/SearchInput";

const SEARCH_PAGES = [
  { label: "Dashboard", href: "/dashboard", keywords: "home overview stats" },
  { label: "Hero Banners", href: "/home/hero-banners", keywords: "carousel slides hero" },
  { label: "Latest Projects", href: "/home/projects", keywords: "projects" },
  { label: "Home Upcoming Events", href: "/home/events", keywords: "events home" },
  { label: "Testimonials", href: "/home/testimonials", keywords: "reviews quotes" },
  { label: "Featured Events", href: "/events/featured", keywords: "featured" },
  { label: "Upcoming Events", href: "/events/upcoming", keywords: "upcoming calendar" },
  { label: "Past Events", href: "/events/gallery", keywords: "past events gallery images legacy" },
  { label: "Contact Messages", href: "/messages/contact", keywords: "inbox mail contact" },
  { label: "Profile", href: "/settings/profile", keywords: "account settings" },
  { label: "Change Password", href: "/settings/password", keywords: "security password" },
];

export default function Topbar({ breadcrumbs = [], onMenuClick }) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [openMenu, setOpenMenu] = useState(false);
  const [openSearch, setOpenSearch] = useState(false);
  const menuRef = useRef(null);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return SEARCH_PAGES.filter(
      (p) =>
        p.label.toLowerCase().includes(q) ||
        p.keywords.includes(q) ||
        p.href.toLowerCase().includes(q)
    ).slice(0, 6);
  }, [query]);

  useEffect(() => {
    const onDoc = (e) => {
      if (!menuRef.current?.contains(e.target)) setOpenMenu(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  return (
    <header className="sticky top-0 z-20 border-b border-[#E2E8F0] bg-white/75 shadow-[0_1px_0_rgba(17,24,39,0.03)] backdrop-blur-2xl">
      <div className="flex h-[76px] items-center gap-4 pl-8 pr-4 lg:pr-6">
        <button
          type="button"
          onClick={onMenuClick}
          className="inline-flex rounded-xl border border-slate-200/90 bg-white/90 p-2.5 text-slate-600 shadow-sm transition hover:bg-slate-50 lg:hidden"
          aria-label="Open menu"
        >
          <Menu className="h-4 w-4" />
        </button>

        <div className="hidden min-w-0 flex-1 items-center md:flex">
          <Breadcrumbs items={breadcrumbs} />
        </div>

        <div className="relative hidden w-full max-w-md items-center lg:flex">
          <SearchInput
            value={query}
            onChange={(v) => {
              setQuery(v);
              setOpenSearch(true);
            }}
            placeholder="Search pages…"
          />
          <AnimatePresence>
            {openSearch && query.trim() ? (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 4, scale: 0.98 }}
                transition={{ duration: 0.16 }}
                className="absolute left-0 right-0 top-[calc(100%+0.5rem)] z-30 overflow-hidden rounded-2xl border border-slate-200/90 bg-white/95 shadow-[var(--shadow-lg)] backdrop-blur-xl"
              >
                {results.length === 0 ? (
                  <p className="px-4 py-3.5 text-sm text-slate-500">No pages found.</p>
                ) : (
                  <ul className="py-1">
                    {results.map((item) => (
                      <li key={item.href}>
                        <button
                          type="button"
                          className="flex w-full px-4 py-2.5 text-left text-sm font-medium text-slate-700 transition hover:bg-[var(--primary-soft)] hover:text-[var(--primary)]"
                          onClick={() => {
                            router.push(item.href);
                            setQuery("");
                            setOpenSearch(false);
                          }}
                        >
                          {item.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>

        <Link
          href="/settings/profile"
          className="hidden items-center rounded-xl border border-slate-200/90 bg-white/90 p-2.5 text-slate-500 shadow-sm transition hover:bg-slate-50 hover:text-slate-800 sm:inline-flex"
          aria-label="Settings"
          title="Settings"
        >
          <Settings className="h-4 w-4" />
        </Link>

        <div className="relative ml-auto flex shrink-0 items-center" ref={menuRef}>
          <button
            type="button"
            onClick={() => setOpenMenu((v) => !v)}
            className="flex items-center gap-2 rounded-2xl border border-slate-200/90 bg-white/90 py-1.5 pl-1.5 pr-2.5 shadow-sm transition hover:bg-slate-50"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-hover)] text-white shadow-sm shadow-blue-500/20">
              <User className="h-4 w-4" />
            </div>
            <div className="hidden min-w-0 text-left sm:block">
              <p className="truncate text-xs font-bold text-slate-900">{user?.name || "Admin"}</p>
              <p className="truncate text-[11px] text-slate-500">Administrator</p>
            </div>
          </button>

          <AnimatePresence>
            {openMenu ? (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 6, scale: 0.98 }}
                className="absolute right-0 top-[calc(100%+0.5rem)] z-30 w-[min(14rem,calc(100vw-1.5rem))] overflow-hidden rounded-2xl border border-slate-200/90 bg-white/95 py-1 shadow-[var(--shadow-lg)] backdrop-blur-xl lg:w-56"
              >
                <div className="min-w-0 border-b border-slate-100 px-4 py-3">
                  <p className="truncate text-sm font-bold text-slate-900">{user?.name}</p>
                  <p className="truncate text-xs text-slate-500">{user?.email}</p>
                </div>
                <Link
                  href="/settings/profile"
                  onClick={() => setOpenMenu(false)}
                  className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  <User className="h-4 w-4 text-slate-400" />
                  Profile
                </Link>
                <Link
                  href="/settings/password"
                  onClick={() => setOpenMenu(false)}
                  className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  <Settings className="h-4 w-4 text-slate-400" />
                  Settings
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setOpenMenu(false);
                    logout();
                  }}
                  className="flex w-full items-center gap-2 px-4 py-2.5 text-sm font-semibold text-[var(--danger)] hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
