<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { suppliersApi } from "../../services/suppliers";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { SUPPLIERS_MANAGE } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Supplier } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Supplier[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Supplier>[] = [
  { key: "name", label: "Supplier" },
  { key: "category", label: "Category" },
  { key: "contact_person", label: "Contact" },
  { key: "phone", label: "Phone" },
  { key: "rating", label: "Rating", numeric: true, render: (r) => (r.rating ? "★".repeat(r.rating) : "—") },
];

async function load() {
  loading.value = true;
  try {
    const result = await suppliersApi.search({ q: search.value || undefined, limit, offset: offset.value });
    rows.value = result.suppliers;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load suppliers.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(search, () => { offset.value = 0; load(); });

const showCreate = ref(false);
const form = reactive({ name: "", contact_person: "", phone: "", email: "", category: "" });
const saving = ref(false);
async function submitCreate() {
  saving.value = true;
  try {
    const created = await suppliersApi.create(form);
    ui.toast("Supplier created.", "success");
    showCreate.value = false;
    router.push(`/suppliers/${created.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create supplier.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Suppliers</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(SUPPLIERS_MANAGE)" class="btn btn-primary" @click="showCreate = true">
        + New Supplier
      </button>
    </div>

    <div class="card">
      <div class="card-header">
        <input v-model="search" class="input" placeholder="Search suppliers…" style="max-width:300px" />
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No suppliers found."
          @row-click="(r) => router.push(`/suppliers/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        />
      </div>
    </div>

    <Modal v-if="showCreate" title="New Supplier" @close="showCreate = false">
      <div class="form-grid">
        <div class="field"><label>Name *</label><input v-model="form.name" class="input" required /></div>
        <div class="field"><label>Category</label><input v-model="form.category" class="input" /></div>
        <div class="field"><label>Contact person</label><input v-model="form.contact_person" class="input" /></div>
        <div class="field"><label>Phone</label><input v-model="form.phone" class="input" /></div>
        <div class="field"><label>Email</label><input v-model="form.email" class="input" /></div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.name" @click="submitCreate">
          {{ saving ? "Creating…" : "Create Supplier" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
