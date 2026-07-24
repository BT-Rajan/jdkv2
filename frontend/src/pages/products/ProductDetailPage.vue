<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { productsApi } from "../../services/products";
import { materialsApi } from "../../services/materials";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { PRODUCTS_MANAGE } from "../../permissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import Modal from "../../components/ui/Modal.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import AttachmentsPanel from "../../components/AttachmentsPanel.vue";
import type { Product, Material } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = Number(route.params.id);
const product = ref<Product | null>(null);
const loading = ref(true);
const allMaterials = ref<Material[]>([]);

async function load() {
  loading.value = true;
  try {
    const [p, m] = await Promise.all([productsApi.get(id), materialsApi.search({ limit: 100 })]);
    product.value = p;
    allMaterials.value = m.materials;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load product.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

async function toggleStatus() {
  if (!product.value) return;
  const next = product.value.status === "active" ? "discontinued" : "active";
  try {
    product.value = await productsApi.setStatus(id, next);
    ui.toast(`Product marked ${next}.`, "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update status.", "error");
  }
}

const showFormula = ref(false);
const formulaForm = reactive({
  effective_from: new Date().toISOString().slice(0, 10),
  lines: [{ material_id: 0, quantity_per_unit: 0 }],
});
function addLine() { formulaForm.lines.push({ material_id: 0, quantity_per_unit: 0 }); }
function removeLine(i: number) { formulaForm.lines.splice(i, 1); }
const savingFormula = ref(false);
async function submitFormula() {
  savingFormula.value = true;
  try {
    product.value = await productsApi.createFormulaVersion(id, {
      effective_from: formulaForm.effective_from,
      lines: formulaForm.lines.filter((l) => l.material_id > 0),
    });
    ui.toast("New formula version created.", "success");
    showFormula.value = false;
    formulaForm.lines = [{ material_id: 0, quantity_per_unit: 0 }];
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create formula version.", "error");
  } finally {
    savingFormula.value = false;
  }
}

const movementDelta = ref<number>(0);
const recordingMovement = ref(false);
async function recordFinishedGoods() {
  if (!movementDelta.value) return;
  recordingMovement.value = true;
  try {
    await productsApi.recordFinishedGoodsMovement(id, movementDelta.value);
    ui.toast("Finished goods updated.", "success");
    movementDelta.value = 0;
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update finished goods.", "error");
  } finally {
    recordingMovement.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="product" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/products')">← Products</button>
        <h1 style="margin-top:8px">{{ product.name }}</h1>
        <div class="row" style="margin-top:6px"><StatusBadge :status="product.status" /></div>
      </div>
      <div class="row" v-if="auth.hasPermission(PRODUCTS_MANAGE)">
        <button class="btn btn-secondary" @click="toggleStatus">
          {{ product.status === "active" ? "Discontinue" : "Reactivate" }}
        </button>
        <button class="btn btn-primary" @click="showFormula = true">New formula version</button>
      </div>
    </div>

    <div class="stat-row">
      <div class="card stat-card">
        <div class="stat-value">{{ product.finished_goods?.available_kg ?? 0 }} kg</div>
        <div class="stat-label">Finished goods available</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ product.finished_goods?.available_bags ?? 0 }}</div>
        <div class="stat-label">Available bags ({{ product.default_bag_size_kg }}kg)</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">v{{ product.active_formula?.version ?? "—" }}</div>
        <div class="stat-label">Active formula version</div>
      </div>
    </div>

    <div class="card" v-if="auth.hasPermission(PRODUCTS_MANAGE)">
      <div class="card-header"><h3>Adjust finished goods</h3></div>
      <div class="card-body row">
        <input v-model.number="movementDelta" type="number" class="input" style="max-width:200px" placeholder="+ / - kg" />
        <button class="btn btn-secondary" :disabled="recordingMovement || !movementDelta" @click="recordFinishedGoods">
          {{ recordingMovement ? "Saving…" : "Apply" }}
        </button>
        <span class="text-sm muted">Positive = production output added; negative = shipped/consumed.</span>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Active formula</h3></div>
      <div class="card-body" style="padding:0">
        <div v-if="!product.active_formula" class="empty-state">No active formula yet.</div>
        <table v-else class="data-table">
          <thead><tr><th>Material</th><th class="numeric">Qty per unit</th></tr></thead>
          <tbody>
            <tr v-for="l in product.active_formula.lines" :key="l.material_id" @click="router.push(`/materials/${l.material_id}`)">
              <td>{{ l.material_name }}</td>
              <td class="numeric">{{ l.quantity_per_unit }} {{ l.unit }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Formula version history</h3></div>
      <div class="card-body" style="padding:0">
        <table class="data-table">
          <thead><tr><th>Version</th><th>Effective from</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="v in product.formula_versions" :key="v.id" style="cursor:default">
              <td>v{{ v.version }}</td>
              <td>{{ v.effective_from }}</td>
              <td><span class="badge" :class="v.is_active ? 'badge-success' : 'badge-neutral'">{{ v.is_active ? "Active" : "Superseded" }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <AttachmentsPanel entity-type="product" :entity-id="id" />

    <Modal v-if="showFormula" title="New formula version" wide @close="showFormula = false">
      <p class="text-sm muted" style="margin-bottom: var(--space-4)">
        Creates a new version and supersedes the current one - past production stays traceable to the version used at the time.
      </p>
      <div class="field"><label>Effective from</label><input v-model="formulaForm.effective_from" type="date" class="input" /></div>
      <div v-for="(line, i) in formulaForm.lines" :key="i" class="row" style="margin-bottom: var(--space-3)">
        <select v-model.number="line.material_id" class="input">
          <option :value="0" disabled>Select material…</option>
          <option v-for="m in allMaterials" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>
        <input v-model.number="line.quantity_per_unit" type="number" step="0.0001" class="input" placeholder="Qty per unit" style="max-width:160px" />
        <button class="btn btn-ghost btn-sm" @click="removeLine(i)" :disabled="formulaForm.lines.length === 1">✕</button>
      </div>
      <button class="btn btn-secondary btn-sm" @click="addLine">+ Add material line</button>
      <template #footer>
        <button class="btn btn-secondary" @click="showFormula = false">Cancel</button>
        <button class="btn btn-primary" :disabled="savingFormula" @click="submitFormula">
          {{ savingFormula ? "Saving…" : "Create version" }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<style scoped>
.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: var(--space-4); }
.stat-card { padding: var(--space-5); text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: 700; }
.stat-label { font-size: var(--text-sm); color: var(--color-neutral-500); margin-top: 4px; }
</style>
