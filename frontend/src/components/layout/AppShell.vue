<script setup lang="ts">
import Sidebar from "./Sidebar.vue";
import Topbar from "./Topbar.vue";
</script>

<template>
  <div class="shell">
    <Sidebar />
    <div class="shell-main">
      <Topbar />
      <main class="shell-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
}

.shell-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.shell-content {
  padding: var(--space-6);
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Smooth scrolling for better UX */
.shell-content {
  scroll-behavior: smooth;
}

/* Hide scrollbar in Firefox */
.shell-content {
  scrollbar-width: thin;
  scrollbar-color: var(--color-neutral-300) transparent;
}

/* Hide scrollbar in Chrome/Safari */
.shell-content::-webkit-scrollbar {
  width: 8px;
}

.shell-content::-webkit-scrollbar-track {
  background: transparent;
}

.shell-content::-webkit-scrollbar-thumb {
  background: var(--color-neutral-300);
  border-radius: 4px;
}

.shell-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-neutral-400);
}
</style>
