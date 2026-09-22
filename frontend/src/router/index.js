import { createRouter, createWebHistory } from 'vue-router'

import Concept from '../views/Concept.vue'
import Dashboard from '../views/Dashboard.vue'
import ExportView from '../views/Export.vue'
import Learning from '../views/Learning.vue'
import Profile from '../views/Profile.vue'
import SettingsView from '../views/Settings.vue'
import Skills from '../views/Skills.vue'
import Timeline from '../views/Timeline.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/profile', name: 'profile', component: Profile },
    { path: '/learning', name: 'learning', component: Learning },
    { path: '/skills', name: 'skills', component: Skills },
    { path: '/timeline', name: 'timeline', component: Timeline },
    { path: '/export', name: 'export', component: ExportView },
    { path: '/concept', name: 'concept', component: Concept },
    { path: '/settings', name: 'settings', component: SettingsView },
  ],
})
