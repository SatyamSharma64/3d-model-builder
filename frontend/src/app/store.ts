import { configureStore } from "@reduxjs/toolkit";
import authReducer from "../features/auth/authSlice";
import projectReducer from "../features/projects/projectSlice";
import chatReducer from "../features/chat/chatSlice"
import websocketReducer from "../features/websocket/websocketSlice"
// import { websocketMiddleware } from "@/features/websocket/websocketMiddleware";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    projects: projectReducer,
    chat: chatReducer,
    websocket: websocketReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
