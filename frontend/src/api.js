async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(await errorMessage(res))
  }
  return res.status === 204 ? null : res.json()
}

async function errorMessage(res) {
  try {
    const body = await res.json()
    if (body.detail) return typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
  } catch (e) {
    // response body wasn't JSON (or was empty); fall through to the generic message
  }
  return `API error ${res.status}`
}

async function requestForm(path, form) {
  const res = await fetch(`/api${path}`, { method: 'POST', body: form })
  if (!res.ok) {
    throw new Error(await errorMessage(res))
  }
  return res.json()
}

async function requestBlob(path, options = {}) {
  const res = await fetch(`/api${path}`, options)
  if (!res.ok) {
    throw new Error(await errorMessage(res))
  }
  return res.blob()
}

export const api = {
  getSkills: () => request('/skills'),
  addSkill: (name, category) =>
    request('/skills', { method: 'POST', body: JSON.stringify({ name, category }) }),
  updateSkill: (id, name, category) =>
    request(`/skills/${id}`, { method: 'PUT', body: JSON.stringify({ name, category }) }),
  setSkillResumeInclusion: (id, includeInResume) =>
    request(`/skills/${id}/resume-inclusion`, {
      method: 'PUT',
      body: JSON.stringify({ include_in_resume: includeInResume }),
    }),
  deleteSkill: (id) => request(`/skills/${id}`, { method: 'DELETE' }),
  importSkillsCsv: (file) => {
    const form = new FormData()
    form.append('file', file)
    return requestForm('/skills/import-csv', form)
  },
  getSkillTimeline: () => request('/skills/timeline'),
  getSkill: (id) => request(`/skills/${id}`),

  getEvidence: (limit = 50, offset = 0, year = null, month = null) => {
    const params = new URLSearchParams({ limit, offset })
    if (year != null) params.set('year', year)
    if (month != null) params.set('month', month)
    return request(`/evidence?${params.toString()}`)
  },
  getEvidenceMonths: () => request('/evidence/months'),
  addTextEvidence: (sourceType, text) =>
    request('/evidence/text', {
      method: 'POST',
      body: JSON.stringify({ source_type: sourceType, text }),
    }),
  addImageEvidence: (file) => {
    const form = new FormData()
    form.append('source_type', 'certification')
    form.append('file', file)
    return requestForm('/evidence/image', form)
  },

  getExports: (limit = 20, offset = 0) => request(`/export?limit=${limit}&offset=${offset}`),
  generateExport: () => request('/export', { method: 'POST' }),
  updateExport: (id, content) =>
    request(`/export/${id}`, { method: 'PUT', body: JSON.stringify({ content }) }),

  getResumeTemplates: () => request('/resume-templates'),
  uploadResumeTemplate: (name, file) => {
    const form = new FormData()
    form.append('name', name)
    form.append('file', file)
    return requestForm('/resume-templates', form)
  },
  updateResumeTemplate: (id, payload) =>
    request(`/resume-templates/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteResumeTemplate: (id) => request(`/resume-templates/${id}`, { method: 'DELETE' }),
  generateResumeDocx: (id) => requestBlob(`/resume-templates/${id}/generate`, { method: 'POST' }),

  getSelfPRs: (limit = 20, offset = 0) => request(`/self-pr?limit=${limit}&offset=${offset}`),
  addSelfPR: (content) => request('/self-pr', { method: 'POST', body: JSON.stringify({ content }) }),
  updateSelfPR: (id, content) =>
    request(`/self-pr/${id}`, { method: 'PUT', body: JSON.stringify({ content }) }),
  selectSelfPR: (id) => request(`/self-pr/${id}/select`, { method: 'PUT' }),
  deleteSelfPR: (id) => request(`/self-pr/${id}`, { method: 'DELETE' }),

  getConsultSessions: (limit = 20, offset = 0) =>
    request(`/consult/sessions?limit=${limit}&offset=${offset}`),
  createConsultSession: () => request('/consult/sessions', { method: 'POST' }),
  getConsultSession: (id) => request(`/consult/sessions/${id}`),
  deleteConsultSession: (id) => request(`/consult/sessions/${id}`, { method: 'DELETE' }),
  getConsultMessages: (sessionId) => request(`/consult/sessions/${sessionId}/messages`),
  sendConsultMessage: (sessionId, content, locale) =>
    request(`/consult/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, locale }),
    }),

  gapCheck: (jobDescription) =>
    request('/ai/gap-check', {
      method: 'POST',
      body: JSON.stringify({ job_description: jobDescription }),
    }),
  getGrowthGuidance: () => request('/ai/growth-guidance', { method: 'POST' }),

  getSettings: () => request('/settings'),
  updateSettings: (payload) =>
    request('/settings', { method: 'PUT', body: JSON.stringify(payload) }),
  testSettings: (payload) =>
    request('/settings/test', { method: 'POST', body: JSON.stringify(payload) }),
  getBackup: () => request('/backup/export'),
  importBackup: (data) => request('/backup/import', { method: 'POST', body: JSON.stringify(data) }),
  loadSampleData: () => request('/backup/load-sample', { method: 'POST' }),
  resetSampleData: () => request('/backup/reset-sample', { method: 'POST' }),

  getGoals: () => request('/goals'),
  updateGoal: (horizon, description) =>
    request(`/goals/${horizon}`, {
      method: 'PUT',
      body: JSON.stringify({ horizon, description }),
    }),
  getGoalHistory: (horizon, limit = 5, offset = 0) =>
    request(`/goals/history?horizon=${horizon}&limit=${limit}&offset=${offset}`),

  getVision: () => request('/vision'),
  updateVision: (content) =>
    request('/vision', {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),

  getReflectionSummary: () => request('/reflection/summary'),
  markReflected: (note = '') => request('/reflection', { method: 'POST', body: JSON.stringify({ note }) }),
  getReflectionHistory: (limit = 5, offset = 0) => request(`/reflection/history?limit=${limit}&offset=${offset}`),

  getEducation: () => request('/profile/education'),
  addEducation: (payload) =>
    request('/profile/education', { method: 'POST', body: JSON.stringify(payload) }),
  deleteEducation: (id) => request(`/profile/education/${id}`, { method: 'DELETE' }),

  getEmployment: () => request('/profile/employment'),
  addEmployment: (payload) =>
    request('/profile/employment', { method: 'POST', body: JSON.stringify(payload) }),
  deleteEmployment: (id) => request(`/profile/employment/${id}`, { method: 'DELETE' }),

  getProjects: () => request('/profile/projects'),
  addProject: (payload) =>
    request('/profile/projects', { method: 'POST', body: JSON.stringify(payload) }),
  deleteProject: (id) => request(`/profile/projects/${id}`, { method: 'DELETE' }),

  getLinks: () => request('/profile/links'),
  addLink: (label, url) =>
    request('/profile/links', { method: 'POST', body: JSON.stringify({ label, url }) }),
  deleteLink: (id) => request(`/profile/links/${id}`, { method: 'DELETE' }),

  getLearning: () => request('/learning'),
  addLearning: (payload) => request('/learning', { method: 'POST', body: JSON.stringify(payload) }),
  deleteLearning: (id) => request(`/learning/${id}`, { method: 'DELETE' }),

  getPortfolioItems: () => request('/portfolio'),
  getPortfolioItem: (id) => request(`/portfolio/${id}`),
  createPortfolioItem: (payload) =>
    request('/portfolio', { method: 'POST', body: JSON.stringify(payload) }),
  updatePortfolioItem: (id, payload) =>
    request(`/portfolio/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deletePortfolioItem: (id) => request(`/portfolio/${id}`, { method: 'DELETE' }),
  addPortfolioLink: (itemId, label, url) =>
    request(`/portfolio/${itemId}/links`, { method: 'POST', body: JSON.stringify({ label, url }) }),
  deletePortfolioLink: (linkId) => request(`/portfolio/links/${linkId}`, { method: 'DELETE' }),
  uploadPortfolioFiles: (itemId, fileList) => {
    const form = new FormData()
    fileList.forEach((f) => form.append('files', f))
    return requestForm(`/portfolio/${itemId}/files`, form)
  },
  deletePortfolioFile: (fileId) => request(`/portfolio/files/${fileId}`, { method: 'DELETE' }),
  downloadPortfolioFile: (fileId) => requestBlob(`/portfolio/files/${fileId}/download`),
}
