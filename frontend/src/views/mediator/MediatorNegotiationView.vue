<template>
  <div class="negotiation-view">
    <div class="chat-layout">
      <!-- 左侧：案件信息 -->
      <div class="chat-sidebar">
        <div class="page-card sidebar-card">
          <h4>{{ t('negotiation.caseInfo') }}</h4>
          <p class="case-num">{{ caseInfo?.case_number }}</p>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item :label="t('negotiation.opponent')">{{ caseInfo?.opponent_name }}</el-descriptions-item>
            <el-descriptions-item :label="t('negotiation.amountLabel')">
              USD {{ formatMoney(caseInfo?.amount) }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.status')">
              <span :class="['status-tag', caseInfo?.status]" style="font-size:11px">
                {{ tr(`case.statusMap.${caseInfo?.status}`, caseInfo?.status || '') }}
              </span>
            </el-descriptions-item>
          </el-descriptions>
          <div class="mediator-badge">
            <el-icon><Avatar /></el-icon>
            {{ t('mediator.enterNegotiation') }}
          </div>
        </div>
        <!-- 调解室入口 -->
        <div class="page-card" style="margin-top: 12px">
          <el-button type="warning" style="width: 100%" @click="goMediation">
            <el-icon><VideoCamera /></el-icon> {{ t('mediator.enterMediation') }}
          </el-button>
        </div>

        <!-- 案件笔记面板 -->
        <div class="page-card" style="margin-top: 12px">
          <h4 style="font-weight: 600; margin-bottom: var(--space-2); color: var(--color-text-primary);">
            📝 {{ t('mediator.caseNotes') }}
          </h4>
          <div class="notes-list" v-if="caseNotes.length > 0">
            <div v-for="note in caseNotes" :key="note.id" class="note-item">
              <div class="note-header">
                <span class="note-time">{{ formatNoteTime(note.created_at) }}</span>
                <el-button link type="danger" size="small" @click="deleteNote(note.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <div v-if="note.note_type === 'image'" class="note-image">
                <el-image :src="resolveUrl(note.content)" fit="cover" style="width: 100%; border-radius: 8px; max-height: 200px"
                  :preview-src-list="[resolveUrl(note.content)]" preview-teleported />
              </div>
              <div v-else-if="note.note_type === 'file'" class="note-file" @click="downloadNoteFile(note)">
                <el-icon size="20" color="#1677ff"><Document /></el-icon>
                <span>{{ note.file_name || 'File' }}</span>
                <el-icon><Download /></el-icon>
              </div>
              <p v-else class="note-text">{{ note.content }}</p>
            </div>
          </div>
          <el-empty v-else :description="t('mediator.noNotes')" :image-size="40" />
          <div class="note-input-area" style="margin-top: var(--space-3)">
            <el-input v-model="noteInput" type="textarea" :rows="2" :placeholder="t('mediator.notePlaceholder')" resize="none" />
            <div class="note-input-actions">
              <input ref="noteImageRef" type="file" accept="image/*" style="display:none" @change="handleNoteImage" />
              <input ref="noteFileRef" type="file" style="display:none" @change="handleNoteFile" />
              <el-button text size="small" @click="noteImageRef?.click()">
                <el-icon><Picture /></el-icon>
              </el-button>
              <el-button text size="small" @click="noteFileRef?.click()">
                <el-icon><FolderOpened /></el-icon>
              </el-button>
              <el-button type="primary" size="small" @click="addNote" :disabled="!noteInput.trim()">
                {{ t('mediator.addNote') }}
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：聊天区 -->
      <div class="chat-main page-card">
        <div class="chat-header">
          <span>💬 {{ t('negotiation.chatHeader') }} · {{ caseInfo?.case_number }}</span>
          <el-tag type="warning" effect="dark" size="small">
            <el-icon style="margin-right:4px"><Avatar /></el-icon> {{ myRoleLabel }}
          </el-tag>
        </div>

        <!-- 消息列表 -->
        <div class="messages-area" ref="messagesEl">
          <div v-for="(group, idx) in messageGroups" :key="idx" class="msg-group">
            <div v-if="group.isDateDivider" class="date-divider">{{ group.date }}</div>
            <div v-else v-for="msg in group.messages" :key="msg.id"
                 :class="['message-item', msg.sender_id === currentUserId ? 'mine' : 'theirs', { 'sys-msg': msg.message_type === 'system' }]">
              <el-avatar v-if="msg.message_type !== 'system'" size="small" class="msg-avatar">{{ msg.sender_name?.[0] || 'U' }}</el-avatar>
              <div class="msg-body">
                <div class="msg-sender">{{ msg.sender_name }} <el-tag size="small" type="warning" style="margin-left:4px">{{ getSenderRoleLabel(msg) }}</el-tag></div>
                <div class="msg-bubble">
                  <template v-if="msg.message_type === 'text'">{{ msg.content }}</template>
                  <template v-else-if="msg.message_type === 'image'">
                    <div class="image-bubble">
                      <el-image :src="resolveUrl(msg.content)" fit="cover" loading="lazy"
                        :preview-src-list="[resolveUrl(msg.content)]" :initial-index="0"
                        hide-on-click-modal preview-teleported
                      />
                    </div>
                  </template>
                  <template v-else-if="msg.message_type === 'file'">
                    <div class="file-bubble" @click="downloadFile(resolveUrl(msg.content), msg.file_name)">
                      <el-icon size="28" color="#1677ff"><Document /></el-icon>
                      <div class="file-info">
                        <span class="file-name">{{ msg.file_name || 'File' }}</span>
                        <span class="file-size">{{ msg.file_size || '' }}</span>
                      </div>
                      <el-icon><Download /></el-icon>
                    </div>
                  </template>
                  <template v-else-if="msg.message_type === 'system'">
                    <div class="sys-msg">{{ msg.content }}</div>
                  </template>
                </div>
                <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
              </div>
            </div>
          </div>
          <div v-if="messages.length === 0" class="empty-chat">
            <el-empty :description="t('mediator.noAssignedCases')" :image-size="80" />
          </div>
        </div>

        <!-- 输入区 -->
        <div class="input-area">
          <div v-if="showEmojiPicker" class="emoji-picker">
            <div class="emoji-picker-inner">
              <div class="emoji-tabs">
                <span v-for="tab in emojiTabs" :key="tab.label"
                      :class="['emoji-tab', { active: activeEmojiTab === tab.label }]"
                      @click="activeEmojiTab = tab.label">{{ tab.icon }}</span>
              </div>
              <div class="emoji-grid">
                <span v-for="emoji in activeEmojis" :key="emoji" class="emoji-item"
                      @click="insertEmoji(emoji)">{{ emoji }}</span>
              </div>
            </div>
          </div>
          <div class="input-toolbar">
            <el-button text @click="showEmojiPicker = !showEmojiPicker" :title="t('negotiation.toolbar.emoji')">😊</el-button>
            <el-button text :title="t('negotiation.toolbar.image')" @click="triggerImageUpload">
              <el-icon><Picture /></el-icon>
            </el-button>
            <el-button text :title="t('negotiation.toolbar.file')" @click="triggerFileUpload">
              <el-icon><FolderOpened /></el-icon>
            </el-button>
          </div>
          <input ref="imageInputRef" type="file" accept="image/*" style="display:none" @change="handleImageSelect" />
          <input ref="fileInputRef" type="file" style="display:none" @change="handleFileSelect" />
          <div class="input-row">
            <el-input v-model="inputText" :placeholder="t('mediator.inputPlaceholder')"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="inputText += '\n'"
              type="textarea" :rows="2" resize="none" />
            <el-button type="primary" @click="sendMessage" :disabled="!inputText.trim()" style="height:auto">
              {{ t('negotiation.sendBtn') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { caseApi, negotiationApi, uploadApi, caseNoteApi, caseStatusApi } from '@/api'
import { Picture, FolderOpened, Document, Download, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const { t, te } = useI18n()
function tr(key: string, fallback: string) { return te(key) ? t(key) : fallback }

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const caseId = Number(route.params.id)

// 根据 specialty 推断当前用户角色标签
const myRoleLabel = computed(() => {
  const specialty = authStore.user?.specialty || ''
  let inferredRole = authStore.user?.role || 'mediator'
  if (specialty.includes('英语') || specialty.includes('翻译') || specialty.includes('商务英语')) {
    inferredRole = 'translator'
  } else if (specialty.includes('数学') || specialty.includes('分析') || specialty.includes('数据')) {
    inferredRole = 'analyst'
  }
  return t(`profile.roles.${inferredRole}`)
})

// 获取消息发送者的角色标签
function getSenderRoleLabel(msg: any) {
  if (msg.sender_id === authStore.user?.id) {
    // 当前用户的消息，使用推断的角色
    return myRoleLabel.value
  }
  // 其他用户的消息，根据 sender_role 显示
  if (msg.sender_role === 'mediator') return t('profile.roles.mediator')
  if (msg.sender_role === 'opponent') return t('negotiation.opponent') || '对方'
  return msg.sender_role || ''
}

const messages = ref<any[]>([])
const inputText = ref('')
const caseInfo = ref<any>(null)
const messagesEl = ref<HTMLElement | null>(null)
const showEmojiPicker = ref(false)
const activeEmojiTab = ref('😊 表情')
const imageInputRef = ref<HTMLInputElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const noteInputRef = ref<HTMLInputElement | null>(null)
const noteFileRef = ref<HTMLInputElement | null>(null)

// 案件笔记
const caseNotes = ref<any[]>([])
const noteInput = ref('')

const currentUserId = computed(() => authStore.user?.id)

function resolveUrl(url: string) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return url
}

function downloadFile(url: string, fileName?: string) {
  const a = document.createElement('a')
  a.href = url; a.download = fileName || 'download'; a.target = '_blank'
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
}

let pollTimer: ReturnType<typeof setInterval> | null = null

const emojiTabs = [
  { label: '😊 表情', icon: '😊', emojis: ['😀','😃','😄','😁','😆','😅','🤣','😂','🙂','😉','😊','😇','🥰','😍','🤩','😘','😗','😚','😙','🥲','😋','😛','😜','🤪','😝','🤑','🤗','🤭','🫢','🤫','🤔','🫡','🤐','🤨','😐','😑','😶','🫥','😏','😒','🙄','😬','🤥','😌','😔','😪','🤤','😴','😷','🤒','🤕','🤢','🤮','🥵','🥶','🥴','😵','🤯','🤠','🥳','🥸','😎','🤓','🧐'] },
  { label: '👍 手势', icon: '👍', emojis: ['👋','🤚','🖐','✋','🖖','👌','🤌','🤏','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','👇','☝️','👍','👎','✊','👊','🤛','🤜','👏','🙌','👐','🤲','🤝','🙏'] },
  { label: '❤️ 符号', icon: '❤️', emojis: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','💯','💢','💥','💫','💦','💨','💣','💬','💭','💤','🔥','⭐','🌟','✨','⚡'] },
]

const activeEmojis = computed(() => {
  const tab = emojiTabs.find(t => t.label === activeEmojiTab.value)
  return tab ? tab.emojis : emojiTabs[0].emojis
})

function insertEmoji(emoji: string) { inputText.value += emoji; showEmojiPicker.value = false }

const messageGroups = computed(() => {
  if (!messages.value.length) return []
  const groups: any[] = []
  let lastDate = ''
  for (const msg of messages.value) {
    const date = msg.created_at ? dayjs(msg.created_at).format('YYYY-MM-DD') : ''
    if (date && date !== lastDate) {
      groups.push({ isDateDivider: true, date: dayjs(date).format('YYYY/MM/DD'), messages: [] })
      lastDate = date
    }
    groups.push({ isDateDivider: false, messages: [msg] })
  }
  return groups
})

onMounted(async () => {
  await loadCaseInfo()
  await loadHistory()
  await loadCaseNotes()
  pollTimer = setInterval(loadHistory, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function loadCaseInfo() {
  const res = await caseApi.getDetail(caseId)
  caseInfo.value = res.data.data
}

async function loadHistory() {
  try {
    const res = await negotiationApi.getMessages(caseId, { page: 1, page_size: 200 })
    const newMsgs = res.data.data || []
    if (JSON.stringify(newMsgs) !== JSON.stringify(messages.value)) {
      messages.value = newMsgs
      await scrollToBottom()
    }
  } catch {}
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return
  try {
    const res = await negotiationApi.sendMessage(caseId, { content: text, message_type: 'text' })
    const newMsg = res.data.data
    if (newMsg && !messages.value.find(m => m.id === newMsg.id)) messages.value.push(newMsg)
    inputText.value = ''
    await scrollToBottom()
  } catch { ElMessage.error(t('common.error')) }
}

function triggerImageUpload() { imageInputRef.value?.click() }
function triggerFileUpload() { fileInputRef.value?.click() }

async function handleImageSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) { ElMessage.error(t('negotiation.fileTooLarge')); input.value = ''; return }
  try {
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await uploadApi.uploadImage(formData)
    const imageUrl = uploadRes.data.data.url
    const res = await negotiationApi.sendMessage(caseId, { content: imageUrl, message_type: 'image', file_name: file.name })
    const newMsg = res.data.data
    if (newMsg) { messages.value.push(newMsg); await scrollToBottom() }
  } catch { ElMessage.error(t('common.error')) }
  input.value = ''
}

async function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) { ElMessage.error(t('negotiation.fileTooLarge')); input.value = ''; return }
  const size = file.size < 1024 ? file.size + ' B' : file.size < 1024 * 1024 ? (file.size / 1024).toFixed(1) + ' KB' : (file.size / (1024 * 1024)).toFixed(1) + ' MB'
  try {
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await uploadApi.uploadFile(formData)
    const fileUrl = uploadRes.data.data.url
    const res = await negotiationApi.sendMessage(caseId, { content: fileUrl, message_type: 'file', file_name: file.name, file_size: size })
    const newMsg = res.data.data
    if (newMsg) { messages.value.push(newMsg); await scrollToBottom() }
    ElMessage.success(t('negotiation.uploadSuccess'))
  } catch { ElMessage.error(t('common.error')) }
  input.value = ''
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}

async function loadCaseNotes() {
  try {
    const res = await caseNoteApi.list(caseId)
    caseNotes.value = res.data.data || []
  } catch {}
}

async function addNote() {
  const text = noteInput.value.trim()
  if (!text) return
  try {
    const res = await caseNoteApi.create(caseId, { content: text, note_type: 'text' })
    const newNote = res.data.data
    if (newNote) caseNotes.value.unshift(newNote)
    noteInput.value = ''
    ElMessage.success(t('common.success'))
  } catch { ElMessage.error(t('common.error')) }
}

async function deleteNote(noteId: number) {
  try {
    await caseNoteApi.delete(caseId, noteId)
    caseNotes.value = caseNotes.value.filter(n => n.id !== noteId)
  } catch { ElMessage.error(t('common.error')) }
}

async function handleNoteImage(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) { ElMessage.error(t('negotiation.fileTooLarge')); input.value = ''; return }
  try {
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await uploadApi.uploadImage(formData)
    const imageUrl = uploadRes.data.data.url
    const res = await caseNoteApi.create(caseId, { content: imageUrl, note_type: 'image', file_name: file.name })
    if (res.data.data) caseNotes.value.unshift(res.data.data)
  } catch { ElMessage.error(t('common.error')) }
  input.value = ''
}

async function handleNoteFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) { ElMessage.error(t('negotiation.fileTooLarge')); input.value = ''; return }
  try {
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await uploadApi.uploadFile(formData)
    const fileUrl = uploadRes.data.data.url
    const res = await caseNoteApi.create(caseId, { content: fileUrl, note_type: 'file', file_name: file.name })
    if (res.data.data) caseNotes.value.unshift(res.data.data)
  } catch { ElMessage.error(t('common.error')) }
  input.value = ''
}

function downloadNoteFile(note: any) {
  const a = document.createElement('a')
  a.href = resolveUrl(note.content); a.download = note.file_name || 'download'; a.target = '_blank'
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
}

function formatNoteTime(d: string) { return d ? dayjs(d).format('MM-DD HH:mm') : '' }

function goMediation() {
  router.push(`/mediator/cases/${caseId}/mediation`)
}

function formatMoney(v: number) { return v ? Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00' }
function formatTime(d: string) { return d ? dayjs(d).format('HH:mm') : '' }
</script>

<style lang="scss" scoped>
.negotiation-view { height: calc(100vh - 120px); }
.chat-layout { display: flex; height: 100%; gap: var(--space-4); }
.chat-sidebar { width: 280px; flex-shrink: 0;
  .sidebar-card { h4 { font-weight: 600; margin-bottom: var(--space-2); color: var(--color-text-primary); } }
  .case-num { font-size: 13px; font-weight: 600; color: var(--color-mediator); margin-bottom: var(--space-3); }
}
.notes-list { display: flex; flex-direction: column; gap: var(--space-2); max-height: 240px; overflow-y: auto; }
.note-item {
  padding: 8px 10px; border-radius: var(--radius-md); background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  .note-header { display: flex; justify-content: space-between; align-items: center; }
  .note-time { font-size: 11px; color: var(--color-text-quaternary); }
  .note-text { font-size: 13px; color: var(--color-text-secondary); line-height: 1.5; margin-top: 4px; word-break: break-word; }
  .note-image { margin-top: 6px; }
  .note-file { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--color-primary); cursor: pointer; margin-top: 6px;
    &:hover { opacity: 0.8; }
  }
}
.note-input-area { border-top: 1px solid var(--color-border); padding-top: var(--space-2); }
.note-input-actions { display: flex; justify-content: space-between; align-items: center; margin-top: var(--space-2); }
.mediator-badge {
  margin-top: var(--space-4); padding: 10px 12px; border-radius: var(--radius-md);
  display: flex; align-items: center; gap: var(--space-2); font-size: 13px; font-weight: 500;
  background: var(--color-mediator-light); color: var(--color-mediator); border: 1px solid #ffd591;
}
.chat-main { flex: 1; display: flex; flex-direction: column; padding: 0; overflow: hidden; }
.chat-header { padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--color-border);
  display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 15px; color: var(--color-text-primary); }
.messages-area { flex: 1; overflow-y: auto; padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-2); }
.date-divider { text-align: center; font-size: 12px; color: var(--color-text-quaternary); padding: var(--space-2) 0; }
.message-item { display: flex; align-items: flex-start; gap: 10px; padding: 4px 0;
  &.mine { flex-direction: row-reverse; .msg-body { align-items: flex-end; }
    .msg-bubble { background: var(--color-mediator); color: white; } .msg-sender { display: none; }
    .image-bubble { background: transparent; }
  }
  &.sys-msg { justify-content: center;
    .msg-bubble { background: transparent; padding: 4px 0; }
  }
}
.msg-body { display: flex; flex-direction: column; max-width: 65%; }
.msg-sender { font-size: 12px; color: var(--color-text-tertiary); margin-bottom: var(--space-1); display: flex; align-items: center; }
.msg-bubble { background: var(--color-bg-page); border-radius: var(--radius-lg); padding: 10px 14px; font-size: 14px; line-height: 1.6; word-break: break-word; transition: background var(--transition-fast); }
.image-bubble {
  display: flex; align-items: center; justify-content: center;
  width: 180px; height: 140px; border-radius: 10px; overflow: hidden;
  cursor: pointer; position: relative; background: var(--color-border);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  &:hover { transform: scale(1.03); box-shadow: 0 2px 12px rgba(0,0,0,0.15); }
  .el-image { width: 100%; height: 100%; }
}
.file-bubble { display: flex; align-items: center; gap: 10px; padding: 4px 0; cursor: pointer;
  &:hover { opacity: 0.8; } .file-info { display: flex; flex-direction: column; }
  .file-name { font-size: 13px; font-weight: 500; } .file-size { font-size: 11px; color: var(--color-text-tertiary); } }
.msg-time { font-size: 11px; color: var(--color-text-quaternary); margin-top: var(--space-1); }
.sys-msg { font-size: 13px; color: var(--color-mediator); text-align: center; background: var(--color-mediator-light); border-radius: var(--radius-md); padding: var(--space-2) var(--space-4); }
.empty-chat { flex: 1; display: flex; align-items: center; justify-content: center; }
.input-area { border-top: 1px solid var(--color-border); padding: var(--space-3) var(--space-4); position: relative; }
.input-toolbar { display: flex; gap: 4px; margin-bottom: var(--space-2); }
.input-toolbar .el-button { font-size: 18px; }
.input-row { display: flex; gap: var(--space-2); align-items: flex-end; }
.input-row .el-button { min-height: 40px; padding: var(--space-2) 20px; }
.emoji-picker { position: absolute; bottom: 100%; left: 0; z-index: 100; background: white; border: 1px solid var(--color-border);
  border-radius: var(--radius-xl); box-shadow: 0 4px 20px rgba(0,0,0,0.12); width: 380px; }
.emoji-picker-inner { padding: var(--space-3); }
.emoji-tabs { display: flex; gap: 4px; margin-bottom: 10px; border-bottom: 1px solid var(--color-border); padding-bottom: var(--space-2); }
.emoji-tab { padding: 4px 10px; border-radius: var(--radius-md); cursor: pointer; font-size: 16px; transition: background var(--transition-fast);
  &:hover { background: var(--color-bg-page); } &.active { background: var(--color-mediator-light); } }
.emoji-grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 2px; max-height: 240px; overflow-y: auto; }
.emoji-item { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  font-size: 20px; cursor: pointer; border-radius: var(--radius-md); transition: background 0.15s;
  &:hover { background: var(--color-border); transform: scale(1.2); } }
</style>
