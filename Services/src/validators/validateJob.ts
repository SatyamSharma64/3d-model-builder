import { z } from "zod";

export const JobSchema = z.object({
  userId: z.string().min(3),
  projectId: z.string().min(3),
  command: z.string().min(2),
  args: z.any().optional(),
  priority: z.enum(["high", "normal", "low"]).optional(),
});
