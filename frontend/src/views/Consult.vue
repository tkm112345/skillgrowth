<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const sessionId = route.params.id
const session = ref(null)
const messages = ref([])
const loading = ref(true)
const newMessage = ref('')
const sending = ref(false)
const sendError = ref('')
const threadEl = ref(null)

async function scrollToBottom() {
  await nextTick()
  if (threadEl.value) threadEl.value.scrollTop = threadEl.value.scrollHeight
}

onMounted(async () => {
  try {
    const [sessionDetail, msgs] = await Promise.all([
      api.getConsultSession(sessionId),
      api.getConsultMessages(sessionId),
    ])
    session.value = sessionDetail
    messages.value = msgs
    await scrollToBottom()
  } catch (e) {
    ElMessage.error(t('common.loadError'))
  } finally {
    loading.value = false
  }
})

function formatDateTime(iso) {
  return new Date(iso).toLocaleString(locale.value)
}

async function send() {
  const content = newMessage.value.trim()
  if (!content || sending.value) return

  sendError.value = ''
  sending.value = true
  messages.value.push({
    id: `pending-${Date.now()}`,
    role: 'user',
    content,
    created_at: new Date().toISOString(),
  })
  newMessage.value = ''
  await scrollToBottom()

  try {
    const reply = await api.sendConsultMessage(sessionId, content, locale.value)
    if (!session.value.title) session.value.title = content.slice(0, 40)
    messages.value.push(reply)
    await scrollToBottom()
  } catch (e) {
    sendError.value = e.message
  } finally {
    sending.value = false
  }
}

async function removeSession() {
  await ElMessageBox.confirm(t('ai.consultConfirmDelete'), t('profile.confirm'))
  await api.deleteConsultSession(sessionId)
  router.push('/ai')
}
</script>

<template>
  <router-link to="/ai" class="back-link">← {{ t('ai.title') }}</router-link>
  <h1 class="page-title">{{ session?.title || t('ai.consultUntitled') }}</h1>
  <p class="page-subtitle">{{ t('ai.consultPageHint') }}</p>

  <el-card shadow="never" class="consult-card" v-loading="loading">
    <div ref="threadEl" class="consult-thread">
      <div v-for="m in messages" :key="m.id" class="consult-row" :class="`consult-row--${m.role}`">
        <div class="consult-bubble" :class="`consult-bubble--${m.role}`">{{ m.content }}</div>
        <div class="consult-time">{{ formatDateTime(m.created_at) }}</div>
      </div>
      <div v-if="sending" class="consult-row consult-row--assistant">
        <div class="consult-bubble consult-bubble--assistant consult-bubble--thinking">
          {{ t('ai.consultThinking') }}
        </div>
      </div>
      <el-empty v-if="!loading && messages.length === 0 && !sending" :description="t('ai.consultEmpty')" />
    </div>

    <el-alert
      v-if="sendError"
      :title="t('ai.consultError', { error: sendError })"
      type="error"
      :closable="false"
      class="consult-error"
    />

    <div class="consult-input-row">
      <el-input
        v-model="newMessage"
        type="textarea"
        :rows="2"
        :placeholder="t('ai.consultPlaceholder')"
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" :loading="sending" @click="send">{{ t('ai.consultSend') }}</el-button>
    </div>
  </el-card>

  <el-button text type="danger" @click="removeSession" class="consult-delete-btn">
    {{ t('ai.consultDeleteSession') }}
  </el-button>
</template>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
  color: var(--accent);
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

.consult-card {
  margin-top: 0.5rem;
}

.consult-thread {
  max-height: 55vh;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.consult-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.consult-row--user {
  align-items: flex-end;
}

.consult-row--assistant {
  align-items: flex-start;
}

.consult-bubble {
  max-width: 80%;
  padding: 0.6rem 0.85rem;
  border-radius: 10px;
  font-size: 0.85rem;
  white-space: pre-wrap;
  line-height: 1.5;
}

.consult-bubble--user {
  background: var(--accent);
  color: #fff;
}

.consult-bubble--assistant {
  background: var(--hover-wash);
  color: var(--ink-primary);
  border: 1px solid var(--el-border-color);
}

.consult-bubble--thinking {
  color: var(--ink-muted);
  font-style: italic;
}

.consult-time {
  margin-top: 0.2rem;
  font-size: 0.7rem;
  color: var(--ink-muted);
}

.consult-error {
  margin-top: 0.75rem;
}

.consult-input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--el-border-color);
}

.consult-input-row :deep(.el-textarea) {
  flex: 1;
}

.consult-delete-btn {
  margin-top: 1rem;
}
</style>
