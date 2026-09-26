<script setup>
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { api } from '../api'

const { t, locale } = useI18n()
const router = useRouter()

const goals = ref([])
const loading = ref(true)
const guidance = ref(null)
const loadingGuidance = ref(false)

const sessions = ref([])
const loadingSessions = ref(true)
const startingSession = ref(false)

const settings = ref(null)
const customInstructions = ref('')
const savingCustomInstructions = ref(false)

onMounted(async () => {
  try {
    goals.value = await api.getGoals()
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
  try {
    sessions.value = await api.getConsultSessions()
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loadingSessions.value = false
  }
  try {
    settings.value = await api.getSettings()
    customInstructions.value = settings.value.consult_custom_instructions
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  }
})

async function saveCustomInstructions() {
  savingCustomInstructions.value = true
  try {
    settings.value = await api.updateSettings({
      ...settings.value,
      consult_custom_instructions: customInstructions.value,
    })
    ElMessage.success(t('ai.consultCustomInstructionsSaved'))
  } finally {
    savingCustomInstructions.value = false
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(locale.value)
}

async function startConsult() {
  startingSession.value = true
  try {
    const session = await api.createConsultSession()
    router.push(`/consult/${session.id}`)
  } finally {
    startingSession.value = false
  }
}

const hasAnyGoal = computed(() => goals.value.some((g) => g.description.trim()))

async function fetchGuidance() {
  loadingGuidance.value = true
  try {
    guidance.value = await api.getGrowthGuidance()
  } catch (e) {
    ElMessage.error(t('ai.guidanceError', { error: e.message }))
  } finally {
    loadingGuidance.value = false
  }
}

// -- gap check --
const jobDescription = ref('')
const checking = ref(false)
const gapResult = ref(null)

async function runGapCheck() {
  if (!jobDescription.value.trim()) return
  checking.value = true
  try {
    gapResult.value = await api.gapCheck(jobDescription.value)
  } catch (e) {
    ElMessage.error(t('ai.gapCheckError', { error: e.message }))
  } finally {
    checking.value = false
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('ai.title') }}</h1>
  <p class="page-subtitle">{{ t('ai.subtitle') }}</p>

  <el-card shadow="never" class="section-card accent-aqua" v-loading="loadingSessions">
    <template #header>{{ t('ai.consultHeader') }}</template>
    <p class="hint">{{ t('ai.consultHint') }}</p>

    <el-collapse class="consult-custom-collapse">
      <el-collapse-item :title="t('ai.consultCustomInstructionsLabel')">
        <p class="hint">{{ t('ai.consultCustomInstructionsHint') }}</p>
        <el-input
          v-model="customInstructions"
          type="textarea"
          :rows="3"
          :placeholder="t('ai.consultCustomInstructionsPlaceholder')"
        />
        <el-button
          size="small"
          type="primary"
          :loading="savingCustomInstructions"
          @click="saveCustomInstructions"
          class="consult-custom-save-btn"
        >
          {{ t('common.save') }}
        </el-button>
      </el-collapse-item>
    </el-collapse>

    <el-button type="primary" :loading="startingSession" @click="startConsult">
      {{ t('ai.consultStart') }}
    </el-button>

    <ul v-if="sessions.length" class="consult-session-list">
      <li v-for="s in sessions" :key="s.id">
        <router-link :to="`/consult/${s.id}`" class="consult-session-link">
          {{ s.title || t('ai.consultUntitled') }}
        </router-link>
        <span class="consult-session-date">{{ formatDate(s.updated_at) }}</span>
      </li>
    </ul>
  </el-card>

  <el-card shadow="never" class="section-card accent-violet" v-loading="loading">
    <template #header>{{ t('ai.guidanceHeader') }}</template>
    <p class="hint">{{ t('ai.guidanceHint') }}</p>

    <el-button
      :disabled="!hasAnyGoal"
      :loading="loadingGuidance"
      @click="fetchGuidance"
    >
      {{ t('ai.guidanceButton') }}
    </el-button>
    <p v-if="!hasAnyGoal" class="need-goal-hint">{{ t('ai.guidanceNeedsGoal') }}</p>

    <div v-if="guidance && guidance.by_horizon.length" class="guidance-result">
      <div v-for="item in guidance.by_horizon" :key="item.horizon" class="guidance-item">
        <div class="guidance-horizon">{{ item.horizon }}</div>
        <p class="guidance-advice">{{ item.advice }}</p>
      </div>
    </div>
  </el-card>

  <el-card shadow="never" class="section-card accent-magenta">
    <template #header>{{ t('ai.gapCheckHeader') }}</template>
    <p class="hint">{{ t('ai.gapCheckHint') }}</p>
    <el-input
      v-model="jobDescription"
      type="textarea"
      :rows="6"
      :placeholder="t('ai.gapCheckPlaceholder')"
    />
    <el-button type="primary" :loading="checking" @click="runGapCheck" class="gap-check-btn">
      {{ t('ai.gapCheckRun') }}
    </el-button>

    <div v-if="gapResult" class="gap-result">
      <p>{{ gapResult.summary }}</p>
      <div class="gap-columns">
        <div>
          <div class="gap-label matched">{{ t('ai.gapCheckMatched') }}</div>
          <el-tag v-for="(m, i) in gapResult.matched" :key="i" type="success" class="gap-tag">{{ m }}</el-tag>
        </div>
        <div>
          <div class="gap-label missing">{{ t('ai.gapCheckMissing') }}</div>
          <el-tag v-for="(m, i) in gapResult.missing" :key="i" type="danger" class="gap-tag">{{ m }}</el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.section-card {
  margin-bottom: 1rem;
}

.hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-top: 0;
}

.consult-custom-collapse {
  margin-bottom: 0.75rem;
}

.consult-custom-save-btn {
  margin-top: 0.5rem;
}

.consult-session-list {
  list-style: none;
  margin: 1rem 0 0;
  padding: 0.75rem 0 0;
  border-top: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.consult-session-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.consult-session-link {
  color: var(--ink-primary);
  text-decoration: none;
  font-size: 0.85rem;
}

.consult-session-link:hover {
  text-decoration: underline;
}

.consult-session-date {
  flex-shrink: 0;
  color: var(--ink-muted);
  font-size: 0.75rem;
}

.need-goal-hint {
  display: inline-block;
  margin: 0.75rem 0 0 0.75rem;
  font-size: 0.8rem;
  color: var(--ink-muted);
}

.guidance-result {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--el-border-color);
}

.guidance-item {
  margin-bottom: 0.75rem;
}

.guidance-item:last-child {
  margin-bottom: 0;
}

.guidance-horizon {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.guidance-advice {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin: 0;
}

.gap-check-btn {
  margin-top: 0.75rem;
}

.gap-result {
  margin-top: 1rem;
}

.gap-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.gap-label {
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.gap-tag {
  margin: 0 0.4rem 0.4rem 0;
}
</style>
