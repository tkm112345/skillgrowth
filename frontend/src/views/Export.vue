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

onMounted(async () => {
  try {
    const [page, prs] = await Promise.all([
      api.getExports(PAGE_SIZE, 0),
      api.getSelfPRs(SELF_PR_PAGE_SIZE, 0),
    ])
    exports.value = page
    hasMore.value = page.length === PAGE_SIZE
    selfPRs.value = prs
    hasMoreSelfPR.value = prs.length === SELF_PR_PAGE_SIZE
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
    loadingSelfPR.value = false
  }
})

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
      <el-collapse-item v-for="pr in selfPRs" :key="pr.id" :title="formatDateTime(pr.created_at)">
        <p class="self-pr-content">{{ pr.content }}</p>
        <el-button size="small" text type="danger" @click="removeSelfPR(pr.id)">{{ t('common.delete') }}</el-button>
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

  <el-button type="primary" :loading="generating" @click="generate">{{ t('export.generate') }}</el-button>

  <div v-loading="loading">
    <el-card v-for="snap in exports" :key="snap.id" shadow="never" class="export-card">
      <template #header>
        <div class="export-header">
          <span>{{ formatDateTime(snap.generated_at) }}</span>
          <el-button size="small" text @click="download(snap)">{{ t('export.download') }}</el-button>
        </div>
      </template>
      <div class="rendered-resume" v-html="renderMarkdown(snap.content)"></div>
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
</style>
