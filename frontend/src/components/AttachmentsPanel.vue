<script setup lang="ts">
import { ref, onMounted } from "vue";
import { attachmentsApi } from "../services/attachments";
import { useUiStore } from "../stores/ui";
import { useAuthStore } from "../stores/auth";
import { FILE_UPLOAD, FILE_DELETE } from "../permissions";
import type { Attachment } from "../types";

const props = defineProps<{ entityType: string; entityId: string | number }>();

const ui = useUiStore();
const auth = useAuthStore();
const attachments = ref<Attachment[]>([]);
const loading = ref(true);
const uploading = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

async function load() {
  loading.value = true;
  try {
    attachments.value = await attachmentsApi.list(props.entityType, props.entityId);
  } catch (e: any) {
    ui.toast(e.message || "Couldn't load attachments.", "error");
  } finally {
    loading.value = false;
  }
}
onMounted(load);

async function handleFileChosen(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  uploading.value = true;
  try {
    await attachmentsApi.upload(props.entityType, props.entityId, file);
    ui.toast("File uploaded.", "success");
    await load();
  } catch (err: any) {
    ui.toast(err.message || "Upload failed.", "error");
  } finally {
    uploading.value = false;
    if (fileInput.value) fileInput.value.value = "";
  }
}

async function handleDownload(a: Attachment) {
  try {
    const { blob, filename } = await attachmentsApi.download(a.id);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename || a.filename;
    link.click();
    URL.revokeObjectURL(url);
  } catch (e: any) {
    ui.toast(e.message || "Download failed.", "error");
  }
}

async function handleDelete(a: Attachment) {
  try {
    await attachmentsApi.delete(a.id);
    attachments.value = attachments.value.filter((x) => x.id !== a.id);
    ui.toast("Attachment removed.", "success");
  } catch (e: any) {
    ui.toast(e.message || "Couldn't remove attachment.", "error");
  }
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h3>Attachments</h3>
      <div v-if="auth.hasPermission(FILE_UPLOAD)">
        <input ref="fileInput" type="file" class="visually-hidden" @change="handleFileChosen" />
        <button class="btn btn-secondary btn-sm" :disabled="uploading" @click="fileInput?.click()">
          {{ uploading ? "Uploading…" : "+ Upload file" }}
        </button>
      </div>
    </div>
    <div class="card-body" style="padding:0">
      <div v-if="loading" class="empty-state">Loading…</div>
      <div v-else-if="!attachments.length" class="empty-state">No files attached yet.</div>
      <table v-else class="data-table">
        <thead><tr><th>File</th><th>Uploaded</th><th></th></tr></thead>
        <tbody>
          <tr v-for="a in attachments" :key="a.id" style="cursor:default">
            <td>{{ a.filename }}</td>
            <td class="text-sm muted">{{ new Date(a.created_at).toLocaleString() }}</td>
            <td class="row" style="justify-content:flex-end">
              <button class="btn btn-ghost btn-sm" @click="handleDownload(a)">Download</button>
              <button v-if="auth.hasPermission(FILE_DELETE)" class="btn btn-ghost btn-sm" @click="handleDelete(a)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
