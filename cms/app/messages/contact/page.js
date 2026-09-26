"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CheckCheck,
  Mail,
  Reply,
  Star,
  Trash2,
} from "lucide-react";
import AdminLayout from "@/layouts/AdminLayout";
import PageHeader from "@/components/common/PageHeader";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import StatusBadge from "@/components/ui/StatusBadge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import SearchInput from "@/components/ui/SearchInput";
import { ConfirmDialog } from "@/components/ui/Modal";
import contactService from "@/services/contactService";
import { useToast } from "@/contexts/ToastContext";
import { cn } from "@/utils/cn";

export default function ContactMessagesPage() {
  const toast = useToast();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [confirm, setConfirm] = useState({ open: false, id: null });
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await contactService.listMessages({
        page,
        per_page: 25,
        search: search || undefined,
        status: status || undefined,
      });
      const data = res.data || [];
      setRows(data);
      setPages(res.pagination?.pages || 1);
      setTotal(res.pagination?.total || 0);
      if (data.length && !selectedId) setSelectedId(data[0].id);
      if (selectedId && !data.find((r) => r.id === selectedId) && data[0]) {
        setSelectedId(data[0].id);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to load messages.");
    } finally {
      setLoading(false);
    }
  }, [page, search, status]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const selected = rows.find((r) => r.id === selectedId) || null;

  const markRead = async (row) => {
    if (!row || row.status === "Read") return;
    try {
      await contactService.markMessageRead(row.id);
      load();
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed.");
    }
  };

  const toggleImportant = async (row) => {
    try {
      await contactService.toggleImportant(row.id, !row.is_important);
      toast.success(row.is_important ? "Unstarred." : "Marked important.");
      load();
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed.");
    }
  };

  const runDelete = async () => {
    setBusy(true);
    try {
      await contactService.deleteMessage(confirm.id);
      toast.success("Message deleted.");
      setConfirm({ open: false, id: null });
      if (selectedId === confirm.id) setSelectedId(null);
      load();
    } catch (err) {
      toast.error(err.response?.data?.message || "Delete failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AdminLayout
      breadcrumbs={[
        { label: "Dashboard", href: "/dashboard" },
        { label: "Contact Messages" },
      ]}
    >
      <PageHeader
        title="Inbox"
        description={`${total} messages · Gmail-style contact inbox`}
        actions={
          <div className="w-40">
            <Select
              value={status}
              onChange={(e) => {
                setPage(1);
                setStatus(e.target.value);
              }}
              options={[
                { value: "", label: "All" },
                { value: "New", label: "Unread" },
                { value: "Read", label: "Read" },
              ]}
            />
          </div>
        }
      />

      <div className="overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-[var(--shadow-sm)]">
        <div className="flex flex-col gap-3 border-b border-slate-100 bg-slate-50/60 px-4 py-3 sm:flex-row sm:items-center">
          <SearchInput
            value={search}
            onChange={(v) => {
              setPage(1);
              setSearch(v);
            }}
            placeholder="Search name, email, phone, message…"
            className="flex-1"
          />
        </div>

        {loading ? (
          <div className="p-4">
            <LoadingSkeleton variant="table" rows={8} />
          </div>
        ) : (
          <div className="grid min-h-[520px] lg:grid-cols-[360px_1fr]">
            <div className="border-r border-slate-100">
              {rows.length === 0 ? (
                <p className="p-6 text-sm text-slate-500">No messages found.</p>
              ) : (
                <ul className="max-h-[640px] overflow-y-auto">
                  {rows.map((row) => {
                    const active = row.id === selectedId;
                    const unread = row.status === "New";
                    return (
                      <li key={row.id}>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedId(row.id);
                            markRead(row);
                          }}
                          className={cn(
                            "flex w-full gap-3 border-b border-slate-50 px-4 py-3 text-left transition",
                            active ? "bg-blue-50/70" : "hover:bg-slate-50",
                            unread && "bg-white"
                          )}
                        >
                          <span
                            role="button"
                            tabIndex={0}
                            className="mt-0.5 shrink-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleImportant(row);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault();
                                e.stopPropagation();
                                toggleImportant(row);
                              }
                            }}
                            aria-label="Toggle important"
                          >
                            <Star
                              className={cn(
                                "h-4 w-4",
                                row.is_important
                                  ? "fill-amber-400 text-amber-400"
                                  : "text-slate-300"
                              )}
                            />
                          </span>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-2">
                              <p
                                className={cn(
                                  "truncate text-sm",
                                  unread ? "font-semibold text-slate-900" : "font-medium text-slate-700"
                                )}
                              >
                                {row.first_name} {row.last_name}
                              </p>
                              <span className="shrink-0 text-[10px] text-slate-400">
                                {row.created_at
                                  ? new Date(row.created_at).toLocaleDateString()
                                  : ""}
                              </span>
                            </div>
                            <p className="truncate text-xs text-slate-500">{row.email}</p>
                            <p className="mt-1 line-clamp-1 text-xs text-slate-500">{row.message}</p>
                          </div>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
              <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-xs text-slate-500">
                <span>
                  Page {page} of {pages}
                </span>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    Prev
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={page >= pages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </div>

            <div className="flex flex-col">
              {selected ? (
                <>
                  <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 px-5 py-3">
                    <StatusBadge status={selected.status} />
                    <Button size="sm" variant="soft" onClick={() => markRead(selected)}>
                      <CheckCheck className="h-4 w-4" />
                      Mark read
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => toggleImportant(selected)}>
                      <Star className="h-4 w-4" />
                      {selected.is_important ? "Unstar" : "Important"}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setConfirm({ open: true, id: selected.id })}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                      Delete
                    </Button>
                    <Button size="sm" variant="outline" disabled title="Coming soon">
                      <Reply className="h-4 w-4" />
                      Reply
                    </Button>
                  </div>
                  <div className="flex-1 space-y-4 p-6">
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">
                        Message from {selected.first_name} {selected.last_name}
                      </h2>
                      <p className="mt-1 text-sm text-slate-500">
                        {selected.email} · {selected.phone}
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        {selected.created_at
                          ? new Date(selected.created_at).toLocaleString()
                          : ""}
                      </p>
                    </div>
                    <div className="rounded-2xl bg-slate-50 p-5 text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
                      {selected.message}
                    </div>
                    <div className="rounded-xl border border-dashed border-slate-200 p-4 text-sm text-slate-400">
                      <Mail className="mb-2 h-4 w-4" />
                      Reply composer is future-ready — wiring SMTP later will enable direct replies.
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex flex-1 items-center justify-center text-sm text-slate-400">
                  Select a message to read
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={confirm.open}
        onClose={() => setConfirm({ open: false, id: null })}
        onConfirm={runDelete}
        title="Delete message?"
        message="This cannot be undone."
        confirmLabel="Delete"
        danger
        loading={busy}
      />
    </AdminLayout>
  );
}
