<template>
  <div class="schedule-view">
    <div class="page-card">
      <div class="card-header">
        <h3>📅 {{ t('mediator.scheduleMeeting') }}</h3>
        <p class="subtitle">{{ t('mediator.scheduleSubtitle') }}</p>
      </div>

      <!-- 可安排会议的案件列表 -->
      <el-table :data="mediatingCases" v-loading="loading" stripe style="margin-top: 16px">
        <el-table-column prop="case_number" :label="t('case.caseNumber')" width="200">
          <template #default="{ row }">
            <span class="case-number">{{ row.case_number }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="opponent_name" :label="t('case.opponentName')" min-width="150" />
        <el-table-column :label="t('case.amountUsd')" width="150" align="right">
          <template #default="{ row }">
            <span class="amount">$ {{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="110">
          <template #default="{ row }">
            <el-tag type="warning" size="small">{{ tr(`case.statusMap.${row.status}`, row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('mediator.meetingStatus')" width="130">
          <template #default="{ row }">
            <el-tag v-if="row._meetingScheduled" type="success" size="small">{{ t('mediator.meetingScheduled') }}</el-tag>
            <el-tag v-else type="info" size="small">{{ t('mediator.notScheduled') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/mediator/cases/${row.id}`)">
              {{ t('common.detail') }}
            </el-button>
            <el-button link type="warning" @click="openScheduleDialog(row)">
              {{ t('mediator.arrangeMeeting') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && mediatingCases.length === 0"
        :description="t('mediator.noMediatingCases')" :image-size="100" />
    </div>

    <!-- 已安排会议列表 -->
    <div class="page-card" style="margin-top: 20px">
      <div class="card-header">
        <h3>📋 {{ t('mediator.scheduledMeetings') }}</h3>
      </div>
      <el-timeline v-if="scheduledMeetings.length > 0" style="margin-top: 16px; padding-left: 8px">
        <el-timeline-item
          v-for="m in scheduledMeetings" :key="m.id"
          :timestamp="formatDateTime(m.scheduled_time)"
          placement="top"
          :type="meetingTimelineType(m.status)"
        >
          <div class="timeline-meeting-card">
            <div class="tl-top">
              <span class="tl-case">{{ m.case_number }}</span>
              <el-tag :type="meetingTagType(m.status)" size="small">
                {{ tr(`mediation.meetingStatusMap.${m.status}`, m.status) }}
              </el-tag>
            </div>
            <div class="tl-detail">
              <span>{{ t('case.opponentName') }}：{{ m.opponent_name }}</span>
              <span style="margin-left: 24px">{{ t('case.amountUsd') }}：$ {{ formatMoney(m.amount) }}</span>
            </div>
            <div class="tl-actions" v-if="m.status !== 'ended'">
              <el-button type="primary" size="small" @click="joinMeeting(m)">
                <el-icon><VideoCamera /></el-icon> {{ t('mediation.enterMeetingRoom') }}
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else :description="t('mediator.noScheduledMeetings')" :image-size="80" />
    </div>

    <!-- 安排会议弹窗 -->
    <el-dialog
      v-model="scheduleDialogVisible"
      :title="t('mediator.arrangeMeeting')"
      width="480px"
      destroy-on-close
    >
      <div v-if="selectedCase" class="schedule-dialog-body">
        <!-- 案件摘要 -->
        <div class="case-summary">
          <div class="cs-row">
            <span class="cs-label">{{ t('case.caseNumber') }}</span>
            <span class="cs-value case-number">{{ selectedCase.case_number }}</span>
          </div>
          <div class="cs-row">
            <span class="cs-label">{{ t('case.opponentName') }}</span>
            <span class="cs-value">{{ selectedCase.opponent_name }}</span>
          </div>
          <div class="cs-row">
            <span class="cs-label">{{ t('case.amountUsd') }}</span>
            <span class="cs-value">$ {{ formatMoney(selectedCase.amount) }}</span>
          </div>
        </div>

        <el-divider />

        <el-form :model="scheduleForm" label-position="top" :rules="scheduleRules" ref="scheduleFormRef">
          <el-form-item :label="t('mediator.meetingTime')" prop="scheduled_time">
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
          <el-form-item :label="t('mediator.meetingNote')" prop="note">
            <el-input
              v-model="scheduleForm.note"
              type="textarea"
              :rows="3"
              :placeholder="t('mediator.meetingNotePlaceholder')"
            />
          </el-form-item>
        </el-form>

        <div class="schedule-tip">
          <el-icon color="#fa8c16"><InfoFilled /></el-icon>
          <span>{{ t('mediator.scheduleTip') }}</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="scheduleDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="scheduling" @click="confirmSchedule">
          {{ t('mediator.confirmSchedule') }}
        </el-button>
      </template>
    </el-dialog>
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
import { meetingApi } from '@/api'
import { VideoCamera, InfoFilled } from '@element-plus/icons-vue'

const { t, te } = useI18n()
const router = useRouter()
function tr(key: string, fallback: string) { return te(key) ? t(key) : fallback }

const loading = ref(false)
const scheduling = ref(false)
const cases = ref<any[]>([])
const scheduledMeetings = ref<any[]>([])
const scheduleDialogVisible = ref(false)
const selectedCase = ref<any>(null)
const scheduleFormRef = ref<FormInstance>()

const scheduleForm = ref({
  scheduled_time: '',
  note: '',
})

const scheduleRules = {
  scheduled_time: [{ required: true, message: t('mediator.selectMeetingTime'), trigger: 'change' }],
}

// 只显示调解中的案件
const mediatingCases = computed(() =>
  cases.value.filter(c => c.status === 'mediating')
)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    // 加载调解中的案件（用于安排会议）
    const res = await mediatorApi.getMyCases({ page: 1, page_size: 50 })
    cases.value = res.data.data?.items || res.data.data || []

    // 从后端真实获取已排期会议列表
    const meetingRes = await mediatorApi.getMyMeetings()
    const rawMeetings = meetingRes.data.data || []
    scheduledMeetings.value = rawMeetings.map((m: any) => ({
      id: m.id,
      case_number: m.case_number,
      scheduled_time: m.scheduled_time,
      status: m.status || 'scheduled',
      channel_name: m.channel_name,
      meeting_id: m.id,
      case_id: m.case_id,
      note: m.note,
    }))
  } finally {
    loading.value = false
  }
}

function openScheduleDialog(row: any) {
  selectedCase.value = row
  scheduleForm.value = { scheduled_time: '', note: '' }
  scheduleDialogVisible.value = true
}

function disablePastDate(time: Date) {
  return time.getTime() < Date.now()
}

async function confirmSchedule() {
  if (!scheduleFormRef.value) return
  await scheduleFormRef.value.validate(async (valid) => {
    if (!valid) return
    scheduling.value = true
    try {
      // 先获取该案件的 mediation request_id
      // 直接用 case_id 作为 request_id（demo 模式兼容）
      await mediationApi.scheduleMeeting({
        request_id: selectedCase.value.id,
        scheduled_time: scheduleForm.value.scheduled_time,
      })
      ElMessage.success(t('mediator.meetingScheduledSuccess'))
      scheduleDialogVisible.value = false
      await loadData()
    } catch (e: any) {
      const msg = e?.response?.data?.message || t('common.error')
      ElMessage.error(msg)
    } finally {
      scheduling.value = false
    }
  })
}

function joinMeeting(m: any) {
  if (m.channel_name) {
    router.push(`/mediator/meeting/${m.channel_name}?meeting_id=${m.meeting_id}&case_id=${m.case_id}`)
  } else {
    ElMessage.warning(t('mediator.noChannelName'))
  }
}

function meetingTimelineType(status: string) {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    scheduled: 'primary', ongoing: 'warning', ended: 'success',
  }
  return map[status] || 'info'
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
.card-header {
  h3 { font-size: 16px; font-weight: 600; margin-bottom: var(--space-1); color: var(--color-text-primary); }
  .subtitle { font-size: 13px; color: var(--color-text-tertiary); }
}
.case-number { font-family: monospace; font-weight: 600; color: var(--color-mediator); }
.amount { font-weight: 500; color: var(--color-text-secondary); }

.timeline-meeting-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  transition: box-shadow var(--transition-fast);
  &:hover { box-shadow: var(--shadow-card); }
  .tl-top {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2);
  }
  .tl-case { font-weight: 600; font-size: 14px; color: var(--color-mediator); font-family: monospace; }
  .tl-detail { font-size: 13px; color: var(--color-text-secondary); margin-bottom: 10px; }
  .tl-actions { display: flex; gap: var(--space-2); }
}

.schedule-dialog-body {
  .case-summary {
    background: #fffbe6;
    border: 1px solid #ffe58f;
    border-radius: var(--radius-lg);
    padding: 14px 16px;
    margin-bottom: var(--space-4);
  }
  .cs-row {
    display: flex; gap: 12px; margin-bottom: 6px; font-size: 13px;
    &:last-child { margin-bottom: 0; }
  }
  .cs-label { color: var(--color-text-tertiary); width: 80px; flex-shrink: 0; }
  .cs-value { font-weight: 500; }
}

.schedule-tip {
  display: flex; align-items: flex-start; gap: var(--space-2);
  background: var(--color-mediator-light); border-radius: var(--radius-md); padding: 10px 14px;
  font-size: 12px; color: var(--color-text-tertiary); line-height: 1.6; margin-top: var(--space-2);
}
</style>
