import rateLimit from "express-rate-limit";

export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: "Too many login/register attempts. Try again later.",
  standardHeaders: true,
  legacyHeaders: false,
});
