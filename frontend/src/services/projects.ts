import { api } from "./api";

export const getProjects = () => api.get("/projects");
export const createProject = (data: { name: string, description: string }) =>
  api.post("/projects", data);
