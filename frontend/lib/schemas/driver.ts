import { z } from "zod";

export const driverFilterSchema = z.object({
  nationality: z.string().optional(),
  min_age: z.coerce.number().min(16).max(60).optional(),
  max_age: z.coerce.number().min(16).max(60).optional(),
  min_wins: z.coerce.number().min(0).optional(),
  min_podiums: z.coerce.number().min(0).optional(),
  min_championships: z.coerce.number().min(0).optional(),
  active_only: z.boolean().optional(),
  sort_by: z
    .enum(["win_rate", "total_wins", "total_podiums", "championships_won"])
    .optional(),
  sort_order: z.enum(["asc", "desc"]).optional(),
});

export type DriverFilterFormData = z.infer<typeof driverFilterSchema>;
