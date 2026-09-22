<script setup>
import {
  Compass,
  DataAnalysis,
  Expand,
  Files,
  Fold,
  List,
  Notebook,
  Reading,
  Setting,
  TrendCharts,
} from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { setLocale } from './i18n'

const route = useRoute()
const { t, locale } = useI18n()

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
        <div class="brand-mark">S</div>
        <span class="brand-text" v-show="!collapsed">{{ t('app.brand') }}</span>
      </div>
      <el-menu :default-active="route.path" :collapse="collapsed" router class="nav">
        <el-menu-item index="/concept">
          <el-icon><Compass /></el-icon>
          <template #title>{{ t('nav.concept') }}</template>
        </el-menu-item>
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>{{ t('nav.dashboard') }}</template>
        </el-menu-item>
        <el-menu-item index="/learning">
          <el-icon><Reading /></el-icon>
          <template #title>{{ t('nav.learning') }}</template>
        </el-menu-item>
        <el-menu-item index="/skills">
          <el-icon><List /></el-icon>
          <template #title>{{ t('nav.skills') }}</template>
        </el-menu-item>
        <el-menu-item index="/timeline">
          <el-icon><TrendCharts /></el-icon>
          <template #title>{{ t('nav.timeline') }}</template>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><Notebook /></el-icon>
          <template #title>{{ t('nav.profile') }}</template>
        </el-menu-item>
        <el-menu-item index="/export">
          <el-icon><Files /></el-icon>
          <template #title>{{ t('nav.export') }}</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>{{ t('nav.settings') }}</template>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <span v-if="!collapsed">© {{ year }} {{ t('app.brand') }}<span v-if="version"> · v{{ version }}</span></span>
        <span v-else>©</span>
      </div>
    </el-aside>
    <el-container class="main-area">
      <el-header class="topbar">
        <el-button text @click="toggleCollapsed" :icon="collapsed ? Expand : Fold" />
        <el-select :model-value="locale" @update:model-value="setLocale" size="small" class="lang-select">
          <el-option value="en" label="English" />
          <el-option value="ja" label="日本語" />
        </el-select>
      </el-header>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
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
  border-radius: 6px;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
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

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color);
  height: 52px;
  flex-shrink: 0;
}

.lang-select {
  width: 105px;
}

.content {
  max-width: 920px;
  flex: 1;
  overflow-y: auto;
}
</style>
