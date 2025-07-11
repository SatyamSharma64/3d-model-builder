import { Request, Response } from "express";
import { User } from "../models/User";
import { comparePassword, generateSalt, generateToken, hashPassword } from "../services/auth";

const isProduction = process.env.NODE_ENV === "production";

export const registerUser = async (req: Request, res: Response) => {
  const { email, password } = req.body;

  const exists = await User.findOne({ email });
  if (exists){
    res.status(409).json({ error: "User already exists" });
    return;
  }

  const salt = await generateSalt;
  const hashed = await hashPassword(password,salt);
  const user = await User.create({ email, password: hashed, provider: "credentials" });

  const token = generateToken(user._id.toString());
  res.cookie("token", token, {
    httpOnly: true,
    secure: isProduction, // ensures cookies are sent only via HTTPS
    sameSite: isProduction ? "none" : "lax", // allow cross-site cookies in prod
    maxAge: 604800000,
  });
  res.json({ user: { _id: user._id, email: user.email } });
};

export const loginUser = async (req: Request, res: Response) => {
  const { email, password } = req.body;

  const user = await User.findOne({ email });
  if (!user || !user.password || !(await comparePassword(password, user.password))) {
    res.status(401).json({ error: "Invalid credentials" });
    return;
  }

  const token = generateToken(user._id.toString());
  res.cookie("token", token, {
    httpOnly: true,
    secure: isProduction, // ensures cookies are sent only via HTTPS
    sameSite: isProduction ? "none" : "lax", // allow cross-site cookies in prod
    maxAge: 604800000,
  });
  res.json({ user: { _id: user._id, email: user.email } });
};



export const getMe = async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.userId;

    const user = await User.findById(userId).select("_id email"); 

    if (!user) {
      res.status(404).json({ error: "User not found" });
      return;
    }

    res.json({ user });
    return;
  } catch (err) {
    console.error("Error in /me:", err);
    res.status(500).json({ error: "Server error" });
    return;
  }
};
