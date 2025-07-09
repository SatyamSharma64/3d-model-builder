import express from "express";
import { registerUser, loginUser, getMe } from "../controllers/authController";
import { validateRequest } from "../middleware/validateRequest";
import { registerSchema, loginSchema } from "../validators/authSchemas";
import { authLimiter } from "../middleware/rateLimiter";
import passport from "passport";
import { generateToken } from "../services/auth";
import { authenticateUser } from "../middleware/auth";

const router = express.Router();

router.post("/register", authLimiter, validateRequest(registerSchema), registerUser);
router.post("/login", authLimiter, validateRequest(loginSchema), loginUser);
router.get("/me", authenticateUser, getMe);

// Google OAuth
router.get("/google", passport.authenticate("google", { scope: ["profile", "email"] }));
router.get("/google/callback", passport.authenticate("google", {
  failureRedirect: "/login",
  session: false,
}), (req, res) => {
  const user = req.user as any;
  const token = generateToken(user._id);
  res.cookie("token", token, { httpOnly: true, sameSite: "lax" });
  res.redirect("http://localhost:5173/dashboard");
});

export default router;
