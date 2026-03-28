import { z } from "zod";

export const createShortlistSchema = z.object({
  name: z.string().min(1, "Name is required").max(100, "Name is too long"),
  description: z.string().max(500, "Description is too long").optional(),
});

export type CreateShortlistFormData = z.infer<typeof createShortlistSchema>;
