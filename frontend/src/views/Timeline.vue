<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t, locale } = useI18n()
const entries = ref([])
const loading = ref(true)

const sourceLabelKeys = {
  resume: 'timeline.sourceResume',
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

onMounted(async () => {
  entries.value = await api.getEvidence()
  loading.value = false
})

const formatDateTime = computed(() => (iso) => new Date(iso).toLocaleString(locale.value))
</script>

<template>
  <h1 class="page-title">{{ t('timeline.title') }}</h1>
  <p class="page-subtitle">{{ t('timeline.subtitle') }}</p>

  <el-timeline v-loading="loading">
    <el-timeline-item
      v-for="entry in entries"
      :key="entry.id"
      :timestamp="formatDateTime(entry.created_at)"
    >
      <el-card shadow="never">
        <el-tag size="small">{{ sourceLabel(entry.source_type) }}</el-tag>
        <p>{{ entry.raw_input || t('timeline.image') }}</p>
      </el-card>
    </el-timeline-item>
  </el-timeline>

  <el-empty v-if="!loading && entries.length === 0" :description="t('timeline.noEntries')" />
</template>
