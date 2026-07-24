<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../../stores/auth";
import { config } from "../../config";
import { ApiError } from "../../services/api";

const email = ref("");
const password = ref("");
const error = ref<string | null>(null);
const submitting = ref(false);

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

async function handleSubmit() {
  error.value = null;
  submitting.value = true;
  try {
    await auth.login(email.value.trim(), password.value);
    const redirect = (route.query.redirect as string) || "/";
    router.push(redirect);
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : "Something went wrong. Please try again.";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <form class="card auth-card" @submit.prevent="handleSubmit" autocomplete="on">
      <div class="brand-mark">J</div>
      <h1>{{ config.appName }}</h1>
      <p class="muted text-sm" style="margin-bottom: var(--space-5)">Sign in to your account</p>

      <div v-if="error" class="field-error" style="margin-bottom: var(--space-4)">{{ error }}</div>

      <div class="field">
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" class="input" required autocomplete="username" autofocus />
      </div>
      <div class="field">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" class="input" required autocomplete="current-password" />
      </div>

      <button class="btn btn-primary" type="submit" :disabled="submitting" style="width:100%; justify-content:center; margin-top: var(--space-2)">
        {{ submitting ? "Signing in…" : "Sign in" }}
      </button>

      <div class="row" style="justify-content:center; margin-top: var(--space-4)">
        <router-link to="/forgot-password" class="text-sm">Forgot your password?</router-link>
      </div>
    </form>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, var(--color-neutral-900), var(--color-primary-700));
  padding: var(--space-4);
}
.auth-card {
  width: 100%;
  max-width: 380px;
  padding: var(--space-6);
  text-align: center;
}
.brand-mark {
  width: 44px; height: 44px;
  border-radius: var(--radius-md);
  background: var(--color-primary-500);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.25rem;
  margin: 0 auto var(--space-4);
}
.auth-card .field { text-align: left; }
</style>
