"use client";

import { useState, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { LayoutGrid, Table2 } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { DriverFilters } from "@/components/drivers/DriverFilters";
import { DriverGrid } from "@/components/drivers/DriverGrid";
import { DriverTable } from "@/components/drivers/DriverTable";
import { AddToShortlistModal } from "@/components/drivers/AddToShortlistModal";
import { Button } from "@/components/ui/Button";
import { useDrivers } from "@/lib/hooks/useDrivers";
import type { DriversQueryParams, DriverSummaryOut, SortBy } from "@/lib/types/driver";

export default function DriversPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [view, setView] = useState<"grid" | "table">("grid");
  const [shortlistTarget, setShortlistTarget] = useState<DriverSummaryOut | null>(null);

  // Parse filter state from URL
  const page = Number(searchParams.get("page") ?? 1);
  const filters: DriversQueryParams = {
    page,
    limit: 18,
    nationality: searchParams.get("nationality") ?? undefined,
    min_wins: searchParams.get("min_wins") ? Number(searchParams.get("min_wins")) : undefined,
    min_podiums: searchParams.get("min_podiums") ? Number(searchParams.get("min_podiums")) : undefined,
    min_championships: searchParams.get("min_championships") ? Number(searchParams.get("min_championships")) : undefined,
    max_age: searchParams.get("max_age") ? Number(searchParams.get("max_age")) : undefined,
    active_only: searchParams.get("active_only") === "true" ? true : undefined,
    sort_by: (searchParams.get("sort_by") as SortBy) ?? "total_wins",
    sort_order: (searchParams.get("sort_order") as "asc" | "desc") ?? "desc",
  };

  const { data, isLoading } = useDrivers(filters);

  function updateFilters(newFilters: DriversQueryParams) {
    const params = new URLSearchParams();
    if (newFilters.nationality) params.set("nationality", newFilters.nationality);
    if (newFilters.min_wins != null) params.set("min_wins", String(newFilters.min_wins));
    if (newFilters.min_podiums != null) params.set("min_podiums", String(newFilters.min_podiums));
    if (newFilters.min_championships != null) params.set("min_championships", String(newFilters.min_championships));
    if (newFilters.max_age != null) params.set("max_age", String(newFilters.max_age));
    if (newFilters.active_only) params.set("active_only", "true");
    if (newFilters.sort_by) params.set("sort_by", newFilters.sort_by);
    if (newFilters.sort_order) params.set("sort_order", newFilters.sort_order);
    params.set("page", "1");
    router.push(`/drivers?${params.toString()}`);
  }

  function handleSort(col: SortBy) {
    const currentSortBy = filters.sort_by;
    const currentOrder = filters.sort_order ?? "desc";
    const newOrder = currentSortBy === col && currentOrder === "desc" ? "asc" : "desc";
    updateFilters({ ...filters, sort_by: col, sort_order: newOrder, page: 1 });
  }

  function goToPage(newPage: number) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(newPage));
    router.push(`/drivers?${params.toString()}`);
  }

  const totalPages = data ? Math.ceil(data.total / 18) : 1;
  const drivers = data?.drivers ?? [];

  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Drivers</h1>
            {data && (
              <p className="text-sm text-text-muted mt-0.5">
                {data.total.toLocaleString()} drivers
              </p>
            )}
          </div>
          <div className="flex items-center gap-1 bg-surface-elevated border border-border rounded-lg p-1">
            <button
              onClick={() => setView("grid")}
              className={`p-1.5 rounded transition-colors ${
                view === "grid"
                  ? "bg-surface text-text-primary shadow-sm"
                  : "text-text-muted hover:text-text-secondary"
              }`}
              title="Grid view"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setView("table")}
              className={`p-1.5 rounded transition-colors ${
                view === "table"
                  ? "bg-surface text-text-primary shadow-sm"
                  : "text-text-muted hover:text-text-secondary"
              }`}
              title="Table view"
            >
              <Table2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex flex-col lg:flex-row gap-6">
          <DriverFilters defaultValues={filters} onChange={updateFilters} />

          <div className="flex-1 flex flex-col gap-4">
            {view === "grid" ? (
              <DriverGrid
                drivers={drivers}
                isLoading={isLoading}
                onAddToShortlist={setShortlistTarget}
              />
            ) : (
              <DriverTable
                drivers={drivers}
                isLoading={isLoading}
                sortBy={filters.sort_by}
                sortOrder={filters.sort_order}
                onSort={handleSort}
                onAddToShortlist={setShortlistTarget}
              />
            )}

            {/* Pagination */}
            {!isLoading && totalPages > 1 && (
              <div className="flex items-center justify-between pt-2">
                <p className="text-sm text-text-muted">
                  Page {page} of {totalPages}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => goToPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => goToPage(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <AddToShortlistModal
        driver={shortlistTarget}
        open={!!shortlistTarget}
        onOpenChange={(open) => !open && setShortlistTarget(null)}
      />
    </PageContainer>
  );
}
