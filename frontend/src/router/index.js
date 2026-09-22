import { createRouter, createWebHistory } from 'vue-router'

import AiIntegration from '../views/AiIntegration.vue'
import Concept from '../views/Concept.vue'
import Dashboard from '../views/Dashboard.vue'
import ExportView from '../views/Export.vue'
import Profile from '../views/Profile.vue'
import SettingsView from '../views/Settings.vue'
import Skills from '../views/Skills.vue'
import Timeline from '../views/Timeline.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/profile', name: 'profile', component: Profile },
    { path: '/skills', name: 'skills', component: Skills },
    { path: '/timeline', name: 'timeline', component: Timeline },
    { path: '/export', name: 'export', component: ExportView },
    { path: '/ai', name: 'ai', component: AiIntegration },
    { path: '/concept', name: 'concept', component: Concept },
    { path: '/settings', name: 'settings', component: SettingsView },
  ],
})
