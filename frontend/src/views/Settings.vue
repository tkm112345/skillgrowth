<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t } = useI18n()

const form = reactive({
  openai_base_url: '',
  openai_api_key: '',
  llm_model: '',
  llm_vision_model: '',
})
const loading = ref(true)
const saving = ref(false)
const downloadingBackup = ref(false)
const importing = ref(false)
const importFile = ref(null)
const loadingSample = ref(false)
const testing = ref(false)
const testResult = ref(null)

onMounted(async () => {
  try {
    const settings = await api.getSettings()
    Object.assign(form, settings)
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await api.testSettings(form)
  } catch (e) {
    testResult.value = { ok: false, message: e.message }
  } finally {
    testing.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await api.updateSettings(form)
    ElMessage.success(t('settings.saveSuccess'))
  } catch (e) {
    ElMessage.error(t('settings.saveError', { error: e.message }))
  } finally {
    saving.value = false
  }
}

async function downloadBackup() {
  downloadingBackup.value = true
  try {
    const data = await api.getBackup()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `skillgrowth-backup-${data.exported_at.slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error(t('settings.backupError', { error: e.message }))
  } finally {
    downloadingBackup.value = false
  }
}

function importedCount(counts) {
  return Object.values(counts).reduce((sum, n) => sum + n, 0)
}

function handleImportFileChange(uploadFile) {
  importFile.value = uploadFile.raw
}

async function submitImport() {
  if (!importFile.value) return
  await ElMessageBox.confirm(t('settings.confirmImport'), t('profile.confirm'))
  importing.value = true
  try {
    const text = await importFile.value.text()
    const data = JSON.parse(text)
    const counts = await api.importBackup(data)
    ElMessage.success(t('settings.importSuccess', { count: importedCount(counts) }))
    importFile.value = null
  } catch (e) {
    ElMessage.error(t('settings.importError', { error: e.message }))
  } finally {
    importing.value = false
  }
}

async function loadSample() {
  await ElMessageBox.confirm(t('settings.confirmLoadSample'), t('profile.confirm'))
  loadingSample.value = true
  try {
    const counts = await api.loadSampleData()
    ElMessage.success(t('settings.importSuccess', { count: importedCount(counts) }))
  } catch (e) {
    ElMessage.error(t('settings.importError', { error: e.message }))
  } finally {
    loadingSample.value = false
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('settings.title') }}</h1>
  <p class="page-subtitle">{{ t('settings.subtitle') }}</p>

  <el-form :model="form" label-width="160px" v-loading="loading" class="form">
    <el-form-item :label="t('settings.baseUrl')">
      <el-input v-model="form.openai_base_url" placeholder="https://api.openai.com/v1" />
    </el-form-item>
    <el-form-item :label="t('settings.apiKey')">
      <el-input v-model="form.openai_api_key" type="password" show-password />
    </el-form-item>
    <el-form-item :label="t('settings.textModel')">
      <el-input v-model="form.llm_model" placeholder="gpt-4o-mini" />
    </el-form-item>
    <el-form-item :label="t('settings.visionModel')">
      <el-input v-model="form.llm_vision_model" placeholder="gpt-4o-mini" />
    </el-form-item>
    <div class="form-actions">
      <el-button @click="testConnection" :loading="testing">{{ t('settings.testConnection') }}</el-button>
      <el-button type="primary" :loading="saving" @click="save">{{ t('settings.save') }}</el-button>
    </div>

    <el-alert
      v-if="testResult"
      class="test-result"
      :type="testResult.ok ? 'success' : 'error'"
      :title="testResult.ok ? t('settings.testSuccess') : t('settings.testFailure', { error: testResult.message })"
      :closable="false"
      show-icon
    />
  </el-form>

  <el-card shadow="never" class="backup-card">
    <template #header>{{ t('settings.backupHeader') }}</template>
    <p class="backup-hint">{{ t('settings.backupHint') }}</p>
    <el-button :loading="downloadingBackup" @click="downloadBackup">{{ t('settings.backupDownload') }}</el-button>
  </el-card>

  <el-card shadow="never" class="backup-card">
    <template #header>{{ t('settings.importHeader') }}</template>
    <p class="backup-hint">{{ t('settings.importHint') }}</p>
    <el-upload :auto-upload="false" :show-file-list="true" :limit="1" accept=".json" :on-change="handleImportFileChange">
      <el-button size="small">{{ t('common.add') }}</el-button>
    </el-upload>
    <el-button :loading="importing" @click="submitImport" class="import-btn">{{ t('settings.importSubmit') }}</el-button>
  </el-card>

  <el-card shadow="never" class="backup-card">
    <template #header>{{ t('settings.sampleHeader') }}</template>
    <p class="backup-hint">{{ t('settings.sampleHint') }}</p>
    <el-button :loading="loadingSample" @click="loadSample">{{ t('settings.sampleLoad') }}</el-button>
  </el-card>
</template>

<style scoped>
.form {
  max-width: 480px;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.test-result {
  margin-top: 0.75rem;
}

.backup-card {
  max-width: 480px;
  margin-top: 1.5rem;
}

.backup-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-top: 0;
}

.import-btn {
  margin-top: 0.75rem;
}
</style>
