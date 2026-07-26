<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { feasibilityWorkflowApi } from "../../services/feasibilityWorkflow";
import { quotationsApi } from "../../services/quotations";
import { customersApi } from "../../services/customers";
import { productsApi } from "../../services/products";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { FEASIBILITY_RUN, SALES_ACCESS, HISTORY_AMEND } from "../../permissions";
import { FEASIBILITY_OUTCOMES } from "../../types";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import type { FeasibilityRun, Customer, Product } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<FeasibilityRun[]>([]);
const total = ref(0);
const loading = ref(true);
const outcomeFilter = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<FeasibilityRun>[] = [
  { key: "customer_name", label: "Customer" },
  { key: "product_name", label: "Product" },
  { key: "quantity_kg", label: "Qty (kg)", numeric: true },
  { key: "requested_delivery_date", label: "Requested date" },
  { key: "estimated_fulfillment_date", label: "Est. fulfillment" },
  { key: "outcome", label: "Outcome", render: (r) => r.outcome.replace(/_/g, " ") },
];

async function load() {
  loading.value = true;
  try {
    const result = await feasibilityWorkflowApi.search({ outcome: outcomeFilter.value || undefined, limit, offset: offset.value });
    rows.value = result.runs;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load feasibility history.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(outcomeFilter, () => { offset.value = 0; load(); });

// ── Run a new feasibility check ────────────────────────────────────────────
const showRun = ref(false);
const customers = ref<Customer[]>([]);
const products = ref<Product[]>([]);
const runForm = reactive({ customer_id: 0, product_id: 0, quantity_kg: 0, requested_delivery_date: "", notes: "" });
const running = ref(false);

async function openRun() {
  showRun.value = true;
  if (!customers.value.length) customers.value = (await customersApi.search({ limit: 100 })).customers;
  if (!products.value.length) products.value = (await productsApi.search({ limit: 100 })).products;
}

async function submitRun() {
  running.value = true;
  try {
    await feasibilityWorkflowApi.run({
      customer_id: runForm.customer_id,
      product_id: runForm.product_id,
      quantity_kg: runForm.quantity_kg,
      requested_delivery_date: runForm.requested_delivery_date,
      notes: runForm.notes || undefined,
    });
    ui.toast("Feasibility check complete.", "success");
    showRun.value = false;
    offset.value = 0;
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't run feasibility check.", "error");
  } finally {
    running.value = false;
  }
}

// ── Generate quotation from a passed run ───────────────────────────────────
const showQuote = ref<FeasibilityRun | null>(null);
const quoteForm = reactive({ unit_price: 0, valid_until: "", terms: "", notes: "" });
const quoting = ref(false);

function openQuote(run: FeasibilityRun) {
  quoteForm.unit_price = 0;
  quoteForm.valid_until = "";
  quoteForm.terms = "";
  quoteForm.notes = "";
  showQuote.value = run;
}

async function submitQuote() {
  if (!showQuote.value) return;
  quoting.value = true;
  try {
    const q = await quotationsApi.create({
      feasibility_id: showQuote.value.id,
      unit_price: quoteForm.unit_price,
      valid_until: quoteForm.valid_until || undefined,
      terms: quoteForm.terms || undefined,
      notes: quoteForm.notes || undefined,
    });
    ui.toast(`Quotation ${q.quote_no} generated.`, "success");
    showQuote.value = null;
    router.push(`/quotations/${q.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't generate quotation.", "error");
  } finally {
    quoting.value = false;
  }
}

// ── Admin amend (notes only) ───────────────────────────────────────────────
const showAmend = ref<FeasibilityRun | null>(null);
const amendNotes = ref("");
const amending = ref(false);

function openAmend(run: FeasibilityRun) {
  amendNotes.value = run.notes || "";
  showAmend.value = run;
}

async function submitAmend() {
  if (!showAmend.value) return;
  amending.value = true;
  try {
    await feasibilityWorkflowApi.amend(showAmend.value.id, amendNotes.value || null);
    ui.toast("Feasibility record amended.", "success");
    showAmend.value = null;
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't amend record.", "error");
  } finally {
    amending.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Feasibility</h1>
        <p>{{ total }} checks · stage 1 of Order: feasibility → quotation → order → delivery</p>
      </div>
      <button v-if="auth.hasPermission(FEASIBILITY_RUN)" class="btn btn-primary" @click="openRun">
        + Run feasibility check
      </button>
    </div>

    <div class="card">
      <div class="card-header row">
        <select v-model="outcomeFilter" class="input" style="max-width:240px">
          <option value="">All outcomes</option>
          <option v-for="o in FEASIBILITY_OUTCOMES" :key="o" :value="o">{{ o.replace(/_/g, " ") }}</option>
        </select>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No feasibility checks yet."
          @page-change="(o) => { offset = o; load(); }"
        >
          <template #actions="{ row }: { row: FeasibilityRun }">
            <StatusBadge :status="row.status" />
            <button v-if="row.can_generate_quotation && auth.hasPermission(SALES_ACCESS)" class="btn btn-sm btn-primary" @click="openQuote(row)">
              Generate quotation
            </button>
            <button v-if="auth.hasPermission(HISTORY_AMEND)" class="btn btn-sm btn-ghost" @click="openAmend(row)">Amend</button>
          </template>
        </DataTable>
      </div>
    </div>

    <Modal v-if="showRun" title="Run feasibility check" wide @close="showRun = false">
      <div class="form-grid">
        <div class="field">
          <label>Customer *</label>
          <select v-model.number="runForm.customer_id" class="input">
            <option :value="0" disabled>Select customer…</option>
            <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Product *</label>
          <select v-model.number="runForm.product_id" class="input">
            <option :value="0" disabled>Select product…</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="field"><label>Quantity (kg) *</label><input v-model.number="runForm.quantity_kg" type="number" class="input" /></div>
        <div class="field"><label>Requested delivery date *</label><input v-model="runForm.requested_delivery_date" type="date" class="input" /></div>
      </div>
      <div class="field"><label>Notes</label><textarea v-model="runForm.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showRun = false">Cancel</button>
        <button class="btn btn-primary" :disabled="running || !runForm.customer_id || !runForm.product_id || !runForm.quantity_kg || !runForm.requested_delivery_date" @click="submitRun">
          {{ running ? "Checking…" : "Run check" }}
        </button>
      </template>
    </Modal>

    <Modal v-if="showQuote" title="Generate quotation" @close="showQuote = null">
      <p class="text-sm muted" style="margin-top:0">
        For {{ showQuote.customer_name }} — {{ showQuote.product_name }}, {{ showQuote.quantity_kg }} kg.
        Customer, product and quantity are locked to this feasibility check.
      </p>
      <div class="form-grid">
        <div class="field"><label>Unit price *</label><input v-model.number="quoteForm.unit_price" type="number" step="0.01" class="input" /></div>
        <div class="field"><label>Valid until</label><input v-model="quoteForm.valid_until" type="date" class="input" /></div>
      </div>
      <div class="field"><label>Terms</label><textarea v-model="quoteForm.terms" class="input" rows="2" /></div>
      <div class="field"><label>Notes</label><textarea v-model="quoteForm.notes" class="input" rows="2" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showQuote = null">Cancel</button>
        <button class="btn btn-primary" :disabled="quoting || !quoteForm.unit_price" @click="submitQuote">
          {{ quoting ? "Generating…" : "Generate quotation" }}
        </button>
      </template>
    </Modal>

    <Modal v-if="showAmend" title="Amend feasibility record (admin)" @close="showAmend = null">
      <p class="text-sm muted" style="margin-top:0">Only notes may be amended - the outcome and figures are the record of what was assessed at the time.</p>
      <div class="field"><label>Notes</label><textarea v-model="amendNotes" class="input" rows="3" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showAmend = null">Cancel</button>
        <button class="btn btn-primary" :disabled="amending" @click="submitAmend">{{ amending ? "Saving…" : "Save" }}</button>
      </template>
    </Modal>
  </div>
</template>
