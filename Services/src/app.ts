import express from "express";
import cookieParser from "cookie-parser";
import cors from "cors";
import authRoutes from "./routes/auth";
import projectRoutes from "./routes/project";
// import jobRoutes from "./routes/job";

import "./strategies/google";

const app = express();

app.set('trust proxy', true);
app.use(cors({ origin: `${process.env.CLIENT_URL}`, credentials: true }));
app.use(express.json());
app.use(cookieParser());

app.use("/api/auth", authRoutes);
app.use("/api/projects", projectRoutes);

// app.use("/api/queue", jobRoutes);

export default app;
