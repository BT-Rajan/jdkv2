<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { materialsApi } from "../../services/materials";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { INVENTORY_ADJUST } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Material } from "../../types";

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
onMounted(load);
watch([search, lowStockOnly], () => { offset.value = 0; load(); });

const showCreate = ref(false);
const form = reactive({ name: "", unit: "kg" });
const saving = ref(false);
async function submitCreate() {
  saving.value = true;
  try {
    const created = await materialsApi.create(form);
    ui.toast("Material created.", "success");
    showCreate.value = false;
    form.name = ""; form.unit = "kg";
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

    <Modal v-if="showCreate" title="New Material" @close="showCreate = false">
      <div class="field"><label>Name *</label><input v-model="form.name" class="input" required /></div>
      <div class="field"><label>Unit</label><input v-model="form.unit" class="input" placeholder="kg" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.name" @click="submitCreate">
          {{ saving ? "Creating…" : "Create Material" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
