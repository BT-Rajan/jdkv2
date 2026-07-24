<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const menuOpen = ref(false);

async function handleLogout() {
  await auth.logout();
  router.push("/login");
}
</script>

<template>
  <header class="topbar">
    <div class="spacer" />
    <div class="user-menu">
      <button class="user-trigger" @click="menuOpen = !menuOpen" @blur="menuOpen = false">
        <span class="avatar">{{ (auth.fullName || auth.email || "?").charAt(0).toUpperCase() }}</span>
        <span class="user-name">{{ auth.fullName || auth.email }}</span>
        <span class="chevron">▾</span>
      </button>
      <div v-if="menuOpen" class="dropdown" @mousedown.prevent>
        <div class="dropdown-header">
          <div class="text-sm" style="font-weight:600">{{ auth.fullName || auth.email }}</div>
          <div class="text-xs muted">{{ auth.roles.join(", ") }}</div>
        </div>
        <button class="dropdown-item" @click="handleLogout">Sign out</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  padding: 0 var(--space-5);
  background: var(--color-neutral-0);
  border-bottom: 1px solid var(--color-neutral-200);
  position: sticky;
  top: 0;
  z-index: 10;
}
.spacer { flex: 1; }
.user-menu { position: relative; }
.user-trigger {
  display: flex; align-items: center; gap: var(--space-2);
  background: none; border: none; cursor: pointer;
  padding: 6px 8px; border-radius: var(--radius-sm);
}
.user-trigger:hover { background: var(--color-neutral-100); }
.avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--color-primary-500); color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--text-xs); font-weight: 700;
}
.user-name { font-size: var(--text-sm); font-weight: 500; color: var(--color-neutral-700); }
.chevron { color: var(--color-neutral-400); font-size: var(--text-xs); }

.dropdown {
  position: absolute; right: 0; top: calc(100% + 6px);
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 200px;
  overflow: hidden;
}
.dropdown-header { padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--color-neutral-100); }
.dropdown-item {
  display: block; width: 100%; text-align: left;
  padding: var(--space-3) var(--space-4);
  background: none; border: none; cursor: pointer;
  font-size: var(--text-sm);
}
.dropdown-item:hover { background: var(--color-neutral-50); }
</style>
