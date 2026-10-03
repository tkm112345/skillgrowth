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
      skills: withMeta(result.skills),
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
      employmentIdByIndex[i] = created.id
      emp._status = 'done'
      successCount++
    } catch (err) {
      emp._status = 'error'
      failCount++
    }
  }

  for (const p of draft.value.projects) {
    if (!p._include || p._status === 'done') continue
    try {
      await api.addProject({
        employment_id: employmentIdByIndex[p.employer_index] ?? null,
        title: p.title,
        role: p.role || '',
        start_date: p.start_date || null,
        end_date: p.end_date || null,
        description: p.description || '',
      })
      p._status = 'done'
      successCount++
    } catch (err) {
      p._status = 'error'
      failCount++
    }
  }

  for (const s of draft.value.skills) {
    if (!s._include || s._status === 'done') continue
    try {
      await api.addSkill(s.name, s.category || '未分類', null)
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
        <el-checkbox v-model="e._include" :disabled="e._status === 'done'" />
        <div class="item-fields">
          <el-input v-model="e.school" :placeholder="t('profile.school')" />
          <el-input v-model="e.major" :placeholder="t('profile.major')" />
          <el-input v-model="e.achievements" type="textarea" :rows="2" :placeholder="t('profile.achievements')" />
        </div>
        <el-tag v-if="e._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
        <el-tag v-else-if="e._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.employmentHeader') }}</h2>
      <el-empty v-if="draft.employment.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="emp in draft.employment" :key="emp.company + emp.start_date" shadow="never" class="item-card">
        <el-checkbox v-model="emp._include" :disabled="emp._status === 'done'" />
        <div class="item-fields">
          <el-input v-model="emp.company" :placeholder="t('profile.company')" />
          <el-input v-model="emp.role" :placeholder="t('profile.role')" />
        </div>
        <el-tag v-if="emp._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
        <el-tag v-else-if="emp._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.projectsHeader') }}</h2>
      <el-empty v-if="draft.projects.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="p in draft.projects" :key="p.title + p.start_date" shadow="never" class="item-card">
        <el-checkbox v-model="p._include" :disabled="p._status === 'done'" />
        <div class="item-fields">
          <el-input v-model="p.title" :placeholder="t('profile.projectTitle')" />
          <el-select v-model="p.employer_index" :placeholder="t('resumeImport.noEmployer')">
            <el-option v-for="(emp, idx) in draft.employment" :key="idx" :label="emp.company" :value="idx" />
          </el-select>
          <el-input v-model="p.description" type="textarea" :rows="2" :placeholder="t('profile.description')" />
          <p class="employer-hint">{{ employerLabel(p.employer_index) }}</p>
        </div>
        <el-tag v-if="p._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
        <el-tag v-else-if="p._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.skillsHeader') }}</h2>
      <el-empty v-if="draft.skills.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="s in draft.skills" :key="s.name" shadow="never" class="item-card">
        <el-checkbox v-model="s._include" :disabled="s._status === 'done'" />
        <div class="item-fields">
          <el-input v-model="s.name" :placeholder="t('resumeImport.skillName')" />
          <el-input v-model="s.category" :placeholder="t('resumeImport.category')" />
        </div>
        <el-tag v-if="s._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
        <el-tag v-else-if="s._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.certificationsHeader') }}</h2>
      <el-empty v-if="draft.certifications.length === 0" :description="t('resumeImport.noneFound')" />
      <el-card v-for="c in draft.certifications" :key="c.title" shadow="never" class="item-card">
        <el-checkbox v-model="c._include" :disabled="c._status === 'done'" />
        <div class="item-fields">
          <el-input v-model="c.title" />
        </div>
        <el-tag v-if="c._status === 'done'" type="success" size="small">{{ t('resumeImport.statusDone') }}</el-tag>
        <el-tag v-else-if="c._status === 'error'" type="danger" size="small">{{ t('resumeImport.statusError') }}</el-tag>
      </el-card>
    </section>

    <section class="section">
      <h2>{{ t('resumeImport.selfPrHeader') }}</h2>
      <el-card shadow="never" class="item-card">
        <el-checkbox v-model="selfPrInclude" :disabled="!selfPr.trim()" />
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

.item-card {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.item-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.employer-hint {
  color: var(--ink-secondary);
  font-size: 0.85rem;
  margin: 0;
}
</style>
