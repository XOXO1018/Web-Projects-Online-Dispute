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
          <!-- 对方在线状态 -->
          <div class="opponent-status" :class="opponentOnline ? 'online' : 'offline'">
            <span class="status-dot"></span>
            {{ opponentOnline ? t('negotiation.opponentOnline') : t('negotiation.opponentOffline') }}
          </div>
          <div v-if="!opponentOnline" class="offline-hint">
            {{ t('negotiation.leaveMsg') }}
          </div>
        </div>
      </div>

      <!-- 右侧：聊天区 -->
      <div class="chat-main page-card">
        <div class="chat-header">
          <span>💬 {{ t('negotiation.chatHeader') }} · {{ caseInfo?.case_number }}</span>
          <div class="poll-status">
            <span class="poll-dot"></span>
            {{ t('negotiation.online') }}
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="messages-area" ref="messagesEl">
          <div v-for="(group, idx) in messageGroups" :key="idx" class="msg-group">
            <div v-if="group.isDateDivider" class="date-divider">{{ group.date }}</div>
            <div v-else v-for="msg in group.messages" :key="msg.id"
                 :class="['message-item', msg.sender_id === currentUserId ? 'mine' : 'theirs']">
              <el-avatar size="small" class="msg-avatar">{{ msg.sender_name?.[0] || 'U' }}</el-avatar>
              <div class="msg-body">
                <div class="msg-sender">{{ msg.sender_name }}</div>
                <div class="msg-bubble">
                  <template v-if="msg.message_type === 'text'">{{ msg.content }}</template>
                  <template v-else-if="msg.message_type === 'image'">
                    <div class="image-bubble" @click="previewImage(resolveUrl(msg.content))">
                      <el-image :src="resolveUrl(msg.content)" fit="cover" loading="lazy"
                        :preview-src-list="[resolveUrl(msg.content)]" :initial-index="0"
                        hide-on-click-modal preview-teleported
                      >
                        <template #placeholder>
                          <div class="img-placeholder"><el-icon size="24"><Loading /></el-icon></div>
                        </template>
                        <template #error>
                          <div class="img-placeholder"><el-icon size="24"><Picture /></el-icon></div>
                        </template>
                      </el-image>
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
            <el-empty :description="t('negotiation.emptyChat')" :image-size="80" />
          </div>
        </div>

        <!-- 输入区 -->
        <div class="input-area">
          <!-- 表情选择器 -->
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
            <el-button text :title="t('negotiation.toolbar.video')" @click="startVideoNegotiation" class="video-btn">
              <el-icon><VideoCamera /></el-icon>
            </el-button>
            <el-button text :title="t('negotiation.toolbar.mediatorIntervene')" @click="showMediatorSelect = true" class="mediator-btn">
              <el-icon><Avatar /></el-icon>
            </el-button>
            <input ref="imageInputRef" type="file" accept="image/*" style="display:none" @change="handleImageSelect" />
            <input ref="fileInputRef" type="file" style="display:none" @change="handleFileSelect" />
          </div>
          <div class="input-row">
            <el-input v-model="inputText" :placeholder="t('negotiation.inputPlaceholder')"
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

    <!-- 调解员介入选择弹窗 -->
    <el-dialog v-model="showMediatorSelect" :title="t('negotiation.toolbar.mediatorIntervene')" width="420px">
      <el-select v-model="selectedMediatorId" :placeholder="t('mediation.selectMediator')" style="width: 100%" size="large">
        <el-option
          v-for="m in mediatorList"
          :key="m.id"
          :label="`${m.name} - ${m.specialty || ''}`"
          :value="m.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="showMediatorSelect = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="doMediatorIntervene" :loading="interveneLoading" :disabled="!selectedMediatorId">
          {{ t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { caseApi, negotiationApi, uploadApi, mediationApi, onlineApi } from '@/api'
import { Picture, FolderOpened, Document, Download, Loading } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const { t, te } = useI18n()

/** 安全翻译：key 不存在时直接返回原始值，而不是显示 key 本身 */
function tr(key: string, fallback: string) {
  return te(key) ? t(key) : fallback
}
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const caseId = Number(route.params.id)

const messages = ref<any[]>([])
const inputText = ref('')
const caseInfo = ref<any>(null)
const messagesEl = ref<HTMLElement | null>(null)
const opponentOnline = ref(false)
const showEmojiPicker = ref(false)
const activeEmojiTab = ref('😊 表情')
const imageInputRef = ref<HTMLInputElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const showMediatorSelect = ref(false)
const selectedMediatorId = ref<number | null>(null)
const mediatorList = ref<any[]>([])
const interveneLoading = ref(false)

const currentUserId = computed(() => authStore.user?.id)

// 解析后端返回的文件 URL（已经是代理路径，直接使用）
function resolveUrl(url: string) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return url
}

// 下载文件
function downloadFile(url: string, fileName?: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = fileName || 'download'
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// 预览图片（el-image 自带 preview-src-list 会处理，此方法用于双重保险）
function previewImage(url: string) {
  // el-image 的 preview-src-list 已自动处理点击放大
}

// 从后端检查在线状态
async function checkOnlineStatus() {
  try {
    const res = await onlineApi.checkStatus()
    opponentOnline.value = res.data.data.online
  } catch {
    opponentOnline.value = false
  }
}

let pollTimer: ReturnType<typeof setInterval> | null = null
let onlineTimer: ReturnType<typeof setInterval> | null = null

// 表情数据
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

// 消息分组（按日期）
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
  await checkOnlineStatus()
  await loadMediatorList()
  pollTimer = setInterval(loadHistory, 3000)
  onlineTimer = setInterval(checkOnlineStatus, 10000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (onlineTimer) clearInterval(onlineTimer)
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
    // 先上传图片到后端，获取 URL
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await uploadApi.uploadImage(formData)
    const imageUrl = uploadRes.data.data.url
    // 再发送消息，content 为图片 URL
    const res = await negotiationApi.sendMessage(caseId, {
      content: imageUrl,
      message_type: 'image',
      file_name: file.name,
    })
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
    // 先上传文件到后端，获取 URL
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await uploadApi.uploadFile(formData)
    const fileUrl = uploadRes.data.data.url
    // 再发送消息，content 为文件 URL
    const res = await negotiationApi.sendMessage(caseId, {
      content: fileUrl,
      message_type: 'file',
      file_name: file.name,
      file_size: size,
    })
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

async function loadMediatorList() {
  try {
    const res = await caseApi.list({})  // 获取调解员列表
    // 使用专门接口
    const mediatorRes = await mediationApi.recommendMediators(caseId)
    mediatorList.value = mediatorRes.data.data || []
  } catch {
    // fallback: 用 api 获取
  }
}

async function doMediatorIntervene() {
  if (!selectedMediatorId.value) return
  interveneLoading.value = true
  try {
    const res = await mediationApi.mediatorIntervene({
      case_id: caseId,
      mediator_id: selectedMediatorId.value,
    })
    const newMsg = res.data.data
    if (newMsg && !messages.value.find(m => m.id === newMsg.id)) {
      messages.value.push(newMsg)
      await scrollToBottom()
    }
    const mediator = mediatorList.value.find(m => m.id === selectedMediatorId.value)
    ElMessage.success(`${mediator?.name || ''} ${t('negotiation.interveneSuccess')}`)
    showMediatorSelect.value = false
    selectedMediatorId.value = null
  } catch {
    ElMessage.error(t('common.error'))
  } finally {
    interveneLoading.value = false
  }
}

function startVideoNegotiation() {
  router.push(`/cases/${caseId}/mediation`)
}

function formatMoney(v: number) { return v ? Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00' }
function formatTime(d: string) { return d ? dayjs(d).format('HH:mm') : '' }
</script>

<style lang="scss" scoped>
.negotiation-view { height: calc(100vh - 120px); }
.chat-layout { display: flex; height: 100%; gap: 16px; }
.chat-sidebar { width: 260px; flex-shrink: 0;
  .sidebar-card { h4 { font-weight: 600; margin-bottom: 8px; } }
  .case-num { font-size: 13px; font-weight: 600; color: #1677ff; margin-bottom: 12px; }
}
.opponent-status { margin-top: 16px; padding: 8px 12px; border-radius: 8px;
  display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500;
  &.online { background: #f6ffed; color: #52c41a; .status-dot { background: #52c41a; } }
  &.offline { background: #fff7e6; color: #fa8c16; .status-dot { background: #fa8c16; } }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  &.online .status-dot { animation: pulse 2s infinite; }
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.offline-hint { margin-top: 8px; font-size: 12px; color: #8c8c8c; padding: 6px 10px; background: #fafafa; border-radius: 6px; }
.chat-main { flex: 1; display: flex; flex-direction: column; padding: 0; overflow: hidden; }
.chat-header { padding: 16px 20px; border-bottom: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 15px; }
.poll-status { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 400; color: #52c41a;
  .poll-dot { width: 8px; height: 8px; border-radius: 50%; background: #52c41a; animation: pulse 2s infinite; } }
.messages-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 8px; }
.date-divider { text-align: center; font-size: 12px; color: #bfbfbf; padding: 8px 0; }
.message-item { display: flex; align-items: flex-start; gap: 10px; padding: 4px 0;
  &.mine { flex-direction: row-reverse; .msg-body { align-items: flex-end; }
    .msg-bubble { background: #1677ff; color: white; } .msg-sender { display: none; }
    .image-bubble { background: transparent; .img-placeholder { background: #2b7de9; color: rgba(255,255,255,0.5); } }
  } }
.msg-body { display: flex; flex-direction: column; max-width: 65%; }
.msg-sender { font-size: 12px; color: #8c8c8c; margin-bottom: 4px; }
.msg-bubble { background: #f5f5f5; border-radius: 12px; padding: 10px 14px; font-size: 14px; line-height: 1.6; word-break: break-word; }
.image-bubble {
  display: flex; align-items: center; justify-content: center;
  width: 180px; height: 140px; border-radius: 10px; overflow: hidden;
  cursor: pointer; position: relative; background: #f0f0f0;
  transition: transform 0.2s, box-shadow 0.2s;
  &:hover { transform: scale(1.03); box-shadow: 0 2px 12px rgba(0,0,0,0.15); }
  .el-image { width: 100%; height: 100%; }
  .img-placeholder {
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
    background: #f5f5f5; color: #c0c0c0;
  }
}
.file-bubble { display: flex; align-items: center; gap: 10px; padding: 4px 0; cursor: pointer;
  &:hover { opacity: 0.8; } .file-info { display: flex; flex-direction: column; }
  .file-name { font-size: 13px; font-weight: 500; } .file-size { font-size: 11px; color: #8c8c8c; } }
.msg-time { font-size: 11px; color: #c0c0c0; margin-top: 4px; }
.empty-chat { flex: 1; display: flex; align-items: center; justify-content: center; }
.input-area { border-top: 1px solid #f0f0f0; padding: 12px 16px; position: relative; }
.input-toolbar { display: flex; gap: 4px; margin-bottom: 8px; }
.input-toolbar .el-button { font-size: 18px; }
.input-row { display: flex; gap: 8px; align-items: flex-end; }
.input-row .el-button { min-height: 40px; padding: 8px 20px; }
.emoji-picker { position: absolute; bottom: 100%; left: 0; z-index: 100; background: white; border: 1px solid #e8e8e8;
  border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.12); width: 380px; }
.emoji-picker-inner { padding: 12px; }
.emoji-tabs { display: flex; gap: 4px; margin-bottom: 10px; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px; }
.emoji-tab { padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 16px; transition: background 0.2s;
  &:hover { background: #f5f5f5; } &.active { background: #e6f4ff; } }
.emoji-grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 2px; max-height: 240px; overflow-y: auto; }
.emoji-item { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  font-size: 20px; cursor: pointer; border-radius: 6px; transition: background 0.15s;
  &:hover { background: #f0f0f0; transform: scale(1.2); } }
.video-btn { color: #1677ff; &:hover { color: #4096ff; } }
.mediator-btn { color: #fa8c16; &:hover { color: #ffa940; } }
</style>
