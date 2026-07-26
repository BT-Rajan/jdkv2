import { apiFetch } from "./api";
import type { ChatMessage, ChatReply } from "../types";

export const chatApi = {
  send: (message: string, history: ChatMessage[]) =>
    apiFetch<ChatReply>("/api/chat", {
      method: "POST",
      body: { message, history },
    }),
};
