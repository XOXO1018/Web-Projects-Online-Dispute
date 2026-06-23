<template>
  <div class="admin-dashboard" v-loading="loading">
    <!-- 管理员欢迎 + 核心指标 -->
    <el-row :gutter="20">
      <el-col :span="18">
        <div class="admin-welcome">
          <div class="welcome-text">
            <h2>{{ t('admin.dashboard') }}</h2>
            <p>{{ t('auth.loginSubtitle') }}</p>
          </div>
          <div class="admin-actions">
            <el-button @click="router.push('/admin/enterprises')">
              <el-icon><OfficeBuilding /></el-icon> {{ t('admin.enterprises') }}
            </el-button>
            <el-button @click="router.push('/admin/mediators')">
              <el-icon><Avatar /></el-icon> {{ t('admin.mediators') }}
            </el-button>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="time-card">
          <div class="time-value">{{ currentTime }}</div>
          <div class="time-date">{{ currentDate }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 核心统计卡片 -->
    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="4" v-for="item in coreStats" :key="item.label">
        <div class="core-card" :style="{ borderTopColor: item.color }">
          <div class="core-value" :style="{ color: item.color }">{{ item.value }}</div>
          <div class="core-label">{{ item.label }}</div>
          <div class="core-trend" :class="item.trend > 0 ? 'up' : 'down'" v-if="item.trend">
            <el-icon><Top v-if="item.trend > 0" /><Bottom v-else /></el-icon>
            {{ Math.abs(item.trend) }}%
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 待审核企业 -->
      <el-col :span="12">
        <div class="page-card">
          <div class="card-title">
            <span>{{ t('admin.stats.pendingAudit') }}</span>
            <el-button link type="primary" @click="router.push('/admin/enterprises')">
              {{ t('dashboard.viewAll') }} <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <el-table :data="pendingEnterprises" size="small" v-loading="entLoading">
            <el-table-column prop="name" :label="t('auth.enterpriseName')" min-width="140" />
            <el-table-column prop="credit_code" :label="t('auth.creditCode')" width="180">
              <template #default="{ row }">
                <span class="mono-text">{{ row.credit_code }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="contact_email" :label="t('profile.email')" min-width="140" />
            <el-table-column :label="t('common.actions')" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="success" @click="audit(row.id, 'approved')">{{ t('admin.actions.approve') }}</el-button>
                <el-button link type="danger" @click="audit(row.id, 'rejected')">{{ t('admin.actions.reject') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="pendingEnterprises.length === 0 && !entLoading" :description="t('admin.stats.pendingAudit')" :image-size="60" />
        </div>
      </el-col>

      <!-- 案件状态分布 -->
      <el-col :span="12">
        <div class="page-card">
          <div class="card-title"><span>{{ t('dashboard.caseOverview') }}</span></div>
          <v-chart class="admin-chart" :option="caseChartOption" autoresize />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 最近案件 -->
      <el-col :span="12">
        <div class="page-card">
          <div class="card-title">
            <span>{{ t('dashboard.recentCases') }}</span>
            <el-button link type="primary" @click="router.push('/admin/cases')">
              {{ t('dashboard.viewAll') }} <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <el-table :data="recentCases" size="small" v-loading="casesLoading">
            <el-table-column prop="case_number" :label="t('case.caseNumber')" width="180">
              <template #default="{ row }">
                <span class="mono-text primary-text">{{ row.case_number }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="opponent_name" :label="t('case.opponentName')" min-width="120" />
            <el-table-column :label="t('case.amountUsd')" width="120" align="right">
              <template #default="{ row }">${{ Number(row.amount || 0).toLocaleString() }}</template>
            </el-table-column>
            <el-table-column :label="t('common.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small">{{ statusMap[row.status] }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <!-- 快捷导航 -->
      <el-col :span="12">
        <div class="page-card">
          <div class="card-title"><span>{{ t('dashboard.quickEntry') }}</span></div>
          <div class="nav-grid">
            <div class="nav-item" @click="router.push('/admin/enterprises')">
              <div class="nav-icon" style="background: #e6f4ff; color: #1677ff">
                <el-icon size="28"><OfficeBuilding /></el-icon>
              </div>
              <div class="nav-text">
                <span class="nav-label">{{ t('admin.enterprises') }}</span>
                <span class="nav-desc">{{ t('admin.quickNav.enterprisesDesc') }}</span>
              </div>
              <el-icon class="nav-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="nav-item" @click="router.push('/admin/mediators')">
              <div class="nav-icon" style="background: #f6ffed; color: #52c41a">
                <el-icon size="28"><Avatar /></el-icon>
              </div>
              <div class="nav-text">
                <span class="nav-label">{{ t('admin.mediators') }}</span>
                <span class="nav-desc">{{ t('admin.quickNav.mediatorsDesc') }}</span>
              </div>
              <el-icon class="nav-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="nav-item" @click="router.push('/admin/cases')">
              <div class="nav-icon" style="background: #fff7e6; color: #fa8c16">
                <el-icon size="28"><Folder /></el-icon>
              </div>
              <div class="nav-text">
                <span class="nav-label">{{ t('admin.cases') }}</span>
                <span class="nav-desc">{{ t('admin.quickNav.casesDesc') }}</span>
              </div>
              <el-icon class="nav-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="nav-item" @click="router.push('/admin/users')">
              <div class="nav-icon" style="background: #f9f0ff; color: #722ed1">
                <el-icon size="28"><User /></el-icon>
              </div>
              <div class="nav-text">
                <span class="nav-label">{{ t('admin.users') }}</span>
                <span class="nav-desc">{{ t('admin.quickNav.usersDesc') }}</span>
              </div>
              <el-icon class="nav-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="nav-item" @click="router.push('/admin/settings')">
              <div class="nav-icon" style="background: #fff1f0; color: #ff4d4f">
                <el-icon size="28"><Setting /></el-icon>
              </div>
              <div class="nav-text">
                <span class="nav-label">{{ t('admin.settings') }}</span>
                <span class="nav-desc">{{ t('admin.quickNav.settingsDesc') }}</span>
              </div>
              <el-icon class="nav-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'
import { adminApi } from '@/api'

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const { t, locale } = useI18n()
const loading = ref(false)
const entLoading = ref(false)
const casesLoading = ref(false)
const pendingEnterprises = ref<any[]>([])
const recentCases = ref<any[]>([])

// 时钟
const currentTime = ref('')
const currentDate = ref('')
let clockTimer: any = null

function updateClock() {
  currentTime.value = dayjs().format('HH:mm:ss')
  currentDate.value = locale.value === 'zh-CN'
    ? dayjs().format('YYYY年MM月DD日 dddd')
    : dayjs().format('YYYY-MM-DD dddd')
}

const coreStats = ref<any[]>([])

// 核心统计卡片 i18n 标签映射
function buildCoreStats(d: any) {
  return [
    { label: t('admin.stats.totalUsers'), value: d.total_users || 0, color: '#1677ff', trend: 12 },
    { label: t('admin.stats.totalEnterprises'), value: d.total_enterprises || 0, color: '#52c41a', trend: 8 },
    { label: t('admin.stats.totalCases'), value: d.total_cases || 0, color: '#fa8c16', trend: 15 },
    { label: t('admin.stats.activeMediators'), value: d.total_mediators || 0, color: '#722ed1', trend: 5 },
    { label: t('admin.stats.pendingAudit'), value: d.pending_audit || 0, color: '#ff4d4f', trend: -10 },
    { label: t('admin.stats.activeCases'), value: d.active_cases || 0, color: '#13c2c2', trend: 3 },
  ]
}

const statusMap = computed(() => ({
  negotiating: t('case.statusMap.negotiating'), mediating: t('case.statusMap.mediating'),
  closed_negotiation: t('case.statusMap.closed_negotiation'), closed_mediation: t('case.statusMap.closed_mediation'),
  closed_failed: t('case.statusMap.closed_failed'), closed_fail: t('case.statusMap.closed_fail'),
  closed_success: t('case.statusMap.closed_success'), archived: t('case.statusMap.archived'),
}))
const statusTagType = (s: string) =>
  ({ negotiating: 'primary', mediating: 'warning', closed_negotiation: 'success', closed_mediation: 'success', closed_success: 'success', closed_failed: 'danger', closed_fail: 'danger', archived: 'info' }[s] || 'info')

const caseChartOption = ref<any>({})

onMounted(async () => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  loading.value = true
  try {
    const [dashRes, entRes, caseRes] = await Promise.all([
      adminApi.dashboard(),
      adminApi.listEnterprises({ audit_status: 'pending', keyword: '', page: 1, page_size: 10 }),
      adminApi.listAllCases({ page: 1, page_size: 10 }),
    ])
    const d = dashRes.data.data
    coreStats.value = buildCoreStats(d)
    pendingEnterprises.value = entRes.data.data.items || []
    recentCases.value = caseRes.data.data.items || []

    // 案件图表
    const caseStats: Record<string, number> = {}
    recentCases.value.forEach((c: any) => { caseStats[c.status] = (caseStats[c.status] || 0) + 1 })
    caseChartOption.value = {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0, itemWidth: 12, itemHeight: 12, textStyle: { fontSize: 12 } },
      series: [{
        type: 'pie', radius: ['40%', '65%'], center: ['50%', '45%'],
        data: Object.entries(caseStats).map(([k, v]) => ({ name: statusMap.value[k] || k, value: v })),
      }],
    }
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
})

async function audit(id: number, action: string) {
  const actionText = action === 'approved' ? t('admin.actions.approve') : t('admin.actions.reject')
  try {
    await ElMessageBox.confirm(
      t('admin.confirmAudit', { action: actionText }),
      t('common.hint'),
      { type: 'warning', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await adminApi.auditEnterprise(id, action === 'approved' ? 'approve' : 'reject')
    ElMessage.success(t('common.success'))
    pendingEnterprises.value = pendingEnterprises.value.filter(e => e.id !== id)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}
</script>

<style lang="scss" scoped>
.admin-dashboard { padding: 0; }

.admin-welcome {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 50%, #0d1b2a 100%);
  border-radius: var(--radius-2xl);
  padding: 28px 32px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
  &::before {
    content: '';
    position: absolute;
    right: -40px;
    top: -40px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(22,119,255,0.2), transparent 70%);
  }
  &::after {
    content: '';
    position: absolute;
    right: 60px;
    bottom: -20px;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.08), transparent 70%);
  }
  h2 { font-size: 22px; font-weight: 700; margin-bottom: 8px; position: relative; z-index: 2; }
  p { font-size: 14px; opacity: 0.7; position: relative; z-index: 2; }
  .admin-actions { display: flex; gap: 12px; position: relative; z-index: 2; }
}

.time-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: 20px 24px;
  text-align: center;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
  .time-value { font-size: 28px; font-weight: 700; color: #0d1b2a; font-family: monospace; font-variant-numeric: tabular-nums; }
  .time-date { font-size: 12px; color: var(--color-text-tertiary); margin-top: var(--space-1); }
}

.core-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  text-align: center;
  border-top: 3px solid;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
  .core-value { font-size: 30px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .core-label { font-size: 12px; color: var(--color-text-tertiary); margin-top: var(--space-1); }
  .core-trend {
    font-size: 12px; margin-top: 6px;
    &.up { color: var(--color-success); }
    &.down { color: var(--color-danger); }
  }
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  font-weight: 600;
  font-size: 15px;
}
.admin-chart { height: 260px; }

.nav-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
  &:hover {
    border-color: var(--color-primary);
    background: var(--color-primary-bg);
    transform: translateX(4px);
  }
}
.nav-icon {
  width: 52px; height: 52px; border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.nav-text { flex: 1; display: flex; flex-direction: column; }
.nav-label { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.nav-desc { font-size: 12px; color: var(--color-text-tertiary); margin-top: 2px; }
.nav-arrow { color: var(--color-text-quaternary); transition: transform var(--transition-fast); }
.nav-item:hover .nav-arrow { transform: translateX(4px); }
.mono-text { font-family: monospace; font-size: 12px; }
.primary-text { color: var(--color-primary); font-weight: 600; }
</style>
