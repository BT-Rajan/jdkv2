<script setup lang="ts">
import { useAuthStore } from "./stores/auth";
import ToastContainer from "./components/ui/ToastContainer.vue";

// auth.ready is guaranteed true by mount time: the router's beforeEach guard
// awaits auth.initialize() on the very first navigation, and main.ts waits
// for router.isReady() before mounting this component. The v-else branch
// below is just a safety net in case that ever changes.
const auth = useAuthStore();
</script>

<template>
  <router-view v-if="auth.ready" />
  <div v-else class="boot-screen">
    <div class="boot-mark">J</div>
  </div>
  <ToastContainer />
</template>

<style scoped>
.boot-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-neutral-50);
}
.boot-mark {
  width: 48px; height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-primary-500);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.5rem;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
