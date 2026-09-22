<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const principleKeys = ['selfHosted', 'freeText', 'pluggableLlm', 'evidenceNotAssessment']
</script>

<template>
  <h1 class="page-title">{{ t('concept.title') }}</h1>
  <p class="page-subtitle">{{ t('concept.tagline') }}</p>

  <el-card shadow="never" class="section-card">
    <template #header>{{ t('concept.loopHeader') }}</template>
    <div class="loop">
      <div class="loop-step">
        <div class="loop-badge">1</div>
        <div class="loop-label">{{ t('concept.loopEvidence') }}</div>
      </div>
      <div class="loop-arrow">→</div>
      <div class="loop-step">
        <div class="loop-badge">2</div>
        <div class="loop-label">{{ t('concept.loopExtraction') }}</div>
      </div>
      <div class="loop-arrow">→</div>
      <div class="loop-step">
        <div class="loop-badge">3</div>
        <div class="loop-label">{{ t('concept.loopSkillPicture') }}</div>
      </div>
      <div class="loop-arrow">→</div>
      <div class="loop-step">
        <div class="loop-badge">4</div>
        <div class="loop-label">{{ t('concept.loopOutput') }}</div>
      </div>
    </div>
    <p class="loop-note">{{ t('concept.loopNote') }}</p>
  </el-card>

  <el-card shadow="never" class="section-card">
    <template #header>{{ t('concept.principlesHeader') }}</template>
    <div v-for="key in principleKeys" :key="key" class="principle">
      <div class="principle-title">{{ t(`concept.${key}Title`) }}</div>
      <div class="principle-body">{{ t(`concept.${key}Body`) }}</div>
    </div>
  </el-card>
</template>

<style scoped>
.section-card {
  margin-bottom: 1rem;
}

.loop {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.loop-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 110px;
}

.loop-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--hover-wash);
  color: var(--ink-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.loop-label {
  font-size: 0.8rem;
  color: var(--ink-secondary);
}

.loop-arrow {
  color: var(--ink-muted);
}

.loop-note {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin-top: 1rem;
  margin-bottom: 0;
}

.principle {
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--el-border-color);
}

.principle:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.principle-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.principle-body {
  color: var(--ink-secondary);
  font-size: 0.85rem;
}
</style>
