<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ordersApi } from "../../services/orders";
import { feasibilityApi } from "../../services/mrp";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { ORDERS_EDIT, ORDERS_DELETE } from "../../permissions";
import { ORDER_STATUSES } from "../../types";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import ConfirmDialog from "../../components/ui/ConfirmDialog.vue";
import Modal from "../../components/ui/Modal.vue";
import AttachmentsPanel from "../../components/AttachmentsPanel.vue";
import type { Order, FeasibilityResult } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = Number(route.params.id);
const order = ref<Order | null>(null);
const feasibility = ref<FeasibilityResult | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    order.value = await ordersApi.get(id);
    try {
      feasibility.value = await feasibilityApi.assessOrder(id);
    } catch {
      feasibility.value = null;
    }
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load order.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

const changingStatus = ref(false);
async function setStatus(status: string) {
  changingStatus.value = true;
  try {
    order.value = await ordersApi.setStatus(id, status);
    ui.toast(`Order marked ${status.replace(/_/g, " ")}.`, "success");
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update status.", "error");
  } finally {
    changingStatus.value = false;
  }
}

const showCancel = ref(false);
const cancelling = ref(false);
async function confirmCancel() {
  cancelling.value = true;
  try {
    order.value = await ordersApi.cancel(id);
    ui.toast("Order cancelled.", "success");
    showCancel.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't cancel order.", "error");
  } finally {
    cancelling.value = false;
  }
}

// ── Edit (everything but customer & product) ───────────────────────────────
const showEdit = ref(false);
const saving = ref(false);
const editForm = reactive({
  quantity_kg: 0, bag_size_kg: 50, order_date: "", delivery_date: "", priority: "normal", notes: "",
});

function openEdit() {
  if (!order.value) return;
  editForm.quantity_kg = order.value.quantity_kg;
  editForm.bag_size_kg = order.value.bag_size_kg;
  editForm.order_date = order.value.order_date || "";
  editForm.delivery_date = order.value.delivery_date || "";
  editForm.priority = order.value.priority;
  editForm.notes = order.value.notes || "";
  showEdit.value = true;
}

async function submitEdit() {
  saving.value = true;
  try {
    order.value = await ordersApi.update(id, {
      quantity_kg: editForm.quantity_kg,
      bag_size_kg: editForm.bag_size_kg,
      order_date: editForm.order_date || undefined,
      delivery_date: editForm.delivery_date || undefined,
      priority: editForm.priority,
      notes: editForm.notes || undefined,
    } as any);
    ui.toast("Order updated.", "success");
    showEdit.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update order. Delivery date must be later than order date.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="order" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/orders')">← Orders</button>
        <h1 style="margin-top:8px">{{ order.order_no }}</h1>
        <div class="row" style="margin-top:6px; gap: var(--space-2)">
          <StatusBadge :status="order.status" />
          <StatusBadge :status="order.priority" />
        </div>
      </div>
      <div class="row" v-if="auth.hasPermission(ORDERS_EDIT)">
        <button class="btn btn-secondary" @click="openEdit">Edit</button>
        <select class="input" style="max-width:220px" :disabled="changingStatus" @change="setStatus(($event.target as HTMLSelectElement).value)">
          <option value="" selected disabled>Change status…</option>
          <option v-for="s in ORDER_STATUSES" :key="s" :value="s">{{ s.replace(/_/g, " ") }}</option>
        </select>
        <button v-if="auth.hasPermission(ORDERS_DELETE) && order.status !== 'cancelled'" class="btn btn-danger" @click="showCancel = true">
          Cancel order
        </button>
      </div>
    </div>

    <div class="card" v-if="feasibility">
      <div class="card-header"><h3>Feasibility (live)</h3></div>
      <div class="card-body">
        <div class="row" style="margin-bottom: var(--space-3)">
          <StatusBadge :status="feasibility.outcome" />
          <span class="text-sm muted">Estimated fulfillment: {{ feasibility.estimated_fulfillment_date }}</span>
        </div>
        <div class="row" style="gap: var(--space-6)">
          <div><div class="text-xs muted">Requested</div><div>{{ feasibility.requested_kg }} kg</div></div>
          <div><div class="text-xs muted">Available now</div><div>{{ feasibility.promptly_available_kg }} kg</div></div>
          <div><div class="text-xs muted">Remaining to produce</div><div>{{ feasibility.remaining_kg }} kg</div></div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Order details</h3></div>
      <div class="card-body form-grid">
        <div><div class="text-xs muted">Customer</div><div><a @click.prevent="router.push(`/customers/${order.customer_id}`)" href="#">{{ order.customer_name }}</a></div></div>
        <div><div class="text-xs muted">Product</div><div><a @click.prevent="router.push(`/products/${order.product_id}`)" href="#">{{ order.product_name }}</a></div></div>
        <div><div class="text-xs muted">Quantity</div><div>{{ order.quantity_kg }} kg ({{ order.bags }} bags of {{ order.bag_size_kg }}kg)</div></div>
        <div><div class="text-xs muted">Order date</div><div>{{ order.order_date || "—" }}</div></div>
        <div><div class="text-xs muted">Delivery date</div><div>{{ order.delivery_date || "—" }}</div></div>
        <div v-if="order.quotation_id">
          <div class="text-xs muted">From quotation</div>
          <div><a href="#" @click.prevent="router.push(`/quotations/${order.quotation_id}`)">View quotation</a></div>
        </div>
        <div style="grid-column:1/-1" v-if="order.notes"><div class="text-xs muted">Notes</div><div>{{ order.notes }}</div></div>
      </div>
    </div>

    <AttachmentsPanel entity-type="order" :entity-id="id" />

    <ConfirmDialog
      v-if="showCancel"
      title="Cancel order"
      :message="`Cancel order ${order.order_no}? This cannot be undone.`"
      confirm-label="Cancel order"
      danger
      :busy="cancelling"
      @confirm="confirmCancel"
      @cancel="showCancel = false"
    />

    <Modal v-if="showEdit" title="Edit order" @close="showEdit = false">
      <p class="text-sm muted" style="margin-top:0">Customer and product are locked to the originating quotation and can't be changed here.</p>
      <div class="form-grid">
        <div class="field"><label>Quantity (kg)</label><input v-model.number="editForm.quantity_kg" type="number" class="input" /></div>
        <div class="field"><label>Bag size (kg)</label><input v-model.number="editForm.bag_size_kg" type="number" class="input" /></div>
        <div class="field"><label>Order date</label><input v-model="editForm.order_date" type="date" class="input" /></div>
        <div class="field"><label>Delivery date</label><input v-model="editForm.delivery_date" type="date" class="input" /></div>
        <div class="field">
          <label>Priority</label>
          <select v-model="editForm.priority" class="input">
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="normal">Normal</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>
      <div class="field"><label>Notes</label><textarea v-model="editForm.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showEdit = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitEdit">{{ saving ? "Saving…" : "Save changes" }}</button>
      </template>
    </Modal>
  </div>
</template>
