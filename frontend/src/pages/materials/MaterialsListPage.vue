<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { materialsApi } from "../../services/materials";
import { suppliersApi } from "../../services/suppliers";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { INVENTORY_ADJUST } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Material, Supplier } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Material[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const lowStockOnly = ref(false);
const offset = ref(0);
const limit = 20;

const columns: Column<Material>[] = [
  { key: "name", label: "Material" },
  { key: "current_stock", label: "Current Stock", numeric: true, render: (r) => `${r.current_stock} ${r.unit}` },
  { key: "reorder_point", label: "Reorder Point", numeric: true, render: (r) => `${r.reorder_point} ${r.unit}` },
  { key: "lead_time_days", label: "Lead Time", numeric: true, render: (r) => `${r.lead_time_days}d` },
];

async function load() {
  loading.value = true;
  try {
    const result = await materialsApi.search({ q: search.value || undefined, low_stock_only: lowStockOnly.value, limit, offset: offset.value });
    rows.value = result.materials;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load materials.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(() => {
  load();
  suppliersApi.search({ limit: 100 }).then((r) => { allSuppliers.value = r.suppliers; });
});
watch([search, lowStockOnly], () => { offset.value = 0; load(); });

const allSuppliers = ref<Supplier[]>([]);

const showCreate = ref(false);
const emptyForm = () => ({
  name: "", unit: "kg", shelf_life_days: null as number | null,
  default_supplier_id: null as number | null,
  minimum_stock: 0, reorder_point: 0, lead_time_days: 0,
  received_date: "" as string, received_qty: null as number | null,
  invoice_id: "", invoice_amt: null as number | null,
});
const form = reactive(emptyForm());
const saving = ref(false);
async function submitCreate() {
  saving.value = true;
  try {
    const created = await materialsApi.create({
      name: form.name, unit: form.unit,
      shelf_life_days: form.shelf_life_days, default_supplier_id: form.default_supplier_id,
      minimum_stock: form.minimum_stock, reorder_point: form.reorder_point, lead_time_days: form.lead_time_days,
      initial_receipt: form.received_qty ? {
        received_date: form.received_date || null, received_qty: form.received_qty,
        invoice_id: form.invoice_id || null, invoice_amt: form.invoice_amt,
      } : null,
    });
    ui.toast("Material created.", "success");
    showCreate.value = false;
    Object.assign(form, emptyForm());
    router.push(`/materials/${created.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create material.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Materials & Inventory</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(INVENTORY_ADJUST)" class="btn btn-primary" @click="showCreate = true">
        + New Material
      </button>
    </div>

    <div class="card">
      <div class="card-header row">
        <input v-model="search" class="input" placeholder="Search materials…" style="max-width:300px" />
        <label class="row text-sm" style="gap:6px; cursor:pointer">
          <input type="checkbox" v-model="lowStockOnly" /> Low stock only
        </label>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No materials found."
          @row-click="(r) => router.push(`/materials/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        />
      </div>
    </div>

    <Modal v-if="showCreate" title="New Material" wide @close="showCreate = false">
      <div class="form-grid">
        <div class="field"><label>Material Name *</label><input v-model="form.name" class="input" required /></div>
        <div class="field"><label>Unit</label><input v-model="form.unit" class="input" placeholder="kg" /></div>
        <div class="field"><label>Minimum Stock</label><input v-model.number="form.minimum_stock" type="number" class="input" /></div>
        <div class="field"><label>Reorder Point</label><input v-model.number="form.reorder_point" type="number" class="input" /></div>
        <div class="field"><label>Lead Time (days)</label><input v-model.number="form.lead_time_days" type="number" class="input" /></div>
        <div class="field">
          <label>Supplier</label>
          <select v-model.number="form.default_supplier_id" class="input">
            <option :value="null">—</option>
            <option v-for="s in allSuppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="field"><label>Shelf-life (days)</label><input v-model.number="form.shelf_life_days" type="number" class="input" /></div>
      </div>

      <div class="card-header" style="margin-top:16px;padding-left:0"><h3 class="text-sm muted">Opening stock receipt (optional)</h3></div>
      <div class="form-grid">
        <div class="field"><label>received date</label><input v-model="form.received_date" type="date" class="input" /></div>
        <div class="field"><label>received qty</label><input v-model.number="form.received_qty" type="number" class="input" /></div>
        <div class="field"><label>invoice id</label><input v-model="form.invoice_id" class="input" /></div>
        <div class="field"><label>invoice amt</label><input v-model.number="form.invoice_amt" type="number" class="input" /></div>
      </div>

      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.name" @click="submitCreate">
          {{ saving ? "Adding…" : "Add Raw Material" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
