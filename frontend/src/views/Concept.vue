<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const principleKeys = ['selfHosted', 'freeText', 'llmOptional', 'pluggableLlm', 'evidenceNotAssessment']

const loopSteps = ['loopVision', 'loopSkillTrack', 'loopRecord', 'loopReflect']
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

    <!-- Narrow screens: the circular layout has no room for outward-facing
         labels, so fall back to a simple vertical list instead of risking
         overlap. Toggled by CSS media queries, not JS, to avoid a layout
         flash. -->
    <ol class="loop-list">
      <li v-for="node in nodes" :key="`${node.key}-list`">
        <span class="loop-list-badge">{{ node.num }}</span>
        {{ t(`concept.${node.key}`) }}
      </li>
      <li class="loop-list-branch">
        <span class="loop-list-badge loop-list-badge--branch">5</span>
        {{ t('concept.loopPrepare') }}
      </li>
    </ol>

    <!-- Step 5 is a deliberate exception to the circular 1-2-3-4-1 layout
         above: the main flow is 4 back to 1, and 5 is only an occasional
         detour off of step 4 — not a step every pass through the loop
         takes. Drawn as a separate branch rather than folded into the
         circle so that asymmetry stays visible instead of implying 5 is
         just as central as 1-4. -->
    <div class="loop-branch">
      <p class="loop-branch-note">{{ t('concept.loopBranchLabel') }}</p>
      <div class="loop-branch-flow">
        <span class="loop-branch-chip">4</span>
        <span class="loop-branch-arrow">╌╌▶</span>
        <span class="loop-branch-chip loop-branch-chip--five">5</span>
        <span class="loop-branch-arrow">╌╌▶</span>
        <span class="loop-branch-chip">1</span>
      </div>
      <p class="loop-branch-text">{{ t('concept.loopPrepare') }}</p>
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
  max-width: 540px;
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
  transform: translate(-50%, calc(-100% - 48px));
  text-align: center;
}

.loop-label--bottom {
  transform: translate(-50%, 48px);
  text-align: center;
}

.loop-label--right {
  transform: translate(48px, -50%);
  text-align: left;
}

.loop-label--left {
  transform: translate(calc(-100% - 48px), -50%);
  text-align: right;
}

.loop-list {
  display: none;
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 1.5rem;
}

.loop-list li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0;
  font-size: 0.85rem;
  color: var(--ink-secondary);
  border-bottom: 1px solid var(--el-border-color);
}

.loop-list li:last-child {
  border-bottom: none;
}

.loop-list-badge {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  color: var(--ink-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.loop-list-badge--branch {
  border-style: dashed;
  border-color: var(--ink-muted);
  color: var(--ink-muted);
}

.loop-list-branch {
  color: var(--ink-muted);
}

@media (max-width: 560px) {
  .loop-circle {
    display: none;
  }

  .loop-list {
    display: block;
  }
}

.loop-branch {
  max-width: 540px;
  margin: 0 auto 1rem;
  padding: 0.75rem 1rem;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
}

.loop-branch-note {
  margin: 0 0 0.5rem;
  font-size: 0.78rem;
  color: var(--ink-muted);
}

.loop-branch-flow {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.loop-branch-chip {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--ink-muted);
  color: var(--ink-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.loop-branch-chip--five {
  border-color: var(--accent);
  color: var(--accent);
}

.loop-branch-arrow {
  color: var(--ink-muted);
  font-size: 0.8rem;
  letter-spacing: -1px;
}

.loop-branch-text {
  margin: 0.5rem 0 0;
  font-size: 0.82rem;
  color: var(--ink-secondary);
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
