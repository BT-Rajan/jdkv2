<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { materialsApi } from "../../services/materials";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { INVENTORY_ADJUST } from "../../permissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Material } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = Number(route.params.id);
const material = ref<Material | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    material.value = await materialsApi.get(id);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load material.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

const showReorder = ref(false);
const reorderForm = reactive({ minimum_stock: 0, reorder_point: 0, lead_time_days: 0 });
function openReorder() {
  if (!material.value) return;
  Object.assign(reorderForm, {
    minimum_stock: material.value.minimum_stock,
    reorder_point: material.value.reorder_point,
    lead_time_days: material.value.lead_time_days,
  });
  showReorder.value = true;
}
const savingReorder = ref(false);
async function submitReorder() {
  savingReorder.value = true;
  try {
    material.value = await materialsApi.setReorderConfig(id, reorderForm);
    ui.toast("Reorder configuration updated.", "success");
    showReorder.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update reorder configuration.", "error");
  } finally {
    savingReorder.value = false;
  }
}

const showMovement = ref(false);
const movementForm = reactive({ movement_type: "receipt", quantity: 0, reference: "" });
const savingMovement = ref(false);
async function submitMovement() {
  savingMovement.value = true;
  try {
    material.value = await materialsApi.recordMovement(id, movementForm);
    ui.toast("Movement recorded.", "success");
    showMovement.value = false;
    movementForm.quantity = 0; movementForm.reference = "";
  } catch (e: any) {
    ui.toast(e.message || "Couldn't record movement.", "error");
  } finally {
    savingMovement.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="material" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/materials')">← Materials</button>
        <h1 style="margin-top:8px">{{ material.name }}</h1>
      </div>
      <div class="row" v-if="auth.hasPermission(INVENTORY_ADJUST)">
        <button class="btn btn-secondary" @click="openReorder">Reorder config</button>
        <button class="btn btn-primary" @click="showMovement = true">Record movement</button>
      </div>
    </div>

    <div class="stat-row">
      <div class="card stat-card" :class="{ alert: material.current_stock <= material.reorder_point }">
        <div class="stat-value">{{ material.current_stock }} {{ material.unit }}</div>
        <div class="stat-label">Current stock</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ material.reorder_point }} {{ material.unit }}</div>
        <div class="stat-label">Reorder point</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ material.lead_time_days }}d</div>
        <div class="stat-label">Lead time</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Used in products</h3></div>
      <div class="card-body">
        <div v-if="!material.used_by_products?.length" class="empty-state">Not used in any active formula.</div>
        <div v-else class="row" style="flex-wrap:wrap; gap: var(--space-2)">
          <span v-for="p in material.used_by_products" :key="p.id" class="badge badge-info" style="cursor:pointer" @click="router.push(`/products/${p.id}`)">
            {{ p.name }}
          </span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Recent movements</h3></div>
      <div class="card-body" style="padding:0">
        <div v-if="!material.recent_movements?.length" class="empty-state">No movements recorded yet.</div>
        <table v-else class="data-table">
          <thead><tr><th>Type</th><th class="numeric">Quantity</th><th>Reference</th><th>Date</th></tr></thead>
          <tbody>
            <tr v-for="m in material.recent_movements" :key="m.id" style="cursor:default">
              <td>{{ m.movement_type }}</td>
              <td class="numeric">{{ m.quantity }} {{ material.unit }}</td>
              <td>{{ m.reference || "—" }}</td>
              <td class="text-sm muted">{{ new Date(m.created_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal v-if="showReorder" title="Reorder configuration" @close="showReorder = false">
      <div class="field"><label>Minimum stock</label><input v-model.number="reorderForm.minimum_stock" type="number" class="input" /></div>
      <div class="field"><label>Reorder point</label><input v-model.number="reorderForm.reorder_point" type="number" class="input" /></div>
      <div class="field"><label>Lead time (days)</label><input v-model.number="reorderForm.lead_time_days" type="number" class="input" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showReorder = false">Cancel</button>
        <button class="btn btn-primary" :disabled="savingReorder" @click="submitReorder">
          {{ savingReorder ? "Saving…" : "Save" }}
        </button>
      </template>
    </Modal>

    <Modal v-if="showMovement" title="Record inventory movement" @close="showMovement = false">
      <div class="field">
        <label>Type</label>
        <select v-model="movementForm.movement_type" class="input">
          <option value="receipt">Receipt (stock in)</option>
          <option value="consumption">Consumption (stock out)</option>
          <option value="adjustment">Adjustment (+/-)</option>
        </select>
      </div>
      <div class="field">
        <label>Quantity ({{ material.unit }})</label>
        <input v-model.number="movementForm.quantity" type="number" class="input" />
        <span v-if="movementForm.movement_type === 'adjustment'" class="field-hint">Use a negative number to reduce stock.</span>
      </div>
      <div class="field"><label>Reference</label><input v-model="movementForm.reference" class="input" placeholder="PO number, batch, etc." /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showMovement = false">Cancel</button>
        <button class="btn btn-primary" :disabled="savingMovement" @click="submitMovement">
          {{ savingMovement ? "Recording…" : "Record" }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<style scoped>
.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: var(--space-4); }
.stat-card { padding: var(--space-5); text-align: center; }
.stat-card.alert { border-color: var(--color-danger-500); background: var(--color-danger-50); }
.stat-value { font-size: 1.75rem; font-weight: 700; }
.stat-label { font-size: var(--text-sm); color: var(--color-neutral-500); margin-top: 4px; }
</style>
