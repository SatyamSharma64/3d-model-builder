import { Request, Response } from "express";
import { Project } from "../models/Project";

export const createProject = async (req: Request, res: Response) => {
  const { name, description } = req.body;
  const userId = (req as any).user.userId;

  const project = await Project.create({ name, description, userId });
  res.status(201).json(project);
};

export const getProjects = async (req: Request, res: Response) => {
  const userId = (req as any).user.userId;
  const projects = await Project.find({ userId }).sort({ updatedAt: -1 });
  res.json(projects);
};
