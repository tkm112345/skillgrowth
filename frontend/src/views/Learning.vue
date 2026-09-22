<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { tagStyle } from '../hue'

const { t } = useI18n()

const activities = ref([])
const loading = ref(true)
const dialog = ref(false)
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

function typeLabel(value) {
  return typeOptions.value.find((o) => o.value === value)?.label || value
}

async function reload() {
  activities.value = await api.getLearning()
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
    dialog.value = false
    await reload()
    ElMessage.success(t('learning.added'))
  } finally {
    submitting.value = false
  }
}

async function remove(id) {
  await ElMessageBox.confirm(t('learning.confirmDelete'), t('profile.confirm'))
  await api.deleteLearning(id)
  await reload()
}
</script>

<template>
  <h1 class="page-title">{{ t('learning.title') }}</h1>
  <p class="page-subtitle">{{ t('learning.subtitle') }}</p>

  <el-button type="primary" @click="dialog = true">{{ t('learning.add') }}</el-button>

  <el-table :data="activities" v-loading="loading" style="width: 100%; margin-top: 1rem">
    <el-table-column :label="t('learning.type')" width="110">
      <template #default="{ row }"><el-tag :style="tagStyle(row.activity_type)" plain>{{ typeLabel(row.activity_type) }}</el-tag></template>
    </el-table-column>
    <el-table-column prop="title" :label="t('learning.titleLabel')" min-width="180" />
    <el-table-column prop="activity_date" :label="t('learning.date')" width="120" />
    <el-table-column prop="notes" :label="t('learning.notes')" min-width="200" />
    <el-table-column width="80">
      <template #default="{ row }">
        <el-button size="small" text type="danger" @click="remove(row.id)">{{ t('common.delete') }}</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-empty v-if="!loading && activities.length === 0" :description="t('learning.noEntries')" />

  <el-dialog v-model="dialog" :title="t('learning.add')" width="480px">
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
        <el-input v-model="form.notes" type="textarea" :rows="3" />
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
    <template #footer>
      <el-button type="primary" :loading="submitting" @click="submit">{{ t('common.add') }}</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.upload-hint {
  color: var(--ink-secondary);
  font-size: 0.8rem;
}
</style>
