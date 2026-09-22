<script setup>
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'
import { isDark } from '../theme'

const { t } = useI18n()

const skills = ref([])
const timeline = ref([])
const goals = ref([])
const loading = ref(true)
const savingGoal = ref('')
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
  const [, goalList] = await Promise.all([reloadSkillData(), api.getGoals()])
  goals.value = goalList
  loading.value = false
})

async function saveGoal(goal) {
  savingGoal.value = goal.horizon
  try {
    await api.updateGoal(goal.horizon, goal.description)
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

  <el-card shadow="never" class="chart-card">
    <template #header>{{ t('dashboard.checkinHeader') }}</template>
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

  <el-card shadow="never" class="chart-card">
    <template #header>{{ t('dashboard.goalsHeader') }}</template>
    <el-row :gutter="16">
      <el-col :span="8" v-for="goal in goals" :key="goal.horizon">
        <div class="goal-label">{{ t(horizonLabelKeys[goal.horizon]) }}</div>
        <el-input
          v-model="goal.description"
          type="textarea"
          :rows="3"
          :placeholder="t('dashboard.goalPlaceholder')"
          @blur="saveGoal(goal)"
        />
        <span v-if="savingGoal === goal.horizon" class="saving">{{ t('dashboard.goalSaving') }}</span>
      </el-col>
    </el-row>
  </el-card>

  <el-card shadow="never" class="chart-card">
    <template #header>{{ t('dashboard.growthHeader') }}</template>
    <v-chart v-if="!loading" :option="growthOption" autoresize style="height: 260px" />
  </el-card>

  <el-card shadow="never" class="chart-card">
    <template #header>{{ t('dashboard.categoryHeader') }}</template>
    <v-chart v-if="!loading" :option="categoryOption" autoresize style="height: 260px" />
  </el-card>

  <el-row :gutter="16" class="stats">
    <el-col :span="8">
      <el-card shadow="never"><div class="stat-label">{{ t('dashboard.statTotalSkills') }}</div><div class="stat-value">{{ skills.length }}</div></el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="never"><div class="stat-label">{{ t('dashboard.statCategories') }}</div><div class="stat-value">{{ categoryCount }}</div></el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="never"><div class="stat-label">{{ t('dashboard.statRecent') }}</div><div class="stat-value">{{ recentCount }}</div></el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.concept-link {
  display: inline-block;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  color: var(--accent);
  text-decoration: none;
}

.concept-link:hover {
  text-decoration: underline;
}

.goal-label {
  font-size: 0.85rem;
  color: var(--ink-secondary);
  margin-bottom: 0.25rem;
}

.saving {
  font-size: 0.75rem;
  color: var(--ink-muted);
}

.checkin-btn {
  margin-top: 0.75rem;
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
