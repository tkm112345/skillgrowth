<script setup>
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { api } from '../api'
import { hueFor } from '../hue'
import { isDark } from '../theme'

const { t } = useI18n()
const router = useRouter()

const graph = ref({ nodes: [], edges: [] })
const loading = ref(true)

onMounted(async () => {
  try {
    graph.value = await api.getGraph()
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

const ink = computed(() => (isDark.value ? '#c3c2b7' : '#52514e'))

// Fixed hues for the non-skill node types (skills reuse hueFor(category), the
// existing category color-coding pattern) — chosen to match this app's own
// nav icon colors where a 1:1 page mapping exists (certifications=aqua,
// portfolio=red), and otherwise picked to stay visually distinct from those.
const TYPE_HUE = {
  learning_activity: 'aqua',
  education: 'yellow',
  employment: 'violet',
  project: 'green',
  portfolio_item: 'red',
}

const HUE_HEX = {
  blue: { light: '#2a78d6', dark: '#3987e5' },
  orange: { light: '#eb6834', dark: '#d95926' },
  aqua: { light: '#1baf7a', dark: '#199e70' },
  yellow: { light: '#eda100', dark: '#c98500' },
  magenta: { light: '#e87ba4', dark: '#d55181' },
  green: { light: '#008300', dark: '#008300' },
  violet: { light: '#4a3aa7', dark: '#9085e9' },
  red: { light: '#e34948', dark: '#e66767' },
}

function colorFor(node) {
  const hue = node.type === 'skill' ? hueFor(node.category || '') : TYPE_HUE[node.type]
  return HUE_HEX[hue][isDark.value ? 'dark' : 'light']
}

const TYPE_LABEL_KEYS = {
  skill: 'connections.typeSkill',
  learning_activity: 'connections.typeLearningActivity',
  education: 'connections.typeEducation',
  employment: 'connections.typeEmployment',
  project: 'connections.typeProject',
  portfolio_item: 'connections.typePortfolioItem',
}

const ENTITY_ROUTES = {
  skill: '/skills',
  learning_activity: '/certifications',
  education: '/profile',
  employment: '/profile',
  project: '/profile',
  portfolio_item: '/portfolio',
}

const graphOption = computed(() => {
  const degree = {}
  for (const e of graph.value.edges) {
    degree[e.source] = (degree[e.source] || 0) + 1
    degree[e.target] = (degree[e.target] || 0) + 1
  }
  const categories = Object.keys(TYPE_LABEL_KEYS).map((type) => ({ name: t(TYPE_LABEL_KEYS[type]) }))
  const categoryIndex = Object.fromEntries(Object.keys(TYPE_LABEL_KEYS).map((type, i) => [type, i]))

  return {
    tooltip: {
      formatter: (params) => (params.dataType === 'node' ? `${t(TYPE_LABEL_KEYS[params.data.rawType])}: ${params.name}` : ''),
    },
    legend: { data: categories.map((c) => c.name), textStyle: { color: ink.value } },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        force: { repulsion: 140, edgeLength: 90 },
        categories,
        label: { show: true, color: ink.value, fontSize: 14 },
        lineStyle: { color: 'source', opacity: 0.4, curveness: 0.1 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
        data: graph.value.nodes.map((n) => ({
          id: n.id,
          name: n.label,
          rawType: n.type,
          category: categoryIndex[n.type],
          symbol: n.type === 'skill' ? 'circle' : 'diamond',
          symbolSize: 16 + Math.min(degree[n.id] || 0, 10) * 3,
          itemStyle: { color: colorFor(n) },
        })),
        links: graph.value.edges.map((e) => ({ source: e.source, target: e.target })),
      },
    ],
  }
})

function onNodeClick(params) {
  if (params.dataType !== 'node') return
  const route = ENTITY_ROUTES[params.data.rawType]
  if (route) router.push(route)
}
</script>

<template>
  <h1 class="page-title">{{ t('connections.title') }}</h1>
  <p class="page-subtitle">{{ t('connections.subtitle') }}</p>

  <el-card v-if="!loading && graph.nodes.length === 0" shadow="never" class="empty-card">
    {{ t('connections.empty') }}
  </el-card>
  <el-card v-else shadow="never" class="graph-card">
    <v-chart v-if="!loading" :option="graphOption" autoresize style="height: 600px" @click="onNodeClick" />
  </el-card>
</template>

<style scoped>
.graph-card {
  margin-top: 1rem;
}

.empty-card {
  margin-top: 1rem;
  color: var(--ink-muted);
  text-align: center;
  padding: 2rem 0;
}
</style>
