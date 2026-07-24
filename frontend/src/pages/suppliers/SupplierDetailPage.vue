<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { suppliersApi } from "../../services/suppliers";
import { materialsApi } from "../../services/materials";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { SUPPLIERS_MANAGE } from "../../permissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import Modal from "../../components/ui/Modal.vue";
import ConfirmDialog from "../../components/ui/ConfirmDialog.vue";
import AttachmentsPanel from "../../components/AttachmentsPanel.vue";
import type { Supplier, Material } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = Number(route.params.id);
const supplier = ref<Supplier | null>(null);
const loading = ref(true);
const allMaterials = ref<Material[]>([]);

async function load() {
  loading.value = true;
  try {
    const [s, m] = await Promise.all([
      suppliersApi.get(id),
      materialsApi.search({ limit: 100 }),
    ]);
    supplier.value = s;
    allMaterials.value = m.materials;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load supplier.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

const showEdit = ref(false);
const editForm = reactive({ name: "", contact_person: "", phone: "", email: "", category: "", gstin: "", notes: "" });
function openEdit() {
  if (!supplier.value) return;
  Object.assign(editForm, supplier.value);
  showEdit.value = true;
}
const saving = ref(false);
async function submitEdit() {
  saving.value = true;
  try {
    supplier.value = await suppliersApi.update(id, editForm);
    ui.toast("Supplier updated.", "success");
    showEdit.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update supplier.", "error");
  } finally {
    saving.value = false;
  }
}

const showDeactivate = ref(false);
const deactivating = ref(false);
async function confirmDeactivate() {
  deactivating.value = true;
  try {
    supplier.value = await suppliersApi.deactivate(id);
    ui.toast("Supplier deactivated.", "success");
    showDeactivate.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't deactivate supplier.", "error");
  } finally {
    deactivating.value = false;
  }
}

const showSupplyTerms = ref(false);
const supplyForm = reactive({
  material_id: 0, price: 0, lead_time_days: 0, minimum_order_qty: 0,
  payment_terms: "", delivery_cost: 0,
});
const savingSupply = ref(false);
async function submitSupplyTerms() {
  savingSupply.value = true;
  try {
    supplier.value = await suppliersApi.setSupplyTerms(id, supplyForm);
    ui.toast("Supply terms saved.", "success");
    showSupplyTerms.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't save supply terms.", "error");
  } finally {
    savingSupply.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="supplier" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/suppliers')">← Suppliers</button>
        <h1 style="margin-top:8px">{{ supplier.name }}</h1>
      </div>
      <div class="row" v-if="auth.hasPermission(SUPPLIERS_MANAGE)">
        <button class="btn btn-secondary" @click="openEdit">Edit</button>
        <button v-if="supplier.status === 'active'" class="btn btn-danger" @click="showDeactivate = true">Deactivate</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Details</h3></div>
      <div class="card-body form-grid">
        <div><div class="text-xs muted">Category</div><div>{{ supplier.category || "—" }}</div></div>
        <div><div class="text-xs muted">Contact person</div><div>{{ supplier.contact_person || "—" }}</div></div>
        <div><div class="text-xs muted">Phone</div><div>{{ supplier.phone || "—" }}</div></div>
        <div><div class="text-xs muted">Email</div><div>{{ supplier.email || "—" }}</div></div>
        <div><div class="text-xs muted">GSTIN</div><div>{{ supplier.gstin || "—" }}</div></div>
        <div><div class="text-xs muted">Rating</div><div>{{ supplier.rating ? "★".repeat(supplier.rating) : "—" }}</div></div>
      </div>
    </div>

    <div class="card">
      <div class="card-header row-between">
        <h3>Materials supplied</h3>
        <button v-if="auth.hasPermission(SUPPLIERS_MANAGE)" class="btn btn-secondary btn-sm" @click="showSupplyTerms = true">
          + Add / update terms
        </button>
      </div>
      <div class="card-body" style="padding:0">
        <div v-if="!supplier.materials_supplied?.length" class="empty-state">No materials linked yet.</div>
        <table v-else class="data-table">
          <thead><tr><th>Material</th><th class="numeric">Price</th><th class="numeric">Lead time</th><th class="numeric">MOQ</th><th>Payment terms</th></tr></thead>
          <tbody>
            <tr v-for="t in supplier.materials_supplied" :key="t.id" @click="router.push(`/materials/${t.material_id}`)">
              <td>{{ t.material_name }}</td>
              <td class="numeric">₹{{ t.price }}</td>
              <td class="numeric">{{ t.lead_time_days }}d</td>
              <td class="numeric">{{ t.minimum_order_qty }} {{ t.unit }}</td>
              <td>{{ t.payment_terms || "—" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <AttachmentsPanel entity-type="supplier" :entity-id="id" />

    <Modal v-if="showEdit" title="Edit Supplier" @close="showEdit = false">
      <div class="form-grid">
        <div class="field"><label>Name</label><input v-model="editForm.name" class="input" /></div>
        <div class="field"><label>Category</label><input v-model="editForm.category" class="input" /></div>
        <div class="field"><label>Contact person</label><input v-model="editForm.contact_person" class="input" /></div>
        <div class="field"><label>Phone</label><input v-model="editForm.phone" class="input" /></div>
        <div class="field"><label>Email</label><input v-model="editForm.email" class="input" /></div>
        <div class="field"><label>GSTIN</label><input v-model="editForm.gstin" class="input" /></div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showEdit = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitEdit">{{ saving ? "Saving…" : "Save changes" }}</button>
      </template>
    </Modal>

    <Modal v-if="showSupplyTerms" title="Material supply terms" @close="showSupplyTerms = false">
      <div class="field">
        <label>Material</label>
        <select v-model.number="supplyForm.material_id" class="input">
          <option :value="0" disabled>Select a material…</option>
          <option v-for="m in allMaterials" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>
      </div>
      <div class="form-grid">
        <div class="field"><label>Price</label><input v-model.number="supplyForm.price" type="number" class="input" /></div>
        <div class="field"><label>Lead time (days)</label><input v-model.number="supplyForm.lead_time_days" type="number" class="input" /></div>
        <div class="field"><label>Minimum order qty</label><input v-model.number="supplyForm.minimum_order_qty" type="number" class="input" /></div>
        <div class="field"><label>Delivery cost</label><input v-model.number="supplyForm.delivery_cost" type="number" class="input" /></div>
      </div>
      <div class="field"><label>Payment terms</label><input v-model="supplyForm.payment_terms" class="input" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showSupplyTerms = false">Cancel</button>
        <button class="btn btn-primary" :disabled="savingSupply || !supplyForm.material_id" @click="submitSupplyTerms">
          {{ savingSupply ? "Saving…" : "Save terms" }}
        </button>
      </template>
    </Modal>

    <ConfirmDialog
      v-if="showDeactivate"
      title="Deactivate supplier"
      :message="`Deactivate ${supplier.name}?`"
      confirm-label="Deactivate"
      danger
      :busy="deactivating"
      @confirm="confirmDeactivate"
      @cancel="showDeactivate = false"
    />
  </div>
</template>
