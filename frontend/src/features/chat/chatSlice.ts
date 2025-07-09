import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

interface ChatMessage {
  sender: "user" | "ai" | "system";
  content: string;
  timestamp?: string;
}

interface ChatSession {
  messages: ChatMessage[];
  loading: boolean;
}

interface ChatState {
  chats: {
    [projectId: string]: ChatSession;
  };
  activeProjectId: string | null;
}

const initialState: ChatState = {
  chats: {},
  activeProjectId: null,
};

export const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    setActiveProjectId: (state, action: PayloadAction<string>) =>{
      state.activeProjectId = action.payload;
      if(!state.chats[action.payload]){
        state.chats[action.payload] = { messages: [], loading: false};
      }
    },
    sendMessage: (state, action: PayloadAction<{ projectId: string, content: string}>) => {
      const { projectId, content } = action.payload;
      const chat = state.chats[projectId] || { messages: [], loading: false };

      chat.messages.push({ sender: "user", content, timestamp: new Date().toISOString() });
      chat.loading = true;
      state.chats[projectId] = chat;
    },
    receiveMessage: (state, action: PayloadAction<{ projectId: string, message: ChatMessage}>) => {
      const { projectId, message } = action.payload;
      const chat = state.chats[projectId] || { messages: [], loading: false };
      chat.messages.push({ ...message, timestamp: message.timestamp || new Date().toISOString() });
      chat.loading = false;
      state.chats[projectId] = chat;
    },
    resetChat: (state, action: PayloadAction<string>) => {
      delete state.chats[action.payload];
    },
  },
});

export const { setActiveProjectId, sendMessage, receiveMessage, resetChat } = chatSlice.actions;
export default chatSlice.reducer;
