<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { quotationsApi } from "../../services/quotations";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { SALES_ACCESS, HISTORY_AMEND } from "../../permissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Quotation } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = String(route.params.id);
const quotation = ref<Quotation | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    quotation.value = await quotationsApi.get(id);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load quotation.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

// ── Edit while draft ────────────────────────────────────────────────────────
const showEdit = ref(false);
const saving = ref(false);
const editForm = reactive({ unit_price: 0, valid_until: "", terms: "", notes: "" });

function openEdit() {
  if (!quotation.value) return;
  editForm.unit_price = quotation.value.unit_price;
  editForm.valid_until = quotation.value.valid_until || "";
  editForm.terms = quotation.value.terms || "";
  editForm.notes = quotation.value.notes || "";
  showEdit.value = true;
}

async function submitEdit() {
  saving.value = true;
  try {
    quotation.value = await quotationsApi.update(id, {
      unit_price: editForm.unit_price,
      valid_until: editForm.valid_until || undefined,
      terms: editForm.terms || undefined,
      notes: editForm.notes || undefined,
    });
    ui.toast("Quotation updated.", "success");
    showEdit.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update quotation.", "error");
  } finally {
    saving.value = false;
  }
}

// ── Status transitions ──────────────────────────────────────────────────────
const changingStatus = ref(false);
async function setStatus(status: string) {
  changingStatus.value = true;
  try {
    quotation.value = await quotationsApi.setStatus(id, status);
    ui.toast(`Quotation marked ${status}.`, "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update status.", "error");
  } finally {
    changingStatus.value = false;
  }
}

// ── Convert to order ─────────────────────────────────────────────────────────
const showConvert = ref(false);
const converting = ref(false);
const convertForm = reactive({ order_date: "", delivery_date: "", bag_size_kg: 50, priority: "normal", notes: "" });

function openConvert() {
  if (!quotation.value) return;
  convertForm.order_date = quotation.value.quote_date;
  convertForm.delivery_date = quotation.value.requested_delivery_date;
  showConvert.value = true;
}

async function submitConvert() {
  converting.value = true;
  try {
    const order = await quotationsApi.convertToOrder(id, {
      order_date: convertForm.order_date || undefined,
      delivery_date: convertForm.delivery_date,
      bag_size_kg: convertForm.bag_size_kg,
      priority: convertForm.priority,
      notes: convertForm.notes || undefined,
    });
    ui.toast(`Order ${order.order_no} created.`, "success");
    showConvert.value = false;
    router.push(`/orders/${order.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't convert to order. Delivery date must be later than order date, and order date can't be before the quote date.", "error");
  } finally {
    converting.value = false;
  }
}

// ── Admin amend ──────────────────────────────────────────────────────────────
const showAmend = ref(false);
const amending = ref(false);
const amendForm = reactive({ unit_price: 0, valid_until: "", terms: "", notes: "" });

function openAmend() {
  if (!quotation.value) return;
  amendForm.unit_price = quotation.value.unit_price;
  amendForm.valid_until = quotation.value.valid_until || "";
  amendForm.terms = quotation.value.terms || "";
  amendForm.notes = quotation.value.notes || "";
  showAmend.value = true;
}

async function submitAmend() {
  amending.value = true;
  try {
    quotation.value = await quotationsApi.amend(id, {
      unit_price: amendForm.unit_price,
      valid_until: amendForm.valid_until || undefined,
      terms: amendForm.terms || undefined,
      notes: amendForm.notes || undefined,
    });
    ui.toast("Quotation amended.", "success");
    showAmend.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't amend quotation.", "error");
  } finally {
    amending.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="quotation" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/quotations')">← Quotations</button>
        <h1 style="margin-top:8px">{{ quotation.quote_no }}</h1>
        <div class="row" style="margin-top:6px"><StatusBadge :status="quotation.status" /></div>
      </div>
      <div class="row" v-if="auth.hasPermission(SALES_ACCESS)">
        <button v-if="quotation.status === 'draft'" class="btn btn-secondary" @click="openEdit">Edit</button>
        <button v-if="quotation.status === 'draft'" class="btn btn-primary" :disabled="changingStatus" @click="setStatus('sent')">Mark sent</button>
        <button v-if="quotation.status === 'sent'" class="btn btn-primary" :disabled="changingStatus" @click="setStatus('accepted')">Mark accepted</button>
        <button v-if="quotation.status === 'sent'" class="btn btn-danger" :disabled="changingStatus" @click="setStatus('rejected')">Mark rejected</button>
        <button v-if="quotation.status === 'sent'" class="btn btn-ghost" :disabled="changingStatus" @click="setStatus('expired')">Mark expired</button>
        <button v-if="quotation.can_convert_to_order" class="btn btn-primary" @click="openConvert">Generate order</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Quotation details</h3></div>
      <div class="card-body form-grid">
        <div><div class="text-xs muted">Customer</div><div><a @click.prevent="router.push(`/customers/${quotation.customer_id}`)" href="#">{{ quotation.customer_name }}</a></div></div>
        <div><div class="text-xs muted">Product</div><div><a @click.prevent="router.push(`/products/${quotation.product_id}`)" href="#">{{ quotation.product_name }}</a></div></div>
        <div><div class="text-xs muted">Quantity</div><div>{{ quotation.quantity_kg }} kg</div></div>
        <div><div class="text-xs muted">Unit price</div><div>{{ quotation.unit_price }}</div></div>
        <div><div class="text-xs muted">Total</div><div>{{ quotation.total_amount }}</div></div>
        <div><div class="text-xs muted">Quote date</div><div>{{ quotation.quote_date }}</div></div>
        <div><div class="text-xs muted">Valid until</div><div>{{ quotation.valid_until || "—" }}</div></div>
        <div><div class="text-xs muted">Requested delivery</div><div>{{ quotation.requested_delivery_date }}</div></div>
        <div>
          <div class="text-xs muted">From feasibility check</div>
          <div><a href="#" @click.prevent="router.push('/feasibility')">View feasibility history</a></div>
        </div>
        <div style="grid-column:1/-1" v-if="quotation.terms"><div class="text-xs muted">Terms</div><div>{{ quotation.terms }}</div></div>
        <div style="grid-column:1/-1" v-if="quotation.notes"><div class="text-xs muted">Notes</div><div>{{ quotation.notes }}</div></div>
      </div>
    </div>

    <div v-if="auth.hasPermission(HISTORY_AMEND) && quotation.status !== 'draft'" class="row" style="justify-content:flex-end">
      <button class="btn btn-ghost btn-sm" @click="openAmend">Amend (admin)</button>
    </div>

    <Modal v-if="showEdit" title="Edit quotation" @close="showEdit = false">
      <p class="text-sm muted" style="margin-top:0">Customer, product and quantity are locked to the originating feasibility check.</p>
      <div class="form-grid">
        <div class="field"><label>Unit price</label><input v-model.number="editForm.unit_price" type="number" step="0.01" class="input" /></div>
        <div class="field"><label>Valid until</label><input v-model="editForm.valid_until" type="date" class="input" /></div>
      </div>
      <div class="field"><label>Terms</label><textarea v-model="editForm.terms" class="input" rows="2" /></div>
      <div class="field"><label>Notes</label><textarea v-model="editForm.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showEdit = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitEdit">{{ saving ? "Saving…" : "Save" }}</button>
      </template>
    </Modal>

    <Modal v-if="showConvert" title="Generate order" @close="showConvert = false">
      <p class="text-sm muted" style="margin-top:0">
        Customer, product and quantity carry over from this quotation. Order date must be on or after the quote date ({{ quotation.quote_date }}); delivery date must be later than the order date.
      </p>
      <div class="form-grid">
        <div class="field"><label>Order date</label><input v-model="convertForm.order_date" type="date" class="input" /></div>
        <div class="field"><label>Delivery date *</label><input v-model="convertForm.delivery_date" type="date" class="input" /></div>
        <div class="field"><label>Bag size (kg)</label><input v-model.number="convertForm.bag_size_kg" type="number" class="input" /></div>
        <div class="field">
          <label>Priority</label>
          <select v-model="convertForm.priority" class="input">
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="normal">Normal</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>
      <div class="field"><label>Notes</label><textarea v-model="convertForm.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showConvert = false">Cancel</button>
        <button class="btn btn-primary" :disabled="converting || !convertForm.delivery_date" @click="submitConvert">
          {{ converting ? "Creating…" : "Generate order" }}
        </button>
      </template>
    </Modal>

    <Modal v-if="showAmend" title="Amend quotation (admin)" @close="showAmend = false">
      <div class="form-grid">
        <div class="field"><label>Unit price</label><input v-model.number="amendForm.unit_price" type="number" step="0.01" class="input" /></div>
        <div class="field"><label>Valid until</label><input v-model="amendForm.valid_until" type="date" class="input" /></div>
      </div>
      <div class="field"><label>Terms</label><textarea v-model="amendForm.terms" class="input" rows="2" /></div>
      <div class="field"><label>Notes</label><textarea v-model="amendForm.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showAmend = false">Cancel</button>
        <button class="btn btn-primary" :disabled="amending" @click="submitAmend">{{ amending ? "Saving…" : "Save" }}</button>
      </template>
    </Modal>
  </div>
</template>
