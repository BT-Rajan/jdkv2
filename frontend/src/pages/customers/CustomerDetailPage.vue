<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { customersApi } from "../../services/customers";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { CUSTOMERS_MANAGE } from "../../permissions";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import Modal from "../../components/ui/Modal.vue";
import ConfirmDialog from "../../components/ui/ConfirmDialog.vue";
import AttachmentsPanel from "../../components/AttachmentsPanel.vue";
import type { Customer } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = Number(route.params.id);
const customer = ref<Customer | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    customer.value = await customersApi.get(id);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load customer.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

const showEdit = ref(false);
const editForm = reactive({
  name: "", contact_person: "", email: "", phone: "", address: "",
  billing_address: "", gstin: "", payment_terms: "", credit_limit: 0, notes: "",
});
function openEdit() {
  if (!customer.value) return;
  Object.assign(editForm, customer.value);
  showEdit.value = true;
}
const saving = ref(false);
async function submitEdit() {
  saving.value = true;
  try {
    customer.value = await customersApi.update(id, editForm);
    ui.toast("Customer updated.", "success");
    showEdit.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update customer.", "error");
  } finally {
    saving.value = false;
  }
}

const showDeactivate = ref(false);
const deactivating = ref(false);
async function confirmDeactivate() {
  deactivating.value = true;
  try {
    customer.value = await customersApi.deactivate(id);
    ui.toast("Customer deactivated.", "success");
    showDeactivate.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't deactivate customer.", "error");
  } finally {
    deactivating.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="customer" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/customers')">← Customers</button>
        <h1 style="margin-top:8px">{{ customer.name }}</h1>
        <div class="row" style="margin-top:6px"><StatusBadge :status="customer.status" /></div>
      </div>
      <div class="row" v-if="auth.hasPermission(CUSTOMERS_MANAGE)">
        <button class="btn btn-secondary" @click="openEdit">Edit</button>
        <button v-if="customer.status === 'active'" class="btn btn-danger" @click="showDeactivate = true">Deactivate</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Details</h3></div>
      <div class="card-body form-grid">
        <div><div class="text-xs muted">Contact person</div><div>{{ customer.contact_person || "—" }}</div></div>
        <div><div class="text-xs muted">Email</div><div>{{ customer.email || "—" }}</div></div>
        <div><div class="text-xs muted">Phone</div><div>{{ customer.phone || "—" }}</div></div>
        <div><div class="text-xs muted">GSTIN</div><div>{{ customer.gstin || "—" }}</div></div>
        <div><div class="text-xs muted">Payment terms</div><div>{{ customer.payment_terms || "—" }}</div></div>
        <div><div class="text-xs muted">Credit limit</div><div>₹{{ customer.credit_limit.toLocaleString() }}</div></div>
        <div style="grid-column: 1 / -1"><div class="text-xs muted">Address</div><div>{{ customer.address || "—" }}</div></div>
        <div style="grid-column: 1 / -1" v-if="customer.notes"><div class="text-xs muted">Notes</div><div>{{ customer.notes }}</div></div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Order history</h3></div>
      <div class="card-body" style="padding:0">
        <div v-if="!customer.orders?.length" class="empty-state">No orders yet.</div>
        <table v-else class="data-table">
          <thead><tr><th>Order</th><th>Product</th><th class="numeric">Qty (kg)</th><th>Delivery</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="o in customer.orders" :key="o.id" @click="router.push(`/orders/${o.id}`)">
              <td>{{ o.order_no }}</td>
              <td>{{ o.product_name }}</td>
              <td class="numeric">{{ o.quantity_kg }}</td>
              <td>{{ o.delivery_date || "—" }}</td>
              <td><StatusBadge :status="o.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <AttachmentsPanel entity-type="customer" :entity-id="id" />

    <Modal v-if="showEdit" title="Edit Customer" wide @close="showEdit = false">
      <form class="form-grid" @submit.prevent="submitEdit">
        <div class="field"><label>Name</label><input v-model="editForm.name" class="input" /></div>
        <div class="field"><label>Contact person</label><input v-model="editForm.contact_person" class="input" /></div>
        <div class="field"><label>Email</label><input v-model="editForm.email" class="input" /></div>
        <div class="field"><label>Phone</label><input v-model="editForm.phone" class="input" /></div>
        <div class="field"><label>GSTIN</label><input v-model="editForm.gstin" class="input" /></div>
        <div class="field"><label>Payment terms</label><input v-model="editForm.payment_terms" class="input" /></div>
        <div class="field"><label>Credit limit</label><input v-model.number="editForm.credit_limit" type="number" class="input" /></div>
        <div class="field" style="grid-column:1/-1"><label>Address</label><textarea v-model="editForm.address" class="input" rows="2" /></div>
        <div class="field" style="grid-column:1/-1"><label>Notes</label><textarea v-model="editForm.notes" class="input" rows="2" /></div>
      </form>
      <template #footer>
        <button class="btn btn-secondary" @click="showEdit = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitEdit">{{ saving ? "Saving…" : "Save changes" }}</button>
      </template>
    </Modal>

    <ConfirmDialog
      v-if="showDeactivate"
      title="Deactivate customer"
      :message="`Deactivate ${customer.name}? They'll be hidden from active customer lists.`"
      confirm-label="Deactivate"
      danger
      :busy="deactivating"
      @confirm="confirmDeactivate"
      @cancel="showDeactivate = false"
    />
  </div>
</template>
