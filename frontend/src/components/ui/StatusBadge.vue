<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ status: string }>();

const SUCCESS = new Set(["active", "fulfilled", "confirmed", "completed", "feasible"]);
const WARNING = new Set(["pending", "draft", "planned", "partially_fulfilled", "at_risk", "partially_feasible", "feasible_on_later_date"]);
const DANGER = new Set(["inactive", "cancelled", "delayed", "not_feasible", "locked", "suspended"]);
const INFO = new Set(["in_progress", "in_production", "shipped", "ready"]);

const variant = computed(() => {
  const s = props.status?.toLowerCase();
  if (SUCCESS.has(s)) return "success";
  if (WARNING.has(s)) return "warning";
  if (DANGER.has(s)) return "danger";
  if (INFO.has(s)) return "info";
  return "neutral";
});

const label = computed(() =>
  props.status ? props.status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) : "—"
);
</script>

<template>
  <span class="badge" :class="`badge-${variant}`">{{ label }}</span>
</template>
