<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t, locale } = useI18n()
const certifications = ref([])
const loading = ref(true)
const dialog = ref(false)
const form = reactive({ title: '', activity_date: '', expiry_date: '', notes: '' })
const editingId = ref(null)

async function reload() {
  const activities = await api.getLearning()
  certifications.value = activities.filter((a) => a.activity_type === 'certification')
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

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(locale.value)
}

function isExpired(row) {
  if (!row.expiry_date) return false
  return row.expiry_date < new Date().toISOString().slice(0, 10)
}

function openAddDialog() {
  editingId.value = null
  Object.assign(form, { title: '', activity_date: '', expiry_date: '', notes: '' })
  dialog.value = true
}

function openEditDialog(row) {
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    activity_date: row.activity_date || '',
    expiry_date: row.expiry_date || '',
    notes: row.notes || '',
  })
  dialog.value = true
}

async function submit() {
  if (!form.title.trim()) return
  const payload = {
    activity_type: 'certification',
    title: form.title,
    activity_date: form.activity_date || null,
    expiry_date: form.expiry_date || null,
    notes: form.notes,
  }
  if (editingId.value) {
    await api.updateLearning(editingId.value, payload)
    ElMessage.success(t('certifications.updated'))
  } else {
    await api.addLearning(payload)
    ElMessage.success(t('certifications.added'))
  }
  dialog.value = false
  await reload()
}

async function remove(id) {
  await ElMessageBox.confirm(t('certifications.confirmDelete'), t('profile.confirm'))
  await api.deleteLearning(id)
  await reload()
}

async function toggleResumeInclusion(row) {
  const next = !row.include_in_resume
  row.include_in_resume = next
  try {
    await api.setLearningResumeInclusion(row.id, next)
  } catch (e) {
    row.include_in_resume = !next
    ElMessage.error(t('skills.resumeToggleError'))
  }
}
</script>

<template>
  <div class="header-row">
    <div>
      <h1 class="page-title">{{ t('certifications.title') }}</h1>
      <p class="page-subtitle">{{ t('certifications.subtitle') }}</p>
    </div>
    <div class="header-actions">
      <el-button type="primary" @click="openAddDialog">{{ t('certifications.add') }}</el-button>
    </div>
  </div>

  <el-table :data="certifications" v-loading="loading" style="width: 100%">
    <el-table-column :label="t('certifications.columnTitle')" min-width="200">
      <template #default="{ row }">{{ row.title }}</template>
    </el-table-column>
    <el-table-column :label="t('certifications.columnDate')" width="130">
      <template #default="{ row }">{{ formatDate(row.activity_date) }}</template>
    </el-table-column>
    <el-table-column :label="t('certifications.columnExpiry')" width="150">
      <template #default="{ row }">
        <el-tag v-if="isExpired(row)" type="danger" size="small">
          {{ formatDate(row.expiry_date) }} ({{ t('certifications.expired') }})
        </el-tag>
        <span v-else>{{ formatDate(row.expiry_date) }}</span>
      </template>
    </el-table-column>
    <el-table-column :label="t('skills.columnIncludeInResume')" width="110" align="center">
      <template #default="{ row }">
        <el-switch :model-value="row.include_in_resume" @change="toggleResumeInclusion(row)" />
      </template>
    </el-table-column>
    <el-table-column width="140">
      <template #default="{ row }">
        <el-button size="small" text @click="openEditDialog(row)">{{ t('common.edit') }}</el-button>
        <el-button size="small" text type="danger" @click="remove(row.id)">{{ t('common.delete') }}</el-button>
      </template>
    </el-table-column>
    <template #empty><span></span></template>
  </el-table>

  <el-empty v-if="!loading && certifications.length === 0" :description="t('certifications.noEntries')" />

  <el-dialog v-model="dialog" :title="editingId ? t('certifications.edit') : t('certifications.add')" width="420px">
    <el-form :model="form" label-position="top">
      <el-form-item :label="t('learning.titleLabel')">
        <el-input v-model="form.title" :placeholder="t('learning.titlePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('learning.date')">
        <el-date-picker v-model="form.activity_date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item :label="t('certifications.expiryLabel')">
        <el-date-picker v-model="form.expiry_date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item :label="t('learning.notes')">
        <el-input v-model="form.notes" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button type="primary" @click="submit">{{ editingId ? t('common.save') : t('common.add') }}</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}
</style>
