<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t } = useI18n()
const bookmarks = ref([])
const loading = ref(true)
const dialog = ref(false)
const form = reactive({ url: '', title: '', memo: '' })
const editingId = ref(null)

async function reload() {
  bookmarks.value = await api.getBookmarks()
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

function openAddDialog() {
  editingId.value = null
  Object.assign(form, { url: '', title: '', memo: '' })
  dialog.value = true
}

function openEditDialog(row) {
  editingId.value = row.id
  Object.assign(form, { url: row.url, title: row.title, memo: row.memo || '' })
  dialog.value = true
}

async function submit() {
  if (!form.url.trim() || !form.title.trim()) return
  const payload = { url: form.url, title: form.title, memo: form.memo }
  try {
    if (editingId.value) {
      await api.updateBookmark(editingId.value, payload)
      ElMessage.success(t('bookmarks.updated'))
    } else {
      await api.addBookmark(payload)
      ElMessage.success(t('bookmarks.added'))
    }
    dialog.value = false
    await reload()
  } catch (e) {
    ElMessage.error(t('common.saveError'))
  }
}

async function remove(id) {
  await ElMessageBox.confirm(t('bookmarks.confirmDelete'), t('profile.confirm'))
  try {
    await api.deleteBookmark(id)
    await reload()
  } catch (e) {
    ElMessage.error(t('common.deleteError'))
  }
}
</script>

<template>
  <div class="header-row">
    <div>
      <h1 class="page-title">{{ t('bookmarks.title') }}</h1>
      <p class="page-subtitle">{{ t('bookmarks.subtitle') }}</p>
    </div>
    <div class="header-actions">
      <el-button type="primary" @click="openAddDialog">{{ t('bookmarks.add') }}</el-button>
    </div>
  </div>

  <el-table :data="bookmarks" v-loading="loading" style="width: 100%">
    <el-table-column :label="t('bookmarks.columnTitle')" min-width="200">
      <template #default="{ row }">
        <a :href="row.url" target="_blank" rel="noopener noreferrer">{{ row.title }}</a>
      </template>
    </el-table-column>
    <el-table-column :label="t('bookmarks.columnMemo')" min-width="200">
      <template #default="{ row }">{{ row.memo }}</template>
    </el-table-column>
    <el-table-column width="140">
      <template #default="{ row }">
        <el-button size="small" text @click="openEditDialog(row)">{{ t('common.edit') }}</el-button>
        <el-button size="small" text type="danger" @click="remove(row.id)">{{ t('common.delete') }}</el-button>
      </template>
    </el-table-column>
    <template #empty><span></span></template>
  </el-table>

  <el-empty v-if="!loading && bookmarks.length === 0" :description="t('bookmarks.noEntries')" />

  <el-dialog v-model="dialog" :title="editingId ? t('bookmarks.edit') : t('bookmarks.add')" width="420px">
    <el-form :model="form" label-position="top">
      <el-form-item :label="t('bookmarks.urlLabel')">
        <el-input v-model="form.url" placeholder="https://..." />
      </el-form-item>
      <el-form-item :label="t('bookmarks.titleLabel')">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item :label="t('bookmarks.memoLabel')">
        <el-input v-model="form.memo" type="textarea" :rows="3" />
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
