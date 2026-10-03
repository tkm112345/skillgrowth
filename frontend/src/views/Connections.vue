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

// User-adjustable graph display settings, persisted per-browser (same
// localStorage pattern App.vue uses for the sidebar width) — not everyone's
// screen or data density wants the same label length or node spacing.
const LABEL_WRAP_KEY = 'skillgrowth-graph-label-wrap-chars'
const REPULSION_KEY = 'skillgrowth-graph-repulsion'
const EDGE_LENGTH_KEY = 'skillgrowth-graph-edge-length'

function storedNumber(key, fallback, min, max) {
  const stored = Number(localStorage.getItem(key))
  return stored >= min && stored <= max ? stored : fallback
}

const labelWrapChars = ref(storedNumber(LABEL_WRAP_KEY, 10, 1, 40))
const nodeRepulsion = ref(storedNumber(REPULSION_KEY, 140, 20, 500))
const edgeLength = ref(storedNumber(EDGE_LENGTH_KEY, 90, 20, 400))

function onLabelWrapChange(value) {
  localStorage.setItem(LABEL_WRAP_KEY, String(value))
}
function onRepulsionChange(value) {
  localStorage.setItem(REPULSION_KEY, String(value))
}
function onEdgeLengthChange(value) {
  localStorage.setItem(EDGE_LENGTH_KEY, String(value))
}

function wrapLabel(text, maxChars) {
  if (!maxChars || text.length <= maxChars) return text
  const lines = []
  for (let i = 0; i < text.length; i += maxChars) {
    lines.push(text.slice(i, i + maxChars))
  }
  return lines.join('\n')
}

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
      formatter: (params) =>
        params.dataType === 'node' ? `${t(TYPE_LABEL_KEYS[params.data.rawType])}: ${params.data.rawLabel}` : '',
    },
    legend: { data: categories.map((c) => c.name), textStyle: { color: ink.value } },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        force: { repulsion: nodeRepulsion.value, edgeLength: edgeLength.value },
        categories,
        label: { show: true, color: ink.value, fontSize: 14, lineHeight: 16 },
        lineStyle: { color: 'source', opacity: 0.4, curveness: 0.1 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
        data: graph.value.nodes.map((n) => ({
          id: n.id,
          name: wrapLabel(n.label, labelWrapChars.value),
          rawLabel: n.label,
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
  <template v-else>
    <el-card shadow="never" class="display-settings-card">
      <div class="display-setting">
        <span>{{ t('connections.labelWrapChars') }}</span>
        <el-input-number
          v-model="labelWrapChars"
          :min="1"
          :max="40"
          size="small"
          controls-position="right"
          @change="onLabelWrapChange"
        />
      </div>
      <div class="display-setting">
        <span>{{ t('connections.nodeSpacing') }}</span>
        <el-input-number
          v-model="nodeRepulsion"
          :min="20"
          :max="500"
          :step="10"
          size="small"
          controls-position="right"
          @change="onRepulsionChange"
        />
      </div>
      <div class="display-setting">
        <span>{{ t('connections.edgeLength') }}</span>
        <el-input-number
          v-model="edgeLength"
          :min="20"
          :max="400"
          :step="10"
          size="small"
          controls-position="right"
          @change="onEdgeLengthChange"
        />
      </div>
    </el-card>

    <el-card shadow="never" class="graph-card">
      <v-chart v-if="!loading" :option="graphOption" autoresize style="height: 600px" @click="onNodeClick" />
    </el-card>
  </template>
</template>

<style scoped>
.display-settings-card {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.display-setting {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--ink-secondary);
}

.display-setting .el-input-number {
  width: 110px;
}

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
