import { createRouter, createWebHistory } from 'vue-router'

import AiIntegration from '../views/AiIntegration.vue'
import Certifications from '../views/Certifications.vue'
import Concept from '../views/Concept.vue'
import Connections from '../views/Connections.vue'
import Consult from '../views/Consult.vue'
import Dashboard from '../views/Dashboard.vue'
import ExportView from '../views/Export.vue'
import Portfolio from '../views/Portfolio.vue'
import Profile from '../views/Profile.vue'
import ResumeImport from '../views/ResumeImport.vue'
import SelfFeedback from '../views/SelfFeedback.vue'
import SettingsView from '../views/Settings.vue'
import Skills from '../views/Skills.vue'
import Timeline from '../views/Timeline.vue'
import Vision from '../views/Vision.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/vision', name: 'vision', component: Vision },
    { path: '/self-feedback', name: 'self-feedback', component: SelfFeedback },
    { path: '/profile', name: 'profile', component: Profile },
    { path: '/portfolio', name: 'portfolio', component: Portfolio },
    { path: '/resume-import', name: 'resume-import', component: ResumeImport },
    { path: '/skills', name: 'skills', component: Skills },
    { path: '/timeline', name: 'timeline', component: Timeline },
    { path: '/certifications', name: 'certifications', component: Certifications },
    { path: '/connections', name: 'connections', component: Connections },
    { path: '/export', name: 'export', component: ExportView },
    { path: '/ai', name: 'ai', component: AiIntegration },
    { path: '/consult/:id', name: 'consult', component: Consult },
    { path: '/concept', name: 'concept', component: Concept },
    { path: '/settings', name: 'settings', component: SettingsView },
  ],
})
