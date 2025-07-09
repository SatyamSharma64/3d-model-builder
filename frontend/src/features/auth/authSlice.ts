import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import { api } from "@/services/api";


export const login = createAsyncThunk(
  "auth/login",
  async ({ email, password }: { email: string; password: string }, thunkAPI) => {
    try {
      const res = await api.post("/auth/login", { email, password }, { withCredentials: true });
      return res.data.user;
    } catch (err: any) {
      return thunkAPI.rejectWithValue(err.response?.data?.message || "Login failed");
    }
  }
);

export const signup = createAsyncThunk(
  "auth/signup",
  async ({ email, password }: { email: string; password: string }, thunkAPI) => {
    try {
      const res = await api.post("/auth/register", { email, password }, { withCredentials: true });
      return res.data.user;
    } catch (err: any) {
      return thunkAPI.rejectWithValue(err.response?.data?.message || "Signup failed");
    }
  }
);


interface User {
  _id: string;
  email: string;
}

interface AuthState {
  user: User | null; 
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null; 
  isLoading: boolean;
}

const initialState: AuthState = {
  user: null,
  status: "idle",
  error: null, 
  isLoading: true,
};


const authSlice = createSlice({
  name: "auth",
  initialState, 
  reducers: {
    logout: (state) => {
      state.user = null;
      state.status = "idle"; 
      state.error = null;    
      state.isLoading = false;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.status = "succeeded";
      state.error = null;
      state.isLoading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.status = "loading";
        state.error = null; 
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<User>) => { 
        state.status = "succeeded";
        state.user = action.payload; 
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.status = "failed";
        state.error = (action.payload as string) || action.error.message || "Login failed";
        state.user = null; 
      })
      .addCase(signup.pending, (state) => { 
        state.status = "loading";
        state.error = null;
      })
      .addCase(signup.fulfilled, (state, action: PayloadAction<User>) => {
        state.status = "succeeded";
        state.user = action.payload;
        state.error = null;
      })
      .addCase(signup.rejected, (state, action) => {
        state.status = "failed";
        state.error = (action.payload as string) || action.error.message || "Signup failed";
        state.user = null;
      });
  },
});

export const { logout, setUser } = authSlice.actions;
export default authSlice.reducer;
