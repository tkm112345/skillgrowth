<script setup>
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t, locale } = useI18n()

const content = ref('')
const loading = ref(true)
const saving = ref(false)
const updatedAt = ref(null)

onMounted(async () => {
  try {
    const vision = await api.getVision()
    content.value = vision.content
    updatedAt.value = vision.updated_at
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

function formatDateTime(iso) {
  return new Date(iso).toLocaleString(locale.value)
}

async function save() {
  saving.value = true
  try {
    const updated = await api.updateVision(content.value)
    updatedAt.value = updated.updated_at
    ElMessage.success(t('vision.saved'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('vision.title') }}</h1>
  <p class="page-subtitle">{{ t('vision.subtitle') }}</p>

  <el-card shadow="never" class="chart-card accent-aqua" v-loading="loading">
    <el-input v-model="content" type="textarea" :rows="10" :placeholder="t('vision.placeholder')" />
    <div class="vision-footer">
      <span v-if="updatedAt" class="vision-updated">
        {{ t('vision.updatedAt', { date: formatDateTime(updatedAt) }) }}
      </span>
      <el-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
    </div>
  </el-card>
</template>

<style scoped>
.chart-card {
  margin-bottom: 1rem;
}

.vision-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
}

.vision-updated {
  font-size: 0.78rem;
  color: var(--ink-muted);
}
</style>
