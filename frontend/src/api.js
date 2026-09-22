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

export const api = {
  getSkills: () => request('/skills'),
  addSkill: (name, category) =>
    request('/skills', { method: 'POST', body: JSON.stringify({ name, category }) }),
  deleteSkill: (id) => request(`/skills/${id}`, { method: 'DELETE' }),
  importSkillsCsv: (file) => {
    const form = new FormData()
    form.append('file', file)
    return requestForm('/skills/import-csv', form)
  },
  getSkillTimeline: () => request('/skills/timeline'),
  getSkill: (id) => request(`/skills/${id}`),

  getEvidence: (limit = 50, offset = 0) => request(`/evidence?limit=${limit}&offset=${offset}`),
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

  getSelfPRs: () => request('/self-pr'),
  addSelfPR: (content) => request('/self-pr', { method: 'POST', body: JSON.stringify({ content }) }),
  deleteSelfPR: (id) => request(`/self-pr/${id}`, { method: 'DELETE' }),

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
  getGoalHistory: () => request('/goals/history'),

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
}
