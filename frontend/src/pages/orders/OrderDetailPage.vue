<script setup lang="ts">
import { ref, onMounted } from "vue";
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
      <div class="card-header"><h3>Feasibility</h3></div>
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
        <div><div class="text-xs muted">Delivery date</div><div>{{ order.delivery_date || "—" }}</div></div>
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
  </div>
</template>
