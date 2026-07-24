<template>
  <div class="row" style="justify-content:center; padding: var(--space-6) 0;">
    <div class="spinner" aria-label="Loading" role="status"></div>
  </div>
</template>

<style scoped>
.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
