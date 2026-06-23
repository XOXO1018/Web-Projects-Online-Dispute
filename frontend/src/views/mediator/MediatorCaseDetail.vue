<template>
  <div class="case-detail" v-loading="loading">
    <template v-if="caseData">
      <!-- 头部信息 -->
      <div class="page-card case-header">
        <div class="case-meta">
          <h2 class="case-number">{{ caseData.case_number }}</h2>
          <span :class="['status-tag', caseData.status]">{{ tr(`case.statusMap.${caseData.status}`, caseData.status) }}</span>
        </div>
        <div class="case-actions">
          <el-button type="primary" @click="router.push(`/mediator/cases/${caseData.id}/negotiation`)">
            <el-icon><ChatDotRound /></el-icon> {{ t('mediator.enterNegotiation') }}
          </el-button>
          <el-button v-if="caseData.status === 'mediating'" type="warning" @click="openScheduleDialog">
            <el-icon><Calendar /></el-icon> {{ t('mediator.arrangeMeeting') }}
          </el-button>
          <el-button v-if="caseData.status === 'mediating'" type="warning" plain
            @click="router.push('/mediator/mediation-workspace')">
            <el-icon><EditPen /></el-icon> {{ t('mediator.mediationWorkspace') }}
          </el-button>
          <el-button @click="router.push('/mediator/cases')">
            {{ t('common.back') }}
          </el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <!-- 基本信息 -->
        <el-col :span="14">
          <div class="page-card">
            <h3 class="section-title">{{ t('case.caseInfo') }}</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="t('case.caseNumber')">{{ caseData.case_number }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.caseStatus')">
                <span :class="['status-tag', caseData.status]">{{ tr(`case.statusMap.${caseData.status}`, caseData.status) }}</span>
              </el-descriptions-item>
              <el-descriptions-item :label="t('case.opponentName')">{{ caseData.opponent_name }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.opponentCountry')">{{ tr(`countries.${caseData.opponent_country || 'OTHER'}`, caseData.opponent_country || 'OTHER') }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.contractType')">{{ tr(`case.contractTypes.${caseData.contract_type}`, caseData.contract_type) }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.expectedMethod')">{{ tr(`case.methods.${caseData.expected_method}`, caseData.expected_method) }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.amount')">
                <strong style="color:#e63946">USD {{ formatMoney(caseData.amount) }}</strong>
              </el-descriptions-item>
              <el-descriptions-item :label="t('common.createTime')">{{ formatDate(caseData.created_at) }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.disputeDesc')" :span="2">{{ caseData.dispute_desc }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 证据列表（只读 + 预览下载） -->
          <div class="page-card" style="margin-top: 16px">
            <h3 class="section-title">{{ t('case.evidenceFiles') }}</h3>
            <el-table :data="evidences" v-loading="evLoading" size="small">
              <el-table-column prop="file_name" :label="t('case.fileName')" />
              <el-table-column :label="t('case.evidenceType')" width="100">
                <template #default="{ row }">{{ tr(`case.evidenceTypes.${row.evidence_type}`, row.evidence_type) }}</template>
              </el-table-column>
              <el-table-column :label="t('common.uploadTime')" width="140">
                <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
              </el-table-column>
              <el-table-column :label="t('common.actions')" width="140">
                <template #default="{ row }">
                  <el-button link type="primary" @click="previewEvidence(row)">
                    <el-icon><View /></el-icon> {{ t('common.preview') }}
                  </el-button>
                  <el-button link type="primary" @click="downloadEvidence(row)">
                    <el-icon><Download /></el-icon> {{ t('common.download') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!evLoading && evidences.length === 0" :description="t('common.noData')" :image-size="60" />
          </div>

          <!-- 案件状态管理 -->
          <div class="page-card" style="margin-top: 16px" v-if="caseData && ['negotiating', 'mediating'].includes(caseData.status)">
            <h3 class="section-title">{{ t('mediator.caseStatus') }}</h3>
            <div class="status-management">
              <p class="status-desc">{{ t('mediator.caseStatusDesc') }}</p>
              <div class="status-options">
                <el-button
                  v-for="opt in statusOptions"
                  :key="opt.value"
                  :type="caseData.status === opt.value ? 'warning' : 'default'"
                  plain
                  @click="changeCaseStatus(opt.value)"
                  :disabled="caseData.status === opt.value"
                >
                  <el-icon><component :is="opt.icon" /></el-icon>
                  {{ opt.label }}
                </el-button>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 时间轴 -->
        <el-col :span="10">
          <div class="page-card timeline-card">
            <h3 class="section-title">{{ t('case.caseTimeline') }}</h3>
            <div class="timeline">
              <div v-for="(item, idx) in caseData.timeline" :key="idx" class="timeline-item">
                <div class="tl-action">{{ item.action || item.event }}</div>
                <div class="tl-meta">{{ item.operator }} · {{ formatDate(item.time) }}</div>
              </div>
            </div>
            <el-empty v-if="!caseData.timeline?.length" :description="t('case.noTimeline')" :image-size="60" />
          </div>
        </el-col>
      </el-row>
    </template>

    <!-- 安排会议弹窗 -->
    <el-dialog
      v-model="scheduleDialogVisible"
      :title="t('mediator.arrangeMeeting')"
      width="420px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item :label="t('mediator.meetingTime')" required>
          <el-date-picker
            v-model="scheduledTime"
            type="datetime"
            :placeholder="t('mediator.selectMeetingTime')"
            :disabled-date="disablePastDate"
            style="width: 100%"
            value-format="YYYY-MM-DDTHH:mm:ss"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
        <div class="schedule-tip">
          <el-icon color="#fa8c16" style="margin-right: 6px"><InfoFilled /></el-icon>
          {{ t('mediator.scheduleTip') }}
        </div>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="schedulingMeeting" @click="confirmSchedule">
          {{ t('mediator.confirmSchedule') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { caseApi, evidenceApi, mediationApi } from '@/api'
import { ChatDotRound, Calendar, EditPen, InfoFilled, View, Download } from '@element-plus/icons-vue'

const { t, te } = useI18n()
function tr(key: string, fallback: string) { return te(key) ? t(key) : fallback }

const router = useRouter()
const route = useRoute()
const caseId = Number(route.params.id)

const loading = ref(false)
const evLoading = ref(false)
const caseData = ref<any>(null)
const evidences = ref<any[]>([])

// 安排会议弹窗
const scheduleDialogVisible = ref(false)
const schedulingMeeting = ref(false)
const scheduledTime = ref('')

onMounted(async () => {
  await loadCase()
  await loadEvidences()
})

async function loadCase() {
  loading.value = true
  try {
    const res = await caseApi.getDetail(caseId)
    caseData.value = res.data.data
  } finally {
    loading.value = false
  }
}

async function loadEvidences() {
  evLoading.value = true
  try {
    const res = await evidenceApi.list(caseId)
    evidences.value = res.data.data || []
  } finally {
    evLoading.value = false
  }
}

function openScheduleDialog() {
  scheduledTime.value = ''
  scheduleDialogVisible.value = true
}

function disablePastDate(time: Date) { return time.getTime() < Date.now() }

async function confirmSchedule() {
  if (!scheduledTime.value) { ElMessage.warning(t('mediator.selectMeetingTime')); return }
  schedulingMeeting.value = true
  try {
    await mediationApi.scheduleMeeting({
      request_id: caseId,
      scheduled_time: scheduledTime.value,
    })
    ElMessage.success(t('mediator.meetingScheduledSuccess'))
    scheduleDialogVisible.value = false
    await loadCase()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || t('common.error'))
  } finally {
    schedulingMeeting.value = false
  }
}

function previewEvidence(ev: any) {
  const url = ev.file_url || ev.file_path || ''
  if (!url) { ElMessage.warning(t('common.noFile')); return }
  // 图片类型直接预览，其他类型新窗口打开
  if (/\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(ev.file_name || url)) {
    window.open(url, '_blank')
  } else {
    window.open(url, '_blank')
  }
}

function downloadEvidence(ev: any) {
  const url = ev.file_url || ev.file_path || ''
  if (!url) { ElMessage.warning(t('common.noFile')); return }
  const a = document.createElement('a')
  a.href = url
  a.download = ev.file_name || 'download'
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const statusOptions = computed(() => [
  { value: 'negotiating', label: t('case.statusMap.negotiating'), icon: 'ChatDotRound' },
  { value: 'mediating', label: t('case.statusMap.mediating'), icon: 'VideoCamera' },
  { value: 'closed_success', label: t('case.statusMap.closed_success'), icon: 'CircleCheck' },
  { value: 'closed_failed', label: t('case.statusMap.closed_failed'), icon: 'CircleClose' },
])

async function changeCaseStatus(newStatus: string) {
  if (newStatus === caseData.value?.status) return
  if (['closed_success', 'closed_failed'].includes(newStatus)) {
    try {
      await ElMessageBox.confirm(
        t('mediator.confirmCloseCase'),
        t('common.hint'),
        { type: 'warning', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
      )
    } catch { return }
  }
  try {
    await caseApi.updateStatus(caseId, { status: newStatus })
    ElMessage.success(t('common.success'))
    await loadCase()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}

function formatMoney(v: number) { return Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) }
function formatDate(d: string) { return d ? dayjs(d).format('MM-DD HH:mm') : '-' }
</script>

<style lang="scss" scoped>
.case-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4);
}
.case-meta { display: flex; align-items: center; gap: 12px; }
.case-number { font-size: 20px; font-weight: 700; color: var(--color-mediator); }
.case-actions { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: var(--space-4); color: var(--color-text-primary); }

:deep(.el-descriptions) {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.timeline-card { height: fit-content; }
.timeline { padding: var(--space-2) 0; }
.timeline-item {
  position: relative; padding-left: 20px; padding-bottom: var(--space-4);
  &::before { content: ''; position: absolute; left: 5px; top: 10px; bottom: -2px; width: 2px; background: var(--color-border); }
  &::after { content: ''; position: absolute; left: 1px; top: 6px; width: 10px; height: 10px; border-radius: 50%; background: var(--color-mediator); border: 2px solid var(--color-bg-card); box-shadow: 0 0 0 2px var(--color-mediator); }
  &:last-child::before { display: none; }
  .tl-action { font-size: 13px; font-weight: 500; margin-bottom: var(--space-1); }
  .tl-meta { font-size: 12px; color: var(--color-text-tertiary); }
}
.schedule-tip {
  display: flex; align-items: flex-start;
  background: var(--color-mediator-light); border-radius: var(--radius-md); padding: 10px 14px;
  font-size: 12px; color: var(--color-text-tertiary); line-height: 1.6; margin-top: var(--space-2);
}
.status-management {
  .status-desc { font-size: 13px; color: var(--color-text-tertiary); margin-bottom: var(--space-3); }
  .status-options { display: flex; gap: var(--space-2); flex-wrap: wrap; }
}
</style>
