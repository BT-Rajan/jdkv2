<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { apiFetch, ApiError } from "../../services/api";

const route = useRoute();
const status = ref<"working" | "success" | "error">("working");
const message = ref("");

onMounted(async () => {
  const token = route.query.token as string;
  if (!token) {
    status.value = "error";
    message.value = "This link is missing its verification token.";
    return;
  }
  try {
    await apiFetch(`/api/auth/verify-email?${new URLSearchParams({ token }).toString()}`, { method: "POST", auth: false });
    status.value = "success";
  } catch (e) {
    status.value = "error";
    message.value = e instanceof ApiError ? e.message : "Something went wrong.";
  }
});
</script>

<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Email verification</h1>
      <p v-if="status === 'working'" class="text-sm muted" style="margin-top: var(--space-3)">Verifying…</p>
      <p v-else-if="status === 'success'" class="text-sm" style="margin-top: var(--space-3)">
        Your email is verified. You can now sign in.
      </p>
      <p v-else class="field-error" style="margin-top: var(--space-3)">{{ message }}</p>
      <div class="row" style="justify-content:center; margin-top: var(--space-4)">
        <router-link to="/login" class="text-sm">Back to sign in</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(160deg, var(--color-neutral-900), var(--color-primary-700));
  padding: var(--space-4);
}
.auth-card { width: 100%; max-width: 380px; padding: var(--space-6); text-align: center; }
</style>
