<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { deliveriesApi } from "../../services/deliveries";
import { ordersApi } from "../../services/orders";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { DELIVERIES_MANAGE } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import type { Delivery } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Delivery[]>([]);
const total = ref(0);
const loading = ref(true);
const statusFilter = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Delivery>[] = [
  { key: "delivery_no", label: "Delivery #" },
  { key: "order_no", label: "Order" },
  { key: "delivery_date", label: "Delivery date" },
  { key: "dispatched_qty_kg", label: "Qty (kg)", numeric: true },
  { key: "carrier", label: "Carrier" },
  { key: "tracking_ref", label: "Tracking" },
];

async function load() {
  loading.value = true;
  try {
    const result = await deliveriesApi.search({ status: statusFilter.value || undefined, limit, offset: offset.value });
    rows.value = result.deliveries;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load deliveries.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(statusFilter, () => { offset.value = 0; load(); });

// ── Issue a delivery ─────────────────────────────────────────────────────────
const showCreate = ref(false);
const creating = ref(false);
const orderQuery = ref("");
const orderResults = ref<any[]>([]);
const form = reactive({ order_id: 0, order_no: "", delivery_date: "", dispatched_qty_kg: 0, carrier: "", tracking_ref: "", notes: "" });

async function searchOrders() {
  if (!orderQuery.value) { orderResults.value = []; return; }
  const result = await ordersApi.search({ q: orderQuery.value, limit: 10 });
  orderResults.value = result.orders;
}
function pickOrder(o: any) {
  form.order_id = o.id;
  form.order_no = o.order_no;
  form.dispatched_qty_kg = o.quantity_kg;
  form.delivery_date = o.delivery_date || "";
  orderResults.value = [];
  orderQuery.value = o.order_no;
}

async function submitCreate() {
  creating.value = true;
  try {
    await deliveriesApi.create({
      order_id: form.order_id,
      delivery_date: form.delivery_date,
      dispatched_qty_kg: form.dispatched_qty_kg,
      carrier: form.carrier || undefined,
      tracking_ref: form.tracking_ref || undefined,
      notes: form.notes || undefined,
    });
    ui.toast("Delivery issued.", "success");
    showCreate.value = false;
    offset.value = 0;
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't issue delivery.", "error");
  } finally {
    creating.value = false;
  }
}

// ── Status transitions ──────────────────────────────────────────────────────
async function setStatus(d: Delivery, status: string) {
  try {
    await deliveriesApi.setStatus(d.id, status);
    ui.toast(`Delivery marked ${status}.`, "success");
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update delivery.", "error");
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Deliveries</h1>
        <p>{{ total }} total · final stage of Order: feasibility → quotation → order → delivery</p>
      </div>
      <button v-if="auth.hasPermission(DELIVERIES_MANAGE)" class="btn btn-primary" @click="showCreate = true">
        + Issue delivery
      </button>
    </div>

    <div class="card">
      <div class="card-header row">
        <select v-model="statusFilter" class="input" style="max-width:200px">
          <option value="">All statuses</option>
          <option value="scheduled">Scheduled</option>
          <option value="dispatched">Dispatched</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No deliveries yet — deliveries can only be issued against an order."
          @row-click="(r) => router.push(`/orders/${r.order_id}`)"
          @page-change="(o) => { offset = o; load(); }"
        >
          <template #actions="{ row }: { row: Delivery }">
            <StatusBadge :status="row.status" />
            <button v-if="row.status === 'scheduled' && auth.hasPermission(DELIVERIES_MANAGE)" class="btn btn-sm btn-secondary" @click="setStatus(row, 'dispatched')">Dispatch</button>
            <button v-if="row.status === 'dispatched' && auth.hasPermission(DELIVERIES_MANAGE)" class="btn btn-sm btn-primary" @click="setStatus(row, 'delivered')">Mark delivered</button>
            <button v-if="row.status !== 'delivered' && row.status !== 'cancelled' && auth.hasPermission(DELIVERIES_MANAGE)" class="btn btn-sm btn-ghost" @click="setStatus(row, 'cancelled')">Cancel</button>
          </template>
        </DataTable>
      </div>
    </div>

    <Modal v-if="showCreate" title="Issue delivery" wide @close="showCreate = false">
      <div class="field">
        <label>Order *</label>
        <input v-model="orderQuery" class="input" placeholder="Search order #…" @input="searchOrders" />
        <div v-if="orderResults.length" class="card" style="margin-top:4px; max-height:180px; overflow:auto">
          <div v-for="o in orderResults" :key="o.id" class="row-between" style="padding:6px 10px; cursor:pointer" @click="pickOrder(o)">
            <span>{{ o.order_no }} — {{ o.customer_name }}</span>
            <span class="text-sm muted">{{ o.quantity_kg }} kg</span>
          </div>
        </div>
        <div v-if="form.order_no" class="text-sm muted" style="margin-top:4px">Selected: {{ form.order_no }}</div>
      </div>
      <div class="form-grid">
        <div class="field"><label>Delivery date *</label><input v-model="form.delivery_date" type="date" class="input" /></div>
        <div class="field"><label>Dispatched qty (kg) *</label><input v-model.number="form.dispatched_qty_kg" type="number" class="input" /></div>
        <div class="field"><label>Carrier</label><input v-model="form.carrier" class="input" /></div>
        <div class="field"><label>Tracking ref</label><input v-model="form.tracking_ref" class="input" /></div>
      </div>
      <div class="field"><label>Notes</label><textarea v-model="form.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="creating || !form.order_id || !form.delivery_date || !form.dispatched_qty_kg" @click="submitCreate">
          {{ creating ? "Issuing…" : "Issue delivery" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
