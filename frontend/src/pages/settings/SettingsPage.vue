<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { settingsApi } from "../../services/settings";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { SETTINGS_MANAGE } from "../../permissions";
import { DISPLAY_ROLES, DISPLAY_AREAS, roleHasArea } from "../../rolePermissions";
import type { AppSettings } from "../../types";

const ui = useUiStore();
const auth = useAuthStore();
const canManage = auth.hasPermission(SETTINGS_MANAGE);

const tabs = [
  { id: "ai", label: "AI Assistant" },
  { id: "production", label: "Production" },
  { id: "company", label: "Company" },
  { id: "roles", label: "Roles & Permissions" },
] as const;
type TabId = (typeof tabs)[number]["id"];
const activeTab = ref<TabId>("ai");

const loading = ref(true);
const savingSection = ref<string | null>(null);

// Form state, seeded from the server response once loaded.
const form = reactive({
  deepseek_api_key: "",
  deepseek_model: "deepseek-chat",
  deepseek_base_url: "https://api.deepseek.com",
  batch_size_kg: 1000,
  daily_capacity_kg: 20000,
  planning_horizon_days: 30,
  app_name: "",
  company_name: "",
  company_address: "",
  company_phone: "",
  company_email: "",
  company_gstin: "",
  company_website: "",
});

const apiKeySet = ref(false);
const apiKeyPreview = ref<string | null>(null);
const showApiKey = ref(false);

function applyServerState(s: AppSettings) {
  form.deepseek_model = s.deepseek_model;
  form.deepseek_base_url = s.deepseek_base_url;
  form.batch_size_kg = s.batch_size_kg;
  form.daily_capacity_kg = s.daily_capacity_kg;
  form.planning_horizon_days = s.planning_horizon_days;
  form.app_name = s.app_name;
  form.company_name = s.company_name;
  form.company_address = s.company_address;
  form.company_phone = s.company_phone;
  form.company_email = s.company_email;
  form.company_gstin = s.company_gstin;
  form.company_website = s.company_website;
  apiKeySet.value = s.deepseek_api_key_set;
  apiKeyPreview.value = s.deepseek_api_key_preview;
  form.deepseek_api_key = ""; // never pre-filled - see backend AppSettings docstring
}

async function load() {
  loading.value = true;
  try {
    applyServerState(await settingsApi.get());
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load settings.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

async function saveAi() {
  savingSection.value = "ai";
  try {
    const body: Record<string, unknown> = {
      deepseek_model: form.deepseek_model,
      deepseek_base_url: form.deepseek_base_url,
    };
    if (form.deepseek_api_key.trim()) body.deepseek_api_key = form.deepseek_api_key.trim();
    applyServerState(await settingsApi.update(body));
    ui.toast("AI settings saved", "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't save AI settings.", "error");
  } finally {
    savingSection.value = null;
  }
}

async function saveProduction() {
  savingSection.value = "production";
  try {
    applyServerState(await settingsApi.update({
      batch_size_kg: form.batch_size_kg,
      daily_capacity_kg: form.daily_capacity_kg,
      planning_horizon_days: form.planning_horizon_days,
      app_name: form.app_name,
    }));
    ui.toast("Production settings saved", "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't save production settings.", "error");
  } finally {
    savingSection.value = null;
  }
}

async function saveCompany() {
  savingSection.value = "company";
  try {
    applyServerState(await settingsApi.update({
      company_name: form.company_name,
      company_address: form.company_address,
      company_phone: form.company_phone,
      company_email: form.company_email,
      company_gstin: form.company_gstin,
      company_website: form.company_website,
    }));
    ui.toast("Company info saved", "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't save company info.", "error");
  } finally {
    savingSection.value = null;
  }
}
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Settings</h1>
      <p>AI configuration, production parameters, company info, and role permissions</p>
    </div>

    <div class="tab-list">
      <button
        v-for="t in tabs" :key="t.id"
        class="tab" :class="{ active: activeTab === t.id }"
        @click="activeTab = t.id"
      >{{ t.label }}</button>
    </div>

    <div v-if="loading" class="card"><div class="card-body muted">Loading settings…</div></div>

    <template v-else>
      <!-- AI Assistant -->
      <div v-if="activeTab === 'ai'" class="card" style="max-width:600px;">
        <div class="card-body">
          <div class="alert-info">
            DeepSeek powers the AI Chat assistant. Get an API key at
            <a href="https://platform.deepseek.com" target="_blank" rel="noopener">platform.deepseek.com</a>.
          </div>
          <div class="field">
            <label>DeepSeek API Key</label>
            <div class="row">
              <input
                :type="showApiKey ? 'text' : 'password'"
                class="input" v-model="form.deepseek_api_key"
                :disabled="!canManage"
                :placeholder="apiKeySet ? `Currently set (${apiKeyPreview})` : 'sk-...'"
                autocomplete="new-password"
              />
              <button class="btn btn-ghost btn-sm" type="button" @click="showApiKey = !showApiKey">
                {{ showApiKey ? "Hide" : "Show" }}
              </button>
            </div>
            <p class="field-hint">Leave blank to keep the current key. Never displayed in full once saved.</p>
          </div>
          <div class="form-grid">
            <div class="field">
              <label>Model</label>
              <select v-model="form.deepseek_model" class="input" :disabled="!canManage">
                <option value="deepseek-chat">deepseek-chat</option>
                <option value="deepseek-reasoner">deepseek-reasoner</option>
              </select>
            </div>
            <div class="field">
              <label>Base URL</label>
              <input v-model="form.deepseek_base_url" class="input" :disabled="!canManage" />
            </div>
          </div>
          <button v-if="canManage" class="btn btn-primary" :disabled="savingSection === 'ai'" @click="saveAi">
            {{ savingSection === 'ai' ? "Saving…" : "Save AI Settings" }}
          </button>
        </div>
      </div>

      <!-- Production -->
      <div v-if="activeTab === 'production'" class="card" style="max-width:600px;">
        <div class="card-body">
          <div class="form-grid">
            <div class="field">
              <label>Batch Size (kg)</label>
              <input type="number" min="1" v-model.number="form.batch_size_kg" class="input" :disabled="!canManage" />
            </div>
            <div class="field">
              <label>Daily Capacity (kg)</label>
              <input type="number" min="1" v-model.number="form.daily_capacity_kg" class="input" :disabled="!canManage" />
            </div>
          </div>
          <div class="field">
            <label>Planning Horizon (days)</label>
            <input type="number" min="1" v-model.number="form.planning_horizon_days" class="input" :disabled="!canManage" />
          </div>
          <div class="field">
            <label>App Name</label>
            <input v-model="form.app_name" class="input" :disabled="!canManage" />
          </div>
          <button v-if="canManage" class="btn btn-primary" :disabled="savingSection === 'production'" @click="saveProduction">
            {{ savingSection === 'production' ? "Saving…" : "Save Production Settings" }}
          </button>
        </div>
      </div>

      <!-- Company -->
      <div v-if="activeTab === 'company'" class="card" style="max-width:600px;">
        <div class="card-body">
          <div class="alert-info">Used to auto-fill the header on printed documents - set it once here.</div>
          <div class="field">
            <label>Company Name</label>
            <input v-model="form.company_name" class="input" :disabled="!canManage" placeholder="JDK Smart Factory Pvt Ltd" />
          </div>
          <div class="field">
            <label>Address</label>
            <textarea v-model="form.company_address" class="input" rows="2" :disabled="!canManage"
              placeholder="Plot 4, SIPCOT Industrial Park, Tamil Nadu"></textarea>
          </div>
          <div class="form-grid">
            <div class="field">
              <label>Phone</label>
              <input v-model="form.company_phone" class="input" :disabled="!canManage" placeholder="+91 44 1234 5678" />
            </div>
            <div class="field">
              <label>Email</label>
              <input type="email" v-model="form.company_email" class="input" :disabled="!canManage" placeholder="sales@company.com" />
            </div>
          </div>
          <div class="form-grid">
            <div class="field">
              <label>GSTIN</label>
              <input v-model="form.company_gstin" class="input" :disabled="!canManage" placeholder="33AAAAA0000A1Z5" />
            </div>
            <div class="field">
              <label>Website</label>
              <input v-model="form.company_website" class="input" :disabled="!canManage" placeholder="www.company.com" />
            </div>
          </div>
          <button v-if="canManage" class="btn btn-primary" :disabled="savingSection === 'company'" @click="saveCompany">
            {{ savingSection === 'company' ? "Saving…" : "Save Company Info" }}
          </button>
        </div>
      </div>

      <!-- Roles & Permissions (read-only) -->
      <div v-if="activeTab === 'roles'" class="card">
        <div class="card-body">
          <div class="alert-info">
            Roles are assigned per-user on the <router-link to="/users">Users</router-link> page.
            This table shows which areas each role can see; it isn't editable here.
          </div>
          <div style="overflow-x:auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th v-for="a in DISPLAY_AREAS" :key="a.key">{{ a.label }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in DISPLAY_ROLES" :key="r.code">
                  <td><strong>{{ r.label }}</strong><div class="text-xs muted">{{ r.description }}</div></td>
                  <td v-for="a in DISPLAY_AREAS" :key="a.key" class="numeric">
                    <span :class="roleHasArea(r.code, a) ? 'badge badge-success' : 'badge badge-neutral'">
                      {{ roleHasArea(r.code, a) ? "✓" : "—" }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.tab-list {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-neutral-200);
}
.tab {
  padding: 10px 16px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-neutral-500);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.tab:hover { color: var(--color-neutral-800); }
.tab.active { color: var(--color-primary-600); border-bottom-color: var(--color-primary-500); }
</style>
