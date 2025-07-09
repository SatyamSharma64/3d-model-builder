import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface WebSocketState {
  connected: boolean;
  error: string | null;
}

const initialState: WebSocketState = {
  connected: false,
  error: null,
};

const websocketSlice = createSlice({
  name: "websocket",
  initialState,
  reducers: {
    connectionOpened: (state) => {
      state.connected = true;
      state.error = null;
    },
    connectionClosed: (state) => {
      state.connected = false;
    },
    connectionError: (state, action: PayloadAction<string>) => {
      state.connected = false;
      state.error = action.payload;
    },
    messageReceived: (state, action: PayloadAction<any>) => {
      // Message is passed to middleware or component-level selectors
    },
  },
});

export const {
  connectionOpened,
  connectionClosed,
  connectionError,
  messageReceived,
} = websocketSlice.actions;

export default websocketSlice.reducer;
