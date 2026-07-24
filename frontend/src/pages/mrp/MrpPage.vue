<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { mrpApi } from "../../services/mrp";
import { useUiStore } from "../../stores/ui";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import type { MrpSnapshot } from "../../types";

const router = useRouter();
const ui = useUiStore();
const loading = ref(true);
const snapshot = ref<MrpSnapshot | null>(null);
const expandedMaterial = ref<number | null>(null);

async function load() {
  loading.value = true;
  try {
    snapshot.value = await mrpApi.calculate();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't calculate MRP.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>MRP & ATP</h1>
        <p>Material requirements calculated from every open order</p>
      </div>
      <button class="btn btn-secondary" @click="load" :disabled="loading">Recalculate</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="snapshot" class="stack">
      <div class="card" :class="{ 'shortage-banner': snapshot.has_shortages }">
        <div class="card-body row">
          <strong v-if="snapshot.has_shortages">⚠ Material shortages detected below.</strong>
          <strong v-else>✓ All required materials are covered by current stock.</strong>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>Material requirements</h3></div>
        <div class="card-body" style="padding:0">
          <table class="data-table">
            <thead>
              <tr>
                <th>Material</th><th class="numeric">Gross required</th><th class="numeric">Current stock</th>
                <th class="numeric">Net required</th><th>Suggested supplier</th><th>Est. supply date</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="m in snapshot.material_requirements" :key="m.material_id">
                <tr @click="expandedMaterial = expandedMaterial === m.material_id ? null : m.material_id" :class="{ shortage: m.shortage }">
                  <td>{{ m.material_name }}</td>
                  <td class="numeric">{{ m.gross_required.toFixed(1) }} {{ m.unit }}</td>
                  <td class="numeric">{{ m.current_stock.toFixed(1) }} {{ m.unit }}</td>
                  <td class="numeric">{{ m.net_required.toFixed(1) }} {{ m.unit }}</td>
                  <td>
                    <span v-if="m.suggested_supplier">
                      {{ m.suggested_supplier.supplier_name }} · ₹{{ m.suggested_supplier.price }} · {{ m.suggested_supplier.lead_time_days }}d
                      <span class="text-xs muted">(projected)</span>
                    </span>
                    <span v-else class="muted">—</span>
                  </td>
                  <td>{{ m.estimated_supply_date || "—" }}</td>
                </tr>
                <tr v-if="expandedMaterial === m.material_id" style="cursor:default">
                  <td colspan="6" style="background: var(--color-neutral-50)">
                    <div class="text-sm" style="padding: var(--space-2) 0">
                      <strong>Driven by:</strong>
                      <span
                        v-for="pid in m.affected_product_ids" :key="pid"
                        class="badge badge-info" style="margin-left: 6px; cursor:pointer"
                        @click.stop="router.push(`/products/${pid}`)"
                      >
                        {{ snapshot.production_requirements.find(p => p.product_id === pid)?.product_name || pid }}
                      </span>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>Production requirements</h3></div>
        <div class="card-body" style="padding:0">
          <table class="data-table">
            <thead><tr><th>Product</th><th class="numeric">Total ordered</th><th class="numeric">Finished goods</th><th class="numeric">Production required</th><th>Contributing orders</th></tr></thead>
            <tbody>
              <tr v-for="p in snapshot.production_requirements" :key="p.product_id" @click="router.push(`/products/${p.product_id}`)">
                <td>{{ p.product_name }}</td>
                <td class="numeric">{{ p.total_ordered_kg.toFixed(1) }} kg</td>
                <td class="numeric">{{ p.finished_goods_kg.toFixed(1) }} kg</td>
                <td class="numeric">{{ p.production_required_kg.toFixed(1) }} kg</td>
                <td class="text-sm">{{ p.contributing_orders.length }} order(s)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shortage-banner { border-color: var(--color-warning-500); background: var(--color-warning-50); }
tr.shortage td:first-child { border-left: 3px solid var(--color-danger-500); }
</style>
