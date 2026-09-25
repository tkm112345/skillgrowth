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
const selectedMonth = ref(null)
const monthBuckets = ref([])

const submitting = ref(false)
const form = reactive({ activity_type: '', title: '', activity_date: '', notes: '' })
const certFile = ref(null)

const activityTypes = ref([])
const manageTypesVisible = ref(false)
const newTypeLabel = ref('')
const addingType = ref(false)
const editingTypeId = ref(null)
const draftTypeLabel = ref('')
const savingType = ref(false)

function typeDisplayLabel(type) {
  return type.translation_key ? t('learning.' + type.translation_key) : type.label
}

const selectedTypeIsProtected = computed(
  () => activityTypes.value.find((type) => type.label === form.activity_type)?.is_protected ?? false
)

async function loadActivityTypes() {
  activityTypes.value = await api.getActivityTypes()
  if (!activityTypes.value.some((type) => type.label === form.activity_type)) {
    form.activity_type = activityTypes.value[0]?.label ?? ''
  }
}

async function addActivityType() {
  const label = newTypeLabel.value.trim()
  if (!label) return
  addingType.value = true
  try {
    await api.addActivityType(label)
    newTypeLabel.value = ''
    await loadActivityTypes()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    addingType.value = false
  }
}

function startEditType(type) {
  editingTypeId.value = type.id
  draftTypeLabel.value = type.label
}

function cancelEditType() {
  editingTypeId.value = null
}

async function saveTypeEdit(type) {
  const label = draftTypeLabel.value.trim()
  if (!label) return
  savingType.value = true
  try {
    await api.updateActivityType(type.id, label)
    editingTypeId.value = null
    await loadActivityTypes()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    savingType.value = false
  }
}

async function removeType(type) {
  await ElMessageBox.confirm(t('learning.deleteTypeConfirm'), t('profile.confirm'))
  await api.deleteActivityType(type.id)
  await loadActivityTypes()
}

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

function selectedYearMonth() {
  if (!selectedMonth.value) return [null, null]
  const [year, month] = selectedMonth.value.split('-').map(Number)
  return [year, month]
}

async function reload() {
  const [year, month] = selectedYearMonth()
  const [page, learningList] = await Promise.all([api.getEvidence(PAGE_SIZE, 0, year, month), api.getLearning()])
  entries.value = page
  hasMore.value = page.length === PAGE_SIZE
  learningByEvidenceId.value = Object.fromEntries(learningList.map((l) => [l.evidence_id, l.id]))
}

async function loadMonths() {
  monthBuckets.value = await api.getEvidenceMonths()
}

onMounted(async () => {
  try {
    await Promise.all([reload(), loadMonths(), loadActivityTypes()])
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

async function loadMore() {
  loadingMore.value = true
  try {
    const [year, month] = selectedYearMonth()
    const page = await api.getEvidence(PAGE_SIZE, entries.value.length, year, month)
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
    Object.assign(form, {
      activity_type: activityTypes.value[0]?.label ?? '',
      title: '',
      activity_date: '',
      notes: '',
    })
    certFile.value = null
    await Promise.all([reload(), loadMonths()])
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

const monthGroups = computed(() => {
  const formatMonth = new Intl.DateTimeFormat(locale.value, { month: 'long' })
  const groupsByYear = {}
  const groups = []
  for (const bucket of monthBuckets.value) {
    let group = groupsByYear[bucket.year]
    if (!group) {
      group = { year: bucket.year, months: [] }
      groupsByYear[bucket.year] = group
      groups.push(group)
    }
    const label = formatMonth.format(new Date(bucket.year, bucket.month - 1, 1))
    group.months.push({
      key: `${bucket.year}-${String(bucket.month).padStart(2, '0')}`,
      label: `${label} (${bucket.count})`,
    })
  }
  return groups
})
</script>

<template>
  <h1 class="page-title">{{ t('timeline.title') }}</h1>
  <p class="page-subtitle">{{ t('timeline.subtitle') }}</p>

  <el-card shadow="never" class="chart-card accent-aqua">
    <template #header>{{ t('timeline.addHeader') }}</template>
    <el-form :model="form" label-position="top">
      <el-form-item :label="t('learning.type')">
        <el-select v-model="form.activity_type">
          <el-option v-for="type in activityTypes" :key="type.id" :label="typeDisplayLabel(type)" :value="type.label" />
        </el-select>
        <el-button size="small" text @click="manageTypesVisible = true">{{ t('learning.manageTypes') }}</el-button>
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
      <el-form-item v-if="selectedTypeIsProtected" :label="t('learning.certImage')">
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

  <el-select
    v-if="monthGroups.length"
    v-model="selectedMonth"
    clearable
    :placeholder="t('timeline.jumpToMonth')"
    class="month-jump"
    @change="reload"
  >
    <el-option-group v-for="group in monthGroups" :key="group.year" :label="String(group.year)">
      <el-option v-for="m in group.months" :key="m.key" :label="m.label" :value="m.key" />
    </el-option-group>
  </el-select>

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

  <el-dialog v-model="manageTypesVisible" :title="t('learning.manageTypes')" width="420px">
    <div v-for="type in activityTypes" :key="type.id" class="type-row">
      <template v-if="editingTypeId === type.id">
        <el-input v-model="draftTypeLabel" size="small" />
        <el-button size="small" @click="cancelEditType">{{ t('common.cancel') }}</el-button>
        <el-button size="small" type="primary" :loading="savingType" @click="saveTypeEdit(type)">
          {{ t('common.save') }}
        </el-button>
      </template>
      <template v-else>
        <span class="type-row-label">{{ typeDisplayLabel(type) }}</span>
        <template v-if="type.is_protected">
          <span class="type-row-hint">{{ t('learning.protectedTypeHint') }}</span>
        </template>
        <template v-else>
          <el-button size="small" text @click="startEditType(type)">{{ t('common.edit') }}</el-button>
          <el-button size="small" text type="danger" @click="removeType(type)">{{ t('common.delete') }}</el-button>
        </template>
      </template>
    </div>
    <div class="type-row">
      <el-input
        v-model="newTypeLabel"
        size="small"
        :placeholder="t('learning.typeLabelPlaceholder')"
        @keyup.enter="addActivityType"
      />
      <el-button size="small" type="primary" :loading="addingType" @click="addActivityType">
        {{ t('common.add') }}
      </el-button>
    </div>
    <template #footer><el-button @click="manageTypesVisible = false">{{ t('common.close') }}</el-button></template>
  </el-dialog>
</template>

<style scoped>
.upload-hint {
  color: var(--ink-secondary);
  font-size: 0.8rem;
}

.type-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0;
}

.type-row + .type-row {
  border-top: 1px solid var(--border);
}

.type-row-label {
  flex: 1;
}

.type-row-hint {
  color: var(--ink-secondary);
  font-size: 0.8rem;
}

.chart-card {
  margin-bottom: 1.5rem;
}

.month-jump {
  display: block;
  margin-bottom: 1rem;
  width: 220px;
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
