<script setup lang="ts">
import { ref, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";
import { chatApi } from "../services/chat";
import { useAuthStore } from "../stores/auth";
import { useUiStore } from "../stores/ui";
import type { ChatMessage } from "../types";

const auth = useAuthStore();
const ui = useUiStore();
const router = useRouter();

const messages = ref<ChatMessage[]>([
  { role: "assistant", content: `Hi ${auth.fullName || ""}. Ask me about stock, open orders, or customers.` },
]);
const input = ref("");
const sending = ref(false);
const scrollEl = ref<HTMLElement | null>(null);

const quickPrompts = [
  "What's running low?",
  "Any orders due this week?",
  "What's our finished stock look like?",
];

async function scrollToBottom() {
  await nextTick();
  scrollEl.value?.scrollTo({ top: scrollEl.value.scrollHeight, behavior: "smooth" });
}

async function send(text?: string) {
  const message = (text ?? input.value).trim();
  if (!message || sending.value) return;

  messages.value.push({ role: "user", content: message });
  input.value = "";
  sending.value = true;
  scrollToBottom();

  try {
    const history = messages.value.slice(0, -1);
    const result = await chatApi.send(message, history);
    messages.value.push({ role: "assistant", content: result.reply });

    if (result.action && result.action.action === "navigate" && result.action.page) {
      router.push(`/${result.action.page}`);
    }
  } catch (e: any) {
    ui.toast(e.message || "The assistant didn't respond. Please try again.", "error");
    messages.value.push({ role: "assistant", content: "Sorry, something went wrong on my end." });
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}

onMounted(scrollToBottom);
</script>

<template>
  <div class="chat-page">
    <div class="page-header">
      <h1>AI Assistant</h1>
      <p>Ask about stock, orders, and customers in plain language</p>
    </div>

    <div class="card chat-card">
      <div ref="scrollEl" class="chat-body">
        <div v-for="(m, i) in messages" :key="i" class="bubble-row" :class="m.role">
          <div class="bubble" :class="m.role">{{ m.content }}</div>
        </div>
        <div v-if="sending" class="bubble-row assistant">
          <div class="bubble assistant typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="quick-prompts" v-if="messages.length <= 1">
        <button v-for="p in quickPrompts" :key="p" class="btn btn-secondary" @click="send(p)">{{ p }}</button>
      </div>

      <form class="chat-input" @submit.prevent="send()">
        <input
          v-model="input"
          type="text"
          placeholder="Ask something..."
          :disabled="sending"
          autocomplete="off"
        />
        <button type="submit" class="btn btn-primary" :disabled="sending || !input.trim()">Send</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.chat-page { display: flex; flex-direction: column; height: 100%; }
.chat-card { display: flex; flex-direction: column; flex: 1; padding: 0; overflow: hidden; }

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  min-height: 320px;
}

.bubble-row { display: flex; }
.bubble-row.user { justify-content: flex-end; }
.bubble-row.assistant { justify-content: flex-start; }

.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  white-space: pre-wrap;
  line-height: 1.5;
}
.bubble.user { background: var(--color-primary-500); color: white; border-bottom-right-radius: 2px; }
.bubble.assistant { background: var(--color-neutral-100); color: var(--color-neutral-900); border-bottom-left-radius: 2px; }

.bubble.typing { display: flex; gap: 4px; padding: 14px; }
.bubble.typing span {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--color-neutral-400);
  animation: pulse 1.2s infinite ease-in-out;
}
.bubble.typing span:nth-child(2) { animation-delay: 0.15s; }
.bubble.typing span:nth-child(3) { animation-delay: 0.3s; }
@keyframes pulse { 0%, 80%, 100% { opacity: 0.3; } 40% { opacity: 1; } }

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  padding: 0 var(--space-5) var(--space-4);
}

.chat-input {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-neutral-200);
}
.chat-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}
.chat-input input:focus { outline: none; border-color: var(--color-primary-500); }
</style>
