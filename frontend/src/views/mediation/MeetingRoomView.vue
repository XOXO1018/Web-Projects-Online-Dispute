<template>
  <div class="meeting-room">
    <!-- 顶部工具栏 -->
    <div class="meeting-toolbar">
      <div class="meeting-title">
        <span class="live-dot"></span>
        {{ t('admin.meetingRoom') }} · {{ channelName }}
      </div>
      <div class="meeting-timer">
        ⏱ {{ formatDuration(duration) }}
      </div>
      <div class="toolbar-actions">
        <el-button :type="isMuted ? 'danger' : 'default'" circle @click="toggleMute" :title="t('admin.meetingToolbar.mic')">
          <el-icon><Microphone v-if="!isMuted" /><Mute v-else /></el-icon>
        </el-button>
        <el-button :type="isCameraOff ? 'danger' : 'default'" circle @click="toggleCamera" :title="t('admin.meetingToolbar.camera')">
          <el-icon><VideoCamera v-if="!isCameraOff" /><VideoCameraFilled v-else /></el-icon>
        </el-button>
        <el-button circle @click="toggleScreenShare" :title="t('admin.meetingToolbar.screenShare')">
          <el-icon><Monitor /></el-icon>
        </el-button>
        <el-button type="danger" @click="leaveMeeting">
          <el-icon><SwitchButton /></el-icon> {{ t('admin.leaveMeeting') }}
        </el-button>
        <el-button v-if="isMediator" type="warning" @click="endMeeting">
          <el-icon><CircleClose /></el-icon> {{ t('admin.endMeeting') }}
        </el-button>
      </div>
    </div>

    <div class="meeting-body">
      <!-- 视频区域 -->
      <div class="video-area">
        <div class="video-grid">
          <!-- 本地视频 -->
          <div class="video-player local">
            <video ref="localVideo" autoplay muted playsinline></video>
            <div class="video-label">{{ t('admin.localVideo') }}</div>
          </div>
          <!-- 远程参与者 -->
          <div v-for="user in remoteUsers" :key="user.uid" class="video-player remote">
            <video :ref="el => setRemoteVideo(el, user.uid)" autoplay playsinline></video>
            <div class="video-label">{{ user.name }}</div>
          </div>
          <!-- 空位 -->
          <div v-if="remoteUsers.length === 0" class="video-placeholder">
            <el-icon size="48"><UserFilled /></el-icon>
            <p>{{ t('admin.waitingParticipants') }}</p>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="side-panel">
        <!-- Mock 提示 -->
        <el-alert
          v-if="isMockMode"
          type="warning"
          :title="t('admin.mockModeHint')"
          :closable="false"
          style="margin-bottom: 12px; font-size: 12px"
        />

        <!-- 参与者管理 -->
        <div class="panel-section">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px">
            <h4>👥 {{ t('admin.participants') }}</h4>
            <el-button v-if="isMediator" size="small" type="primary" text @click="showAddParticipant = true">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
          <div class="participant-list">
            <div v-for="p in participants" :key="p.name" class="participant-item">
              <el-avatar size="small" :style="{ background: p.color }">{{ p.name[0] }}</el-avatar>
              <span class="participant-name">{{ p.name }}</span>
              <el-tag size="small" :type="p.role === 'mediator' ? 'warning' : ''">{{ p.roleLabel }}</el-tag>
            </div>
          </div>
        </div>

        <!-- 证据列表 -->
        <div class="panel-section">
          <h4>📎 {{ t('admin.evidenceList') }}</h4>
          <div v-for="ev in evidences" :key="ev.id" class="ev-item" @click="openFile(ev)">
            <el-icon><Document /></el-icon>
            <span>{{ ev.file_name }}</span>
          </div>
          <el-empty v-if="!evidences.length" :description="t('admin.noEvidence')" :image-size="40" />
        </div>

        <!-- 调解员意见 (仅调解员可见) -->
        <div class="panel-section" v-if="isMediator">
          <h4>📝 {{ t('mediation.mediatorOpinion') }}</h4>
          <el-input v-model="mediatorOpinion" type="textarea" :rows="4" :placeholder="t('mediation.mediatorOpinionPlaceholder')" />
          <div class="opinion-actions" style="margin-top: 8px">
            <el-button type="success" size="small" @click="submitOpinion(true)">{{ t('mediation.mediationSuccess') }}</el-button>
            <el-button type="danger" size="small" @click="submitOpinion(false)">{{ t('mediation.mediationFailed') }}</el-button>
          </div>
          <el-input v-if="opinionSuccess" v-model="agreementContent" type="textarea" :rows="3"
            :placeholder="t('mediation.agreementContent')" style="margin-top: 8px" />
        </div>
      </div>
    </div>

    <!-- 添加参与者弹窗 -->
    <el-dialog v-model="showAddParticipant" :title="t('admin.addParticipant')" width="360px">
      <el-form label-position="top">
        <el-form-item :label="t('admin.participantName')">
          <el-input v-model="newParticipantName" :placeholder="t('admin.participantNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('admin.participantRole')">
          <el-select v-model="newParticipantRole" style="width:100%">
            <el-option :label="t('admin.participantRoles.plaintiff')" value="plaintiff" />
            <el-option :label="t('admin.participantRoles.defendant')" value="defendant" />
            <el-option :label="t('admin.participantRoles.observer')" value="observer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddParticipant = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="addParticipant">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { mediationApi, evidenceApi } from '@/api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const channelName = route.params.channelName as string
const meetingId = Number(route.query.meeting_id)
const caseId = Number(route.query.case_id)

const localVideo = ref<HTMLVideoElement | null>(null)
const remoteUsers = ref<any[]>([])
const isMuted = ref(false)
const isCameraOff = ref(false)
const duration = ref(0)
const evidences = ref<any[]>([])
const mediatorOpinion = ref('')
const agreementContent = ref('')
const opinionSuccess = ref(false)
const isMockMode = ref(true)
const showAddParticipant = ref(false)
const newParticipantName = ref('')
const newParticipantRole = ref('observer')
const meetingStatus = ref('in_progress') // pending | in_progress | ended

let durationTimer: any = null
let localStream: MediaStream | null = null

const isMediator = computed(() => authStore.isMediator)

const participants = ref([
  { name: authStore.user?.real_name || 'Mediator', role: 'mediator', roleLabel: 'Mediator', color: '#fa8c16' },
  { name: 'Plaintiff Enterprise', role: 'plaintiff', roleLabel: 'Plaintiff', color: '#1677ff' },
  { name: 'Defendant Enterprise', role: 'defendant', roleLabel: 'Defendant', color: '#52c41a' },
])

onMounted(async () => {
  await initMedia()
  durationTimer = setInterval(() => duration.value++, 1000)
  if (caseId) {
    const res = await evidenceApi.list(caseId)
    evidences.value = res.data.data || []
  }
})

onUnmounted(() => {
  clearInterval(durationTimer)
  localStream?.getTracks().forEach(t => t.stop())
})

async function initMedia() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (localVideo.value) {
      localVideo.value.srcObject = localStream
    }
    isMockMode.value = true // 真实Agora需要配置AppID
    ElMessage.info(t('admin.mockEntered'))
  } catch (e) {
    ElMessage.warning(t('admin.cameraDenied'))
  }
}

function toggleMute() {
  isMuted.value = !isMuted.value
  localStream?.getAudioTracks().forEach(t => { t.enabled = !isMuted.value })
}

function toggleCamera() {
  isCameraOff.value = !isCameraOff.value
  localStream?.getVideoTracks().forEach(t => { t.enabled = !isCameraOff.value })
}

function toggleScreenShare() {
  ElMessage.info(t('admin.screenShareHint'))
}

function setRemoteVideo(el: HTMLVideoElement | null, uid: number) {
  // 真实Agora SDK中绑定远程视频流
}

async function submitOpinion(success: boolean) {
  opinionSuccess.value = success
  if (success && !agreementContent.value) {
    ElMessage.warning(t('admin.inputAgreement'))
    return
  }
  try {
    await mediationApi.submitOpinion({
      meeting_id: meetingId,
      opinion: mediatorOpinion.value,
      success: success,
      agreement_content: agreementContent.value,
    })
    ElMessage.success(success ? t('mediation.agreementSaved') : t('mediation.failedMarked'))
  } catch {}
}

function leaveMeeting() {
  ElMessageBox.confirm(t('admin.leaveConfirm'), t('admin.leaveConfirmTitle'), {
    type: 'warning',
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
  }).then(() => {
    localStream?.getTracks().forEach(t => t.stop())
    router.back()
  })
}

function endMeeting() {
  ElMessageBox.confirm(t('admin.endMeetingConfirm'), t('admin.endMeetingTitle'), {
    type: 'warning',
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
  }).then(() => {
    meetingStatus.value = 'ended'
    localStream?.getTracks().forEach(t => t.stop())
    ElMessage.success(t('admin.meetingEnded'))
    setTimeout(() => router.back(), 1500)
  })
}

function addParticipant() {
  if (!newParticipantName.value.trim()) { ElMessage.warning(t('admin.participantNamePlaceholder')); return }
  const roleLabels: Record<string, string> = {
    plaintiff: 'Plaintiff',
    defendant: 'Defendant',
    observer: 'Observer',
  }
  const roleColors: Record<string, string> = {
    plaintiff: '#1677ff',
    defendant: '#52c41a',
    observer: '#8c8c8c',
  }
  participants.value.push({
    name: newParticipantName.value,
    role: newParticipantRole.value,
    roleLabel: roleLabels[newParticipantRole.value] || 'Observer',
    color: roleColors[newParticipantRole.value] || '#8c8c8c',
  })
  showAddParticipant.value = false
  newParticipantName.value = ''
  ElMessage.success(t('common.success'))
}

function openFile(ev: any) {
  window.open(ev.file_url, '_blank')
}

function formatDuration(secs: number) {
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60
  return h > 0
    ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    : `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
</script>

<style lang="scss" scoped>
.meeting-room {
  height: calc(100vh - var(--header-height));
  display: flex; flex-direction: column;
  background: #0d1117;
  color: white;
  margin: calc(var(--space-6) * -1);
}
.meeting-toolbar {
  height: 60px; background: #1a1f2e; border-bottom: 1px solid #2d3340;
  display: flex; align-items: center; justify-content: space-between; padding: 0 var(--space-6);
}
.meeting-title {
  display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 15px;
}
.live-dot {
  width: 10px; height: 10px; background: var(--color-danger); border-radius: 50%;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.meeting-timer { font-size: 18px; font-weight: 700; color: var(--color-success); font-family: monospace; font-variant-numeric: tabular-nums; }
.toolbar-actions { display: flex; gap: var(--space-2); }
.meeting-body { flex: 1; display: flex; overflow: hidden; }
.video-area { flex: 1; padding: var(--space-4); overflow: hidden; }
.video-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-3); height: 100%;
}
.video-player {
  position: relative; border-radius: var(--radius-xl); overflow: hidden; background: #1a1f2e;
  transition: box-shadow var(--transition-fast);
  video { width: 100%; height: 100%; object-fit: cover; }
  .video-label {
    position: absolute; bottom: 8px; left: 8px;
    background: rgba(0,0,0,0.6); padding: 2px 10px; border-radius: 100px; font-size: 12px;
  }
  &.local { border: 2px solid var(--color-primary); }
  &:hover { box-shadow: 0 0 0 2px rgba(22,119,255,0.3); }
}
.video-placeholder {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.3); gap: var(--space-3); background: #1a1f2e; border-radius: var(--radius-xl);
}
.side-panel {
  width: 300px; background: #1a1f2e; padding: var(--space-4); overflow-y: auto; border-left: 1px solid #2d3340;
}
.panel-section {
  margin-bottom: var(--space-5);
  h4 { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.7); margin-bottom: 10px; }
}
.participant-list { display: flex; flex-direction: column; gap: 8px; }
.participant-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px;
  border-radius: var(--radius-md); background: rgba(255,255,255,0.05);
  .participant-name { flex: 1; font-size: 13px; color: rgba(255,255,255,0.85); }
}
.ev-item {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2); border-radius: var(--radius-md); cursor: pointer;
  font-size: 13px; color: rgba(255,255,255,0.8);
  transition: background var(--transition-fast);
  &:hover { background: rgba(255,255,255,0.05); }
}
.opinion-actions { display: flex; gap: var(--space-2); }
</style>
