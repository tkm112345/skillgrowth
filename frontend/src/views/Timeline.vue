<script setup>
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { tagStyle } from '../hue'

const PAGE_SIZE = 50

const { t, locale } = useI18n()
const entries = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)

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

onMounted(async () => {
  try {
    const page = await api.getEvidence(PAGE_SIZE, 0)
    entries.value = page
    hasMore.value = page.length === PAGE_SIZE
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
        <el-tag size="small" :style="tagStyle(entry.source_type)" plain>{{ sourceLabel(entry.source_type) }}</el-tag>
        <p>{{ entry.raw_input || t('timeline.image') }}</p>
      </el-card>
    </el-timeline-item>
  </el-timeline>

  <el-button v-if="hasMore" :loading="loadingMore" @click="loadMore" class="load-more-btn">
    {{ t('timeline.loadMore') }}
  </el-button>

  <el-empty v-if="!loading && entries.length === 0" :description="t('timeline.noEntries')" />
</template>

<style scoped>
.load-more-btn {
  display: block;
  margin: 0.5rem auto 0;
}
</style>
