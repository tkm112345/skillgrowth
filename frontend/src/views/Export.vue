<script setup>
import DOMPurify from 'dompurify'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t, locale } = useI18n()
const exports = ref([])
const loading = ref(true)
const generating = ref(false)

onMounted(async () => {
  exports.value = await api.getExports()
  loading.value = false
})

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

// -- gap check --
const jobDescription = ref('')
const checking = ref(false)
const gapResult = ref(null)

async function runGapCheck() {
  if (!jobDescription.value.trim()) return
  checking.value = true
  try {
    gapResult.value = await api.gapCheck(jobDescription.value)
  } finally {
    checking.value = false
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('export.title') }}</h1>
  <p class="page-subtitle">{{ t('export.subtitle') }}</p>

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

  <el-empty v-if="!loading && exports.length === 0" :description="t('export.noEntries')" />

  <el-card shadow="never" class="export-card gap-check-card">
    <template #header>{{ t('export.gapCheckHeader') }}</template>
    <p class="gap-check-hint">{{ t('export.gapCheckHint') }}</p>
    <el-input
      v-model="jobDescription"
      type="textarea"
      :rows="6"
      :placeholder="t('export.gapCheckPlaceholder')"
    />
    <el-button type="primary" :loading="checking" @click="runGapCheck" class="gap-check-btn">
      {{ t('export.gapCheckRun') }}
    </el-button>

    <div v-if="gapResult" class="gap-result">
      <p>{{ gapResult.summary }}</p>
      <div class="gap-columns">
        <div>
          <div class="gap-label matched">{{ t('export.gapCheckMatched') }}</div>
          <el-tag v-for="(m, i) in gapResult.matched" :key="i" type="success" class="gap-tag">{{ m }}</el-tag>
        </div>
        <div>
          <div class="gap-label missing">{{ t('export.gapCheckMissing') }}</div>
          <el-tag v-for="(m, i) in gapResult.missing" :key="i" type="danger" class="gap-tag">{{ m }}</el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.export-card {
  margin-top: 1rem;
}

.export-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.gap-check-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-top: 0;
}

.gap-check-btn {
  margin-top: 0.75rem;
}

.gap-result {
  margin-top: 1rem;
}

.gap-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.gap-label {
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.gap-tag {
  margin: 0 0.4rem 0.4rem 0;
}
</style>
