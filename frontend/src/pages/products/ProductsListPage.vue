<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { productsApi } from "../../services/products";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { PRODUCTS_MANAGE } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Product } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Product[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Product>[] = [
  { key: "name", label: "Product" },
  { key: "category", label: "Category" },
  { key: "unit_of_measure", label: "Unit" },
  { key: "default_bag_size_kg", label: "Bag size", numeric: true, render: (r) => `${r.default_bag_size_kg} kg` },
  { key: "status", label: "Status" },
];

async function load() {
  loading.value = true;
  try {
    const result = await productsApi.search({ q: search.value || undefined, limit, offset: offset.value });
    rows.value = result.products;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load products.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(search, () => { offset.value = 0; load(); });

const showCreate = ref(false);
const form = reactive({ name: "", category: "", unit_of_measure: "kg", default_bag_size_kg: 50 });
const saving = ref(false);
async function submitCreate() {
  saving.value = true;
  try {
    const created = await productsApi.create(form);
    ui.toast("Product created.", "success");
    showCreate.value = false;
    router.push(`/products/${created.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create product.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Products & Formulas</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(PRODUCTS_MANAGE)" class="btn btn-primary" @click="showCreate = true">
        + New Product
      </button>
    </div>

    <div class="card">
      <div class="card-header">
        <input v-model="search" class="input" placeholder="Search products…" style="max-width:300px" />
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No products found."
          @row-click="(r) => router.push(`/products/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        />
      </div>
    </div>

    <Modal v-if="showCreate" title="New Product" @close="showCreate = false">
      <div class="form-grid">
        <div class="field"><label>Name *</label><input v-model="form.name" class="input" required /></div>
        <div class="field"><label>Category</label><input v-model="form.category" class="input" /></div>
        <div class="field"><label>Unit of measure</label><input v-model="form.unit_of_measure" class="input" /></div>
        <div class="field"><label>Default bag size (kg)</label><input v-model.number="form.default_bag_size_kg" type="number" class="input" /></div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.name" @click="submitCreate">
          {{ saving ? "Creating…" : "Create Product" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
