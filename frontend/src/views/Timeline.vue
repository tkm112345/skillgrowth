<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { tagStyle } from '../hue'

const PAGE_SIZE = 50

const { t, locale } = useI18n()
const entries = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)
const learningByEvidenceId = ref({})

const submitting = ref(false)
const form = reactive({ activity_type: 'reading', title: '', activity_date: '', notes: '' })
const certFile = ref(null)

const typeOptions = computed(() => [
  { value: 'reading', label: t('learning.typeReading') },
  { value: 'talk_given', label: t('learning.typeTalkGiven') },
  { value: 'talk_attended', label: t('learning.typeTalkAttended') },
  { value: 'certification', label: t('learning.typeCertification') },
  { value: 'other', label: t('learning.typeOther') },
])

const sourceLabelKeys = {
  certification: 'timeline.sourceCertification',
  checkin: 'timeline.sourceCheckin',
  education: 'timeline.sourceEducation',
  employment: 'timeline.sourceEmployment',
  project: 'timeline.sourceProject',
  learning_activity: 'timeline.sourceLearningActivity',
}

function sourceLabel(sourceType) {
  const key = sourceLabelKeys[sourceType]
  return key ? t(key) : sourceType
}

async function reload() {
  const [page, learningList] = await Promise.all([api.getEvidence(PAGE_SIZE, 0), api.getLearning()])
  entries.value = page
  hasMore.value = page.length === PAGE_SIZE
  learningByEvidenceId.value = Object.fromEntries(learningList.map((l) => [l.evidence_id, l.id]))
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
    const page = await api.getEvidence(PAGE_SIZE, entries.value.length)
    entries.value.push(...page)
    hasMore.value = page.length === PAGE_SIZE
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loadingMore.value = false
  }
}

function handleCertFileChange(uploadFile) {
  certFile.value = uploadFile.raw
}

async function submit() {
  submitting.value = true
  try {
    if (certFile.value) {
      await api.addImageEvidence(certFile.value)
    }
    await api.addLearning(form)
    Object.assign(form, { activity_type: 'reading', title: '', activity_date: '', notes: '' })
    certFile.value = null
    await reload()
    ElMessage.success(t('timeline.added'))
  } finally {
    submitting.value = false
  }
}

async function removeLearning(learningActivityId) {
  await ElMessageBox.confirm(t('timeline.confirmDeleteLearning'), t('profile.confirm'))
  await api.deleteLearning(learningActivityId)
  await reload()
}

const formatDateTime = computed(() => (iso) => new Date(iso).toLocaleString(locale.value))

const groupedEntries = computed(() => {
  const formatMonth = new Intl.DateTimeFormat(locale.value, { year: 'numeric', month: 'long' })
  const groups = []
  const groupByKey = {}
  for (const entry of entries.value) {
    const date = new Date(entry.created_at)
    const key = `${date.getFullYear()}-${date.getMonth()}`
    let group = groupByKey[key]
    if (!group) {
      group = { key, label: formatMonth.format(date), items: [] }
      groupByKey[key] = group
      groups.push(group)
    }
    group.items.push(entry)
  }
  return groups
})
</script>

<template>
  <h1 class="page-title">{{ t('timeline.title') }}</h1>
  <p class="page-subtitle">{{ t('timeline.subtitle') }}</p>

  <el-card shadow="never" class="chart-card accent-aqua">
    <template #header>{{ t('timeline.addHeader') }}</template>
    <el-form :model="form" label-width="80px">
      <el-form-item :label="t('learning.type')">
        <el-select v-model="form.activity_type">
          <el-option v-for="o in typeOptions" :key="o.value" :label="o.label" :value="o.value" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('learning.titleLabel')">
        <el-input v-model="form.title" :placeholder="t('learning.titlePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('learning.date')">
        <el-date-picker v-model="form.activity_date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item :label="t('learning.notes')">
        <el-input v-model="form.notes" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item v-if="form.activity_type === 'certification'" :label="t('learning.certImage')">
        <el-upload
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          accept="image/*"
          :on-change="handleCertFileChange"
        >
          <el-button size="small">{{ t('common.add') }}</el-button>
          <template #tip><div class="upload-hint">{{ t('learning.certImageHint') }}</div></template>
        </el-upload>
      </el-form-item>
    </el-form>
    <el-button type="primary" :loading="submitting" @click="submit">{{ t('common.add') }}</el-button>
  </el-card>

  <div v-loading="loading">
    <div v-for="group in groupedEntries" :key="group.key" class="month-group">
      <h2 class="month-heading">{{ group.label }}</h2>
      <el-timeline>
        <el-timeline-item
          v-for="entry in group.items"
          :key="entry.id"
          :timestamp="formatDateTime(entry.created_at)"
        >
          <el-card shadow="never">
            <div class="entry-header">
              <el-tag size="small" :style="tagStyle(entry.source_type)" plain>{{ sourceLabel(entry.source_type) }}</el-tag>
              <el-button
                v-if="learningByEvidenceId[entry.id]"
                size="small"
                text
                type="danger"
                @click="removeLearning(learningByEvidenceId[entry.id])"
              >
                {{ t('common.delete') }}
              </el-button>
            </div>
            <p>{{ entry.raw_input || t('timeline.image') }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>

  <el-button v-if="hasMore" :loading="loadingMore" @click="loadMore" class="load-more-btn">
    {{ t('timeline.loadMore') }}
  </el-button>

  <el-empty v-if="!loading && entries.length === 0" :description="t('timeline.noEntries')" />
</template>

<style scoped>
.upload-hint {
  color: var(--ink-secondary);
  font-size: 0.8rem;
}

.chart-card {
  margin-bottom: 1.5rem;
}

.month-group + .month-group {
  margin-top: 1rem;
}

.month-heading {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink-secondary);
  margin: 0 0 0.5rem;
}

.entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.load-more-btn {
  display: block;
  margin: 0.5rem auto 0;
}
</style>
