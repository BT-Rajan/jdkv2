<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { apiFetch, ApiError } from "../../services/api";

const route = useRoute();
const router = useRouter();
const token = (route.query.token as string) || "";

const password = ref("");
const confirmPassword = ref("");
const error = ref<string | null>(null);
const submitting = ref(false);
const done = ref(false);

async function handleSubmit() {
  error.value = null;
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords don't match.";
    return;
  }
  submitting.value = true;
  try {
    const qs = new URLSearchParams({ token, new_password: password.value }).toString();
    await apiFetch(`/api/auth/reset-password?${qs}`, { method: "POST", auth: false });
    done.value = true;
    setTimeout(() => router.push("/login"), 2000);
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : "Something went wrong.";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Set a new password</h1>
      <p v-if="!token" class="field-error" style="margin-top: var(--space-3)">
        This link is missing its reset token. Please use the link from your email.
      </p>
      <template v-else-if="!done">
        <div v-if="error" class="field-error" style="margin: var(--space-3) 0">{{ error }}</div>
        <form @submit.prevent="handleSubmit" style="margin-top: var(--space-4)">
          <div class="field" style="text-align:left">
            <label for="password">New password</label>
            <input id="password" v-model="password" type="password" class="input" required autofocus />
          </div>
          <div class="field" style="text-align:left">
            <label for="confirm">Confirm new password</label>
            <input id="confirm" v-model="confirmPassword" type="password" class="input" required />
          </div>
          <button class="btn btn-primary" type="submit" :disabled="submitting" style="width:100%; justify-content:center">
            {{ submitting ? "Saving…" : "Save new password" }}
          </button>
        </form>
      </template>
      <p v-else class="text-sm" style="margin-top: var(--space-3)">Password updated. Redirecting to sign in…</p>
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
