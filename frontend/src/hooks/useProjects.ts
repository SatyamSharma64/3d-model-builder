import { useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadProjects } from "../features/projects/projectSlice";
import type { RootState, AppDispatch } from "../app/store";
import type { Project } from "../types/project";

interface UseProjectsResult {
  projects: Project[];
  status: "idle" | "loading" | "succeeded" | "failed";
  activeProject?: Project;
}

export function useProjects(): UseProjectsResult {
  const dispatch = useDispatch<AppDispatch>();
  const { projects, status } = useSelector((state: RootState) => state.projects);
  const activeProjectId = useSelector((state: RootState) => state.projects.activeProjectId);

  useEffect(() => {
    if (status === "idle") {
      dispatch(loadProjects());
    }
  }, [dispatch, status]);

  const activeProject = useMemo(() => {
    return projects.find((p) => p._id === activeProjectId);
  }, [projects, activeProjectId]);

  return {
    projects: projects,
    status,
    activeProject,
  };
}
