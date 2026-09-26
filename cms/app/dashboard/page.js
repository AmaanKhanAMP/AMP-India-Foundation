"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowUpRight,
  CalendarDays,
  FileEdit,
  GalleryHorizontalEnd,
  Image as ImageIcon,
  Mail,
  MessageSquareQuote,
  Plus,
  Sparkles,
  Star,
  Upload,
  Trash2,
} from "lucide-react";
import AdminLayout from "@/layouts/AdminLayout";
import PageHeader from "@/components/common/PageHeader";
import StatCard from "@/components/common/StatCard";
import Surface from "@/components/common/Surface";
import Button from "@/components/ui/Button";
import StatusBadge from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/common/LoadingSkeleton";
import dashboardService from "@/services/dashboardService";
import { useToast } from "@/contexts/ToastContext";
import { resolveImageUrl } from "@/utils/imageUrl";
import { useAuth } from "@/contexts/AuthContext";

const QUICK = [
  { href: "/home/hero-banners/new", label: "Add hero banner", icon: Sparkles },
  { href: "/home/projects/new", label: "Add project", icon: GalleryHorizontalEnd },
  { href: "/events/featured/new", label: "Add featured event", icon: Star },
  { href: "/messages/contact", label: "Open inbox", icon: Mail },
];

export default function DashboardPage() {
  const toast = useToast();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await dashboardService.getDashboardStats();
        setStats(res.data || {});
      } catch (err) {
        toast.error(err.response?.data?.message || "Failed to load stats.");
      } finally {
        setLoading(false);
      }
    })();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const cards = [
    { title: "Hero Banners", value: stats?.hero_banners ?? "—", icon: Sparkles, href: "/home/hero-banners" },
    { title: "Latest Projects", value: stats?.home_projects ?? "—", icon: GalleryHorizontalEnd, href: "/home/projects" },
    { title: "Testimonials", value: stats?.testimonials ?? "—", icon: MessageSquareQuote, href: "/home/testimonials" },
    {
      title: "Events",
      value:
        stats
          ? (stats.home_events || 0) +
            (stats.featured_events || 0) +
            (stats.upcoming_events || 0)
          : "—",
      icon: CalendarDays,
      href: "/events/upcoming",
    },
    { title: "Past Events", value: stats?.past_events ?? stats?.gallery_items ?? "—", icon: ImageIcon, href: "/events/gallery" },
    {
      title: "Contact Messages",
      value: stats?.contact_messages ?? "—",
      icon: Mail,
      hint: stats ? `${stats.unread_messages || 0} unread` : undefined,
      href: "/messages/contact",
    },
    { title: "Published", value: stats?.published_items ?? "—", icon: Star },
    { title: "Drafts", value: stats?.draft_items ?? "—", icon: FileEdit },
    {
      title: "Items in Trash",
      value: stats?.trash_items ?? "—",
      icon: Trash2,
      href: "/trash",
      hint: stats?.trash_items ? "Review & restore" : "Empty",
    },
    { title: "Uploads", value: stats?.total_uploads ?? "—", icon: Upload },
  ];

  const chartHeights = [40, 65, 45, 80, 55, 70, 90, 60, 75, 50, 85, 68];
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <AdminLayout breadcrumbs={[{ label: "Dashboard" }]}>
      <div className="mb-8 overflow-hidden rounded-[20px] border border-blue-100/50 bg-gradient-to-br from-[#2563EB] via-[#1D4ED8] to-[#111827] p-6 text-white shadow-[var(--shadow-md)] sm:p-8">
        <div className="pointer-events-none absolute inset-0" />
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-blue-100/80">
              AMP India Foundation
            </p>
            <h1 className="font-display mt-2 text-2xl font-extrabold sm:text-3xl">
              {greeting}
              {user?.name ? `, ${user.name.split(" ")[0]}` : ""}
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-blue-100/90">
              Manage homepage banners, events, testimonials, and inbox — changes sync to the
              public website instantly.
            </p>
          </div>
          <Link href="/home/hero-banners/new">
            <Button variant="secondary" className="border-0 bg-white text-[#2563EB] hover:bg-blue-50">
              <Plus className="h-4 w-4" />
              New banner
            </Button>
          </Link>
        </div>
      </div>

      <PageHeader
        title="Overview"
        description="Live counts across website modules and publishing status."
      />

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {cards.map((card, i) => {
            const body = <StatCard {...card} />;
            return (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                {card.href ? (
                  <Link href={card.href} className="block">
                    {body}
                  </Link>
                ) : (
                  body
                )}
              </motion.div>
            );
          })}
        </div>
      )}

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <Surface
          className="xl:col-span-2"
          title="Content pulse"
          description="Publishing activity snapshot across modules."
          action={
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-[var(--primary)] ring-1 ring-blue-100">
              {stats?.published_items || 0} published
            </span>
          }
        >
          <div className="flex h-48 items-end gap-2 rounded-xl bg-gradient-to-b from-slate-50 to-white p-4 ring-1 ring-slate-100">
            {chartHeights.map((h, i) => (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                animate={{ height: `${h}%` }}
                transition={{ delay: 0.05 * i, duration: 0.4 }}
                className="flex-1 rounded-t-md bg-gradient-to-t from-[#1E3A8A] to-[#2563EB] opacity-90"
              />
            ))}
          </div>
        </Surface>

        <Surface title="Quick actions" description="Jump into common workflows.">
          <div className="space-y-2">
            {QUICK.map((item) => (
              <Link key={item.href} href={item.href} className="block">
                <div className="group flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/60 px-3 py-3 transition hover:border-blue-100 hover:bg-blue-50/50">
                  <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-[var(--primary)] shadow-sm ring-1 ring-slate-100">
                    <item.icon className="h-4 w-4" />
                  </span>
                  <span className="flex-1 text-sm font-semibold text-slate-800">{item.label}</span>
                  <ArrowUpRight className="h-4 w-4 text-slate-300 transition group-hover:text-[var(--primary)]" />
                </div>
              </Link>
            ))}
          </div>
        </Surface>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Surface
          title="Unread messages"
          action={
            <Link href="/messages/contact" className="text-xs font-bold text-[var(--primary)]">
              View all
            </Link>
          }
        >
          <div className="space-y-3">
            {(stats?.recent_messages || [])
              .filter((m) => m.status === "New")
              .slice(0, 4)
              .map((m) => (
                <div
                  key={m.id}
                  className="rounded-xl border border-slate-100 bg-gradient-to-r from-blue-50/50 to-white p-3"
                >
                  <p className="text-sm font-bold text-slate-900">
                    {m.first_name} {m.last_name}
                  </p>
                  <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">
                    {m.message}
                  </p>
                </div>
              ))}
            {!loading && !(stats?.recent_messages || []).some((m) => m.status === "New") ? (
              <p className="text-sm text-slate-500">No unread messages.</p>
            ) : null}
          </div>
        </Surface>

        <Surface title="Recent updates">
          <div className="space-y-3">
            {(stats?.recent_updates || []).slice(0, 6).map((item) => (
              <div key={`${item.type}-${item.id}`} className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-slate-800">{item.title}</p>
                  <p className="text-[11px] capitalize text-slate-400">
                    {item.type.replace(/_/g, " ")}
                  </p>
                </div>
                <StatusBadge status={item.status} />
              </div>
            ))}
            {!loading && !(stats?.recent_updates || []).length ? (
              <p className="text-sm text-slate-500">No updates yet.</p>
            ) : null}
          </div>
        </Surface>

        <Surface title="Latest images">
          <div className="grid grid-cols-4 gap-2">
            {(stats?.recent_images || []).slice(0, 8).map((img) => (
              <div
                key={`${img.type}-${img.id}`}
                className="aspect-square overflow-hidden rounded-xl bg-slate-100 ring-1 ring-slate-100 transition hover:ring-blue-200"
                title={img.title}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={resolveImageUrl(img.url)}
                  alt={img.title}
                  className="h-full w-full object-cover"
                />
              </div>
            ))}
          </div>
          {!loading && !(stats?.recent_images || []).length ? (
            <p className="text-sm text-slate-500">No images yet.</p>
          ) : null}
        </Surface>
      </div>
    </AdminLayout>
  );
}
