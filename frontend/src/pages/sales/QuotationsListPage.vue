<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { quotationsApi } from "../../services/quotations";
import { useUiStore } from "../../stores/ui";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import type { Quotation } from "../../types";

const router = useRouter();
const ui = useUiStore();

const rows = ref<Quotation[]>([]);
const total = ref(0);
const loading = ref(true);
const statusFilter = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Quotation>[] = [
  { key: "quote_no", label: "Quote #" },
  { key: "customer_name", label: "Customer" },
  { key: "product_name", label: "Product" },
  { key: "quantity_kg", label: "Qty (kg)", numeric: true },
  { key: "total_amount", label: "Total", numeric: true },
  { key: "quote_date", label: "Quote date" },
  { key: "requested_delivery_date", label: "Requested delivery" },
];

async function load() {
  loading.value = true;
  try {
    const result = await quotationsApi.search({ status: statusFilter.value || undefined, limit, offset: offset.value });
    rows.value = result.quotations;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load quotations.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(statusFilter, () => { offset.value = 0; load(); });
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Quotations</h1>
        <p>{{ total }} total · stage 2 of Order: feasibility → quotation → order → delivery</p>
      </div>
      <button class="btn btn-secondary" @click="router.push('/feasibility')">Run a feasibility check</button>
    </div>

    <div class="card">
      <div class="card-header row">
        <select v-model="statusFilter" class="input" style="max-width:200px">
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="expired">Expired</option>
          <option value="converted">Converted</option>
        </select>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No quotations yet — generate one from a passing feasibility check."
          @row-click="(r) => router.push(`/quotations/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        >
          <template #actions="{ row }: { row: Quotation }">
            <StatusBadge :status="row.status" />
          </template>
        </DataTable>
      </div>
    </div>
  </div>
</template>
