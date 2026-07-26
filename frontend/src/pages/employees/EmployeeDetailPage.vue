<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { employeesApi } from "../../services/employees";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { EMPLOYEES_MANAGE } from "../../permissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import Modal from "../../components/ui/Modal.vue";
import ConfirmDialog from "../../components/ui/ConfirmDialog.vue";
import type { Employee } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const id = Number(route.params.id);
const employee = ref<Employee | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    employee.value = await employeesApi.get(id);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load this record.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

const showEdit = ref(false);
const editForm = reactive({
  full_name: "", designation: "", phone: "", email: "", address: "",
  start_date: "", end_date: "", role: "",
});
function openEdit() {
  if (!employee.value) return;
  Object.assign(editForm, {
    ...employee.value,
    start_date: employee.value.start_date || "",
    end_date: employee.value.end_date || "",
  });
  showEdit.value = true;
}
const saving = ref(false);
async function submitEdit() {
  saving.value = true;
  try {
    employee.value = await employeesApi.update(id, {
      ...editForm,
      start_date: editForm.start_date || null,
      end_date: editForm.end_date || null,
    } as Partial<Employee>);
    ui.toast("Record updated.", "success");
    showEdit.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update this record.", "error");
  } finally {
    saving.value = false;
  }
}

const showDelete = ref(false);
const deleting = ref(false);
async function confirmDelete() {
  deleting.value = true;
  try {
    await employeesApi.delete(id);
    ui.toast("Removed.", "success");
    router.push("/users-directory");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't remove this record.", "error");
  } finally {
    deleting.value = false;
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="employee" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/users-directory')">← Employees</button>
        <h1 style="margin-top:8px">{{ employee.full_name }}</h1>
        <div class="text-sm muted" style="margin-top:4px">{{ employee.designation || "—" }}</div>
      </div>
      <div class="row" v-if="auth.hasPermission(EMPLOYEES_MANAGE)">
        <button class="btn btn-secondary" @click="openEdit">Edit</button>
        <button class="btn btn-danger" @click="showDelete = true">Remove</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Details</h3></div>
      <div class="card-body form-grid">
        <div><div class="text-xs muted">Designation</div><div>{{ employee.designation || "—" }}</div></div>
        <div><div class="text-xs muted">id</div><div>{{ employee.id }}</div></div>
        <div><div class="text-xs muted">Phone</div><div>{{ employee.phone || "—" }}</div></div>
        <div><div class="text-xs muted">Email</div><div>{{ employee.email || "—" }}</div></div>
        <div><div class="text-xs muted">Start-date</div><div>{{ employee.start_date || "—" }}</div></div>
        <div><div class="text-xs muted">end-date</div><div>{{ employee.end_date || "Current" }}</div></div>
        <div><div class="text-xs muted">role</div><div>{{ employee.role || "—" }}</div></div>
        <div style="grid-column: 1 / -1"><div class="text-xs muted">Address</div><div>{{ employee.address || "—" }}</div></div>
      </div>
    </div>

    <Modal v-if="showEdit" title="Edit User" wide @close="showEdit = false">
      <div class="form-grid">
        <div class="field"><label>Name</label><input v-model="editForm.full_name" class="input" /></div>
        <div class="field"><label>Designation</label><input v-model="editForm.designation" class="input" /></div>
        <div class="field"><label>Phone</label><input v-model="editForm.phone" class="input" /></div>
        <div class="field"><label>Email</label><input v-model="editForm.email" class="input" /></div>
        <div class="field"><label>Start-date</label><input v-model="editForm.start_date" type="date" class="input" /></div>
        <div class="field"><label>end-date</label><input v-model="editForm.end_date" type="date" class="input" /></div>
        <div class="field"><label>role</label><input v-model="editForm.role" class="input" /></div>
        <div class="field" style="grid-column:1/-1"><label>Address</label><textarea v-model="editForm.address" class="input" rows="2" /></div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showEdit = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitEdit">{{ saving ? "Saving…" : "Save changes" }}</button>
      </template>
    </Modal>

    <ConfirmDialog
      v-if="showDelete"
      title="Remove user"
      :message="`Remove ${employee.full_name} from the directory? This can't be undone.`"
      confirm-label="Remove"
      danger
      :busy="deleting"
      @confirm="confirmDelete"
      @cancel="showDelete = false"
    />
  </div>
</template>
