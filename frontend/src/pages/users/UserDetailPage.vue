<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { usersApi, ASSIGNABLE_ROLES } from "../../services/users";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { USERS_MANAGE } from "../../permissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import StatusBadge from "../../components/ui/StatusBadge.vue";
import Modal from "../../components/ui/Modal.vue";
import ConfirmDialog from "../../components/ui/ConfirmDialog.vue";
import type { UserSummary, AuditEntry } from "../../types";

const route = useRoute();
const router = useRouter();
const ui = useUiStore();
const auth = useAuthStore();

const subjectId = route.params.id as string;
const user = ref<UserSummary | null>(null);
const audit = ref<AuditEntry[]>([]);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    const [u, a] = await Promise.all([usersApi.get(subjectId), usersApi.audit(subjectId)]);
    user.value = u;
    audit.value = a;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load user.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

const showEdit = ref(false);
const editForm = reactive({ full_name: "", phone: "", department: "" });
function openEdit() {
  if (!user.value) return;
  Object.assign(editForm, user.value);
  showEdit.value = true;
}
const saving = ref(false);
async function submitEdit() {
  saving.value = true;
  try {
    user.value = await usersApi.updateProfile(subjectId, editForm);
    ui.toast("Profile updated.", "success");
    showEdit.value = false;
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update profile.", "error");
  } finally {
    saving.value = false;
  }
}

const showRoleChange = ref(false);
const newRole = ref("");
const changingRole = ref(false);
function openRoleChange() {
  newRole.value = user.value?.roles[0] || "operations";
  showRoleChange.value = true;
}
async function submitRoleChange() {
  changingRole.value = true;
  try {
    user.value = await usersApi.changeRole(subjectId, newRole.value);
    ui.toast("Role updated.", "success");
    showRoleChange.value = false;
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't update role.", "error");
  } finally {
    changingRole.value = false;
  }
}

const showDeactivate = ref(false);
const deactivating = ref(false);
async function confirmDeactivate() {
  deactivating.value = true;
  try {
    user.value = await usersApi.deactivate(subjectId);
    ui.toast("User deactivated.", "success");
    showDeactivate.value = false;
    await load();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't deactivate user.", "error");
  } finally {
    deactivating.value = false;
  }
}

function describeAction(a: AuditEntry): string {
  const labels: Record<string, string> = {
    "user.created": "Account created",
    "user.profile_updated": "Profile updated",
    "user.role_changed": "Role changed",
    "user.deactivated": "Deactivated",
  };
  return labels[a.action] || a.action;
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else-if="user" class="stack">
    <div class="row-between page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="router.push('/users')">← Users</button>
        <h1 style="margin-top:8px">{{ user.full_name || user.email }}</h1>
        <div class="row" style="margin-top:6px"><StatusBadge :status="user.status" /></div>
      </div>
      <div class="row" v-if="auth.hasPermission(USERS_MANAGE)">
        <button class="btn btn-secondary" @click="openEdit">Edit profile</button>
        <button class="btn btn-secondary" @click="openRoleChange">Change role</button>
        <button v-if="user.status !== 'disabled'" class="btn btn-danger" @click="showDeactivate = true">Deactivate</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Details</h3></div>
      <div class="card-body form-grid">
        <div><div class="text-xs muted">Email</div><div>{{ user.email }}</div></div>
        <div><div class="text-xs muted">Phone</div><div>{{ user.phone || "—" }}</div></div>
        <div><div class="text-xs muted">Department</div><div>{{ user.department || "—" }}</div></div>
        <div><div class="text-xs muted">Roles</div><div>{{ user.roles.join(", ") || "—" }}</div></div>
        <div><div class="text-xs muted">Member since</div><div>{{ new Date(user.created_at).toLocaleDateString() }}</div></div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Audit trail</h3></div>
      <div class="card-body" style="padding:0">
        <div v-if="!audit.length" class="empty-state">No history yet.</div>
        <table v-else class="data-table">
          <thead><tr><th>Action</th><th>Date</th></tr></thead>
          <tbody>
            <tr v-for="(a, i) in audit" :key="i" style="cursor:default">
              <td>{{ describeAction(a) }}</td>
              <td class="text-sm muted">{{ new Date(a.created_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal v-if="showEdit" title="Edit profile" @close="showEdit = false">
      <div class="field"><label>Full name</label><input v-model="editForm.full_name" class="input" /></div>
      <div class="field"><label>Phone</label><input v-model="editForm.phone" class="input" /></div>
      <div class="field"><label>Department</label><input v-model="editForm.department" class="input" /></div>
      <template #footer>
        <button class="btn btn-secondary" @click="showEdit = false">Cancel</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitEdit">{{ saving ? "Saving…" : "Save changes" }}</button>
      </template>
    </Modal>

    <Modal v-if="showRoleChange" title="Change role" @close="showRoleChange = false">
      <p class="text-sm muted" style="margin-bottom: var(--space-4)">
        This replaces all current role assignments with the selected role.
      </p>
      <div class="field">
        <label>New role</label>
        <select v-model="newRole" class="input">
          <option v-for="r in ASSIGNABLE_ROLES" :key="r.code" :value="r.code">{{ r.label }}</option>
        </select>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showRoleChange = false">Cancel</button>
        <button class="btn btn-primary" :disabled="changingRole" @click="submitRoleChange">
          {{ changingRole ? "Updating…" : "Update role" }}
        </button>
      </template>
    </Modal>

    <ConfirmDialog
      v-if="showDeactivate"
      title="Deactivate user"
      message="This revokes all active sessions and removes all role assignments. The account record is preserved."
      confirm-label="Deactivate"
      danger
      :busy="deactivating"
      @confirm="confirmDeactivate"
      @cancel="showDeactivate = false"
    />
  </div>
</template>
