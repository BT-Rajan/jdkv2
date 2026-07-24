<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { dashboardApi } from "../services/mrp";
import { useUiStore } from "../stores/ui";
import LoadingSpinner from "../components/ui/LoadingSpinner.vue";
import StatusBadge from "../components/ui/StatusBadge.vue";
import type { DashboardSummary } from "../types";

const ui = useUiStore();
const router = useRouter();
const loading = ref(true);
const summary = ref<DashboardSummary | null>(null);

async function load() {
  loading.value = true;
  try {
    summary.value = await dashboardApi.summary();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load the dashboard.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>What needs attention today</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="summary" class="stack">
      <div class="stat-grid">
        <div class="card stat-card">
          <div class="stat-value">{{ summary.open_order_count }}</div>
          <div class="stat-label">Open orders</div>
        </div>
        <div class="card stat-card">
          <div class="stat-value">{{ summary.products_with_open_demand }}</div>
          <div class="stat-label">Products with open demand</div>
        </div>
        <div class="card stat-card" :class="{ alert: summary.low_stock_material_count > 0 }">
          <div class="stat-value">{{ summary.low_stock_material_count }}</div>
          <div class="stat-label">Low-stock materials</div>
        </div>
        <div class="card stat-card" :class="{ alert: summary.material_shortage_count > 0 }">
          <div class="stat-value">{{ summary.material_shortage_count }}</div>
          <div class="stat-label">Material shortages</div>
        </div>
        <div class="card stat-card" :class="{ alert: summary.orders_needing_attention_count > 0 }">
          <div class="stat-value">{{ summary.orders_needing_attention_count }}</div>
          <div class="stat-label">Orders needing attention</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>Orders needing attention</h3></div>
        <div class="card-body">
          <div v-if="!summary.orders_needing_attention.length" class="empty-state">Nothing at risk right now.</div>
          <table v-else class="data-table">
            <thead><tr><th>Order</th><th>Outcome</th><th>Required date</th><th>Estimated date</th></tr></thead>
            <tbody>
              <tr v-for="o in summary.orders_needing_attention" :key="o.order_id" @click="router.push(`/orders/${o.order_id}`)">
                <td>{{ o.order_no }}</td>
                <td><StatusBadge :status="o.outcome" /></td>
                <td>{{ o.required_date || "—" }}</td>
                <td>{{ o.estimated_fulfillment_date }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>Top material shortages</h3></div>
        <div class="card-body">
          <div v-if="!summary.top_material_shortages.length" class="empty-state">No shortages right now.</div>
          <table v-else class="data-table">
            <thead><tr><th>Material</th><th class="numeric">Net required</th><th>Suggested supplier</th></tr></thead>
            <tbody>
              <tr v-for="m in summary.top_material_shortages" :key="m.material_id" @click="router.push(`/materials/${m.material_id}`)">
                <td>{{ m.material_name }}</td>
                <td class="numeric">{{ m.net_required.toFixed(1) }} {{ m.unit }}</td>
                <td>
                  <span v-if="m.suggested_supplier">
                    {{ m.suggested_supplier.supplier_name }} · {{ m.suggested_supplier.lead_time_days }}d lead
                  </span>
                  <span v-else class="muted">No active supplier</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>Low-stock materials</h3></div>
        <div class="card-body">
          <div v-if="!summary.low_stock_materials.length" class="empty-state">All materials are above their reorder point.</div>
          <table v-else class="data-table">
            <thead><tr><th>Material</th><th class="numeric">Current stock</th><th class="numeric">Reorder point</th></tr></thead>
            <tbody>
              <tr v-for="m in summary.low_stock_materials" :key="m.id" @click="router.push(`/materials/${m.id}`)">
                <td>{{ m.name }}</td>
                <td class="numeric">{{ m.current_stock }} {{ m.unit }}</td>
                <td class="numeric">{{ m.reorder_point }} {{ m.unit }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-4);
}
.stat-card { padding: var(--space-5); text-align: center; }
.stat-card.alert { border-color: var(--color-danger-500); background: var(--color-danger-50); }
.stat-value { font-size: 2rem; font-weight: 700; color: var(--color-neutral-900); }
.stat-label { font-size: var(--text-sm); color: var(--color-neutral-500); margin-top: var(--space-1); }
</style>
