<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const principleKeys = ['selfHosted', 'freeText', 'pluggableLlm', 'evidenceNotAssessment']

const loopSteps = ['loopEvidence', 'loopExtraction', 'loopSkillPicture', 'loopReflect']
const SIDES = ['top', 'right', 'bottom', 'left']

const CENTER = 120
const NODE_R = 78

function polarToCartesian(angleDeg, r) {
  const rad = ((angleDeg - 90) * Math.PI) / 180
  return { x: CENTER + r * Math.cos(rad), y: CENTER + r * Math.sin(rad) }
}

const nodes = computed(() =>
  loopSteps.map((key, i) => {
    const angle = (360 / loopSteps.length) * i
    const point = polarToCartesian(angle, NODE_R)
    return {
      key,
      num: i + 1,
      x: point.x,
      y: point.y,
      leftPct: (point.x / (CENTER * 2)) * 100,
      topPct: (point.y / (CENTER * 2)) * 100,
      side: SIDES[i],
    }
  }),
)

const arcPaths = computed(() => {
  const n = loopSteps.length
  return Array.from({ length: n }, (_, i) => {
    const start = polarToCartesian((360 / n) * i, NODE_R)
    const end = polarToCartesian((360 / n) * (i + 1), NODE_R)
    return `M ${start.x} ${start.y} A ${NODE_R} ${NODE_R} 0 0 1 ${end.x} ${end.y}`
  })
})
</script>

<template>
  <h1 class="page-title">{{ t('concept.title') }}</h1>
  <p class="page-subtitle">{{ t('concept.tagline') }}</p>

  <el-card shadow="never" class="section-card">
    <template #header>{{ t('concept.loopHeader') }}</template>

    <div class="loop-circle">
      <svg viewBox="0 0 240 240" class="loop-svg">
        <defs>
          <marker
            id="loop-arrow"
            viewBox="0 0 10 10"
            refX="7"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)" />
          </marker>
        </defs>
        <path
          v-for="(d, i) in arcPaths"
          :key="i"
          :d="d"
          fill="none"
          stroke="var(--accent)"
          stroke-width="2"
          marker-end="url(#loop-arrow)"
        />
        <circle
          v-for="node in nodes"
          :key="node.key"
          :cx="node.x"
          :cy="node.y"
          r="14"
          fill="var(--surface)"
          stroke="var(--accent)"
          stroke-width="2"
        />
        <text
          v-for="node in nodes"
          :key="`${node.key}-num`"
          :x="node.x"
          :y="node.y"
          text-anchor="middle"
          dominant-baseline="central"
          class="loop-num"
        >
          {{ node.num }}
        </text>
      </svg>

      <div
        v-for="node in nodes"
        :key="`${node.key}-label`"
        class="loop-label"
        :class="`loop-label--${node.side}`"
        :style="{ left: `${node.leftPct}%`, top: `${node.topPct}%` }"
      >
        {{ t(`concept.${node.key}`) }}
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

.loop-circle {
  position: relative;
  width: 100%;
  max-width: 460px;
  margin: 0.5rem auto 1.5rem;
  aspect-ratio: 1 / 1;
}

.loop-svg {
  width: 100%;
  height: 100%;
}

.loop-num {
  font-size: 13px;
  font-weight: 700;
  fill: var(--ink-primary);
}

.loop-label {
  position: absolute;
  width: 118px;
  font-size: 0.78rem;
  line-height: 1.35;
  color: var(--ink-secondary);
}

.loop-label--top {
  transform: translate(-50%, calc(-100% - 20px));
  text-align: center;
}

.loop-label--bottom {
  transform: translate(-50%, 20px);
  text-align: center;
}

.loop-label--right {
  transform: translate(20px, -50%);
  text-align: left;
}

.loop-label--left {
  transform: translate(calc(-100% - 20px), -50%);
  text-align: right;
}

.loop-note {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin: 0;
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
