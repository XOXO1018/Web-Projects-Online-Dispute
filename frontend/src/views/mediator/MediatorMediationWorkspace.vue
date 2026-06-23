<template>
  <div class="mediation-workspace">
    <!-- 页面标题 -->
    <div class="ws-header page-card">
      <div>
        <h2>⚖️ {{ t('mediator.mediationWorkspace') }}</h2>
        <p class="ws-subtitle">{{ t('mediator.wsSubtitle') }}</p>
      </div>
      <div class="header-stats">
        <div class="hstat" v-for="s in headerStats" :key="s.key">
          <div class="hstat-val" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="hstat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧：调解中案件列表 -->
      <el-col :span="10">
        <div class="page-card case-list-panel">
          <div class="panel-title">
            📁 {{ t('mediator.mediatingCases') }}
            <el-tag type="warning" size="small" style="margin-left: 8px">{{ mediatingCases.length }}</el-tag>
          </div>

          <el-scrollbar max-height="600px">
            <div
              v-for="c in mediatingCases" :key="c.id"
              :class="['case-item', { active: selectedCaseId === c.id }]"
              @click="selectCase(c)"
            >
              <div class="ci-left">
                <span class="ci-number">{{ c.case_number }}</span>
                <span class="ci-opponent">{{ c.opponent_name }}</span>
              </div>
              <div class="ci-right">
                <span class="ci-amount">$ {{ formatMoney(c.amount) }}</span>
                <el-tag type="warning" size="small">{{ t('case.statusMap.mediating') }}</el-tag>
              </div>
            </div>
            <div v-if="!loading && mediatingCases.length === 0" class="no-cases">
              <el-empty :description="t('mediator.noMediatingCases')" :image-size="80" />
            </div>
          </el-scrollbar>
        </div>
      </el-col>

      <!-- 右侧：选中案件的调解操作区 -->
      <el-col :span="14">
        <div v-if="!selectedCase" class="page-card empty-workspace">
          <el-empty :description="t('mediator.selectCaseToStart')" :image-size="120">
            <template #image>
              <div class="empty-icon">⚖️</div>
            </template>
          </el-empty>
        </div>

        <template v-else>
          <!-- 案件信息卡 -->
          <div class="page-card case-info-card">
            <div class="cic-header">
              <div>
                <h3 class="cic-number">{{ selectedCase.case_number }}</h3>
                <span class="cic-opponent">{{ selectedCase.opponent_name }}</span>
              </div>
              <div class="cic-actions">
                <el-button type="primary" size="small" @click="goNegotiation">
                  <el-icon><ChatDotRound /></el-icon> {{ t('mediator.enterNegotiation') }}
                </el-button>
                <el-button type="warning" size="small" v-if="currentMeeting" @click="goMeetingRoom">
                  <el-icon><VideoCamera /></el-icon> {{ t('mediation.enterMeetingRoom') }}
                </el-button>
              </div>
            </div>
            <el-descriptions :column="3" size="small" style="margin-top: 12px">
              <el-descriptions-item :label="t('case.amount')">
                <strong style="color: #e63946">$ {{ formatMoney(selectedCase.amount) }}</strong>
              </el-descriptions-item>
              <el-descriptions-item :label="t('case.contractType')">
                {{ tr(`case.contractTypes.${selectedCase.contract_type}`, selectedCase.contract_type) }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('case.opponentCountry')">
                {{ tr(`countries.${selectedCase.opponent_country || 'OTHER'}`, selectedCase.opponent_country || '-') }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 调解流程步骤条 -->
          <div class="page-card" style="margin-top: 16px">
            <el-steps :active="currentStep" finish-status="success" style="padding: 8px 0">
              <el-step :title="t('mediator.step1')" :description="t('mediator.step1Desc')" />
              <el-step :title="t('mediator.step2')" :description="t('mediator.step2Desc')" />
              <el-step :title="t('mediator.step3')" :description="t('mediator.step3Desc')" />
              <el-step :title="t('mediator.step4')" :description="t('mediator.step4Desc')" />
            </el-steps>
          </div>

          <!-- Step 1: 安排会议 -->
          <div class="page-card op-card" style="margin-top: 16px" v-if="currentStep === 0">
            <div class="op-card-title">
              <el-icon color="#fa8c16"><Calendar /></el-icon>
              {{ t('mediator.arrangeMeeting') }}
            </div>
            <el-form :model="scheduleForm" label-position="top" ref="scheduleFormRef">
              <el-form-item :label="t('mediator.meetingTime')" required>
                <el-date-picker
                  v-model="scheduleForm.scheduled_time"
                  type="datetime"
                  :placeholder="t('mediator.selectMeetingTime')"
                  :disabled-date="disablePastDate"
                  style="width: 100%"
                  value-format="YYYY-MM-DDTHH:mm:ss"
                  format="YYYY-MM-DD HH:mm"
                />
              </el-form-item>
              <el-form-item :label="t('mediator.meetingNote')">
                <el-input
                  v-model="scheduleForm.note"
                  type="textarea" :rows="2"
                  :placeholder="t('mediator.meetingNotePlaceholder')"
                />
              </el-form-item>
              <el-button type="primary" :loading="actionLoading" @click="handleSchedule"
                :disabled="!scheduleForm.scheduled_time">
                {{ t('mediator.confirmSchedule') }}
              </el-button>
            </el-form>
          </div>

          <!-- Step 2: 进行中会议 -->
          <div class="page-card op-card" style="margin-top: 16px" v-if="currentStep === 1">
            <div class="op-card-title">
              <el-icon color="#fa8c16"><VideoCamera /></el-icon>
              {{ t('mediator.ongoingMeeting') }}
            </div>
            <div v-if="currentMeeting" class="meeting-info">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item :label="t('mediation.meetingTime')">
                  {{ formatDateTime(currentMeeting.scheduled_time) }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('mediation.meetingStatus')">
                  <el-tag :type="meetingTagType(currentMeeting.status)" size="small">
                    {{ tr(`mediation.meetingStatusMap.${currentMeeting.status}`, currentMeeting.status) }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
              <div style="margin-top: 16px; display: flex; gap: 12px">
                <el-button type="primary" @click="goMeetingRoom">
                  <el-icon><VideoCamera /></el-icon> {{ t('mediation.enterMeetingRoom') }}
                </el-button>
                <el-button type="warning" @click="currentStep = 2">
                  {{ t('mediator.proceedToOpinion') }} →
                </el-button>
              </div>
            </div>
          </div>

          <!-- Step 3: 提交调解意见 -->
          <div class="page-card op-card" style="margin-top: 16px" v-if="currentStep === 2">
            <div class="op-card-title">
              <el-icon color="#fa8c16"><EditPen /></el-icon>
              {{ t('mediator.submitOpinion') }}
            </div>
            <el-form :model="opinionForm" label-position="top" ref="opinionFormRef">
              <el-form-item :label="t('mediator.opinionLabel')" required>
                <el-input
                  v-model="opinionForm.opinion"
                  type="textarea" :rows="5"
                  :placeholder="t('mediator.opinionPlaceholder')"
                />
              </el-form-item>

              <el-form-item :label="t('mediator.mediationResult')" required>
                <el-radio-group v-model="opinionForm.success">
                  <el-radio :value="true">
                    <el-tag type="success" effect="dark">✅ {{ t('mediator.resultSuccess') }}</el-tag>
                  </el-radio>
                  <el-radio :value="false">
                    <el-tag type="danger" effect="dark">❌ {{ t('mediator.resultFailed') }}</el-tag>
                  </el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item v-if="opinionForm.success" :label="t('mediator.agreementContent')" required>
                <el-input
                  v-model="opinionForm.agreement_content"
                  type="textarea" :rows="6"
                  :placeholder="t('mediator.agreementPlaceholder')"
                />
                <div class="form-tip">{{ t('mediator.agreementTip') }}</div>
              </el-form-item>

              <div style="display: flex; gap: 12px; margin-top: 8px">
                <el-button @click="currentStep = 1">← {{ t('common.back') }}</el-button>
                <el-button type="primary" :loading="actionLoading" @click="handleSubmitOpinion"
                  :disabled="!opinionForm.opinion">
                  {{ t('mediator.submitOpinion') }}
                </el-button>
              </div>
            </el-form>
          </div>

          <!-- Step 4: 完成 -->
          <div class="page-card op-card" style="margin-top: 16px" v-if="currentStep === 3">
            <div class="op-card-title">
              <el-icon color="#52c41a"><CircleCheck /></el-icon>
              {{ t('mediator.mediationDone') }}
            </div>
            <div class="done-content">
              <template v-if="opinionForm.success">
                <el-result icon="success" :title="t('mediator.mediationSuccessTitle')"
                  :sub-title="t('mediator.mediationSuccessDesc')">
                  <template #extra>
                    <el-button type="primary" @click="router.push('/mediator/cases')">
                      {{ t('mediator.backToCases') }}
                    </el-button>
                  </template>
                </el-result>
              </template>
              <template v-else>
                <el-result icon="warning" :title="t('mediator.mediationFailedTitle')"
                  :sub-title="t('mediator.mediationFailedDesc')">
                  <template #extra>
                    <el-button type="primary" @click="router.push('/mediator/cases')">
                      {{ t('mediator.backToCases') }}
                    </el-button>
                  </template>
                </el-result>
              </template>
            </div>
          </div>
        </template>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import type { FormInstance } from 'element-plus'
import { mediatorApi, mediationApi } from '@/api'
import { ChatDotRound, VideoCamera, Calendar, EditPen, CircleCheck } from '@element-plus/icons-vue'

const { t, te } = useI18n()
const router = useRouter()
function tr(key: string, fallback: string) { return te(key) ? t(key) : fallback }

const loading = ref(false)
const actionLoading = ref(false)
const cases = ref<any[]>([])
const selectedCaseId = ref<number | null>(null)
const selectedCase = ref<any>(null)
const currentMeeting = ref<any>(null)
const currentStep = ref(0)
const scheduleFormRef = ref<FormInstance>()
const opinionFormRef = ref<FormInstance>()

const scheduleForm = ref({ scheduled_time: '', note: '' })
const opinionForm = ref({
  opinion: '',
  success: true,
  agreement_content: '',
  meeting_id: 0,
})

const mediatingCases = computed(() => cases.value.filter(c => c.status === 'mediating'))

const headerStats = computed(() => [
  { key: 'mediating', label: t('mediator.inMediation'), value: mediatingCases.value.length, color: '#fa8c16' },
  { key: 'total', label: t('dashboard.stats.total'), value: cases.value.length, color: '#1677ff' },
])

onMounted(async () => {
  await loadCases()
})

async function loadCases() {
  loading.value = true
  try {
    const res = await mediatorApi.getMyCases({ page: 1, page_size: 100 })
    cases.value = res.data.data.items || []
  } finally {
    loading.value = false
  }
}

function selectCase(c: any) {
  selectedCaseId.value = c.id
  selectedCase.value = c
  // 重置流程
  currentStep.value = 0
  currentMeeting.value = null
  scheduleForm.value = { scheduled_time: '', note: '' }
  opinionForm.value = { opinion: '', success: true, agreement_content: '', meeting_id: 0 }
}

function goNegotiation() {
  router.push(`/mediator/cases/${selectedCase.value.id}/negotiation`)
}

function goMeetingRoom() {
  if (currentMeeting.value?.channel_name) {
    router.push(`/mediator/meeting/${currentMeeting.value.channel_name}?meeting_id=${currentMeeting.value.id}&case_id=${selectedCase.value.id}`)
  }
}

function disablePastDate(time: Date) { return time.getTime() < Date.now() }

async function handleSchedule() {
  if (!scheduleForm.value.scheduled_time) return
  actionLoading.value = true
  try {
    const res = await mediationApi.scheduleMeeting({
      request_id: selectedCase.value.id,
      scheduled_time: scheduleForm.value.scheduled_time,
    })
    const data = res.data.data
    currentMeeting.value = {
      id: data.meeting_id,
      channel_name: data.channel_name,
      scheduled_time: data.scheduled_time,
      status: 'scheduled',
    }
    opinionForm.value.meeting_id = data.meeting_id
    currentStep.value = 1
    ElMessage.success(t('mediator.meetingScheduledSuccess'))
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || t('common.error'))
  } finally {
    actionLoading.value = false
  }
}

async function handleSubmitOpinion() {
  if (!opinionForm.value.opinion) { ElMessage.warning(t('mediator.opinionRequired')); return }
  if (opinionForm.value.success && !opinionForm.value.agreement_content) {
    ElMessage.warning(t('mediator.agreementRequired')); return
  }
  actionLoading.value = true
  try {
    await mediationApi.submitOpinion({
      meeting_id: opinionForm.value.meeting_id || selectedCase.value.id,
      opinion: opinionForm.value.opinion,
      success: opinionForm.value.success,
      agreement_content: opinionForm.value.agreement_content,
    })
    currentStep.value = 3
    ElMessage.success(opinionForm.value.success ? t('mediator.opinionSuccessMsg') : t('mediator.opinionFailedMsg'))
    // 刷新案件列表
    await loadCases()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || t('common.error'))
  } finally {
    actionLoading.value = false
  }
}

function meetingTagType(status: string) {
  const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    scheduled: '', ongoing: 'warning', ended: 'success',
  }
  return map[status] ?? ''
}

function formatMoney(v: number) { return Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2 }) }
function formatDateTime(d: string) { return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-' }
</script>

<style lang="scss" scoped>
.ws-header {
  display: flex; justify-content: space-between; align-items: center;
  h2 { font-size: 20px; font-weight: 700; margin-bottom: var(--space-1); color: var(--color-text-primary); }
  .ws-subtitle { font-size: 13px; color: var(--color-text-tertiary); }
}
.header-stats {
  display: flex; gap: 32px;
  .hstat { text-align: center; }
  .hstat-val { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .hstat-label { font-size: 12px; color: var(--color-text-tertiary); margin-top: 2px; }
}

.case-list-panel {
  padding: var(--space-4);
  .panel-title {
    font-size: 14px; font-weight: 600; margin-bottom: var(--space-3);
    display: flex; align-items: center; color: var(--color-text-primary);
  }
}
.case-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 14px; border-radius: var(--radius-md); cursor: pointer;
  border: 1px solid var(--color-border); margin-bottom: var(--space-2);
  transition: all var(--transition-fast);
  &:hover { border-color: var(--color-mediator); background: var(--color-mediator-light); }
  &.active { border-color: var(--color-mediator); background: var(--color-mediator-light); box-shadow: 0 0 0 2px rgba(250,140,22,.2); }
}
.ci-left { display: flex; flex-direction: column; gap: var(--space-1); }
.ci-number { font-family: monospace; font-weight: 600; color: var(--color-mediator); font-size: 13px; }
.ci-opponent { font-size: 12px; color: var(--color-text-secondary); }
.ci-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.ci-amount { font-size: 12px; font-weight: 500; color: var(--color-text-secondary); }

.no-cases { padding: 32px 0; }

.empty-workspace {
  display: flex; align-items: center; justify-content: center; min-height: 400px;
  .empty-icon { font-size: 80px; }
}

.case-info-card {
  .cic-header { display: flex; justify-content: space-between; align-items: flex-start; }
  .cic-number { font-size: 18px; font-weight: 700; color: var(--color-mediator); font-family: monospace; }
  .cic-opponent { font-size: 13px; color: var(--color-text-tertiary); margin-top: 2px; display: block; }
  .cic-actions { display: flex; gap: var(--space-2); }
}

.op-card {
  .op-card-title {
    display: flex; align-items: center; gap: var(--space-2);
    font-size: 15px; font-weight: 600; margin-bottom: var(--space-4); color: var(--color-text-primary);
  }
}

.meeting-info { .el-descriptions { margin-bottom: 0; } }

.form-tip { font-size: 12px; color: var(--color-text-tertiary); margin-top: var(--space-2); line-height: 1.6; }

.done-content { padding: var(--space-2) 0; }
</style>
