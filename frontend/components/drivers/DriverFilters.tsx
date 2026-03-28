"use client";

import { useForm } from "react-hook-form";
import { SlidersHorizontal, X } from "lucide-react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import type { DriversQueryParams, SortBy } from "@/lib/types/driver";

interface DriverFilterFormData {
  nationality: string;
  min_wins: string;
  min_podiums: string;
  min_championships: string;
  max_age: string;
  active_only: boolean;
  sort_by: SortBy;
  sort_order: "asc" | "desc";
}

interface DriverFiltersProps {
  defaultValues?: DriversQueryParams;
  onChange: (filters: DriversQueryParams) => void;
}

export function DriverFilters({ defaultValues, onChange }: DriverFiltersProps) {
  const { register, handleSubmit, reset } = useForm<DriverFilterFormData>({
    defaultValues: {
      nationality: defaultValues?.nationality ?? "",
      min_wins: defaultValues?.min_wins?.toString() ?? "",
      min_podiums: defaultValues?.min_podiums?.toString() ?? "",
      min_championships: defaultValues?.min_championships?.toString() ?? "",
      max_age: defaultValues?.max_age?.toString() ?? "",
      active_only: defaultValues?.active_only ?? false,
      sort_by: defaultValues?.sort_by ?? "total_wins",
      sort_order: defaultValues?.sort_order ?? "desc",
    },
  });

  function onSubmit(data: DriverFilterFormData) {
    const cleaned: DriversQueryParams = {};
    if (data.nationality) cleaned.nationality = data.nationality;
    if (data.min_wins) cleaned.min_wins = Number(data.min_wins);
    if (data.min_podiums) cleaned.min_podiums = Number(data.min_podiums);
    if (data.min_championships) cleaned.min_championships = Number(data.min_championships);
    if (data.max_age) cleaned.max_age = Number(data.max_age);
    if (data.active_only) cleaned.active_only = true;
    if (data.sort_by) cleaned.sort_by = data.sort_by;
    if (data.sort_order) cleaned.sort_order = data.sort_order;
    onChange(cleaned);
  }

  function handleClear() {
    reset({
      nationality: "",
      min_wins: "",
      min_podiums: "",
      min_championships: "",
      max_age: "",
      active_only: false,
      sort_by: "total_wins",
      sort_order: "desc",
    });
    onChange({});
  }

  return (
    <aside className="w-full lg:w-64 flex-shrink-0">
      <div className="bg-surface border border-border rounded-lg p-4 lg:sticky lg:top-24">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-text-primary font-semibold text-sm">
            <SlidersHorizontal className="w-4 h-4 text-accent" />
            Filters
          </div>
          <button
            type="button"
            onClick={handleClear}
            className="text-xs text-text-muted hover:text-text-secondary transition-colors flex items-center gap-1"
          >
            <X className="w-3 h-3" />
            Clear
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <Input
            id="nationality"
            label="Nationality"
            placeholder="British, German…"
            {...register("nationality")}
          />

          <Input
            id="min_wins"
            label="Min wins"
            type="number"
            placeholder="0"
            min={0}
            {...register("min_wins")}
          />

          <Input
            id="min_podiums"
            label="Min podiums"
            type="number"
            placeholder="0"
            min={0}
            {...register("min_podiums")}
          />

          <Input
            id="min_championships"
            label="Min championships"
            type="number"
            placeholder="0"
            min={0}
            {...register("min_championships")}
          />

          <Input
            id="max_age"
            label="Max age"
            type="number"
            placeholder="Any"
            min={16}
            max={60}
            {...register("max_age")}
          />

          <div className="flex items-center gap-2">
            <input
              id="active_only"
              type="checkbox"
              className="w-4 h-4 rounded border-border bg-surface accent-accent"
              {...register("active_only")}
            />
            <label
              htmlFor="active_only"
              className="text-sm text-text-secondary cursor-pointer"
            >
              Active drivers only
            </label>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-text-secondary">
              Sort by
            </label>
            <select
              className="bg-surface border border-border rounded px-3 py-2 text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent"
              {...register("sort_by")}
            >
              <option value="total_wins">Total Wins</option>
              <option value="total_podiums">Total Podiums</option>
              <option value="championships_won">Championships</option>
              <option value="win_rate">Win Rate</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-text-secondary">
              Order
            </label>
            <select
              className="bg-surface border border-border rounded px-3 py-2 text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent"
              {...register("sort_order")}
            >
              <option value="desc">Highest first</option>
              <option value="asc">Lowest first</option>
            </select>
          </div>

          <Button type="submit" className="w-full">
            Apply filters
          </Button>
        </form>
      </div>
    </aside>
  );
}
