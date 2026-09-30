<script setup>
import { Search } from '@element-plus/icons-vue'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { api } from '../api'

const { t } = useI18n()
const router = useRouter()

const query = ref('')
const results = ref([])
const popoverVisible = ref(false)
let debounceTimer = null

const ENTITY_ROUTES = {
  skill: '/skills',
  learning_activity: '/timeline',
  portfolio_item: '/portfolio',
}

const ENTITY_LABEL_KEYS = {
  skill: 'nav.skills',
  learning_activity: 'nav.timeline',
  portfolio_item: 'nav.portfolio',
}

const groupedResults = computed(() => {
  const groups = {}
  for (const r of results.value) {
    ;(groups[r.entity_type] ??= []).push(r)
  }
  return groups
})

async function onInput() {
  clearTimeout(debounceTimer)
  const q = query.value.trim()
  if (q.length < 2) {
    results.value = []
    popoverVisible.value = false
    return
  }
  debounceTimer = setTimeout(async () => {
    results.value = await api.search(q)
    popoverVisible.value = true
  }, 300)
}

function goTo(result) {
  popoverVisible.value = false
  query.value = ''
  results.value = []
  router.push({ path: ENTITY_ROUTES[result.entity_type], query: { highlight: result.entity_id } })
}
</script>

<template>
  <el-popover :visible="popoverVisible" placement="bottom-start" :width="320" trigger="manual">
    <template #reference>
      <el-input
        v-model="query"
        :prefix-icon="Search"
        :placeholder="t('search.placeholder')"
        clearable
        class="global-search-input"
        @input="onInput"
        @focus="() => results.length && (popoverVisible = true)"
        @blur="() => setTimeout(() => (popoverVisible = false), 150)"
      />
    </template>
    <div v-if="results.length === 0" class="search-empty">{{ t('search.noResults') }}</div>
    <div v-for="(items, entityType) in groupedResults" :key="entityType" class="search-group">
      <div class="search-group-label">{{ t(ENTITY_LABEL_KEYS[entityType]) }}</div>
      <div v-for="r in items" :key="`${r.entity_type}-${r.entity_id}`" class="search-result" @mousedown="goTo(r)">
        <div class="search-result-title">{{ r.title }}</div>
        <div class="search-result-snippet">{{ r.snippet }}</div>
      </div>
    </div>
  </el-popover>
</template>

<style scoped>
.global-search-input {
  width: 260px;
}

.search-empty {
  padding: 0.5rem 0.25rem;
  font-size: 0.85rem;
  color: var(--ink-muted);
}

.search-group {
  padding: 0.35rem 0;
}

.search-group-label {
  padding: 0.15rem 0.25rem;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--ink-muted);
}

.search-result {
  padding: 0.35rem 0.25rem;
  border-radius: 4px;
  cursor: pointer;
}

.search-result:hover {
  background: var(--hover-wash);
}

.search-result-title {
  font-size: 0.88rem;
  font-weight: 500;
}

.search-result-snippet {
  font-size: 0.78rem;
  color: var(--ink-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
