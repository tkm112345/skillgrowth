<script setup>
import DOMPurify from 'dompurify'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const PAGE_SIZE = 20
const SELF_PR_PAGE_SIZE = 10

const { t, locale } = useI18n()
const exports = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)
const generating = ref(false)

const selfPRs = ref([])
const loadingSelfPR = ref(true)
const loadingMoreSelfPR = ref(false)
const hasMoreSelfPR = ref(false)
const newSelfPR = ref('')
const submittingSelfPR = ref(false)

const editingExportId = ref(null)
const draftContent = ref('')
const savingExport = ref(false)

const SECTION_FORMAT_FIELDS = [
  { key: 'employment', labelKey: 'export.resumeTemplateFormatEmployment', options: ['bullet', 'table'] },
  { key: 'projects', labelKey: 'export.resumeTemplateFormatProjects', options: ['bullet', 'table'] },
  { key: 'skills', labelKey: 'export.resumeTemplateFormatSkills', options: ['list', 'table'] },
  { key: 'certifications', labelKey: 'export.resumeTemplateFormatCertifications', options: ['list', 'table'] },
]
const FORMAT_OPTION_LABEL_KEYS = {
  bullet: 'export.resumeTemplateFormatBullet',
  table: 'export.resumeTemplateFormatTable',
  list: 'export.resumeTemplateFormatList',
}
const RESUME_TAGS = [
  { tag: 'self_pr', labelKey: 'export.resumeTemplateTagSelfPr' },
  { tag: 'employment', labelKey: 'export.resumeTemplateTagEmployment' },
  { tag: 'projects', labelKey: 'export.resumeTemplateTagProjects' },
  { tag: 'education', labelKey: 'export.resumeTemplateTagEducation' },
  { tag: 'skills', labelKey: 'export.resumeTemplateTagSkills' },
  { tag: 'certifications', labelKey: 'export.resumeTemplateTagCertifications' },
]

const resumeTemplates = ref([])
const loadingResumeTemplates = ref(true)
const newTemplateName = ref('')
const newTemplateFile = ref(null)
const uploadingTemplate = ref(false)
const generatingTemplateId = ref(null)
const savingFormatId = ref(null)

const editingSelfPRId = ref(null)
const draftSelfPR = ref('')
const savingSelfPR = ref(false)
const selectingSelfPRId = ref(null)

onMounted(async () => {
  try {
    const [page, prs, templates] = await Promise.all([
      api.getExports(PAGE_SIZE, 0),
      api.getSelfPRs(SELF_PR_PAGE_SIZE, 0),
      api.getResumeTemplates(),
    ])
    exports.value = page
    hasMore.value = page.length === PAGE_SIZE
    selfPRs.value = prs
    hasMoreSelfPR.value = prs.length === SELF_PR_PAGE_SIZE
    resumeTemplates.value = templates
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
    loadingSelfPR.value = false
    loadingResumeTemplates.value = false
  }
})

function parseSectionFormats(tpl) {
  try {
    return JSON.parse(tpl.section_formats || '{}')
  } catch (e) {
    return {}
  }
}

function handleTemplateFileChange(uploadFile) {
  newTemplateFile.value = uploadFile.raw
}

async function uploadTemplate() {
  if (!newTemplateName.value.trim() || !newTemplateFile.value) return
  uploadingTemplate.value = true
  try {
    const template = await api.uploadResumeTemplate(newTemplateName.value, newTemplateFile.value)
    resumeTemplates.value.unshift(template)
    newTemplateName.value = ''
    newTemplateFile.value = null
    ElMessage.success(t('export.resumeTemplateUploaded'))
  } catch (e) {
    ElMessage.error(t('export.resumeTemplateUploadError', { error: e.message }))
  } finally {
    uploadingTemplate.value = false
  }
}

async function setDefaultTemplate(tpl) {
  const updated = await api.updateResumeTemplate(tpl.id, { is_selected: true })
  for (const other of resumeTemplates.value) other.is_selected = other.id === updated.id
  ElMessage.success(t('export.resumeTemplateSelected'))
}

async function updateSectionFormat(tpl, key, value) {
  const formats = { ...parseSectionFormats(tpl), [key]: value }
  savingFormatId.value = tpl.id
  try {
    const updated = await api.updateResumeTemplate(tpl.id, { section_formats: formats })
    tpl.section_formats = updated.section_formats
    ElMessage.success(t('export.resumeTemplateFormatSaved'))
  } finally {
    savingFormatId.value = null
  }
}

async function generateFromTemplate(tpl) {
  generatingTemplateId.value = tpl.id
  try {
    const blob = await api.generateResumeDocx(tpl.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${tpl.name}.docx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error(t('export.resumeTemplateGenerateError', { error: e.message }))
  } finally {
    generatingTemplateId.value = null
  }
}

function tagSyntax(tag) {
  return `{{p ${tag} }}`
}

async function removeTemplate(id) {
  await ElMessageBox.confirm(t('export.confirmDeleteResumeTemplate'), t('profile.confirm'))
  await api.deleteResumeTemplate(id)
  resumeTemplates.value = resumeTemplates.value.filter((tpl) => tpl.id !== id)
}

async function loadMoreSelfPR() {
  loadingMoreSelfPR.value = true
  try {
    const page = await api.getSelfPRs(SELF_PR_PAGE_SIZE, selfPRs.value.length)
    selfPRs.value.push(...page)
    hasMoreSelfPR.value = page.length === SELF_PR_PAGE_SIZE
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loadingMoreSelfPR.value = false
  }
}

async function loadMore() {
  loadingMore.value = true
  try {
    const page = await api.getExports(PAGE_SIZE, exports.value.length)
    exports.value.push(...page)
    hasMore.value = page.length === PAGE_SIZE
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loadingMore.value = false
  }
}

async function generate() {
  generating.value = true
  try {
    const snapshot = await api.generateExport()
    exports.value.unshift(snapshot)
    ElMessage.success(t('export.generateSuccess'))
  } catch (e) {
    ElMessage.error(t('export.generateError', { error: e.message }))
  } finally {
    generating.value = false
  }
}

function renderMarkdown(content) {
  return DOMPurify.sanitize(marked.parse(content || ''))
}

function startEditExport(snap) {
  editingExportId.value = snap.id
  draftContent.value = snap.content
}

function cancelEditExport() {
  editingExportId.value = null
}

async function saveExport(snap) {
  savingExport.value = true
  try {
    const updated = await api.updateExport(snap.id, draftContent.value)
    snap.content = updated.content
    snap.edited_at = updated.edited_at
    editingExportId.value = null
    ElMessage.success(t('export.editSaved'))
  } finally {
    savingExport.value = false
  }
}

function download(snap) {
  const blob = new Blob([snap.content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `resume-${snap.generated_at.slice(0, 10)}.md`
  a.click()
  URL.revokeObjectURL(url)
}

function formatDateTime(iso) {
  return new Date(iso).toLocaleString(locale.value)
}

async function submitSelfPR() {
  if (!newSelfPR.value.trim()) return
  submittingSelfPR.value = true
  try {
    const entry = await api.addSelfPR(newSelfPR.value)
    for (const p of selfPRs.value) p.is_selected = false
    selfPRs.value.unshift(entry)
    newSelfPR.value = ''
    ElMessage.success(t('export.selfPrAdded'))
  } finally {
    submittingSelfPR.value = false
  }
}

async function removeSelfPR(id) {
  await ElMessageBox.confirm(t('export.confirmDeleteSelfPr'), t('profile.confirm'))
  await api.deleteSelfPR(id)
  selfPRs.value = selfPRs.value.filter((e) => e.id !== id)
}

function isEffectivelySelected(pr) {
  if (pr.is_selected) return true
  return !selfPRs.value.some((p) => p.is_selected) && selfPRs.value[0]?.id === pr.id
}

function startEditSelfPR(pr) {
  editingSelfPRId.value = pr.id
  draftSelfPR.value = pr.content
}

function cancelEditSelfPR() {
  editingSelfPRId.value = null
}

async function saveSelfPREdit(pr) {
  savingSelfPR.value = true
  try {
    const updated = await api.updateSelfPR(pr.id, draftSelfPR.value)
    pr.content = updated.content
    editingSelfPRId.value = null
    ElMessage.success(t('export.selfPrEditSaved'))
  } finally {
    savingSelfPR.value = false
  }
}

async function selectSelfPR(pr) {
  selectingSelfPRId.value = pr.id
  try {
    await api.selectSelfPR(pr.id)
    for (const p of selfPRs.value) p.is_selected = p.id === pr.id
    ElMessage.success(t('export.selfPrSelected'))
  } finally {
    selectingSelfPRId.value = null
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('export.title') }}</h1>
  <p class="page-subtitle">{{ t('export.subtitle') }}</p>

  <el-card shadow="never" class="export-card accent-green" v-loading="loadingSelfPR">
    <template #header>{{ t('export.selfPrHeader') }}</template>
    <p class="self-pr-hint">{{ t('export.selfPrHint') }}</p>
    <el-input
      v-model="newSelfPR"
      type="textarea"
      :rows="4"
      :placeholder="t('export.selfPrPlaceholder')"
    />
    <el-button type="primary" :loading="submittingSelfPR" @click="submitSelfPR" class="self-pr-btn">
      {{ t('export.selfPrSubmit') }}
    </el-button>

    <el-collapse v-if="selfPRs.length" class="self-pr-history">
      <el-collapse-item v-for="pr in selfPRs" :key="pr.id">
        <template #title>
          <span>{{ formatDateTime(pr.created_at) }}</span>
          <el-tag v-if="isEffectivelySelected(pr)" size="small" type="success" class="self-pr-selected-tag">
            {{ t('export.selfPrInUse') }}
          </el-tag>
        </template>

        <template v-if="editingSelfPRId === pr.id">
          <el-input v-model="draftSelfPR" type="textarea" :rows="4" />
          <div class="self-pr-actions">
            <el-button size="small" @click="cancelEditSelfPR">{{ t('common.cancel') }}</el-button>
            <el-button size="small" type="primary" :loading="savingSelfPR" @click="saveSelfPREdit(pr)">
              {{ t('common.save') }}
            </el-button>
          </div>
        </template>
        <template v-else>
          <p class="self-pr-content">{{ pr.content }}</p>
          <div class="self-pr-actions">
            <el-button size="small" text @click="startEditSelfPR(pr)">{{ t('common.edit') }}</el-button>
            <el-button
              v-if="!isEffectivelySelected(pr)"
              size="small"
              text
              :loading="selectingSelfPRId === pr.id"
              @click="selectSelfPR(pr)"
            >
              {{ t('export.selfPrUseThis') }}
            </el-button>
            <el-button size="small" text type="danger" @click="removeSelfPR(pr.id)">{{ t('common.delete') }}</el-button>
          </div>
        </template>
      </el-collapse-item>
    </el-collapse>
    <el-button
      v-if="hasMoreSelfPR"
      :loading="loadingMoreSelfPR"
      size="small"
      text
      @click="loadMoreSelfPR"
      class="self-pr-load-more"
    >
      {{ t('export.loadMore') }}
    </el-button>
  </el-card>

  <el-card shadow="never" class="export-card accent-blue" v-loading="loadingResumeTemplates">
    <template #header>{{ t('export.resumeTemplateHeader') }}</template>
    <p class="self-pr-hint">{{ t('export.resumeTemplateHint') }}</p>

    <div class="template-upload-row">
      <el-input v-model="newTemplateName" :placeholder="t('export.resumeTemplateNamePlaceholder')" />
      <el-upload
        :auto-upload="false"
        :show-file-list="true"
        :limit="1"
        accept=".docx"
        :on-change="handleTemplateFileChange"
      >
        <el-button size="small">{{ t('export.resumeTemplateChooseFile') }}</el-button>
      </el-upload>
      <el-button
        type="primary"
        :loading="uploadingTemplate"
        :disabled="!newTemplateName.trim() || !newTemplateFile"
        @click="uploadTemplate"
      >
        {{ t('export.resumeTemplateUpload') }}
      </el-button>
    </div>

    <el-empty
      v-if="!loadingResumeTemplates && resumeTemplates.length === 0"
      :description="t('export.resumeTemplateEmpty')"
    />

    <el-card v-for="tpl in resumeTemplates" :key="tpl.id" shadow="never" class="template-card">
      <template #header>
        <div class="export-header">
          <span>
            {{ tpl.name }}
            <el-tag v-if="tpl.is_selected" size="small" type="success" class="self-pr-selected-tag">
              {{ t('export.resumeTemplateDefault') }}
            </el-tag>
          </span>
          <div class="export-header-actions">
            <el-button
              v-if="!tpl.is_selected"
              size="small"
              text
              @click="setDefaultTemplate(tpl)"
            >
              {{ t('export.resumeTemplateUseAsDefault') }}
            </el-button>
            <el-button
              size="small"
              text
              type="primary"
              :loading="generatingTemplateId === tpl.id"
              @click="generateFromTemplate(tpl)"
            >
              {{ t('export.resumeTemplateGenerate') }}
            </el-button>
            <el-button size="small" text type="danger" @click="removeTemplate(tpl.id)">
              {{ t('common.delete') }}
            </el-button>
          </div>
        </div>
      </template>
      <div class="template-format-row" v-for="field in SECTION_FORMAT_FIELDS" :key="field.key">
        <span class="template-format-label">{{ t(field.labelKey) }}</span>
        <el-select
          :model-value="parseSectionFormats(tpl)[field.key] || field.options[0]"
          size="small"
          :disabled="savingFormatId === tpl.id"
          @update:model-value="(value) => updateSectionFormat(tpl, field.key, value)"
        >
          <el-option
            v-for="opt in field.options"
            :key="opt"
            :value="opt"
            :label="t(FORMAT_OPTION_LABEL_KEYS[opt])"
          />
        </el-select>
      </div>
    </el-card>

    <el-collapse class="resume-tags-collapse">
      <el-collapse-item :title="t('export.resumeTemplateTagsHeader')">
        <p class="self-pr-hint">{{ t('export.resumeTemplateTagsHint') }}</p>
        <ul class="resume-tags-list">
          <li v-for="item in RESUME_TAGS" :key="item.tag">
            <code>{{ tagSyntax(item.tag) }}</code> — {{ t(item.labelKey) }}
          </li>
        </ul>
      </el-collapse-item>
    </el-collapse>
  </el-card>

  <el-button type="primary" :loading="generating" @click="generate">{{ t('export.generate') }}</el-button>

  <div v-loading="loading">
    <el-card v-for="snap in exports" :key="snap.id" shadow="never" class="export-card">
      <template #header>
        <div class="export-header">
          <span>
            {{ formatDateTime(snap.generated_at) }}
            <span v-if="snap.edited_at" class="export-edited-badge">
              {{ t('export.editedAt', { date: formatDateTime(snap.edited_at) }) }}
            </span>
          </span>
          <div class="export-header-actions">
            <template v-if="editingExportId === snap.id">
              <el-button size="small" text @click="cancelEditExport">{{ t('common.cancel') }}</el-button>
              <el-button size="small" text type="primary" :loading="savingExport" @click="saveExport(snap)">
                {{ t('common.save') }}
              </el-button>
            </template>
            <template v-else>
              <el-button size="small" text @click="startEditExport(snap)">{{ t('common.edit') }}</el-button>
              <el-button size="small" text @click="download(snap)">{{ t('export.download') }}</el-button>
            </template>
          </div>
        </div>
      </template>
      <el-input
        v-if="editingExportId === snap.id"
        v-model="draftContent"
        type="textarea"
        :rows="12"
        class="export-edit-textarea"
      />
      <div v-else class="rendered-resume" v-html="renderMarkdown(snap.content)"></div>
    </el-card>
  </div>

  <el-button v-if="hasMore" :loading="loadingMore" @click="loadMore" class="load-more-btn">
    {{ t('export.loadMore') }}
  </el-button>

  <el-empty v-if="!loading && exports.length === 0" :description="t('export.noEntries')" />
</template>

<style scoped>
.export-card {
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.export-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.export-header-actions {
  display: flex;
  gap: 0.25rem;
}

.export-edited-badge {
  margin-left: 0.5rem;
  font-size: 0.72rem;
  color: var(--ink-muted);
}

.export-edit-textarea :deep(textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.8rem;
}

.load-more-btn {
  display: block;
  margin: 0.75rem auto 0;
}

.rendered-resume {
  font-size: 0.85rem;
  line-height: 1.6;
}

.rendered-resume :deep(h1),
.rendered-resume :deep(h2),
.rendered-resume :deep(h3) {
  font-size: 1rem;
  margin: 1rem 0 0.5rem;
}

.self-pr-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-top: 0;
}

.self-pr-btn {
  margin-top: 0.75rem;
}

.self-pr-history {
  margin-top: 1rem;
}

.self-pr-load-more {
  display: block;
  margin: 0.5rem auto 0;
}

.self-pr-content {
  white-space: pre-wrap;
  font-size: 0.85rem;
}

.self-pr-selected-tag {
  margin-left: 0.5rem;
}

.self-pr-actions {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.template-upload-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.75rem;
}

.template-upload-row .el-input {
  flex: 1;
}

.template-card {
  margin-top: 1rem;
}

.template-format-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.template-format-label {
  font-size: 0.85rem;
  color: var(--ink-secondary);
}

.resume-tags-collapse {
  margin-top: 1rem;
}

.resume-tags-list {
  font-size: 0.85rem;
  line-height: 1.8;
  padding-left: 1.2rem;
}

.resume-tags-list code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  background: rgba(128, 128, 128, 0.12);
  padding: 0.05rem 0.3rem;
  border-radius: 3px;
}
</style>
