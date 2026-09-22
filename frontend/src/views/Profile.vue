<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t } = useI18n()

const education = ref([])
const employment = ref([])
const projects = ref([])
const links = ref([])
const loading = ref(true)

async function reload() {
  const [edu, emp, proj, lnk] = await Promise.all([
    api.getEducation(),
    api.getEmployment(),
    api.getProjects(),
    api.getLinks(),
  ])
  education.value = edu
  employment.value = emp
  projects.value = proj
  links.value = lnk
}

onMounted(async () => {
  try {
    await reload()
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

function projectsFor(employmentId) {
  return projects.value.filter((p) => p.employment_id === employmentId)
}
const standaloneProjects = computed(() => projects.value.filter((p) => !p.employment_id))

function formatPeriod(start, end) {
  const s = start || '?'
  const e = end || '—'
  return `${s} – ${e}`
}

// -- education form --
const eduDialog = ref(false)
const eduForm = reactive({ school: '', degree: '', major: '', start_date: '', end_date: '', achievements: '' })
async function submitEducation() {
  await api.addEducation(eduForm)
  Object.assign(eduForm, { school: '', degree: '', major: '', start_date: '', end_date: '', achievements: '' })
  eduDialog.value = false
  await reload()
  ElMessage.success(t('profile.addedEducation'))
}
async function removeEducation(id) {
  await ElMessageBox.confirm(t('profile.confirmDeleteEducation'), t('profile.confirm'))
  await api.deleteEducation(id)
  await reload()
}

// -- employment form --
const empDialog = ref(false)
const empForm = reactive({ company: '', department: '', role: '', start_date: '', end_date: '' })
async function submitEmployment() {
  await api.addEmployment(empForm)
  Object.assign(empForm, { company: '', department: '', role: '', start_date: '', end_date: '' })
  empDialog.value = false
  await reload()
  ElMessage.success(t('profile.addedEmployment'))
}
async function removeEmployment(id) {
  await ElMessageBox.confirm(t('profile.confirmDeleteEmployment'), t('profile.confirm'))
  await api.deleteEmployment(id)
  await reload()
}

// -- project form --
const projDialog = ref(false)
const projForm = reactive({ employment_id: null, title: '', role: '', start_date: '', end_date: '', description: '' })
function openProjectDialog(employmentId = null) {
  Object.assign(projForm, { employment_id: employmentId, title: '', role: '', start_date: '', end_date: '', description: '' })
  projDialog.value = true
}
async function submitProject() {
  await api.addProject(projForm)
  projDialog.value = false
  await reload()
  ElMessage.success(t('profile.addedProject'))
}
async function removeProject(id) {
  await ElMessageBox.confirm(t('profile.confirmDeleteProject'), t('profile.confirm'))
  await api.deleteProject(id)
  await reload()
}

// -- external links --
const linkDialog = ref(false)
const linkForm = reactive({ label: '', url: '' })
async function submitLink() {
  if (!linkForm.label.trim() || !linkForm.url.trim()) return
  await api.addLink(linkForm.label, linkForm.url)
  Object.assign(linkForm, { label: '', url: '' })
  linkDialog.value = false
  await reload()
  ElMessage.success(t('profile.addedLink'))
}
async function removeLink(id) {
  await ElMessageBox.confirm(t('profile.confirmDeleteLink'), t('profile.confirm'))
  await api.deleteLink(id)
  await reload()
}
</script>

<template>
  <h1 class="page-title">{{ t('profile.title') }}</h1>
  <p class="page-subtitle">{{ t('profile.subtitle') }}</p>

  <section class="section" v-loading="loading">
    <div class="section-header">
      <h2>{{ t('profile.educationHeader') }}</h2>
      <el-button size="small" @click="eduDialog = true">{{ t('common.add') }}</el-button>
    </div>
    <el-card v-for="e in education" :key="e.id" shadow="never" class="item-card">
      <div class="item-title">{{ e.school }} {{ e.degree }} {{ e.major }}</div>
      <div class="item-meta">{{ formatPeriod(e.start_date, e.end_date) }}</div>
      <p v-if="e.achievements">{{ e.achievements }}</p>
      <el-button size="small" text type="danger" @click="removeEducation(e.id)">{{ t('common.delete') }}</el-button>
    </el-card>
    <el-empty v-if="!loading && education.length === 0" :description="t('profile.noEntries')" />
  </section>

  <section class="section" v-loading="loading">
    <div class="section-header">
      <h2>{{ t('profile.employmentHeader') }}</h2>
      <el-button size="small" @click="empDialog = true">{{ t('common.add') }}</el-button>
    </div>
    <el-card v-for="e in employment" :key="e.id" shadow="never" class="item-card">
      <div class="item-title">{{ e.company }}<span v-if="e.department"> / {{ e.department }}</span></div>
      <div class="item-meta">{{ e.role }} · {{ formatPeriod(e.start_date, e.end_date) }}</div>
      <div class="card-actions">
        <el-button size="small" text @click="openProjectDialog(e.id)">{{ t('profile.addProject') }}</el-button>
        <el-button size="small" text type="danger" @click="removeEmployment(e.id)">{{ t('common.delete') }}</el-button>
      </div>

      <div class="nested-projects" v-if="projectsFor(e.id).length">
        <el-card v-for="p in projectsFor(e.id)" :key="p.id" shadow="never" class="project-card">
          <div class="item-title">{{ p.title }}</div>
          <div class="item-meta">{{ p.role }} · {{ formatPeriod(p.start_date, p.end_date) }}</div>
          <p v-if="p.description">{{ p.description }}</p>
          <el-button size="small" text type="danger" @click="removeProject(p.id)">{{ t('common.delete') }}</el-button>
        </el-card>
      </div>
    </el-card>
    <el-empty v-if="!loading && employment.length === 0" :description="t('profile.noEntries')" />
  </section>

  <section class="section" v-loading="loading">
    <div class="section-header">
      <h2>{{ t('profile.otherProjectsHeader') }}</h2>
      <el-button size="small" @click="openProjectDialog(null)">{{ t('common.add') }}</el-button>
    </div>
    <el-card v-for="p in standaloneProjects" :key="p.id" shadow="never" class="item-card">
      <div class="item-title">{{ p.title }}</div>
      <div class="item-meta">{{ p.role }} · {{ formatPeriod(p.start_date, p.end_date) }}</div>
      <p v-if="p.description">{{ p.description }}</p>
      <el-button size="small" text type="danger" @click="removeProject(p.id)">{{ t('common.delete') }}</el-button>
    </el-card>
  </section>

  <section class="section" v-loading="loading">
    <div class="section-header">
      <h2>{{ t('profile.linksHeader') }}</h2>
      <el-button size="small" @click="linkDialog = true">{{ t('common.add') }}</el-button>
    </div>
    <div class="links-row" v-if="links.length">
      <el-tag v-for="l in links" :key="l.id" closable @close="removeLink(l.id)" class="link-tag">
        <a :href="l.url" target="_blank" rel="noopener noreferrer">{{ l.label }}</a>
      </el-tag>
    </div>
    <el-empty v-if="!loading && links.length === 0" :description="t('profile.noEntries')" />
  </section>

  <el-dialog v-model="eduDialog" :title="t('profile.addEducation')" width="480px">
    <el-form :model="eduForm" label-width="80px">
      <el-form-item :label="t('profile.school')"><el-input v-model="eduForm.school" /></el-form-item>
      <el-form-item :label="t('profile.degree')"><el-input v-model="eduForm.degree" /></el-form-item>
      <el-form-item :label="t('profile.major')"><el-input v-model="eduForm.major" /></el-form-item>
      <el-form-item :label="t('profile.startDate')"><el-date-picker v-model="eduForm.start_date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="t('profile.endDate')"><el-date-picker v-model="eduForm.end_date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="t('profile.achievements')"><el-input v-model="eduForm.achievements" type="textarea" :rows="3" /></el-form-item>
    </el-form>
    <template #footer><el-button type="primary" @click="submitEducation">{{ t('common.add') }}</el-button></template>
  </el-dialog>

  <el-dialog v-model="empDialog" :title="t('profile.addEmployment')" width="480px">
    <el-form :model="empForm" label-width="80px">
      <el-form-item :label="t('profile.company')"><el-input v-model="empForm.company" /></el-form-item>
      <el-form-item :label="t('profile.department')"><el-input v-model="empForm.department" /></el-form-item>
      <el-form-item :label="t('profile.role')"><el-input v-model="empForm.role" /></el-form-item>
      <el-form-item :label="t('profile.startDate')"><el-date-picker v-model="empForm.start_date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="t('profile.endDate')"><el-date-picker v-model="empForm.end_date" value-format="YYYY-MM-DD" :placeholder="t('profile.endDatePlaceholder')" /></el-form-item>
    </el-form>
    <template #footer><el-button type="primary" @click="submitEmployment">{{ t('common.add') }}</el-button></template>
  </el-dialog>

  <el-dialog v-model="projDialog" :title="t('profile.addProjectDialog')" width="480px">
    <el-form :model="projForm" label-width="80px">
      <el-form-item :label="t('profile.relatedEmployment')">
        <el-select v-model="projForm.employment_id" clearable :placeholder="t('profile.relatedEmploymentNone')">
          <el-option v-for="e in employment" :key="e.id" :label="e.company" :value="e.id" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('profile.projectTitle')"><el-input v-model="projForm.title" /></el-form-item>
      <el-form-item :label="t('profile.role')"><el-input v-model="projForm.role" /></el-form-item>
      <el-form-item :label="t('profile.startDate')"><el-date-picker v-model="projForm.start_date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="t('profile.endDate')"><el-date-picker v-model="projForm.end_date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="t('profile.description')"><el-input v-model="projForm.description" type="textarea" :rows="3" :placeholder="t('profile.descriptionPlaceholder')" /></el-form-item>
    </el-form>
    <template #footer><el-button type="primary" @click="submitProject">{{ t('common.add') }}</el-button></template>
  </el-dialog>

  <el-dialog v-model="linkDialog" :title="t('profile.addLink')" width="420px">
    <el-form :model="linkForm" label-width="80px">
      <el-form-item :label="t('profile.linkLabel')">
        <el-input v-model="linkForm.label" :placeholder="t('profile.linkLabelPlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('profile.linkUrl')">
        <el-input v-model="linkForm.url" placeholder="https://..." />
      </el-form-item>
    </el-form>
    <template #footer><el-button type="primary" @click="submitLink">{{ t('common.add') }}</el-button></template>
  </el-dialog>
</template>

<style scoped>
.section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.section-header h2 {
  font-size: 1rem;
  margin: 0;
}

.item-card {
  margin-bottom: 0.75rem;
}

.item-title {
  font-weight: 600;
}

.item-meta {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin: 0.25rem 0 0.5rem;
}

.card-actions {
  display: flex;
  justify-content: space-between;
}

.nested-projects {
  margin-top: 0.75rem;
  padding-left: 1rem;
  border-left: 2px solid var(--el-border-color);
}

.project-card {
  margin-bottom: 0.5rem;
}

.links-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.link-tag a {
  color: inherit;
  text-decoration: none;
}
</style>
