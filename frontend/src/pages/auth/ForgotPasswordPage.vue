<script setup lang="ts">
import { ref } from "vue";
import { apiFetch } from "../../services/api";

const email = ref("");
const submitted = ref(false);
const submitting = ref(false);

async function handleSubmit() {
  submitting.value = true;
  try {
    await apiFetch(`/api/auth/forgot-password?email=${encodeURIComponent(email.value.trim())}`, { method: "POST", auth: false });
  } finally {
    // Deliberately always show the same confirmation regardless of outcome -
    // the backend never reveals whether an account exists, and neither do we.
    submitted.value = true;
    submitting.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Reset your password</h1>
      <template v-if="!submitted">
        <p class="muted text-sm" style="margin: var(--space-2) 0 var(--space-5)">
          Enter your email and we'll send you a reset link if an account exists.
        </p>
        <form @submit.prevent="handleSubmit">
          <div class="field" style="text-align:left">
            <label for="email">Email</label>
            <input id="email" v-model="email" type="email" class="input" required autofocus />
          </div>
          <button class="btn btn-primary" type="submit" :disabled="submitting" style="width:100%; justify-content:center">
            {{ submitting ? "Sending…" : "Send reset link" }}
          </button>
        </form>
      </template>
      <p v-else class="text-sm" style="margin-top: var(--space-3)">
        If an account exists for that address, a reset link is on its way.
      </p>
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
