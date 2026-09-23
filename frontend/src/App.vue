<script setup>
import {
  Compass,
  DataAnalysis,
  Expand,
  Files,
  Fold,
  List,
  MagicStick,
  Notebook,
  Promotion,
  Setting,
  Suitcase,
  Sunrise,
  TrendCharts,
} from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const route = useRoute()
const { t } = useI18n()

const contributeVisible = ref(false)

const collapsed = ref(localStorage.getItem('skillgrowth-sidebar-collapsed') === '1')
function toggleCollapsed() {
  collapsed.value = !collapsed.value
  localStorage.setItem('skillgrowth-sidebar-collapsed', collapsed.value ? '1' : '0')
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
  <el-container class="shell">
    <el-aside :width="collapsed ? '60px' : '212px'" class="sidebar">
      <div class="brand">
        <img src="/favicon.svg" alt="" class="brand-mark" />
        <span class="brand-text" v-show="!collapsed">{{ t('app.brand') }}</span>
      </div>
      <el-menu :default-active="route.path" :collapse="collapsed" router class="nav">
        <el-menu-item index="/concept">
          <el-icon style="color: var(--hue-blue)"><Compass /></el-icon>
          <template #title>{{ t('nav.concept') }}</template>
        </el-menu-item>
        <el-menu-item index="/">
          <el-icon style="color: var(--hue-blue)"><DataAnalysis /></el-icon>
          <template #title>{{ t('nav.dashboard') }}</template>
        </el-menu-item>
        <el-menu-item index="/vision">
          <el-icon style="color: var(--hue-aqua)"><Sunrise /></el-icon>
          <template #title>{{ t('nav.vision') }}</template>
        </el-menu-item>
        <el-menu-item index="/skills">
          <el-icon style="color: var(--hue-orange)"><List /></el-icon>
          <template #title>{{ t('nav.skills') }}</template>
        </el-menu-item>
        <el-menu-item index="/timeline">
          <el-icon style="color: var(--hue-magenta)"><TrendCharts /></el-icon>
          <template #title>{{ t('nav.timeline') }}</template>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon style="color: var(--hue-violet)"><Notebook /></el-icon>
          <template #title>{{ t('nav.profile') }}</template>
        </el-menu-item>
        <el-menu-item index="/portfolio">
          <el-icon style="color: var(--hue-red)"><Suitcase /></el-icon>
          <template #title>{{ t('nav.portfolio') }}</template>
        </el-menu-item>
        <el-menu-item index="/export">
          <el-icon style="color: var(--hue-green)"><Files /></el-icon>
          <template #title>{{ t('nav.export') }}</template>
        </el-menu-item>
        <el-menu-item index="/ai">
          <el-icon style="color: var(--hue-yellow)"><MagicStick /></el-icon>
          <template #title>{{ t('nav.ai') }}</template>
        </el-menu-item>
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
    </el-aside>
    <el-container class="main-area">
      <el-header class="topbar">
        <el-button text @click="toggleCollapsed" :icon="collapsed ? Expand : Fold" />
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

.main-area {
  height: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.sidebar {
  --el-menu-active-color: var(--ink-primary);
  --el-menu-text-color: var(--ink-secondary);
  border-right: 1px solid var(--el-border-color);
  background: var(--page-bg);
  transition: width 0.15s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  width: 22px;
  height: 22px;
}

.brand-text {
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: -0.01em;
}

.nav {
  border-right: none;
  background: transparent;
  flex: 1;
  overflow-y: auto;
}

.nav :deep(.el-menu-item) {
  border-radius: 6px;
  margin: 1px 8px;
  height: 32px;
  line-height: 32px;
}

.nav :deep(.el-menu-item.is-active) {
  background: var(--hover-wash);
  font-weight: 600;
}

.nav :deep(.el-menu-item:hover) {
  background: var(--hover-wash);
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
