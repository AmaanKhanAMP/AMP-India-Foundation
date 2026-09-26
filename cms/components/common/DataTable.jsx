"use client";

import { useMemo, useState } from "react";
import { Trash2 } from "lucide-react";
import Button from "@/components/ui/Button";
import SearchInput from "@/components/ui/SearchInput";
import { cn } from "@/utils/cn";

export default function DataTable({
  columns,
  rows,
  rowKey = "id",
  searchable = true,
  searchPlaceholder = "Search…",
  searchValue,
  onSearchChange,
  page = 1,
  pages = 1,
  total = 0,
  onPageChange,
  selectable = false,
  selectedIds = [],
  onSelectionChange,
  bulkActions,
  emptyMessage = "No records found.",
}) {
  const [localSearch, setLocalSearch] = useState("");
  const controlled = typeof onSearchChange === "function";
  const q = controlled ? searchValue || "" : localSearch;

  const visibleRows = useMemo(() => {
    if (controlled || !q) return rows;
    const needle = q.toLowerCase();
    return rows.filter((row) =>
      columns.some((col) =>
        String(col.getValue?.(row) ?? row[col.key] ?? "")
          .toLowerCase()
          .includes(needle)
      )
    );
  }, [rows, q, columns, controlled]);

  const allSelected =
    selectable && visibleRows.length > 0 && visibleRows.every((r) => selectedIds.includes(r[rowKey]));

  const toggleAll = () => {
    if (!onSelectionChange) return;
    if (allSelected) onSelectionChange([]);
    else onSelectionChange(visibleRows.map((r) => r[rowKey]));
  };

  const toggleOne = (id) => {
    if (!onSelectionChange) return;
    if (selectedIds.includes(id)) onSelectionChange(selectedIds.filter((x) => x !== id));
    else onSelectionChange([...selectedIds, id]);
  };

  return (
    <div className="overflow-hidden rounded-[20px] border border-[#E2E8F0] bg-white shadow-[var(--shadow-sm)]">
      <div className="flex flex-col gap-3 border-b border-[#E2E8F0] bg-slate-50/60 p-4 sm:flex-row sm:items-center sm:justify-between">
        {searchable ? (
          <SearchInput
            value={q}
            onChange={(v) => {
              if (controlled) onSearchChange(v);
              else setLocalSearch(v);
            }}
            placeholder={searchPlaceholder}
            className="max-w-sm"
          />
        ) : (
          <div />
        )}
        {bulkActions && selectedIds.length > 0 ? (
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--primary)]">
              {selectedIds.length} selected
            </span>
            {bulkActions}
          </div>
        ) : null}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="sticky top-0 z-10 bg-white/95 text-[11px] uppercase tracking-[0.08em] text-slate-400 backdrop-blur">
            <tr className="border-b border-slate-100">
              {selectable ? (
                <th className="px-4 py-3.5">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleAll}
                    className="h-4 w-4 rounded border-slate-300 text-[var(--primary)]"
                  />
                </th>
              ) : null}
              {columns.map((col) => (
                <th key={col.key} className={cn("px-4 py-3.5 font-bold", col.className)}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (selectable ? 1 : 0)}
                  className="px-4 py-16 text-center text-slate-500"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              visibleRows.map((row) => (
                <tr
                  key={row[rowKey]}
                  className="border-t border-slate-50 transition hover:bg-[var(--primary-soft)]/60"
                >
                  {selectable ? (
                    <td className="px-4 py-3.5">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(row[rowKey])}
                        onChange={() => toggleOne(row[rowKey])}
                        className="h-4 w-4 rounded border-slate-300 text-[var(--primary)]"
                      />
                    </td>
                  ) : null}
                  {columns.map((col) => (
                    <td key={col.key} className={cn("px-4 py-3.5 text-slate-700", col.className)}>
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {pages > 1 || total > 0 ? (
        <div className="flex flex-col gap-3 border-t border-slate-100 bg-slate-50/40 px-4 py-3 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <span className="text-xs font-medium">
            Page {page} of {Math.max(pages, 1)}
            {total ? ` · ${total} total` : ""}
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange?.(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= pages}
              onClick={() => onPageChange?.(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export function BulkDeleteButton({ onClick, loading }) {
  return (
    <Button variant="danger" size="sm" onClick={onClick} loading={loading}>
      <Trash2 className="h-4 w-4" />
      Delete selected
    </Button>
  );
}
