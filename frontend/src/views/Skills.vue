<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t, locale } = useI18n()
const skills = ref([])
const loading = ref(true)
const dialog = ref(false)
const form = reactive({ name: '', category: '' })

async function reload() {
  skills.value = await api.getSkills()
}

onMounted(async () => {
  await reload()
  loading.value = false
})

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(locale.value)
}

async function submit() {
  if (!form.name.trim()) return
  await api.addSkill(form.name, form.category)
  Object.assign(form, { name: '', category: '' })
  dialog.value = false
  await reload()
  ElMessage.success(t('skills.added'))
}

async function remove(id) {
  await ElMessageBox.confirm(t('skills.confirmDelete'), t('profile.confirm'))
  await api.deleteSkill(id)
  await reload()
}
</script>

<template>
  <div class="header-row">
    <div>
      <h1 class="page-title">{{ t('skills.title') }}</h1>
      <p class="page-subtitle">{{ t('skills.subtitle') }}</p>
    </div>
    <el-button type="primary" @click="dialog = true">{{ t('skills.add') }}</el-button>
  </div>

  <el-table :data="skills" v-loading="loading" style="width: 100%">
    <el-table-column prop="name" :label="t('skills.columnSkill')" min-width="200" />
    <el-table-column :label="t('skills.columnCategory')" width="140">
      <template #default="{ row }"><el-tag>{{ row.category }}</el-tag></template>
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
    <el-table-column width="80">
      <template #default="{ row }">
        <el-button size="small" text type="danger" @click="remove(row.id)">{{ t('common.delete') }}</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-empty v-if="!loading && skills.length === 0" :description="t('skills.noEntries')" />

  <el-dialog v-model="dialog" :title="t('skills.add')" width="420px">
    <el-form :model="form" label-width="80px">
      <el-form-item :label="t('skills.columnSkill')">
        <el-input v-model="form.name" :placeholder="t('skills.namePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('skills.columnCategory')">
        <el-input v-model="form.category" :placeholder="t('skills.categoryPlaceholder')" />
      </el-form-item>
    </el-form>
    <template #footer><el-button type="primary" @click="submit">{{ t('common.add') }}</el-button></template>
  </el-dialog>
</template>

<style scoped>
.header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}
</style>
