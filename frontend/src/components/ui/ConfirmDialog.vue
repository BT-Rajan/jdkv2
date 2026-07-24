<script setup lang="ts">
import Modal from "./Modal.vue";

defineProps<{
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  busy?: boolean;
}>();
const emit = defineEmits<{ confirm: []; cancel: [] }>();
</script>

<template>
  <Modal :title="title" @close="emit('cancel')">
    <p>{{ message }}</p>
    <template #footer>
      <button class="btn btn-secondary" @click="emit('cancel')" :disabled="busy">Cancel</button>
      <button :class="danger ? 'btn btn-danger' : 'btn btn-primary'" @click="emit('confirm')" :disabled="busy">
        {{ busy ? "Working…" : (confirmLabel || "Confirm") }}
      </button>
    </template>
  </Modal>
</template>
