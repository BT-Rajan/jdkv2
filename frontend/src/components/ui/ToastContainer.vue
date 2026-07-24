<script setup lang="ts">
import { useUiStore } from "../../stores/ui";

const ui = useUiStore();
</script>

<template>
  <div class="toast-container" aria-live="polite">
    <div
      v-for="t in ui.toasts"
      :key="t.id"
      class="toast"
      :class="`toast-${t.kind}`"
      @click="ui.dismiss(t.id)"
    >
      {{ t.message }}
    </div>
  </div>
</template>
