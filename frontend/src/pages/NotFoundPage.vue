<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();
</script>

<template>
  <div class="notfound-page">
    <div class="card" style="max-width:420px; padding: var(--space-6); text-align:center;">
      <h1>Page not found</h1>
      <p class="muted text-sm" style="margin-top: var(--space-3)">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <button class="btn btn-primary" style="margin-top: var(--space-5)" @click="router.push('/')">
        Back to dashboard
      </button>
    </div>
  </div>
</template>

<style scoped>
.notfound-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--color-neutral-50);
  padding: var(--space-4);
}
</style>
