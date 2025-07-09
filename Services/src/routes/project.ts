import express from "express";
import { createProject, getProjects } from "../controllers/projectController";
import { validateRequest } from "../middleware/validateRequest";
import { createProjectSchema } from "../validators/projectSchemas";
import { authenticateUser } from "../middleware/auth";

const router = express.Router();

router.use(authenticateUser);
router.get("/", getProjects);
router.post("/", validateRequest(createProjectSchema), createProject);

export default router;
