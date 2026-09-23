<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t } = useI18n()

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

const items = ref([])
const projects = ref([])
const details = reactive({}) // itemId -> { links, files }
const loading = ref(true)

const standaloneProjects = computed(() => projects.value.filter((p) => !p.employment_id))

function projectTitle(projectId) {
  return projects.value.find((p) => p.id === projectId)?.title || ''
}

async function reload() {
  const [list, proj] = await Promise.all([api.getPortfolioItems(), api.getProjects()])
  items.value = list
  projects.value = proj
  const loaded = await Promise.all(list.map((item) => api.getPortfolioItem(item.id)))
  loaded.forEach((detail, i) => {
    details[list[i].id] = detail
  })
}

onMounted(async () => {
  try {
    await reload()
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// -- new item --
const newItemDialog = ref(false)
const newItemForm = reactive({ title: '', description: '', project_id: null })
async function submitNewItem() {
  if (!newItemForm.title.trim()) return
  try {
    await api.createPortfolioItem(newItemForm)
    Object.assign(newItemForm, { title: '', description: '', project_id: null })
    newItemDialog.value = false
    await reload()
    ElMessage.success(t('portfolio.itemAdded'))
  } catch (e) {
    ElMessage.error(t('portfolio.createError', { error: e.message }))
  }
}

async function removeItem(id) {
  await ElMessageBox.confirm(t('portfolio.confirmDeleteItem'), t('profile.confirm'))
  await api.deletePortfolioItem(id)
  await reload()
}

// -- links --
const linkDrafts = reactive({})
function linkDraft(itemId) {
  if (!linkDrafts[itemId]) linkDrafts[itemId] = { label: '', url: '' }
  return linkDrafts[itemId]
}
async function submitLink(itemId) {
  const draft = linkDraft(itemId)
  if (!draft.label.trim() || !draft.url.trim()) return
  try {
    await api.addPortfolioLink(itemId, draft.label, draft.url)
    Object.assign(draft, { label: '', url: '' })
    await reload()
  } catch (e) {
    ElMessage.error(t('portfolio.linkAddError', { error: e.message }))
  }
}
async function removeLink(id) {
  await ElMessageBox.confirm(t('portfolio.confirmDeleteLink'), t('profile.confirm'))
  await api.deletePortfolioLink(id)
  await reload()
}

// -- files --
const pendingFiles = reactive({})
const uploadRefs = {}
function setUploadRef(itemId, el) {
  if (el) uploadRefs[itemId] = el
}
function handleFilesChange(itemId, fileList) {
  pendingFiles[itemId] = fileList.map((f) => f.raw)
}
async function submitFiles(itemId) {
  const files = pendingFiles[itemId] || []
  if (!files.length) return
  const oversized = files.find((f) => f.size > MAX_FILE_SIZE_BYTES)
  if (oversized) {
    ElMessage.error(t('portfolio.fileTooLarge', { filename: oversized.name }))
    return
  }
  try {
    await api.uploadPortfolioFiles(itemId, files)
    pendingFiles[itemId] = []
    uploadRefs[itemId]?.clearFiles()
    await reload()
    ElMessage.success(t('portfolio.filesUploaded'))
  } catch (e) {
    ElMessage.error(t('portfolio.uploadError', { error: e.message }))
  }
}
async function removeFile(id) {
  await ElMessageBox.confirm(t('portfolio.confirmDeleteFile'), t('profile.confirm'))
  await api.deletePortfolioFile(id)
  await reload()
}
async function downloadFile(file) {
  const blob = await api.downloadPortfolioFile(file.id)
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = file.original_filename
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <h1 class="page-title">{{ t('portfolio.title') }}</h1>
  <p class="page-subtitle">{{ t('portfolio.subtitle') }}</p>

  <section class="section" v-loading="loading">
    <div class="section-header">
      <h2>{{ t('portfolio.itemsHeader') }}</h2>
      <el-button size="small" @click="newItemDialog = true">{{ t('common.add') }}</el-button>
    </div>

    <el-card v-for="item in items" :key="item.id" shadow="never" class="item-card">
      <div class="item-title">
        {{ item.title }}
        <el-tag v-if="item.project_id" size="small" type="info">{{ projectTitle(item.project_id) }}</el-tag>
      </div>
      <p v-if="item.description">{{ item.description }}</p>

      <div class="sub-block">
        <div class="sub-header">{{ t('portfolio.linksHeader') }}</div>
        <div class="links-row" v-if="details[item.id]?.links?.length">
          <el-tag
            v-for="l in details[item.id].links"
            :key="l.id"
            closable
            @close="removeLink(l.id)"
            class="link-tag"
          >
            <a :href="l.url" target="_blank" rel="noopener noreferrer">{{ l.label }}</a>
          </el-tag>
        </div>
        <div class="inline-form">
          <el-input
            v-model="linkDraft(item.id).label"
            :placeholder="t('portfolio.linkLabelPlaceholder')"
            size="small"
            class="inline-input"
          />
          <el-input
            v-model="linkDraft(item.id).url"
            placeholder="https://..."
            size="small"
            class="inline-input"
          />
          <el-button size="small" @click="submitLink(item.id)">{{ t('portfolio.addLink') }}</el-button>
        </div>
      </div>

      <div class="sub-block">
        <div class="sub-header">{{ t('portfolio.filesHeader') }}</div>
        <ul class="files-list" v-if="details[item.id]?.files?.length">
          <li v-for="f in details[item.id].files" :key="f.id">
            <span class="file-name">{{ f.original_filename }}</span>
            <span class="file-size">({{ formatSize(f.size_bytes) }})</span>
            <el-button size="small" text @click="downloadFile(f)">{{ t('portfolio.download') }}</el-button>
            <el-button size="small" text type="danger" @click="removeFile(f.id)">{{ t('common.delete') }}</el-button>
          </li>
        </ul>
        <div class="inline-form">
          <el-upload
            :ref="(el) => setUploadRef(item.id, el)"
            :auto-upload="false"
            multiple
            :on-change="(_, fileList) => handleFilesChange(item.id, fileList)"
          >
            <el-button size="small">{{ t('portfolio.chooseFiles') }}</el-button>
          </el-upload>
          <el-button
            size="small"
            type="primary"
            :disabled="!pendingFiles[item.id]?.length"
            @click="submitFiles(item.id)"
          >
            {{ t('portfolio.uploadFiles') }}
          </el-button>
        </div>
      </div>

      <div class="card-actions">
        <el-button size="small" text type="danger" @click="removeItem(item.id)">{{ t('common.delete') }}</el-button>
      </div>
    </el-card>
    <el-empty v-if="!loading && items.length === 0" :description="t('portfolio.noEntries')" />
  </section>

  <el-dialog v-model="newItemDialog" :title="t('portfolio.addItem')" width="480px">
    <el-form :model="newItemForm" label-width="100px">
      <el-form-item :label="t('portfolio.titleLabel')">
        <el-input v-model="newItemForm.title" :placeholder="t('portfolio.titlePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('portfolio.descriptionLabel')">
        <el-input
          v-model="newItemForm.description"
          type="textarea"
          :rows="3"
          :placeholder="t('portfolio.descriptionPlaceholder')"
        />
      </el-form-item>
      <el-form-item :label="t('portfolio.projectLabel')">
        <el-select v-model="newItemForm.project_id" clearable :placeholder="t('portfolio.projectPlaceholder')">
          <el-option v-for="p in standaloneProjects" :key="p.id" :label="p.title" :value="p.id" />
        </el-select>
        <div class="field-hint">{{ t('portfolio.projectHint') }}</div>
      </el-form-item>
    </el-form>
    <template #footer><el-button type="primary" @click="submitNewItem">{{ t('common.add') }}</el-button></template>
  </el-dialog>
</template>

<style scoped>
.section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.section-header h2 {
  font-size: 1rem;
  margin: 0;
}

.item-card {
  margin-bottom: 0.75rem;
}

.item-title {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sub-block {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--el-border-color);
}

.sub-header {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
}

.links-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.link-tag a {
  color: inherit;
  text-decoration: none;
}

.files-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.5rem;
}

.files-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.file-size {
  color: var(--ink-secondary);
  font-size: 0.85rem;
}

.inline-form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.inline-input {
  max-width: 200px;
}

.field-hint {
  color: var(--ink-secondary);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.75rem;
}
</style>
