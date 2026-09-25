<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const PAGE_SIZE = 50

const { t, locale } = useI18n()

function today() {
  return new Date().toISOString().slice(0, 10)
}

const entries = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)

const form = reactive({ entry_date: today(), accomplishments: '', reflection: '', next_steps: '' })
const submitting = ref(false)

const dialogVisible = ref(false)
const editingId = ref(null)
const draft = reactive({ entry_date: '', accomplishments: '', reflection: '', next_steps: '' })
const saving = ref(false)

async function reload() {
  const page = await api.getSelfFeedback(PAGE_SIZE, 0)
  entries.value = page
  hasMore.value = page.length === PAGE_SIZE
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

async function loadMore() {
  loadingMore.value = true
  try {
    const page = await api.getSelfFeedback(PAGE_SIZE, entries.value.length)
    entries.value.push(...page)
    hasMore.value = page.length === PAGE_SIZE
  } finally {
    loadingMore.value = false
  }
}

const canSubmit = computed(
  () => form.accomplishments.trim() || form.reflection.trim() || form.next_steps.trim(),
)

async function submit() {
  submitting.value = true
  try {
    await api.addSelfFeedback({ ...form })
    Object.assign(form, { entry_date: today(), accomplishments: '', reflection: '', next_steps: '' })
    await reload()
    ElMessage.success(t('selfFeedback.saved'))
  } finally {
    submitting.value = false
  }
}

function startEdit(entry) {
  editingId.value = entry.id
  Object.assign(draft, {
    entry_date: entry.entry_date,
    accomplishments: entry.accomplishments,
    reflection: entry.reflection,
    next_steps: entry.next_steps,
  })
  dialogVisible.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    await api.updateSelfFeedback(editingId.value, { ...draft })
    dialogVisible.value = false
    await reload()
    ElMessage.success(t('selfFeedback.saved'))
  } finally {
    saving.value = false
  }
}

async function remove(id) {
  await ElMessageBox.confirm(t('selfFeedback.deleteConfirm'), t('profile.confirm'))
  await api.deleteSelfFeedback(id)
  await reload()
}

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString(locale.value, { timeZone: 'UTC' })
}
</script>

<template>
  <h1 class="page-title">{{ t('selfFeedback.title') }}</h1>
  <p class="page-subtitle">{{ t('selfFeedback.subtitle') }}</p>

  <el-card shadow="never" class="chart-card accent-yellow">
    <template #header>{{ t('selfFeedback.add') }}</template>
    <el-form :model="form" label-position="top">
      <el-form-item :label="t('selfFeedback.dateLabel')">
        <el-date-picker v-model="form.entry_date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <div class="feedback-grid">
        <el-form-item :label="t('selfFeedback.accomplishments')">
          <el-input v-model="form.accomplishments" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item :label="t('selfFeedback.reflection')">
          <el-input v-model="form.reflection" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item :label="t('selfFeedback.nextSteps')">
          <el-input v-model="form.next_steps" type="textarea" :rows="4" />
        </el-form-item>
      </div>
    </el-form>
    <el-button type="primary" :disabled="!canSubmit" :loading="submitting" @click="submit">
      {{ t('common.add') }}
    </el-button>
  </el-card>

  <div v-loading="loading">
    <el-card v-for="entry in entries" :key="entry.id" shadow="never" class="entry-card">
      <div class="entry-header">
        <span class="entry-date">{{ formatDate(entry.entry_date) }}</span>
        <div>
          <el-button size="small" text @click="startEdit(entry)">{{ t('common.edit') }}</el-button>
          <el-button size="small" text type="danger" @click="remove(entry.id)">{{ t('common.delete') }}</el-button>
        </div>
      </div>
      <div class="feedback-grid">
        <div>
          <div class="field-label">{{ t('selfFeedback.accomplishments') }}</div>
          <p class="field-text">{{ entry.accomplishments || '—' }}</p>
        </div>
        <div>
          <div class="field-label">{{ t('selfFeedback.reflection') }}</div>
          <p class="field-text">{{ entry.reflection || '—' }}</p>
        </div>
        <div>
          <div class="field-label">{{ t('selfFeedback.nextSteps') }}</div>
          <p class="field-text">{{ entry.next_steps || '—' }}</p>
        </div>
      </div>
    </el-card>
  </div>

  <el-button v-if="hasMore" :loading="loadingMore" @click="loadMore" class="load-more-btn">
    {{ t('selfFeedback.loadMore') }}
  </el-button>

  <el-empty v-if="!loading && entries.length === 0" :description="t('selfFeedback.noEntries')" />

  <el-dialog v-model="dialogVisible" :title="t('selfFeedback.edit')" width="640px">
    <el-form :model="draft" label-position="top">
      <el-form-item :label="t('selfFeedback.dateLabel')">
        <el-date-picker v-model="draft.entry_date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <div class="feedback-grid">
        <el-form-item :label="t('selfFeedback.accomplishments')">
          <el-input v-model="draft.accomplishments" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item :label="t('selfFeedback.reflection')">
          <el-input v-model="draft.reflection" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item :label="t('selfFeedback.nextSteps')">
          <el-input v-model="draft.next_steps" type="textarea" :rows="4" />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="saveEdit">{{ t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.chart-card {
  margin-bottom: 1.5rem;
}

.feedback-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 720px) {
  .feedback-grid {
    grid-template-columns: 1fr;
  }
}

.entry-card {
  margin-bottom: 1rem;
}

.entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.entry-date {
  font-weight: 600;
}

.field-label {
  font-size: 0.8rem;
  color: var(--ink-secondary);
  margin-bottom: 0.25rem;
}

.field-text {
  margin: 0;
  white-space: pre-wrap;
}

.load-more-btn {
  display: block;
  margin: 0.5rem auto 0;
}
</style>
