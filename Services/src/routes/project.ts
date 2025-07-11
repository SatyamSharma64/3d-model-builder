import express from "express";
import { createProject, getProjects } from "../controllers/projectController";
import { validateRequest } from "../middleware/validateRequest";
import { createProjectSchema } from "../validators/projectSchemas";
import { authenticateUser } from "../middleware/auth";
import { rateLimiter } from "../middleware/rateLimiter";

const router = express.Router();

router.use(authenticateUser);
router.get("/", rateLimiter, getProjects);
router.post("/", rateLimiter, validateRequest(createProjectSchema), createProject);

export default router;
