<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { setLocale } from '../i18n'
import { ACCENT_HUES, accentHue, setAccentHue, setThemeMode, themeMode } from '../theme'

const { t, locale } = useI18n()

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
const resettingSample = ref(false)
const testing = ref(false)
const testResult = ref(null)
const aboutVisible = ref(false)
const version = ref('')

onMounted(async () => {
  try {
    const settings = await api.getSettings()
    Object.assign(form, settings)
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
  try {
    const res = await fetch('/api/version')
    version.value = (await res.json()).version
  } catch (e) {
    // version display is cosmetic; ignore failures silently
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

async function resetSample() {
  await ElMessageBox.confirm(t('settings.confirmResetSample'), t('profile.confirm'))
  resettingSample.value = true
  try {
    await api.resetSampleData()
    ElMessage.success(t('settings.sampleResetSuccess'))
  } catch (e) {
    ElMessage.error(t('settings.importError', { error: e.message }))
  } finally {
    resettingSample.value = false
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('settings.title') }}</h1>
  <p class="page-subtitle">{{ t('settings.subtitle') }}</p>

  <el-card shadow="never" class="backup-card accent-blue">
    <template #header>{{ t('settings.appearanceHeader') }}</template>

    <div class="appearance-row">
      <div class="appearance-label">{{ t('settings.languageHeader') }}</div>
      <el-select :model-value="locale" @update:model-value="setLocale" size="small" class="lang-select">
        <el-option value="en" label="English" />
        <el-option value="ja" label="日本語" />
      </el-select>
    </div>

    <div class="appearance-row">
      <div class="appearance-label">{{ t('settings.themeMode') }}</div>
      <el-radio-group :model-value="themeMode" @update:model-value="setThemeMode" size="small">
        <el-radio-button value="system">{{ t('settings.themeSystem') }}</el-radio-button>
        <el-radio-button value="light">{{ t('settings.themeLight') }}</el-radio-button>
        <el-radio-button value="dark">{{ t('settings.themeDark') }}</el-radio-button>
      </el-radio-group>
    </div>

    <div class="appearance-row">
      <div class="appearance-label">{{ t('settings.themeColor') }}</div>
      <div class="accent-swatches">
        <button
          v-for="hue in ACCENT_HUES"
          :key="hue"
          type="button"
          class="accent-swatch"
          :class="{ 'accent-swatch-active': (accentHue || 'blue') === hue }"
          :style="{ background: `var(--hue-${hue})` }"
          :aria-label="hue"
          @click="setAccentHue(hue)"
        />
      </div>
    </div>
  </el-card>

  <el-form :model="form" label-width="160px" v-loading="loading">
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
    <div class="form-actions">
      <el-button :loading="loadingSample" @click="loadSample">{{ t('settings.sampleLoad') }}</el-button>
      <el-button :loading="resettingSample" type="danger" plain @click="resetSample">
        {{ t('settings.sampleReset') }}
      </el-button>
    </div>
  </el-card>

  <el-card shadow="never" class="backup-card">
    <template #header>{{ t('settings.aboutHeader') }}</template>
    <el-button @click="aboutVisible = true">{{ t('settings.aboutOpen') }}</el-button>
  </el-card>

  <el-dialog v-model="aboutVisible" :title="t('settings.aboutHeader')" width="420px">
    <p class="about-line">
      <strong>{{ t('app.brand') }}</strong>
      <span v-if="version"> · v{{ version }}</span>
    </p>
    <p class="about-line">{{ t('settings.aboutLicense') }}</p>
    <p class="about-line">{{ t('settings.aboutFeedback') }}</p>
    <a
      class="about-link"
      href="https://github.com/tkm112345/skillgrowth/issues"
      target="_blank"
      rel="noopener noreferrer"
    >
      {{ t('settings.aboutGithubLink') }} ↗
    </a>
    <template #footer>
      <el-button @click="aboutVisible = false">{{ t('common.close') }}</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.test-result {
  margin-top: 0.75rem;
}

.backup-card {
  margin-top: 1.5rem;
}

.lang-select {
  width: 140px;
}

.appearance-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.appearance-row:last-child {
  margin-bottom: 0;
}

.appearance-label {
  width: 100px;
  flex-shrink: 0;
  font-size: 0.85rem;
  color: var(--ink-secondary);
}

.accent-swatches {
  display: flex;
  gap: 0.5rem;
}

.accent-swatch {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid transparent;
  padding: 0;
  cursor: pointer;
}

.accent-swatch-active {
  border-color: var(--ink-primary);
}

.about-line {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
  color: var(--ink-secondary);
}

.about-link {
  display: inline-block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
}

.about-link:hover {
  text-decoration: underline;
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
