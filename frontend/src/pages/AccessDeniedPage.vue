<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();
</script>

<template>
  <div class="denied-page">
    <div class="card" style="max-width:420px; padding: var(--space-6); text-align:center;">
      <h1>Access denied</h1>
      <p class="muted text-sm" style="margin-top: var(--space-3)">
        You don't have permission to view this page. If you think this is a mistake,
        contact an administrator.
      </p>
      <button class="btn btn-primary" style="margin-top: var(--space-5)" @click="router.push('/')">
        Back to dashboard
      </button>
    </div>
  </div>
</template>

<style scoped>
.denied-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--color-neutral-50);
  padding: var(--space-4);
}
</style>
