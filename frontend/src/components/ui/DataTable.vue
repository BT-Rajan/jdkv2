<script setup lang="ts" generic="T extends Record<string, any>">
import LoadingSpinner from "./LoadingSpinner.vue";

export interface Column<T> {
  key: string;
  label: string;
  numeric?: boolean;
  render?: (row: T) => string;
}

const props = defineProps<{
  columns: Column<T>[];
  rows: T[];
  loading?: boolean;
  emptyMessage?: string;
  total?: number;
  limit?: number;
  offset?: number;
}>();

const emit = defineEmits<{ "row-click": [row: T]; "page-change": [offset: number] }>();

function cell(row: T, col: Column<T>): string {
  if (col.render) return col.render(row);
  const value = row[col.key];
  return value === null || value === undefined ? "—" : String(value);
}

function nextPage() {
  const limit = props.limit ?? 20;
  emit("page-change", (props.offset ?? 0) + limit);
}
function prevPage() {
  const limit = props.limit ?? 20;
  emit("page-change", Math.max(0, (props.offset ?? 0) - limit));
}
</script>

<template>
  <div>
    <div v-if="loading"><LoadingSpinner /></div>

    <div v-else-if="!rows.length" class="empty-state">
      {{ emptyMessage || "Nothing here yet." }}
    </div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" :class="{ numeric: col.numeric }">{{ col.label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="row.id ?? row.subject_id ?? i" @click="emit('row-click', row)">
          <td v-for="col in columns" :key="col.key" :class="{ numeric: col.numeric }">
            {{ cell(row, col) }}
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && total !== undefined && total > (limit ?? 20)" class="row-between" style="margin-top: var(--space-4);">
      <span class="text-sm muted">
        Showing {{ (offset ?? 0) + 1 }}–{{ Math.min((offset ?? 0) + (limit ?? 20), total) }} of {{ total }}
      </span>
      <div class="row">
        <button class="btn btn-secondary btn-sm" :disabled="(offset ?? 0) === 0" @click="prevPage">Previous</button>
        <button class="btn btn-secondary btn-sm" :disabled="(offset ?? 0) + (limit ?? 20) >= total" @click="nextPage">Next</button>
      </div>
    </div>
  </div>
</template>
