<script setup>
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t } = useI18n()

const form = reactive({
  openai_base_url: '',
  openai_api_key: '',
  llm_model: '',
  llm_vision_model: '',
})
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  try {
    const settings = await api.getSettings()
    Object.assign(form, settings)
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

async function save() {
  saving.value = true
  try {
    await api.updateSettings(form)
    ElMessage.success(t('settings.saveSuccess'))
  } catch (e) {
    ElMessage.error(t('settings.saveError', { error: e.message }))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('settings.title') }}</h1>
  <p class="page-subtitle">{{ t('settings.subtitle') }}</p>

  <el-form :model="form" label-width="160px" v-loading="loading" class="form">
    <el-form-item :label="t('settings.baseUrl')">
      <el-input v-model="form.openai_base_url" placeholder="https://api.openai.com/v1" />
    </el-form-item>
    <el-form-item :label="t('settings.apiKey')">
      <el-input v-model="form.openai_api_key" type="password" show-password />
    </el-form-item>
    <el-form-item :label="t('settings.textModel')">
      <el-input v-model="form.llm_model" placeholder="gpt-4o-mini" />
    </el-form-item>
    <el-form-item :label="t('settings.visionModel')">
      <el-input v-model="form.llm_vision_model" placeholder="gpt-4o-mini" />
    </el-form-item>
    <el-button type="primary" :loading="saving" @click="save">{{ t('settings.save') }}</el-button>
  </el-form>
</template>

<style scoped>
.form {
  max-width: 480px;
}
</style>
