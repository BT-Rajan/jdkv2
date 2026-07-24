<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { usersApi, ASSIGNABLE_ROLES } from "../../services/users";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { USERS_MANAGE } from "../../permissions";
import DataTable, { type Column } from "../../components/ui/DataTable.vue";
import Modal from "../../components/ui/Modal.vue";
import type { UserSummary } from "../../types";

const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const rows = ref<UserSummary[]>([]);
const total = ref(0);
const loading = ref(true);
const search = ref("");
const roleFilter = ref("");
const offset = ref(0);
const limit = 20;

const columns: Column<UserSummary>[] = [
  { key: "full_name", label: "Name" },
  { key: "email", label: "Email" },
  { key: "department", label: "Department" },
  { key: "roles", label: "Roles", render: (r) => r.roles.join(", ") || "—" },
  { key: "status", label: "Status" },
];

async function load() {
  loading.value = true;
  try {
    const result = await usersApi.search({ q: search.value || undefined, role: roleFilter.value || undefined, limit, offset: offset.value });
    rows.value = result.users;
    total.value = result.total;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load users.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);
watch([search, roleFilter], () => { offset.value = 0; load(); });

const showCreate = ref(false);
const form = reactive({ email: "", initial_password: "", full_name: "", phone: "", department: "", role: "operations" });
const saving = ref(false);
async function submitCreate() {
  saving.value = true;
  try {
    const created = await usersApi.create(form);
    ui.toast("User created. They must verify their email before signing in.", "success");
    showCreate.value = false;
    router.push(`/users/${created.subject_id}`);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't create user.", "error");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="row-between page-header">
      <div>
        <h1>Users</h1>
        <p>{{ total }} total</p>
      </div>
      <button v-if="auth.hasPermission(USERS_MANAGE)" class="btn btn-primary" @click="showCreate = true">
        + New User
      </button>
    </div>

    <div class="card">
      <div class="card-header row">
        <input v-model="search" class="input" placeholder="Search by name, email, phone…" style="max-width:280px" />
        <select v-model="roleFilter" class="input" style="max-width:200px">
          <option value="">All roles</option>
          <option v-for="r in ASSIGNABLE_ROLES" :key="r.code" :value="r.code">{{ r.label }}</option>
        </select>
      </div>
      <div class="card-body" style="padding:0">
        <DataTable
          :columns="columns" :rows="rows" :loading="loading"
          :total="total" :limit="limit" :offset="offset"
          empty-message="No users found."
          @row-click="(r) => router.push(`/users/${r.subject_id}`)"
          @page-change="(o) => { offset = o; load(); }"
        />
      </div>
    </div>

    <Modal v-if="showCreate" title="New User" @close="showCreate = false">
      <div class="form-grid">
        <div class="field"><label>Full name *</label><input v-model="form.full_name" class="input" required /></div>
        <div class="field"><label>Email *</label><input v-model="form.email" type="email" class="input" required /></div>
        <div class="field"><label>Initial password *</label><input v-model="form.initial_password" type="password" class="input" required /></div>
        <div class="field">
          <label>Role *</label>
          <select v-model="form.role" class="input">
            <option v-for="r in ASSIGNABLE_ROLES" :key="r.code" :value="r.code">{{ r.label }}</option>
          </select>
        </div>
        <div class="field"><label>Phone</label><input v-model="form.phone" class="input" /></div>
        <div class="field"><label>Department</label><input v-model="form.department" class="input" /></div>
      </div>
      <p class="field-hint">The new user must verify their email (link sent to their address) before they can sign in.</p>
      <template #footer>
        <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving || !form.email || !form.full_name || !form.initial_password" @click="submitCreate">
          {{ saving ? "Creating…" : "Create User" }}
        </button>
      </template>
    </Modal>
  </div>
</template>
