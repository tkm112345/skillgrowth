<script setup>
import {
  Compass,
  Connection,
  DataAnalysis,
  DataLine,
  EditPen,
  Expand,
  Files,
  Fold,
  Grid,
  Guide,
  List,
  MagicStick,
  Medal,
  Notebook,
  Postcard,
  Promotion,
  Setting,
  Share,
  Suitcase,
  Sunrise,
  TrendCharts,
} from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import GlobalSearch from './components/GlobalSearch.vue'

const route = useRoute()
const { t } = useI18n()

const contributeVisible = ref(false)

const SIDEBAR_STORAGE_KEY = 'skillgrowth-sidebar-collapsed'
const SIDEBAR_WIDTH_STORAGE_KEY = 'skillgrowth-sidebar-width'
const MOBILE_BREAKPOINT_PX = 768
// Widest nav label (self-feedback, ja) needs ~249px of content width at
// default font size; this default gives it room without truncating.
const DEFAULT_SIDEBAR_WIDTH_PX = 280
const MIN_SIDEBAR_WIDTH_PX = 200
const MAX_SIDEBAR_WIDTH_PX = 420

function initialCollapsed() {
  const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY)
  if (stored !== null) return stored === '1'
  // No stored preference yet (first visit): default to collapsed on a
  // phone-width screen, since the always-expanded sidebar otherwise eats
  // roughly half the viewport there. Once a preference is stored (the
  // user ever toggles it, in either direction), it's respected regardless
  // of screen width from then on.
  return window.innerWidth <= MOBILE_BREAKPOINT_PX
}

const collapsed = ref(initialCollapsed())
function toggleCollapsed() {
  collapsed.value = !collapsed.value
  localStorage.setItem(SIDEBAR_STORAGE_KEY, collapsed.value ? '1' : '0')
}

function initialSidebarWidth() {
  const stored = Number(localStorage.getItem(SIDEBAR_WIDTH_STORAGE_KEY))
  if (stored >= MIN_SIDEBAR_WIDTH_PX && stored <= MAX_SIDEBAR_WIDTH_PX) return stored
  return DEFAULT_SIDEBAR_WIDTH_PX
}

const sidebarWidth = ref(initialSidebarWidth())
const resizing = ref(false)

function startResize(event) {
  resizing.value = true
  const startX = event.clientX
  const startWidth = sidebarWidth.value

  function onMove(moveEvent) {
    const next = startWidth + (moveEvent.clientX - startX)
    sidebarWidth.value = Math.min(MAX_SIDEBAR_WIDTH_PX, Math.max(MIN_SIDEBAR_WIDTH_PX, next))
  }
  function onUp() {
    resizing.value = false
    localStorage.setItem(SIDEBAR_WIDTH_STORAGE_KEY, String(sidebarWidth.value))
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

const year = new Date().getFullYear()
const version = ref('')
onMounted(async () => {
  try {
    const res = await fetch('/api/version')
    version.value = (await res.json()).version
  } catch (e) {
    // version display is cosmetic; ignore failures silently
  }
})
</script>

<template>
  <el-container class="shell" :class="{ 'no-select': resizing }">
    <el-aside :width="collapsed ? '60px' : `${sidebarWidth}px`" class="sidebar" :class="{ 'sidebar-resizing': resizing }">
      <div class="brand">
        <img src="/favicon.svg" alt="" class="brand-mark" />
        <span class="brand-text" v-show="!collapsed">{{ t('app.brand') }}</span>
      </div>
      <el-menu :default-active="route.path" :collapse="collapsed" router class="nav">
        <el-sub-menu index="group-overview">
          <template #title>
            <el-icon><Grid /></el-icon>
            <span>{{ t('nav.groupOverview') }}</span>
          </template>
          <el-menu-item index="/concept">
            <el-icon style="color: var(--hue-blue)"><Compass /></el-icon>
            <template #title>{{ t('nav.concept') }}</template>
          </el-menu-item>
          <el-menu-item index="/">
            <el-icon style="color: var(--hue-blue)"><DataAnalysis /></el-icon>
            <template #title>{{ t('nav.dashboard') }}</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="group-direction">
          <template #title>
            <el-icon><Guide /></el-icon>
            <span>{{ t('nav.groupDirection') }}</span>
          </template>
          <el-menu-item index="/vision">
            <el-icon style="color: var(--hue-aqua)"><Sunrise /></el-icon>
            <template #title>{{ t('nav.vision') }}</template>
          </el-menu-item>
          <el-menu-item index="/self-feedback">
            <el-icon style="color: var(--hue-yellow)"><EditPen /></el-icon>
            <template #title>{{ t('nav.selfFeedback') }}</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="group-skills">
          <template #title>
            <el-icon><DataLine /></el-icon>
            <span>{{ t('nav.groupSkills') }}</span>
          </template>
          <el-menu-item index="/skills">
            <el-icon style="color: var(--hue-orange)"><List /></el-icon>
            <template #title>{{ t('nav.skills') }}</template>
          </el-menu-item>
          <el-menu-item index="/timeline">
            <el-icon style="color: var(--hue-magenta)"><TrendCharts /></el-icon>
            <template #title>{{ t('nav.timeline') }}</template>
          </el-menu-item>
          <el-menu-item index="/certifications">
            <el-icon style="color: var(--hue-aqua)"><Medal /></el-icon>
            <template #title>{{ t('nav.certifications') }}</template>
          </el-menu-item>
          <el-menu-item index="/connections">
            <el-icon style="color: var(--hue-blue)"><Connection /></el-icon>
            <template #title>{{ t('nav.connections') }}</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="group-background">
          <template #title>
            <el-icon><Postcard /></el-icon>
            <span>{{ t('nav.groupBackground') }}</span>
          </template>
          <el-menu-item index="/profile">
            <el-icon style="color: var(--hue-violet)"><Notebook /></el-icon>
            <template #title>{{ t('nav.profile') }}</template>
          </el-menu-item>
          <el-menu-item index="/portfolio">
            <el-icon style="color: var(--hue-red)"><Suitcase /></el-icon>
            <template #title>{{ t('nav.portfolio') }}</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="group-output">
          <template #title>
            <el-icon><Share /></el-icon>
            <span>{{ t('nav.groupOutput') }}</span>
          </template>
          <el-menu-item index="/export">
            <el-icon style="color: var(--hue-green)"><Files /></el-icon>
            <template #title>{{ t('nav.export') }}</template>
          </el-menu-item>
          <el-menu-item index="/ai">
            <el-icon style="color: var(--hue-yellow)"><MagicStick /></el-icon>
            <template #title>{{ t('nav.ai') }}</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>{{ t('nav.settings') }}</template>
        </el-menu-item>
      </el-menu>
      <div class="contribute-wrap">
        <el-button class="contribute-btn" :class="{ 'contribute-btn-collapsed': collapsed }" @click="contributeVisible = true">
          <el-icon><Promotion /></el-icon>
          <span v-if="!collapsed">{{ t('contribute.button') }}</span>
        </el-button>
      </div>
      <div class="sidebar-footer">
        <span v-if="!collapsed">© {{ year }} {{ t('app.brand') }}<span v-if="version"> · v{{ version }}</span></span>
        <span v-else>©</span>
      </div>
      <div v-if="!collapsed" class="sidebar-resize-handle" @mousedown="startResize"></div>
    </el-aside>
    <el-container class="main-area">
      <el-header class="topbar">
        <el-button
          text
          @click="toggleCollapsed"
          :icon="collapsed ? Expand : Fold"
          :aria-label="t('app.toggleSidebar')"
        />
        <GlobalSearch />
      </el-header>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <el-dialog v-model="contributeVisible" :title="t('contribute.title')" width="420px">
    <p class="contribute-line">{{ t('contribute.body') }}</p>
    <a
      class="contribute-link"
      href="https://github.com/tkm112345/skillgrowth"
      target="_blank"
      rel="noopener noreferrer"
    >
      {{ t('contribute.githubLink') }} ↗
    </a>
    <a
      class="contribute-link"
      href="https://github.com/tkm112345/skillgrowth/issues"
      target="_blank"
      rel="noopener noreferrer"
    >
      {{ t('contribute.issueLink') }} ↗
    </a>
    <template #footer>
      <el-button @click="contributeVisible = false">{{ t('common.close') }}</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.shell {
  height: 100vh;
  overflow: hidden;
}

.shell.no-select {
  user-select: none;
}

.main-area {
  height: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.sidebar {
  --el-menu-active-color: var(--ink-primary);
  --el-menu-text-color: var(--ink-secondary);
  position: relative;
  border-right: 1px solid var(--el-border-color);
  background: var(--page-bg);
  transition: width 0.15s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-resizing {
  transition: none;
}

.sidebar-resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 5px;
  cursor: col-resize;
  z-index: 1;
}

.sidebar-resize-handle:hover {
  background: var(--accent);
  opacity: 0.5;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 1.1rem 1rem 0.75rem;
  white-space: nowrap;
}

.brand-mark {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

.brand-text {
  font-weight: 600;
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}

.nav {
  border-right: none;
  background: transparent;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav :deep(.el-menu-item),
.nav :deep(.el-sub-menu__title) {
  border-radius: 6px;
  margin: 1px 8px;
  height: 32px;
  line-height: 32px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav :deep(.el-menu-item.is-active) {
  background: var(--hover-wash);
  font-weight: 600;
}

.nav :deep(.el-menu-item:hover),
.nav :deep(.el-sub-menu__title:hover) {
  background: var(--hover-wash);
}

.nav :deep(.el-sub-menu .el-menu-item) {
  height: 30px;
  line-height: 30px;
  min-width: 0;
}

.sidebar-footer {
  padding: 0.75rem 1rem;
  font-size: 0.72rem;
  color: var(--ink-muted);
  white-space: nowrap;
  border-top: 1px solid var(--el-border-color);
}

.contribute-wrap {
  padding: 0 12px 8px;
}

.contribute-btn {
  width: 100%;
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.contribute-btn:hover {
  filter: brightness(1.08);
}

.contribute-btn-collapsed {
  width: 36px;
  padding: 0;
}

.contribute-line {
  margin: 0 0 0.75rem;
  font-size: 0.85rem;
  color: var(--ink-secondary);
}

.contribute-link {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.85rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
}

.contribute-link:hover {
  text-decoration: underline;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color);
  height: 52px;
  flex-shrink: 0;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 1.75rem;
}
</style>
