import express from "express";
import { registerUser, loginUser, getMe } from "../controllers/authController";
import { validateRequest } from "../middleware/validateRequest";
import { registerSchema, loginSchema } from "../validators/authSchemas";
import { rateLimiter } from "../middleware/rateLimiter";
// import passport from "passport";
// import { generateToken } from "../services/auth";
import { authenticateUser } from "../middleware/auth";

const router = express.Router();

router.post("/register", rateLimiter, validateRequest(registerSchema), registerUser);
router.post("/login", rateLimiter, validateRequest(loginSchema), loginUser);
router.get("/me", rateLimiter, authenticateUser, getMe);

// Google OAuth
// router.get("/google", passport.authenticate("google", { scope: ["profile", "email"] }));
// router.get("/google/callback", passport.authenticate("google", {
//   failureRedirect: "/login",
//   session: false,
// }), (req, res) => {
//   const user = req.user as any;
//   const token = generateToken(user._id);
//   res.cookie("token", token, { httpOnly: true, sameSite: "lax" });
//   res.redirect(`${process.env.GOOGLE_REDIRECT_URL}`);
// });

export default router;
