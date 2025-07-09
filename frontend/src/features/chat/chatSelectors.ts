import type { RootState } from "@/app/store";

export const selectMessagesForProject = (state: RootState, projectId: string) =>
  state.chat.chats[projectId]?.messages || [];

export const selectLoadingForProject = (state: RootState, projectId: string) =>
  state.chat.chats[projectId]?.loading || false;
