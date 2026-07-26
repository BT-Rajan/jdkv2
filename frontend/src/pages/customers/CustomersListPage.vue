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
  { key: "credit_limit", label: "Credit Limit", numeric: true, render: (r) => `${r.credit_limit.toLocaleString()} KWD` },
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
const form = reactive({
  name: "", client_type: "", contact_person: "", phone: "", email: "",
  delivery_address: "", billing_address: "", tax_id: "", payment_terms: "",
  credit_limit: 0, notes: "",
});
const saving = ref(false);

async function submitCreate() {
  saving.value = true;
  try {
    const created = await customersApi.create(form);
    ui.toast("Customer created.", "success");
    showCreate.value = false;
    Object.assign(form, {
      name: "", client_type: "", contact_person: "", phone: "", email: "",
      delivery_address: "", billing_address: "", tax_id: "", payment_terms: "",
      credit_limit: 0, notes: "",
    });
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

    <Modal v-if="showCreate" title="New Customer" wide @close="showCreate = false">
      <form class="stack" @submit.prevent="submitCreate">
        <div class="form-grid">
          <div class="field"><label>Client Name *</label><input v-model="form.name" class="input" required /></div>
          <div class="field"><label>Type</label><input v-model="form.client_type" class="input" /></div>
          <div class="field"><label>Contact Person</label><input v-model="form.contact_person" class="input" placeholder="Contact name" /></div>
          <div class="field"><label>Phone</label><input v-model="form.phone" class="input" /></div>
          <div class="field"><label>Email</label><input v-model="form.email" type="email" class="input" /></div>
          <div class="field"><label>Tax-id</label><input v-model="form.tax_id" class="input" /></div>
          <div class="field"><label>Payment Terms</label><input v-model="form.payment_terms" class="input" /></div>
          <div class="field"><label>Credit Limit (KWD)</label><input v-model.number="form.credit_limit" type="number" class="input" /></div>
          <div class="field" style="grid-column:1/-1">
            <label>Delivery Address</label>
            <textarea v-model="form.delivery_address" class="input" rows="2" placeholder="Delivery site address" />
          </div>
          <div class="field" style="grid-column:1/-1">
            <label>Billing Address</label>
            <textarea v-model="form.billing_address" class="input" rows="2" placeholder="Leave blank if same as delivery" />
          </div>
          <div class="field" style="grid-column:1/-1">
            <label>Notes</label>
            <textarea v-model="form.notes" class="input" rows="2" placeholder="Internal notes about this client" />
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.name" @click="submitCreate">
          {{ saving ? "Adding…" : "Add Client" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
