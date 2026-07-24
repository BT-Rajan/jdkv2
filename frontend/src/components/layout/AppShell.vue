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
.shell { display: flex; min-height: 100vh; }
.shell-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.shell-content { padding: var(--space-6); flex: 1; }
</style>
