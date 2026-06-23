<template>
  <div class="mediation-view" v-loading="loading">
    <!-- 推荐调解员 -->
    <div v-if="showMediatorSelection" class="page-card">
      <h3>{{ t('mediation.selectMediator') }}</h3>
      <p class="hint">{{ t('mediation.recommended') }}</p>
      <el-row :gutter="20" style="margin-top: 16px">
        <el-col :span="8" v-for="m in mediators" :key="m.id">
          <div :class="['mediator-card', { selected: selectedMediatorId === m.id }]" @click="selectedMediatorId = m.id">
            <!-- 调解员卡片：兼容生产字段(real_name/mediator_domain/case_count/intro) 和 demo 字段(name/specialty/cases_count/bio) -->
          <div class="mediator-avatar">{{ (m.real_name || m.name || '?')[0] }}</div>
            <h4>{{ m.real_name || m.name }}</h4>
            <div class="mediator-domain">{{ m.mediator_domain || m.domain || m.specialty }}</div>
            <el-rate :model-value="m.rating" disabled show-score score-template="{value}" size="small" />
            <div class="mediator-stats">
              <span>{{ t('mediation.successRate') }}：{{ m.success_rate }}%</span>
              <span>{{ t('mediation.casesCount') }}：{{ m.case_count || m.cases_count }}</span>
            </div>
            <p class="mediator-intro">{{ m.intro || m.bio }}</p>
          </div>
        </el-col>
      </el-row>
      <div style="margin-top: 16px; text-align: right">
        <el-button type="primary" @click="doSelectMediator" :disabled="!selectedMediatorId" :loading="actionLoading">
          {{ t('mediation.confirmSelect') }}
        </el-button>
      </div>
    </div>

    <!-- 调解进行中 -->
    <div v-else>
      <div class="page-card meeting-info">
        <h3>{{ t('mediation.meetingInfo') }}</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item :label="t('mediation.mediationStatus')">
            <el-tag type="warning">{{ t('case.statusMap.mediating') }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('mediation.meetingTime')" v-if="meetingInfo">
            {{ formatDate(meetingInfo.scheduled_time) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('mediation.meetingStatus')" v-if="meetingInfo">
            {{ meetingStatusMap[meetingInfo.status] }}
          </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 16px" v-if="meetingInfo">
          <el-button type="primary" @click="joinMeeting">{{ t('mediation.enterMeetingRoom') }}</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { mediationApi, caseApi } from '@/api'
import { meetingApi } from '@/api'
import dayjs from 'dayjs'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const caseId = Number(route.params.id)
// 调解申请ID：优先从路由 query 参数获取，fallback 到案件ID（演示模式下允许）
const mediationRequestId = ref<number | null>(
  route.query.request_id ? Number(route.query.request_id) : null
)

const loading = ref(false)
const actionLoading = ref(false)
const mediators = ref<any[]>([])
const selectedMediatorId = ref<number | null>(null)
const showMediatorSelection = ref(true)
const meetingInfo = ref<any>(null)

const meetingStatusMap = computed(() => ({
  scheduled: t('mediation.meetingStatusMap.scheduled'),
  ongoing: t('mediation.meetingStatusMap.ongoing'),
  ended: t('mediation.meetingStatusMap.ended'),
}))

onMounted(async () => {
  loading.value = true
  try {
    // 加载推荐调解员
    const res = await mediationApi.recommendMediators(caseId)
    mediators.value = res.data.data || []

    // 加载该案件的会议信息（如已安排会议则不显示调解员选择）
    try {
      const meetingRes = await meetingApi.getCaseMeetings(caseId)
      const meetings = meetingRes.data.data || []
      if (meetings.length > 0) {
        // 取最新一条会议
        meetingInfo.value = meetings[0]
        showMediatorSelection.value = false
      }
    } catch {}
  } finally {
    loading.value = false
  }
})

async function doSelectMediator() {
  if (!selectedMediatorId.value) return
  actionLoading.value = true
  try {
    // request_id 为 null 时传 case_id 作为 fallback（demo 模式兼容）
    const res = await mediationApi.selectMediator({
      request_id: mediationRequestId.value ?? caseId,
      mediator_id: selectedMediatorId.value,
    })
    ElMessage.success(t('mediation.mediatorSelected'))
    showMediatorSelection.value = false
  } finally {
    actionLoading.value = false
  }
}

function joinMeeting() {
  if (meetingInfo.value?.channel_name) {
    router.push(`/meeting/${meetingInfo.value.channel_name}?meeting_id=${meetingInfo.value.id}&case_id=${caseId}`)
  }
}

function formatDate(d: string) {
  return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.meeting-info { margin-bottom: var(--space-4); h3 { font-size: 16px; font-weight: 600; margin-bottom: var(--space-4); color: var(--color-text-primary); } }
.hint { color: var(--color-text-tertiary); font-size: 14px; }
.mediator-card {
  border: 2px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: var(--space-4);
  &:hover { border-color: var(--color-primary); box-shadow: 0 4px 12px rgba(22,119,255,0.15); transform: translateY(-2px); }
  &.selected { border-color: var(--color-primary); background: var(--color-primary-bg); }
  .mediator-avatar {
    width: 56px; height: 56px; border-radius: 50%; background: var(--color-primary);
    color: white; font-size: 24px; font-weight: 700;
    display: flex; align-items: center; justify-content: center; margin: 0 auto 12px;
  }
  h4 { font-size: 16px; font-weight: 600; margin-bottom: var(--space-1); color: var(--color-text-primary); }
  .mediator-domain { font-size: 12px; color: var(--color-text-tertiary); margin-bottom: var(--space-2); }
  .mediator-stats {
    display: flex; justify-content: center; gap: 16px;
    font-size: 12px; color: var(--color-text-secondary); margin: var(--space-2) 0;
  }
  .mediator-intro { font-size: 12px; color: var(--color-text-tertiary); text-align: left; line-height: 1.6; }
}
</style>
