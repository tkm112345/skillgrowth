<script setup>
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from '../api'

const { t } = useI18n()

const extracting = ref(false)
const registering = ref(false)
const draft = ref(null)
const selfPr = ref('')
const selfPrInclude = ref(false)
const pendingFile = ref(null)

function withMeta(items) {
  return (items || []).map((item) => ({ ...item, _include: true, _status: null }))
}

function withSkillMeta(items) {
  return (items || []).map((item) => ({
    ...item,
    project_indices: item.project_indices || [],
    _include: true,
    _status: null,
  }))
}

function handleFileChange(uploadFile) {
  pendingFile.value = uploadFile.raw
}

async function extract() {
  if (!pendingFile.value) return
  extracting.value = true
  draft.value = null
  try {
    const result = await api.extractResume(pendingFile.value)
    draft.value = {
      education: withMeta(result.education),
      employment: withMeta(result.employment),
      projects: withMeta(result.projects),
      skills: withSkillMeta(result.skills),
      certifications: withMeta(result.certifications),
    }
    selfPr.value = result.self_pr || ''
    selfPrInclude.value = !!selfPr.value.trim()
  } catch (err) {
    ElMessage.error(t('resumeImport.extractError', { error: err.message }))
  } finally {
    extracting.value = false
  }
}

function employerLabel(index) {
  const emp = draft.value?.employment?.[index]
  return emp ? emp.company : t('resumeImport.noEmployer')
}

function projectNamesFor(indices) {
  return indices.map((i) => draft.value?.projects?.[i]?.title).filter(Boolean).join(', ')
}

async function register() {
  if (!draft.value) return
  registering.value = true
  let successCount = 0
  let failCount = 0

  for (const e of draft.value.education) {
    if (!e._include || e._status === 'done') continue
    try {
      await api.addEducation({
        school: e.school,
        degree: e.degree || '',
        major: e.major || '',
        start_date: e.start_date || null,
        end_date: e.end_date || null,
        achievements: e.achievements || '',
      })
      e._status = 'done'
      successCount++
    } catch (err) {
      e._status = 'error'
      failCount++
    }
  }

  const employmentIdByIndex = {}
  for (let i = 0; i < draft.value.employment.length; i++) {
    const emp = draft.value.employment[i]
    if (!emp._include || emp._status === 'done') continue
    try {
      const created = await api.addEmployment({
        company: emp.company,
        department: emp.department || '',
        role: emp.role || '',
        start_date: emp.start_date || null,
        end_date: emp.end_date || null,
      })
      employmentIdByIndex[i] = created.employment.id
      emp._status = 'done'
      successCount++
    } catch (err) {
      emp._status = 'error'
      failCount++
    }
  }

  const projectIdByIndex = {}
  for (let i = 0; i < draft.value.projects.length; i++) {
    const p = draft.value.projects[i]
    if (!p._include || p._status === 'done') continue
    try {
      const created = await api.addProject({
        employment_id: employmentIdByIndex[p.employer_index] ?? null,
        title: p.title,
        role: p.role || '',
        start_date: p.start_date || null,
        end_date: p.end_date || null,
        description: p.description || '',
      })
      projectIdByIndex[i] = created.project.id
      p._status = 'done'
      successCount++
    } catch (err) {
      p._status = 'error'
      failCount++
    }
  }

  // Linked to the projects they came from (via the project's own
  // evidence_id, see POST /api/resume-import/link-skill) rather than
  // registered as a flat, disconnected list — this is what makes them
  // show up in the Skills page and as edges in the Skill Network graph.
  // A skill with no project_indices isn't registered here at all; it stays
  // reference-only in the UI (see the skills section below).
  for (const s of draft.value.skills) {
    if (!s._include || s._status === 'done' || s.project_indices.length === 0) continue
    try {
      for (const idx of s.project_indices) {
        const projectId = projectIdByIndex[idx]
        if (projectId) {
          await api.linkResumeSkill(projectId, s.name, s.category || '未分類')
        }
      }
      s._status = 'done'
      successCount++
    } catch (err) {
      s._status = 'error'
      failCount++
    }
  }

  for (const c of draft.value.certifications) {
    if (!c._include || c._status === 'done') continue
    try {
      await api.addLearning({
        activity_type: 'certification',
        title: c.title,
        activity_date: c.activity_date || null,
        notes: '',
      })
      c._status = 'done'
      successCount++
    } catch (err) {
      c._status = 'error'
      failCount++
    }
  }

  if (selfPrInclude.value && selfPr.value.trim()) {
    try {
      await api.addSelfPR(selfPr.value)
      selfPrInclude.value = false
      successCount++
    } catch (err) {
      failCount++
    }
  }

  registering.value = false
  if (failCount === 0) {
    ElMessage.success(t('resumeImport.registerSuccess', { count: successCount }))
  } else {
    ElMessage.warning(t('resumeImport.registerPartial', { success: successCount, fail: failCount }))
  }
}
</script>

<template>
  <h1 class="page-title">{{ t('resumeImport.title') }}</h1>
  <p class="page-subtitle">{{ t('resumeImport.subtitle') }}</p>

  <el-alert type="info" :closable="false" class="draft-notice" show-icon>
    {{ t('resumeImport.draftNotice') }}
  </el-alert>

  <el-card shadow="never" class="upload-card">
    <el-upload :auto-upload="false" :show-file-list="true" :limit="1" accept=".docx" :on-change="handleFileChange">
      <el-button size="small">{{ t('resumeImport.chooseFile') }}</el-button>
    </el-upload>
    <el-button type="primary" :loading="extracting" :disabled="!pendingFile" @click="extract">
      {{ t('resumeImport.extract') }}
    </el-button>
  </el-card>

  <template v-if="draft">
    <section class="section">
      <h2>{{ t('resumeImport.educationHeader') }}</h2>
      <el-empty v-if="draft.education.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="e in draft.education" :key="e.school + e.start_date" shadow="never" class="item-card">
        <div class="item-header">
          <el-switch
            v-model="e._include"
            :disabled="e._status === 'done'"
            :active-text="t('resumeImport.include')"
            :inactive-text="t('resumeImport.exclude')"
          />
          <el-tag v-if="e._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
          <el-tag v-else-if="e._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
        </div>
        <div class="item-fields">
          <el-input v-model="e.school" :placeholder="t('profile.school')" />
          <el-input v-model="e.major" :placeholder="t('profile.major')" />
          <el-input v-model="e.achievements" type="textarea" :rows="2" :placeholder="t('profile.achievements')" />
        </div>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.employmentHeader') }}</h2>
      <el-empty v-if="draft.employment.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="emp in draft.employment" :key="emp.company + emp.start_date" shadow="never" class="item-card">
        <div class="item-header">
          <el-switch
            v-model="emp._include"
            :disabled="emp._status === 'done'"
            :active-text="t('resumeImport.include')"
            :inactive-text="t('resumeImport.exclude')"
          />
          <el-tag v-if="emp._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
          <el-tag v-else-if="emp._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
        </div>
        <div class="item-fields">
          <el-input v-model="emp.company" :placeholder="t('profile.company')" />
          <el-input v-model="emp.role" :placeholder="t('profile.role')" />
        </div>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.projectsHeader') }}</h2>
      <el-empty v-if="draft.projects.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="p in draft.projects" :key="p.title + p.start_date" shadow="never" class="item-card project-card">
        <div class="item-header">
          <el-switch
            v-model="p._include"
            :disabled="p._status === 'done'"
            :active-text="t('resumeImport.include')"
            :inactive-text="t('resumeImport.exclude')"
          />
          <el-tag v-if="p._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
          <el-tag v-else-if="p._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
        </div>
        <div class="item-fields">
          <el-input v-model="p.title" :placeholder="t('profile.projectTitle')" />
          <el-select v-model="p.employer_index" :placeholder="t('resumeImport.noEmployer')">
            <el-option v-for="(emp, idx) in draft.employment" :key="idx" :label="emp.company" :value="idx" />
          </el-select>
          <p class="employer-hint">{{ employerLabel(p.employer_index) }}</p>
          <el-input v-model="p.description" type="textarea" :rows="5" :placeholder="t('profile.description')" />
        </div>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.skillsHeader') }}</h2>
      <el-empty v-if="draft.skills.length === 0" :description="t('resumeImport.noneFound')" />
      <template v-else>
        <p class="skills-hint">{{ t('resumeImport.skillsLinkedHint') }}</p>
        <el-card
          v-for="s in draft.skills.filter((s) => s.project_indices.length > 0)"
          :key="s.name"
          shadow="never"
          class="item-card"
        >
          <div class="item-header">
            <el-switch
              v-model="s._include"
              :disabled="s._status === 'done'"
              :active-text="t('resumeImport.include')"
              :inactive-text="t('resumeImport.exclude')"
            />
            <el-tag v-if="s._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
            <el-tag v-else-if="s._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
          </div>
          <div class="item-fields">
            <span class="skill-name">{{ s.name }}<span v-if="s.category"> ({{ s.category }})</span></span>
            <p class="employer-hint">{{ t('resumeImport.linkedToProjects', { names: projectNamesFor(s.project_indices) }) }}</p>
          </div>
        </el-card>

        <template v-if="draft.skills.some((s) => s.project_indices.length === 0)">
          <p class="skills-hint">{{ t('resumeImport.skillsUnlinkedHint') }}</p>
          <div class="skills-row">
            <el-tag v-for="s in draft.skills.filter((s) => s.project_indices.length === 0)" :key="s.name" class="skill-tag">
              {{ s.name }}<span v-if="s.category"> ({{ s.category }})</span>
            </el-tag>
          </div>
        </template>
      </template>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.certificationsHeader') }}</h2>
      <el-empty v-if="draft.certifications.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="c in draft.certifications" :key="c.title" shadow="never" class="item-card">
        <div class="item-header">
          <el-switch
            v-model="c._include"
            :disabled="c._status === 'done'"
            :active-text="t('resumeImport.include')"
            :inactive-text="t('resumeImport.exclude')"
          />
          <el-tag v-if="c._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
          <el-tag v-else-if="c._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
        </div>
        <div class="item-fields">
          <el-input v-model="c.title" />
          <el-date-picker v-model="c.activity_date" value-format="YYYY-MM-DD" :placeholder="t('resumeImport.certificationDate')" />
        </div>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.selfPrHeader') }}</h2>
      <el-card shadow="never" class="item-card">
        <div class="item-header">
          <el-switch
            v-model="selfPrInclude"
            :disabled="!selfPr.trim()"
            :active-text="t('resumeImport.include')"
            :inactive-text="t('resumeImport.exclude')"
          />
        </div>
        <div class="item-fields">
          <el-input v-model="selfPr" type="textarea" :rows="4" />
        </div>
      </el-card>
    </section>

    <el-button type="primary" :loading="registering" @click="register">{{ t('resumeImport.register') }}</el-button>
  </template>
</template>

<style scoped>
.draft-notice {
  margin-bottom: 1rem;
}

.upload-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.section {
  margin-bottom: 2rem;
}

.section h2 {
  font-size: 1rem;
  margin: 0 0 0.5rem;
}

.skill-name {
  font-weight: 600;
}

.item-card {
  margin-bottom: 0.75rem;
}

.project-card {
  max-width: none;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.item-fields {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-fields :deep(.el-textarea) {
  width: 100%;
}

.employer-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin: 0;
}

.skills-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin: 0 0 0.5rem;
}

.skills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
