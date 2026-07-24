<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { ordersApi } from "../../services/orders";
import { customersApi } from "../../services/customers";
import { productsApi } from "../../services/products";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { ORDERS_CREATE } from "../../permissions";
import { ORDER_STATUSES } from "../../types";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Order, Customer, Product, Availability } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Order[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const statusFilter = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Order>[] = [
  { key: "order_no", label: "Order" },
  { key: "customer_name", label: "Customer" },
  { key: "product_name", label: "Product" },
  { key: "quantity_kg", label: "Qty (kg)", numeric: true },
  { key: "delivery_date", label: "Delivery" },
  { key: "priority", label: "Priority" },
];

async function load() {
  loading.value = true;
  try {
    const result = await ordersApi.search({ q: search.value || undefined, status: statusFilter.value || undefined, limit, offset: offset.value });
    rows.value = result.orders;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load orders.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch([search, statusFilter], () => { offset.value = 0; load(); });

// ── Create order ────────────────────────────────────────────────────────
const showCreate = ref(false);
const customers = ref<Customer[]>([]);
const products = ref<Product[]>([]);
const form = reactive({
  customer_id: 0, product_id: 0, quantity_kg: 0, bag_size_kg: 50,
  delivery_date: "", priority: "normal", notes: "",
});
const availability = ref<Availability | null>(null);
const saving = ref(false);

async function openCreate() {
  showCreate.value = true;
  availability.value = null;
  if (!customers.value.length) customers.value = (await customersApi.search({ limit: 100 })).customers;
  if (!products.value.length) products.value = (await productsApi.search({ limit: 100 })).products;
}

watch([() => form.product_id, () => form.quantity_kg], async ([productId, qty]) => {
  if (!productId || !qty) { availability.value = null; return; }
  try {
    availability.value = await ordersApi.checkAvailability(productId, qty);
  } catch {
    availability.value = null;
  }
});

async function submitCreate() {
  saving.value = true;
  try {
    const created = await ordersApi.create({
      customer_id: form.customer_id,
      product_id: form.product_id,
      quantity_kg: form.quantity_kg,
      bag_size_kg: form.bag_size_kg,
      delivery_date: form.delivery_date || undefined,
      priority: form.priority,
      notes: form.notes || undefined,
    });
    ui.toast(`Order ${created.order_no} created.`, "success");
    showCreate.value = false;
    router.push(`/orders/${created.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create order.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Customer Orders</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(ORDERS_CREATE)" class="btn btn-primary" @click="openCreate">
        + New Order
      </button>
    </div>

    <div class="card">
      <div class="card-header row">
        <input v-model="search" class="input" placeholder="Search order #, customer, product…" style="max-width:280px" />
        <select v-model="statusFilter" class="input" style="max-width:200px">
          <option value="">All statuses</option>
          <option v-for="s in ORDER_STATUSES" :key="s" :value="s">{{ s.replace(/_/g, " ") }}</option>
        </select>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No orders found."
          @row-click="(r) => router.push(`/orders/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        >
        </DataTable>
      </div>
    </div>

    <Modal v-if="showCreate" title="New Customer Order" wide @close="showCreate = false">
      <div class="form-grid">
        <div class="field">
          <label>Customer *</label>
          <select v-model.number="form.customer_id" class="input">
            <option :value="0" disabled>Select customer…</option>
            <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Product *</label>
          <select v-model.number="form.product_id" class="input">
            <option :value="0" disabled>Select product…</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="field"><label>Quantity (kg) *</label><input v-model.number="form.quantity_kg" type="number" class="input" /></div>
        <div class="field"><label>Bag size (kg)</label><input v-model.number="form.bag_size_kg" type="number" class="input" /></div>
        <div class="field"><label>Delivery date</label><input v-model="form.delivery_date" type="date" class="input" /></div>
        <div class="field">
          <label>Priority</label>
          <select v-model="form.priority" class="input">
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="normal">Normal</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>
      <div class="field"><label>Notes</label><textarea v-model="form.notes" class="input" rows="2" /></div>

      <div v-if="availability" class="availability-note" :class="availability.fulfillable_from_stock ? 'ok' : 'warn'">
        <template v-if="availability.fulfillable_from_stock">
          ✓ Fully available from current finished-goods stock ({{ availability.available_kg }} kg on hand).
        </template>
        <template v-else>
          ⚠ Only {{ availability.available_kg }} kg on hand - {{ availability.shortfall_kg }} kg would need production.
          Check the MRP page after creating this order for material impact.
        </template>
      </div>

      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.customer_id || !form.product_id || !form.quantity_kg" @click="submitCreate">
          {{ saving ? "Creating…" : "Create Order" }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<style scoped>
.availability-note {
  margin-top: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}
.availability-note.ok { background: var(--color-success-50); color: var(--color-success-700); }
.availability-note.warn { background: var(--color-warning-50); color: var(--color-warning-700); }
</style>
