<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { tagStyle } from '../hue'

const { t, tm, locale } = useI18n()
const skills = ref([])
const loading = ref(true)
const dialog = ref(false)
const form = reactive({ name: '', category: '', proficiency: 0 })
const editingSkillId = ref(null)
const csvDialog = ref(false)
const csvFile = ref(null)
const importingCsv = ref(false)

const proficiencyTexts = computed(() => tm('skills.proficiencyLevels'))

async function reload() {
  skills.value = await api.getSkills()
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
  return new Date(iso).toLocaleDateString(locale.value)
}

function openAddDialog() {
  editingSkillId.value = null
  Object.assign(form, { name: '', category: '', proficiency: 0 })
  dialog.value = true
}

function openEditDialog(row) {
  editingSkillId.value = row.id
  Object.assign(form, { name: row.name, category: row.category, proficiency: row.proficiency || 0 })
  dialog.value = true
}

function clearProficiency() {
  form.proficiency = 0
}

async function submit() {
  if (!form.name.trim()) return
  const proficiency = form.proficiency || null
  if (editingSkillId.value) {
    await api.updateSkill(editingSkillId.value, form.name, form.category, proficiency)
    ElMessage.success(t('skills.updated'))
  } else {
    await api.addSkill(form.name, form.category, proficiency)
    ElMessage.success(t('skills.added'))
  }
  dialog.value = false
  await reload()
}

async function remove(id) {
  await ElMessageBox.confirm(t('skills.confirmDelete'), t('profile.confirm'))
  await api.deleteSkill(id)
  await reload()
}

async function toggleResumeInclusion(row) {
  const next = !row.include_in_resume
  row.include_in_resume = next
  try {
    await api.setSkillResumeInclusion(row.id, next)
  } catch (e) {
    row.include_in_resume = !next
    ElMessage.error(t('skills.resumeToggleError'))
  }
}

function handleCsvFileChange(uploadFile) {
  csvFile.value = uploadFile.raw
}

async function submitCsvImport() {
  if (!csvFile.value) return
  importingCsv.value = true
  try {
    const result = await api.importSkillsCsv(csvFile.value)
    ElMessage.success(t('skills.csvImportSuccess', { count: result.imported.length }))
    csvFile.value = null
    csvDialog.value = false
    await reload()
  } finally {
    importingCsv.value = false
  }
}
</script>

<template>
  <div class="header-row">
    <div>
      <h1 class="page-title">{{ t('skills.title') }}</h1>
      <p class="page-subtitle">{{ t('skills.subtitle') }}</p>
    </div>
    <div class="header-actions">
      <el-button @click="csvDialog = true">{{ t('skills.importCsv') }}</el-button>
      <el-button type="primary" @click="openAddDialog">{{ t('skills.add') }}</el-button>
    </div>
  </div>

  <el-table :data="skills" v-loading="loading" style="width: 100%">
    <el-table-column :label="t('skills.columnSkill')" min-width="200">
      <template #default="{ row }">
        {{ row.name }}
        <el-tag v-if="row.is_sample" size="small" type="info" plain class="sample-tag">
          {{ t('common.sampleBadge') }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column :label="t('skills.columnCategory')" width="140">
      <template #default="{ row }"><el-tag :style="tagStyle(row.category)" plain>{{ row.category }}</el-tag></template>
    </el-table-column>
    <el-table-column :label="t('skills.columnProficiency')" width="140">
      <template #default="{ row }">
        <el-rate :model-value="row.proficiency || 0" disabled :texts="proficiencyTexts" show-text />
      </template>
    </el-table-column>
    <el-table-column :label="t('skills.columnEvidence')" width="90">
      <template #default="{ row }">{{ row.evidence_count }}</template>
    </el-table-column>
    <el-table-column :label="t('skills.columnFirstSeen')" width="120">
      <template #default="{ row }">{{ formatDate(row.first_observed_at) }}</template>
    </el-table-column>
    <el-table-column :label="t('skills.columnLastSeen')" width="120">
      <template #default="{ row }">{{ formatDate(row.last_observed_at) }}</template>
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

  <el-empty v-if="!loading && skills.length === 0" :description="t('skills.noEntries')" />

  <el-dialog v-model="dialog" :title="editingSkillId ? t('skills.edit') : t('skills.add')" width="420px">
    <el-form :model="form" label-width="80px">
      <el-form-item :label="t('skills.columnSkill')">
        <el-input v-model="form.name" :placeholder="t('skills.namePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('skills.columnCategory')">
        <el-input v-model="form.category" :placeholder="t('skills.categoryPlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('skills.columnProficiency')">
        <el-rate v-model="form.proficiency" :texts="proficiencyTexts" show-text />
        <el-button v-if="form.proficiency" size="small" text @click="clearProficiency">
          {{ t('skills.clearProficiency') }}
        </el-button>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button type="primary" @click="submit">{{ editingSkillId ? t('common.save') : t('common.add') }}</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="csvDialog" :title="t('skills.importCsv')" width="480px">
    <p class="dialog-hint">{{ t('skills.csvImportHint') }}</p>
    <el-upload
      :auto-upload="false"
      :show-file-list="true"
      :limit="1"
      accept=".csv"
      :on-change="handleCsvFileChange"
    >
      <el-button size="small">{{ t('common.add') }}</el-button>
    </el-upload>
    <template #footer>
      <el-button type="primary" :loading="importingCsv" @click="submitCsvImport">{{ t('common.add') }}</el-button>
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

.dialog-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-top: 0;
}

.sample-tag {
  margin-left: 0.4rem;
}
</style>
