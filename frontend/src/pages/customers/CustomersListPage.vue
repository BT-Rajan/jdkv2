<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { customersApi } from "../../services/customers";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { CUSTOMERS_MANAGE } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Customer } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Customer[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Customer>[] = [
  { key: "name", label: "Name" },
  { key: "contact_person", label: "Contact" },
  { key: "phone", label: "Phone" },
  { key: "credit_limit", label: "Credit Limit", numeric: true, render: (r) => `₹${r.credit_limit.toLocaleString()}` },
  { key: "status", label: "Status" },
];

async function load() {
  loading.value = true;
  try {
    const result = await customersApi.search({ q: search.value || undefined, limit, offset: offset.value });
    rows.value = result.customers;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load customers.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(search, () => { offset.value = 0; load(); });

const showCreate = ref(false);
const form = reactive({ name: "", contact_person: "", email: "", phone: "", credit_limit: 0 });
const saving = ref(false);

async function submitCreate() {
  saving.value = true;
  try {
    const created = await customersApi.create(form);
    ui.toast("Customer created.", "success");
    showCreate.value = false;
    Object.assign(form, { name: "", contact_person: "", email: "", phone: "", credit_limit: 0 });
    router.push(`/customers/${created.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create customer.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Customers</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(CUSTOMERS_MANAGE)" class="btn btn-primary" @click="showCreate = true">
        + New Customer
      </button>
    </div>

    <div class="card">
      <div class="card-header">
        <input v-model="search" class="input" placeholder="Search by name, contact, email, phone…" style="max-width:340px" />
      </div>
      <div class="card-body" style="padding: 0;">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No customers found."
          @row-click="(r) => router.push(`/customers/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        />
      </div>
    </div>

    <Modal v-if="showCreate" title="New Customer" @close="showCreate = false">
      <form class="stack" @submit.prevent="submitCreate">
        <div class="form-grid">
          <div class="field"><label>Name *</label><input v-model="form.name" class="input" required /></div>
          <div class="field"><label>Contact person</label><input v-model="form.contact_person" class="input" /></div>
          <div class="field"><label>Email</label><input v-model="form.email" type="email" class="input" /></div>
          <div class="field"><label>Phone</label><input v-model="form.phone" class="input" /></div>
          <div class="field"><label>Credit limit</label><input v-model.number="form.credit_limit" type="number" class="input" /></div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.name" @click="submitCreate">
          {{ saving ? "Creating…" : "Create Customer" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
