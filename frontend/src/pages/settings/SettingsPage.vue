<script setup lang="ts">
import { reactive, ref, computed, onMounted, onBeforeUnmount } from "vue";
import { settingsApi } from "../../services/settings";
import { attachmentsApi } from "../../services/attachments";
import { useUiStore } from "../../stores/ui";
import { useAuthStore } from "../../stores/auth";
import { SETTINGS_MANAGE, FILE_UPLOAD, FILE_VIEW, FILE_DELETE } from "../../permissions";
import { DISPLAY_ROLES, DISPLAY_AREAS, roleHasArea } from "../../rolePermissions";
import LoadingSpinner from "../../components/ui/LoadingSpinner.vue";
import type { AppSettings, Attachment } from "../../types";

const ui = useUiStore();
const auth = useAuthStore();
const canManage = auth.hasPermission(SETTINGS_MANAGE);

const tabs = [
  { id: "ai", label: "AI Assistant", icon: "✦" },
  { id: "production", label: "Production", icon: "▧" },
  { id: "company", label: "Company", icon: "▢" },
  { id: "roles", label: "Roles & Permissions", icon: "◍" },
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
  assistant_system_prompt: "",
  assistant_data_scope: "",
  batch_size_kg: 1000,
  daily_capacity_kg: 20000,
  planning_horizon_days: 30,
  app_name: "",
  company_name: "",
  company_address: "",
  company_phone: "",
  company_email: "",
  company_tax_id: "",
  company_website: "",
});

const apiKeySet = ref(false);
const apiKeyPreview = ref<string | null>(null);
const showApiKey = ref(false);

function applyServerState(s: AppSettings) {
  form.deepseek_model = s.deepseek_model;
  form.deepseek_base_url = s.deepseek_base_url;
  form.assistant_system_prompt = s.assistant_system_prompt;
  form.assistant_data_scope = s.assistant_data_scope;
  form.batch_size_kg = s.batch_size_kg;
  form.daily_capacity_kg = s.daily_capacity_kg;
  form.planning_horizon_days = s.planning_horizon_days;
  form.app_name = s.app_name;
  form.company_name = s.company_name;
  form.company_address = s.company_address;
  form.company_phone = s.company_phone;
  form.company_email = s.company_email;
  form.company_tax_id = s.company_tax_id;
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
onMounted(async () => {
  await load();
  await loadLogo();
});

async function saveAi() {
  savingSection.value = "ai";
  try {
    const body: Record<string, unknown> = {
      deepseek_model: form.deepseek_model,
      deepseek_base_url: form.deepseek_base_url,
      assistant_system_prompt: form.assistant_system_prompt,
      assistant_data_scope: form.assistant_data_scope,
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
      company_tax_id: form.company_tax_id,
      company_website: form.company_website,
    }));
    ui.toast("Company info saved", "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't save company info.", "error");
  } finally {
    savingSection.value = null;
  }
}

// ── Company logo ──────────────────────────────────────────────────────────
// Reuses the generic attachments system (entity_type="company",
// entity_id="logo") rather than a bespoke upload path, and stores the
// resulting attachment id in settings so the letterhead can reference it.
const LOGO_ENTITY_TYPE = "company";
const LOGO_ENTITY_ID = "logo";

const companyLogo = ref<Attachment | null>(null);
const logoPreviewUrl = ref<string | null>(null);
const logoLoading = ref(true);
const logoUploading = ref(false);
const logoInput = ref<HTMLInputElement | null>(null);

async function refreshLogoPreview() {
  if (logoPreviewUrl.value) URL.revokeObjectURL(logoPreviewUrl.value);
  logoPreviewUrl.value = null;
  if (!companyLogo.value || !auth.hasPermission(FILE_VIEW)) return;
  try {
    const { blob } = await attachmentsApi.download(companyLogo.value.id);
    logoPreviewUrl.value = URL.createObjectURL(blob);
  } catch {
    // Non-fatal - the filename still shows even if the preview fails.
  }
}

async function loadLogo() {
  if (!auth.hasPermission(FILE_VIEW)) { logoLoading.value = false; return; }
  logoLoading.value = true;
  try {
    const existing = await attachmentsApi.list(LOGO_ENTITY_TYPE, LOGO_ENTITY_ID);
    companyLogo.value = existing[0] || null;
    await refreshLogoPreview();
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load the company logo.", "error");
  } finally {
    logoLoading.value = false;
  }
}

async function handleLogoChosen(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    ui.toast("Please choose an image file.", "error");
    if (logoInput.value) logoInput.value.value = "";
    return;
  }
  logoUploading.value = true;
  try {
    if (companyLogo.value) await attachmentsApi.delete(companyLogo.value.id);
    const uploaded = await attachmentsApi.upload(LOGO_ENTITY_TYPE, LOGO_ENTITY_ID, file);
    applyServerState(await settingsApi.update({ company_logo_attachment_id: uploaded.id }));
    companyLogo.value = uploaded;
    await refreshLogoPreview();
    ui.toast("Logo uploaded.", "success");
  } catch (err: any) {
    ui.toast(err.message || "Logo upload failed.", "error");
  } finally {
    logoUploading.value = false;
    if (logoInput.value) logoInput.value.value = "";
  }
}

async function removeLogo() {
  if (!companyLogo.value) return;
  logoUploading.value = true;
  try {
    await attachmentsApi.delete(companyLogo.value.id);
    applyServerState(await settingsApi.update({ company_logo_attachment_id: "" }));
    companyLogo.value = null;
    await refreshLogoPreview();
    ui.toast("Logo removed.", "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't remove the logo.", "error");
  } finally {
    logoUploading.value = false;
  }
}

onBeforeUnmount(() => {
  if (logoPreviewUrl.value) URL.revokeObjectURL(logoPreviewUrl.value);
});

const canUploadFiles = computed(() => canManage && auth.hasPermission(FILE_UPLOAD));
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
      ><span class="tab-icon">{{ t.icon }}</span>{{ t.label }}</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- AI Assistant -->
      <div v-if="activeTab === 'ai'" class="stack">
        <div class="card">
          <div class="card-header"><h3>DeepSeek connection</h3></div>
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
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3>Assistant behavior</h3></div>
          <div class="card-body">
            <div class="field">
              <label>Character &amp; style</label>
              <textarea
                v-model="form.assistant_system_prompt" class="input" rows="5" :disabled="!canManage"
                placeholder="e.g. Speak concisely and professionally. Focus on production, inventory, and order questions. Avoid speculation - point to the relevant JDK page when unsure."
              ></textarea>
              <p class="field-hint">Sets the assistant's tone and personality when it responds to staff.</p>
            </div>
            <div class="field">
              <label>Data this assistant can access</label>
              <textarea
                v-model="form.assistant_data_scope" class="input" rows="5" :disabled="!canManage"
                placeholder="e.g. Product names, formulas, and stock levels. Never share customer contact details, pricing, or supplier terms."
              ></textarea>
              <p class="field-hint">Describes what JDK data is in scope to share with the AI when answering.</p>
            </div>
            <button v-if="canManage" class="btn btn-primary" :disabled="savingSection === 'ai'" @click="saveAi">
              {{ savingSection === 'ai' ? "Saving…" : "Save AI Settings" }}
            </button>
          </div>
        </div>
      </div>

      <!-- Production -->
      <div v-if="activeTab === 'production'" class="stack">
        <div class="card">
          <div class="card-header"><h3>Factory-wide defaults</h3></div>
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
        <div class="alert-info">
          Batch size, timing, manpower, and machinery for an individual product are set on that
          product's own page under <router-link to="/products">Products &amp; Formulas</router-link> -
          each product runs its own production cycle.
        </div>
      </div>

      <!-- Company -->
      <div v-if="activeTab === 'company'" class="stack">
        <div class="card">
          <div class="card-header"><h3>Letterhead</h3></div>
          <div class="card-body">
            <div class="alert-info">Used to auto-fill the header on printed documents - set it once here.</div>
            <div class="field">
              <label>Company Name</label>
              <input v-model="form.company_name" class="input" :disabled="!canManage" placeholder="JDK Smart Factory Pvt Ltd" />
            </div>
            <div class="field">
              <label>Address</label>
              <textarea v-model="form.company_address" class="input" rows="2" :disabled="!canManage"
                placeholder="Shuwaikh Industrial Area, Block 3, Kuwait City, Kuwait"></textarea>
            </div>
            <div class="form-grid">
              <div class="field">
                <label>Phone</label>
                <input v-model="form.company_phone" class="input" :disabled="!canManage" placeholder="+965 2xxx xxxx" />
              </div>
              <div class="field">
                <label>Email</label>
                <input type="email" v-model="form.company_email" class="input" :disabled="!canManage" placeholder="sales@company.com" />
              </div>
            </div>
            <div class="form-grid">
              <div class="field">
                <label>Tax ID</label>
                <input v-model="form.company_tax_id" class="input" :disabled="!canManage" placeholder="e.g. 123456789012345" />
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

        <div class="card" v-if="auth.hasPermission(FILE_VIEW)">
          <div class="card-header"><h3>Logo</h3></div>
          <div class="card-body">
            <p class="text-sm muted" style="margin-bottom: var(--space-4)">Shown on printed documents alongside the letterhead above.</p>
            <div v-if="logoLoading" class="muted text-sm">Loading…</div>
            <div v-else class="row" style="align-items:flex-start; gap: var(--space-5)">
              <div class="logo-preview">
                <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="Company logo" />
                <span v-else class="muted text-sm">No logo uploaded</span>
              </div>
              <div v-if="canUploadFiles" class="stack" style="gap: var(--space-2)">
                <input ref="logoInput" type="file" accept="image/*" class="visually-hidden" @change="handleLogoChosen" />
                <button class="btn btn-secondary btn-sm" :disabled="logoUploading" @click="logoInput?.click()">
                  {{ logoUploading ? "Working…" : companyLogo ? "Replace logo" : "Upload logo" }}
                </button>
                <button
                  v-if="companyLogo && auth.hasPermission(FILE_DELETE)"
                  class="btn btn-ghost btn-sm" :disabled="logoUploading" @click="removeLogo"
                >Remove logo</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Roles & Permissions (read-only) -->
      <div v-if="activeTab === 'roles'" class="card">
        <div class="card-header"><h3>Role matrix</h3></div>
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
  margin-bottom: var(--space-5);
  border-bottom: 1px solid var(--color-neutral-200);
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 10px 16px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-neutral-500);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.tab:hover { color: var(--color-neutral-800); }
.tab.active { color: var(--color-primary-600); border-bottom-color: var(--color-primary-500); }
.tab-icon { width: 16px; text-align: center; color: inherit; opacity: 0.85; }

.logo-preview {
  width: 160px;
  height: 100px;
  border: 1px dashed var(--color-neutral-300);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2);
  flex-shrink: 0;
}
.logo-preview img { max-width: 100%; max-height: 100%; object-fit: contain; }
</style>
