<template>
  <div class="mediator-dashboard">
    <!-- 欢迎卡片 + 统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="16">
        <div class="welcome-card">
          <div class="welcome-text">
            <h2>👋 {{ t('dashboard.welcome') }}，{{ authStore.user?.real_name }}</h2>
            <p>{{ welcomeMessage }}</p>
          </div>
          <div class="quick-actions">
            <el-button type="primary" @click="router.push('/mediator/cases')">
              <el-icon><Folder /></el-icon> {{ t('dashboard.viewCases') }}
            </el-button>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-cards-mini">
          <div class="mini-card" v-for="stat in miniStats" :key="stat.key">
            <div class="mini-value" :style="{ color: stat.color }">{{ stat.value }}</div>
            <div class="mini-label">{{ t(stat.label) }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 统计卡片（已被移除，统计数据移入欢迎卡片右侧迷你卡片） -->

    <el-row :gutter="20" class="content-row">
      <!-- 待办案件 -->
      <el-col :span="14">
        <div class="page-card">
          <div class="card-title">
            <span>⏰ {{ t('dashboard.todoList') }}</span>
            <el-button link type="primary" @click="router.push('/mediator/cases')">{{ t('dashboard.viewAll') }}</el-button>
          </div>
          <div v-if="pendingCases.length > 0" class="todo-list">
            <div
              v-for="item in pendingCases"
              :key="item.id"
              class="todo-item"
              @click="router.push(`/mediator/cases/${item.id}/negotiation`)"
            >
              <div class="todo-left">
                <el-tag :type="getStatusTagType(item.status)" size="small" class="todo-tag">
                  {{ getStatusLabel(item.status) }}
                </el-tag>
                <div class="todo-info">
                  <span class="todo-number">{{ item.case_number }}</span>
                  <span class="todo-opponent">{{ item.opponent_name }}</span>
                </div>
              </div>
              <div class="todo-right">
                <span class="todo-amount">USD {{ formatMoney(item.amount) }}</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
          <el-empty v-else :description="t('dashboard.noCases')" :image-size="80" />
        </div>
      </el-col>

      <!-- 案件状态分布 -->
      <el-col :span="10">
        <div class="page-card">
          <div class="card-title"><span>📊 {{ t('dashboard.caseOverview') }}</span></div>
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>

        <!-- 快捷入口 -->
        <div class="page-card" style="margin-top: 16px">
          <div class="card-title"><span>🚀 {{ t('dashboard.quickEntry') }}</span></div>
          <div class="quick-grid">
            <div class="quick-item" @click="router.push('/mediator/cases')">
              <div class="quick-icon" style="background: #fff7e6; color: #fa8c16">
                <el-icon size="24"><Folder /></el-icon>
              </div>
              <span>{{ t('dashboard.caseList') }}</span>
            </div>
            <div class="quick-item" @click="router.push('/notifications')">
              <div class="quick-icon" style="background: #e6f4ff; color: #1677ff">
                <el-icon size="24"><Bell /></el-icon>
              </div>
              <span>{{ t('nav.messages') }}</span>
            </div>
            <div class="quick-item" @click="router.push('/mediator/schedule')">
              <div class="quick-icon" style="background: #f6ffed; color: #52c41a">
                <el-icon size="24"><Calendar /></el-icon>
              </div>
              <span>{{ t('mediator.mySchedule') }}</span>
            </div>
            <div class="quick-item" @click="router.push('/mediator/profile')">
              <div class="quick-icon" style="background: #f9f0ff; color: #722ed1">
                <el-icon size="24"><User /></el-icon>
              </div>
              <span>{{ t('nav.profile') }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'
import { mediatorApi } from '@/api'

const { t, te } = useI18n()

function tr(key: string, fallback: string) {
  return te(key) ? t(key) : fallback
}

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const cases = ref<any[]>([])
const stats = ref<Record<string, number>>({})

const welcomeMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return t('dashboard.greeting.morning')
  if (hour < 18) return t('dashboard.greeting.afternoon')
  return t('dashboard.greeting.evening')
})

const statusLabelMap = computed(() => ({
  negotiating: t('case.statusMap.negotiating'),
  mediating: t('case.statusMap.mediating'),
  closed_success: t('case.statusMap.closed_success'),
  closed_fail: t('case.statusMap.closed_fail'),
  closed_failed: t('case.statusMap.closed_failed'),
  closed_negotiation: t('case.statusMap.closed_negotiation'),
  closed_mediation: t('case.statusMap.closed_mediation'),
  archived: t('case.statusMap.archived'),
}))

const miniStats = computed(() => [
  { key: 'mediating', label: 'dashboard.stats.mediating', value: stats.value.mediating || 0, color: '#fa8c16' },
  { key: 'closed', label: 'dashboard.stats.closed', value: (stats.value.closed_success || 0) + (stats.value.closed_negotiation || 0) + (stats.value.closed_mediation || 0), color: '#52c41a' },
  { key: 'total', label: 'dashboard.stats.total', value: Object.values(stats.value).reduce((a, b) => a + b, 0), color: '#8c8c8c' },
  { key: 'failed', label: 'dashboard.stats.failed', value: (stats.value.closed_fail || 0) + (stats.value.closed_failed || 0), color: '#ff4d4f' },
])

const pendingCases = computed(() =>
  cases.value.filter(c => ['negotiating', 'mediating'].includes(c.status)).slice(0, 5)
)

const chartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0, itemWidth: 12, itemHeight: 12, textStyle: { fontSize: 12 } },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
    data: Object.entries(stats.value).map(([k, v]) => ({
      name: statusLabelMap.value[k] || k, value: v,
    })).filter(d => d.value > 0),
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,.5)' } },
  }],
}))

onMounted(async () => {
  loading.value = true
  try {
    // 使用调解员专属接口，调解员无权访问企业端案件列表
    const res = await mediatorApi.getMyCases({ page: 1, page_size: 100 })
    cases.value = res.data.data.items || []
    const s: Record<string, number> = {}
    cases.value.forEach(c => { s[c.status] = (s[c.status] || 0) + 1 })
    stats.value = s
  } finally {
    loading.value = false
  }
})

function getStatusLabel(status: string) {
  return statusLabelMap.value[status] || status
}
function getStatusTagType(status: string) {
  const map: Record<string, string> = {
    negotiating: 'primary', mediating: 'warning',
    closed_success: 'success', closed_negotiation: 'success', closed_mediation: 'success',
    closed_fail: 'danger', closed_failed: 'danger', archived: 'info',
  }
  return map[status] || 'info'
}
function formatMoney(v: number) { return Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) }
</script>

<style lang="scss" scoped>
.mediator-dashboard { padding: 0; }

.welcome-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 100%);
  border-radius: var(--radius-2xl);
  padding: 28px 32px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 120px;
  z-index: 1;
  &::before {
    content: '';
    position: absolute;
    right: -30px;
    top: -30px;
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(250,140,22,0.2), transparent 70%);
  }
  &::after {
    content: '';
    position: absolute;
    left: 50%;
    bottom: -20px;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.06), transparent 70%);
  }
  h2 { font-size: 22px; font-weight: 700; margin-bottom: 8px; position: relative; z-index: 2; }
  p { font-size: 14px; opacity: 0.85; position: relative; z-index: 2; }
  .quick-actions { display: flex; gap: 12px; position: relative; z-index: 2; .el-button { border-radius: var(--radius-md); } }
}

.stat-cards-mini {
  display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); height: 100%;
}
.mini-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex; flex-direction: column; justify-content: center;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
  .mini-value { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .mini-label { font-size: 12px; color: var(--color-text-tertiary); margin-top: var(--space-1); }
}

.stat-cards-row { margin-top: var(--space-4); }
.quick-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.quick-item {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  padding: 16px 8px; border-radius: var(--radius-xl); border: 1px solid var(--color-border);
  cursor: pointer; font-size: 13px; color: var(--color-text-secondary);
  transition: all var(--transition-normal);
  &:hover { border-color: var(--color-mediator); color: var(--color-mediator); transform: translateY(-3px); box-shadow: 0 6px 20px rgba(250,140,22,0.12); }
}
.quick-icon {
  width: 48px; height: 48px; border-radius: var(--radius-xl);
  display: flex; align-items: center; justify-content: center;
}
.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex; justify-content: space-between; align-items: center;
  border-left: 4px solid;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
  .stat-value { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .stat-label { font-size: 13px; color: var(--color-text-tertiary); margin-top: var(--space-1); }
  .stat-icon { font-size: 36px; opacity: 0.3; }
}

.content-row { margin-top: var(--space-5); }
.card-title {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-4); font-weight: 600; font-size: 15px;
}
.chart { height: 260px; }

.todo-list { display: flex; flex-direction: column; gap: var(--space-2); }
.todo-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
  &:hover { border-color: var(--color-mediator); background: var(--color-mediator-light); }
}
.todo-left { display: flex; align-items: center; gap: 12px; }
.todo-tag { min-width: 64px; text-align: center; }
.todo-info { display: flex; flex-direction: column; }
.todo-number { font-size: 14px; font-weight: 600; color: var(--color-mediator); }
.todo-opponent { font-size: 12px; color: var(--color-text-tertiary); margin-top: 2px; }
.todo-right { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--color-text-tertiary); }
</style>
