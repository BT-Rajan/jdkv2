<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { employeesApi } from "../../services/employees";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { EMPLOYEES_MANAGE } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { Employee } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<Employee[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<Employee>[] = [
  { key: "full_name", label: "Name" },
  { key: "designation", label: "Designation" },
  { key: "phone", label: "Phone" },
  { key: "role", label: "Role" },
  { key: "start_date", label: "Start Date" },
  { key: "end_date", label: "End Date", render: (r) => r.end_date || "Current" },
];

async function load() {
  loading.value = true;
  try {
    const result = await employeesApi.search({ q: search.value || undefined, limit, offset: offset.value });
    rows.value = result.employees;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load employees.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch(search, () => { offset.value = 0; load(); });

const showCreate = ref(false);
const emptyForm = () => ({
  full_name: "", designation: "", phone: "", email: "", address: "",
  start_date: "", end_date: "", role: "",
});
const form = reactive(emptyForm());
const saving = ref(false);
async function submitCreate() {
  saving.value = true;
  try {
    const created = await employeesApi.create({
      ...form,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
    } as Partial<Employee>);
    ui.toast("User added.", "success");
    showCreate.value = false;
    Object.assign(form, emptyForm());
    router.push(`/users-directory/${created.id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't add user.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Employees</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(EMPLOYEES_MANAGE)" class="btn btn-primary" @click="showCreate = true">
        + Add User
      </button>
    </div>

    <div class="card">
      <div class="card-header">
        <input v-model="search" class="input" placeholder="Search by name…" style="max-width:300px" />
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No users found."
          @row-click="(r) => router.push(`/users-directory/${r.id}`)"
          @page-change="(o) => { offset = o; load(); }"
        />
      </div>
    </div>

    <Modal v-if="showCreate" title="Add User" wide @close="showCreate = false">
      <div class="form-grid">
        <div class="field"><label>Name *</label><input v-model="form.full_name" class="input" required /></div>
        <div class="field"><label>Designation</label><input v-model="form.designation" class="input" /></div>
        <div class="field"><label>id</label><div class="input" style="opacity:.6">(assigned automatically)</div></div>
        <div class="field"><label>Phone</label><input v-model="form.phone" class="input" /></div>
        <div class="field"><label>Email</label><input v-model="form.email" class="input" /></div>
        <div class="field"><label>Start-date</label><input v-model="form.start_date" type="date" class="input" /></div>
        <div class="field"><label>end-date</label><input v-model="form.end_date" type="date" class="input" /></div>
        <div class="field"><label>role</label><input v-model="form.role" class="input" /></div>
        <div class="field" style="grid-column:1/-1"><label>Address</label><textarea v-model="form.address" class="input" rows="2" /></div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.full_name" @click="submitCreate">
          {{ saving ? "Adding…" : "Add User" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
