<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { ordersApi } from "../../services/orders";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { SALES_ACCESS } from "../../permissions";
import { ORDER_STATUSES } from "../../types";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import type { Order } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Order[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const statusFilter = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Order>[] = [
  { key: "order_no", label: "Order" },
  { key: "customer_name", label: "Customer" },
  { key: "product_name", label: "Product" },
  { key: "quantity_kg", label: "Qty (kg)", numeric: true },
  { key: "order_date", label: "Order date" },
  { key: "delivery_date", label: "Delivery" },
  { key: "priority", label: "Priority" },
];

async function load() {
  loading.value = true;
  try {
    const result = await ordersApi.search({ q: search.value || undefined, status: statusFilter.value || undefined, limit, offset: offset.value });
    rows.value = result.orders;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load orders.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch([search, statusFilter], () => { offset.value = 0; load(); });
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Orders</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(SALES_ACCESS)" class="btn btn-primary" @click="router.push('/quotations')">
        + New order (via quotation)
      </button>
    </div>

    <p class="text-sm muted" style="margin-top:-8px; margin-bottom: var(--space-4)">
      Orders are only created by converting an accepted quotation. Start from
      <a href="#" @click.prevent="router.push('/feasibility')">Feasibility</a> or
      <a href="#" @click.prevent="router.push('/quotations')">Quotations</a>.
    </p>

    <div class="card">
      <div class="card-header row">
        <input v-model="search" class="input" placeholder="Search order #, customer, product…" style="max-width:280px" />
        <select v-model="statusFilter" class="input" style="max-width:200px">
          <option value="">All statuses</option>
          <option v-for="s in ORDER_STATUSES" :key="s" :value="s">{{ s.replace(/_/g, " ") }}</option>
        </select>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No orders found."
          @row-click="(r) => router.push(`/orders/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        >
        </DataTable>
      </div>
    </div>
  </div>
</template>
