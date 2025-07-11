import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import { fetchProjects, createProject } from "./projectAPI";
// import type { Project } from "../../types/project";

interface Project {
  _id: string;
  name: string;
  previewUrl: string | null;
  description?: string;
  createdAt?: string;
}

interface ProjectState {
  projects: Project[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
  activeProjectId: string | null;
}

const initialState: ProjectState = {
  projects: [],
  status: "idle",
  error: null,
  activeProjectId: null,
};

export const loadProjects = createAsyncThunk("projects/fetchAll", fetchProjects);

export const createNewProject = createAsyncThunk("projects/create", 
  async (name: string, thunkAPI) => {
    try{
      const res = await createProject({name});
      return res;
    } catch (error: any){
      return thunkAPI.rejectWithValue(error?.response?.data?.message || "Project creation failed")
    }
  }
)

const projectSlice = createSlice({
  name: "projects",
  initialState,
  reducers: {
    setActiveProject: (state, action: PayloadAction<string>) => {
      state.activeProjectId = action.payload;
    },
    setPreviewUrl: (state, action: PayloadAction<{ projectId: string; url: string }>) => {
      const project = state.projects.find(p => p._id === action.payload.projectId);
      if (project) {
        project.previewUrl = action.payload.url;
      }
    },
    clearPreview: (state, action: PayloadAction<{ projectId: string }>) => {
      const project = state.projects.find(p => p._id === action.payload.projectId);
      if (project) {
        project.previewUrl = null;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadProjects.pending, (state) => {
        state.status = "loading";
      })
      .addCase(loadProjects.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.projects = action.payload;
      })
      .addCase(loadProjects.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || "Could not load projects";
      })
      .addCase(createNewProject.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.projects.push(action.payload);
      })
      .addCase(createNewProject.rejected, (state, action) => {
        state.status = "failed";
        state.error = (action.payload as string) || "Could not create project";
      });
  },
});


export const { setActiveProject, setPreviewUrl, clearPreview } = projectSlice.actions;
export default projectSlice.reducer;
