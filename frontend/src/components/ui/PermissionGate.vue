<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "../../stores/auth";

const props = defineProps<{
  permission?: string;
  anyOf?: string[];
}>();

const auth = useAuthStore();

const allowed = computed(() => {
  if (props.anyOf && props.anyOf.length) return auth.hasAnyPermission(props.anyOf);
  if (props.permission) return auth.hasPermission(props.permission);
  return true;
});
</script>

<template>
  <template v-if="allowed"><slot /></template>
</template>
