<script setup>
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { isDark } from '../theme'

const HISTORY_PAGE_SIZE = 5

const { t, locale } = useI18n()

const skills = ref([])
const timeline = ref([])
const goals = ref([])
const loading = ref(true)
const savingGoal = ref('')
const editingHorizon = ref(null)
const draftText = ref('')
const historyOpenHorizon = ref(null)
const historyByHorizon = reactive({})
const historyHasMoreByHorizon = reactive({})
const historyLoadingByHorizon = reactive({})
const checkinText = ref('')
const submittingCheckin = ref(false)

const horizonLabelKeys = {
  this_year: 'dashboard.horizonThisYear',
  '5_years': 'dashboard.horizon5Years',
  '10_years': 'dashboard.horizon10Years',
}

async function reloadSkillData() {
  const [skillList, timelineList] = await Promise.all([api.getSkills(), api.getSkillTimeline()])
  skills.value = skillList
  timeline.value = timelineList
}

onMounted(async () => {
  try {
    const [, goalList] = await Promise.all([reloadSkillData(), api.getGoals()])
    goals.value = goalList
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(locale.value)
}

function startEditGoal(goal) {
  editingHorizon.value = goal.horizon
  draftText.value = goal.description
}

function cancelEditGoal() {
  editingHorizon.value = null
}

async function loadHistoryPage(horizon) {
  historyLoadingByHorizon[horizon] = true
  try {
    const offset = historyByHorizon[horizon]?.length || 0
    const page = await api.getGoalHistory(horizon, HISTORY_PAGE_SIZE, offset)
    historyByHorizon[horizon] = [...(historyByHorizon[horizon] || []), ...page]
    historyHasMoreByHorizon[horizon] = page.length === HISTORY_PAGE_SIZE
  } finally {
    historyLoadingByHorizon[horizon] = false
  }
}

async function toggleHistory(horizon) {
  if (historyOpenHorizon.value === horizon) {
    historyOpenHorizon.value = null
    return
  }
  historyOpenHorizon.value = horizon
  if (!historyByHorizon[horizon]) {
    await loadHistoryPage(horizon)
  }
}

async function saveGoal(goal) {
  savingGoal.value = goal.horizon
  try {
    const updated = await api.updateGoal(goal.horizon, draftText.value)
    goal.description = updated.description
    editingHorizon.value = null
    if (historyOpenHorizon.value === goal.horizon) {
      historyByHorizon[goal.horizon] = []
      await loadHistoryPage(goal.horizon)
    }
    ElMessage.success(t('dashboard.goalSaved'))
  } finally {
    savingGoal.value = ''
  }
}

async function submitCheckin() {
  if (!checkinText.value.trim()) return
  submittingCheckin.value = true
  try {
    const result = await api.addTextEvidence('checkin', checkinText.value)
    ElMessage.success(t('dashboard.checkinSuccess', { count: result.linked_skills.length }))
    checkinText.value = ''
    await reloadSkillData()
  } finally {
    submittingCheckin.value = false
  }
}

const categoryCount = computed(() => new Set(skills.value.map((s) => s.category)).size)

const recentCount = computed(() => {
  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  return skills.value.filter((s) => new Date(s.first_observed_at).getTime() >= sevenDaysAgo).length
})

const ink = computed(() => (isDark.value ? '#c3c2b7' : '#52514e'))
const grid = computed(() => (isDark.value ? '#2c2c2a' : '#e1e0d9'))
const seriesBlue = computed(() => (isDark.value ? '#3987e5' : '#2a78d6'))

const growthOption = computed(() => {
  const points = timeline.value.map((t, i) => [t.date, i + 1])
  return {
    grid: { left: 40, right: 16, top: 20, bottom: 32 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: grid.value } },
      axisLabel: { color: ink.value },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      axisLabel: { color: ink.value },
      splitLine: { lineStyle: { color: grid.value } },
    },
    series: [
      {
        type: 'line',
        step: 'end',
        data: points,
        symbolSize: 8,
        lineStyle: { width: 2, color: seriesBlue.value },
        itemStyle: { color: seriesBlue.value },
        areaStyle: { color: seriesBlue.value, opacity: 0.08 },
      },
    ],
  }
})

const categoryOption = computed(() => {
  const counts = {}
  for (const s of skills.value) counts[s.category] = (counts[s.category] || 0) + 1
  const entries = Object.entries(counts)
  return {
    grid: { left: 40, right: 16, top: 20, bottom: 48 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: entries.map(([name]) => name),
      axisLine: { lineStyle: { color: grid.value } },
      axisLabel: { color: ink.value, rotate: 20 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      axisLabel: { color: ink.value },
      splitLine: { lineStyle: { color: grid.value } },
    },
    series: [
      {
        type: 'bar',
        data: entries.map(([, count]) => count),
        barMaxWidth: 40,
        itemStyle: { color: seriesBlue.value, borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: 'top', color: ink.value },
      },
    ],
  }
})
</script>

<template>
  <h1 class="page-title">{{ t('dashboard.title') }}</h1>
  <p class="page-subtitle">{{ t('dashboard.subtitle') }}</p>

  <router-link to="/concept" class="concept-link">{{ t('dashboard.conceptLink') }} →</router-link>

  <el-card shadow="never" class="chart-card accent-blue">
    <template #header>{{ t('dashboard.checkinHeader') }}</template>
    <p class="card-hint">{{ t('dashboard.checkinHint') }}</p>
    <el-input
      v-model="checkinText"
      type="textarea"
      :rows="2"
      :placeholder="t('dashboard.checkinPlaceholder')"
    />
    <el-button
      type="primary"
      :loading="submittingCheckin"
      @click="submitCheckin"
      class="checkin-btn"
    >
      {{ t('dashboard.checkinSubmit') }}
    </el-button>
  </el-card>

  <el-card shadow="never" class="chart-card accent-violet">
    <template #header>{{ t('dashboard.goalsHeader') }}</template>
    <p class="card-hint">{{ t('dashboard.goalsHint') }}</p>
    <router-link to="/vision" class="card-hint-link">{{ t('dashboard.goalsVisionLink') }} →</router-link>
    <el-row :gutter="16">
      <el-col :span="8" :xs="24" v-for="goal in goals" :key="goal.horizon">
        <div class="goal-label">{{ t(horizonLabelKeys[goal.horizon]) }}</div>

        <template v-if="editingHorizon === goal.horizon">
          <el-input
            v-model="draftText"
            type="textarea"
            :rows="3"
            :placeholder="t('dashboard.goalPlaceholder')"
          />
          <div class="goal-actions">
            <el-button size="small" @click="cancelEditGoal">{{ t('common.cancel') }}</el-button>
            <el-button
              size="small"
              type="primary"
              :loading="savingGoal === goal.horizon"
              @click="saveGoal(goal)"
            >
              {{ t('common.save') }}
            </el-button>
          </div>
        </template>
        <template v-else>
          <p class="goal-text" :class="{ 'goal-text-empty': !goal.description }">
            {{ goal.description || t('dashboard.goalPlaceholder') }}
          </p>
          <div class="goal-actions">
            <el-button size="small" text @click="startEditGoal(goal)">{{ t('dashboard.goalEdit') }}</el-button>
            <el-button size="small" text @click="toggleHistory(goal.horizon)">
              {{ historyOpenHorizon === goal.horizon ? t('dashboard.goalHistoryHide') : t('dashboard.goalHistory') }}
            </el-button>
          </div>
        </template>

        <div v-if="historyOpenHorizon === goal.horizon" class="goal-history-panel">
          <ul v-if="historyByHorizon[goal.horizon]?.length" class="goal-history">
            <li v-for="h in historyByHorizon[goal.horizon]" :key="h.id">
              <span class="goal-history-date">{{ formatDate(h.created_at) }}</span>
              <span class="goal-history-text">{{ h.description }}</span>
            </li>
          </ul>
          <p v-else-if="!historyLoadingByHorizon[goal.horizon]" class="goal-history-empty">
            {{ t('dashboard.goalHistoryEmpty') }}
          </p>
          <el-button
            v-if="historyHasMoreByHorizon[goal.horizon]"
            size="small"
            text
            :loading="historyLoadingByHorizon[goal.horizon]"
            @click="loadHistoryPage(goal.horizon)"
            class="goal-history-load-more"
          >
            {{ t('dashboard.goalHistoryLoadMore') }}
          </el-button>
        </div>
      </el-col>
    </el-row>

    <router-link to="/ai" class="ai-link">{{ t('dashboard.aiLink') }} →</router-link>
  </el-card>

  <el-card shadow="never" class="chart-card accent-aqua">
    <template #header>{{ t('dashboard.growthHeader') }}</template>
    <v-chart v-if="!loading" :option="growthOption" autoresize style="height: 260px" />
  </el-card>

  <el-card shadow="never" class="chart-card accent-orange">
    <template #header>{{ t('dashboard.categoryHeader') }}</template>
    <v-chart v-if="!loading" :option="categoryOption" autoresize style="height: 260px" />
  </el-card>

  <el-row :gutter="16" class="stats">
    <el-col :span="8">
      <el-card shadow="never" class="stat-card accent-blue"><div class="stat-label">{{ t('dashboard.statTotalSkills') }}</div><div class="stat-value">{{ skills.length }}</div></el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="never" class="stat-card accent-violet"><div class="stat-label">{{ t('dashboard.statCategories') }}</div><div class="stat-value">{{ categoryCount }}</div></el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="never" class="stat-card accent-aqua"><div class="stat-label">{{ t('dashboard.statRecent') }}</div><div class="stat-value">{{ recentCount }}</div></el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.concept-link {
  display: inline-block;
  margin-bottom: 1rem;
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
}

.concept-link:hover {
  background: color-mix(in srgb, var(--accent) 20%, transparent);
  text-decoration: underline;
}

.card-hint {
  font-size: 0.8rem;
  color: var(--ink-secondary);
  margin: 0 0 0.75rem;
}

.card-hint-link {
  display: inline-block;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: var(--accent);
  text-decoration: none;
}

.card-hint-link:hover {
  text-decoration: underline;
}

.goal-label {
  font-size: 0.85rem;
  color: var(--ink-secondary);
  margin-bottom: 0.25rem;
}

.goal-text {
  min-height: 4.2rem;
  margin: 0;
  white-space: pre-wrap;
  font-size: 0.85rem;
}

.goal-text-empty {
  color: var(--ink-muted);
}

.goal-actions {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.goal-history-panel {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--el-border-color);
}

.goal-history {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.goal-history-empty {
  margin: 0;
  font-size: 0.78rem;
  color: var(--ink-muted);
}

.goal-history-load-more {
  display: block;
  margin: 0.4rem auto 0;
}

.goal-history li {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.goal-history-date {
  font-size: 0.72rem;
  color: var(--ink-muted);
}

.goal-history-text {
  font-size: 0.8rem;
  color: var(--ink-secondary);
  white-space: pre-wrap;
}

.checkin-btn {
  margin-top: 0.75rem;
}

.ai-link {
  display: inline-block;
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--hue-violet);
  text-decoration: none;
  font-weight: 600;
}

.ai-link:hover {
  text-decoration: underline;
}

.stats {
  margin-bottom: 1rem;
}

.stat-label {
  color: var(--ink-secondary);
  font-size: 0.85rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  margin-top: 0.25rem;
}

.chart-card {
  margin-bottom: 1rem;
}
</style>
