<template>
  <div class="enterprise-dashboard">
    <!-- 欢迎卡片 + 统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="16">
        <div class="welcome-card">
          <div class="welcome-text">
            <h2>👋 {{ t('dashboard.welcome') }}，{{ authStore.user?.real_name }}</h2>
            <p>{{ welcomeMessage }}</p>
          </div>
          <div class="quick-actions">
            <el-button type="primary" @click="router.push('/cases/create')">
              <el-icon><Plus /></el-icon> {{ t('dashboard.newCase') }}
            </el-button>
            <el-button @click="router.push('/cases')">
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

    <!-- 统计卡片已移除，统计数据移入欢迎卡片右侧迷你卡片 -->

    <el-row :gutter="20" class="content-row">
      <!-- 待办事项 -->
      <el-col :span="14">
        <div class="page-card">
          <div class="card-title">
            <span>⏰ {{ t('dashboard.todoList') }}</span>
            <el-button link type="primary" @click="router.push('/cases')">{{ t('dashboard.viewAll') }}</el-button>
          </div>
          <div v-if="pendingCases.length > 0" class="todo-list">
            <div
              v-for="item in pendingCases"
              :key="item.id"
              class="todo-item"
              @click="router.push(`/cases/${item.id}`)"
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
      </el-col>
    </el-row>

    <!-- 最近案件 + 快捷入口 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <div class="page-card">
          <div class="card-title">
            <span>📋 {{ t('dashboard.recentCases') }}</span>
            <el-button type="primary" size="small" @click="router.push('/cases/create')">
              <el-icon><Plus /></el-icon> {{ t('dashboard.newCase') }}
            </el-button>
          </div>
          <el-table :data="recentCases" v-loading="loading" stripe>
            <el-table-column prop="case_number" :label="t('case.caseNumber')" width="200">
              <template #default="{ row }">
                <span class="case-number">{{ row.case_number }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="opponent_name" :label="t('case.opponentName')" />
            <el-table-column prop="opponent_country" :label="t('case.opponentCountry')" width="100">
              <template #default="{ row }">{{ tr(`countries.${row.opponent_country || 'OTHER'}`, row.opponent_country || 'OTHER') }}</template>
            </el-table-column>
            <el-table-column :label="t('dashboard.amountUsd')" width="140" align="right">
              <template #default="{ row }">
                <span class="amount">{{ formatMoney(row.amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.status')" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.createTime')" width="160">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push(`/cases/${row.id}`)">{{ t('case.actions.detail') }}</el-button>
                <el-button
                  v-if="row.status === 'negotiating'"
                  link type="warning"
                  @click="router.push(`/cases/${row.id}/negotiation`)"
                >{{ t('case.actions.negotiate') }}</el-button>
                <el-button
                  v-if="row.status === 'mediating'"
                  link type="success"
                  @click="router.push(`/cases/${row.id}/mediation`)"
                >{{ t('case.actions.mediate') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <!-- 快捷入口 + 企业信息 -->
      <el-col :span="8">
        <div class="page-card">
          <div class="card-title"><span>🚀 {{ t('dashboard.quickEntry') }}</span></div>
          <div class="quick-grid">
            <div class="quick-item" @click="router.push('/cases/create')">
              <div class="quick-icon" style="background: #e6f4ff; color: #1677ff">
                <el-icon size="24"><Plus /></el-icon>
              </div>
              <span>{{ t('dashboard.createCase') }}</span>
            </div>
            <div class="quick-item" @click="router.push('/cases')">
              <div class="quick-icon" style="background: #f6ffed; color: #52c41a">
                <el-icon size="24"><Folder /></el-icon>
              </div>
              <span>{{ t('dashboard.caseList') }}</span>
            </div>
            <div class="quick-item" @click="router.push('/notifications')">
              <div class="quick-icon" style="background: #fff7e6; color: #fa8c16">
                <el-icon size="24"><Bell /></el-icon>
              </div>
              <span>{{ t('nav.messages') }}</span>
            </div>
            <div class="quick-item" @click="router.push('/profile')">
              <div class="quick-icon" style="background: #f9f0ff; color: #722ed1">
                <el-icon size="24"><User /></el-icon>
              </div>
              <span>{{ t('nav.profile') }}</span>
            </div>
          </div>
        </div>

        <div class="page-card" style="margin-top: 16px">
          <div class="card-title"><span>🏢 {{ t('dashboard.enterpriseInfo') }}</span></div>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item :label="t('dashboard.enterpriseName')">
              {{ authStore.user?.enterprise_name || t('dashboard.defaultEnterpriseName') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('dashboard.userRole')">
              <el-tag size="small">{{ roleLabel }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="t('profile.email')">
              {{ authStore.user?.username || '-' }}
            </el-descriptions-item>
          </el-descriptions>
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
import { caseApi } from '@/api'

const { t, te } = useI18n()

/** 安全翻译：key 不存在时直接返回原始值，而不是显示 key 本身 */
function tr(key: string, fallback: string) {
  return te(key) ? t(key) : fallback
}

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const cases = ref<any[]>([])
const stats = ref<Record<string, number>>({})

const roleLabel = computed(() => {
  const role = authStore.user?.role || ''
  return t(`dashboard.roleName.${role}`) || role
})

const welcomeMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return t('dashboard.greeting.morning')
  if (hour < 18) return t('dashboard.greeting.afternoon')
  return t('dashboard.greeting.evening')
})

const statusLabelMap = computed(() => ({
  negotiating: t('case.statusMap.negotiating'),
  mediating: t('case.statusMap.mediating'),
  closed_negotiation: t('case.statusMap.closed_negotiation'),
  closed_mediation: t('case.statusMap.closed_mediation'),
  closed_success: t('case.statusMap.closed_success'),
  closed_failed: t('case.statusMap.closed_failed'),
  closed_fail: t('case.statusMap.closed_fail'),
  archived: t('case.statusMap.archived'),
}))

const miniStats = computed(() => [
  { key: 'pending', label: 'dashboard.stats.pending', value: stats.value.negotiating || 0, color: '#1677ff' },
  { key: 'mediating', label: 'dashboard.stats.mediating', value: stats.value.mediating || 0, color: '#fa8c16' },
  { key: 'closed', label: 'dashboard.stats.closed', value: (stats.value.closed_negotiation || 0) + (stats.value.closed_mediation || 0) + (stats.value.closed_success || 0), color: '#52c41a' },
  { key: 'total', label: 'dashboard.stats.total', value: Object.values(stats.value).reduce((a, b) => a + b, 0), color: '#8c8c8c' },
])

const pendingCases = computed(() =>
  cases.value.filter(c => ['negotiating', 'mediating'].includes(c.status)).slice(0, 5)
)

const recentCases = computed(() => cases.value.slice(0, 8))

const chartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0, itemWidth: 12, itemHeight: 12, textStyle: { fontSize: 12 } },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['50%', '45%'],
    data: Object.entries(stats.value).map(([k, v]) => ({
      name: statusLabelMap.value[k] || k,
      value: v,
    })).filter(d => d.value > 0),
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,.5)' } },
  }],
}))

onMounted(async () => {
  loading.value = true
  try {
    const res = await caseApi.list({ page: 1, page_size: 50 })
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
    negotiating: 'primary',
    mediating: 'warning',
    closed_negotiation: 'success',
    closed_mediation: 'success',
    closed_success: 'success',
    closed_failed: 'danger',
    closed_fail: 'danger',
    archived: 'info',
  }
  return map[status] || 'info'
}
function formatMoney(v: number) {
  return Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })
}
function formatDate(d: string) {
  return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.enterprise-dashboard { padding: 0; }

// 欢迎卡片
.welcome-card {
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 60%, #003eb3 100%);
  border-radius: var(--radius-2xl);
  padding: 32px 36px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 130px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(22, 119, 255, 0.25);
  animation: slideIn 0.6s ease-out;

  /* 装饰 */
  &::before {
    content: '';
    position: absolute;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    top: -80px;
    right: -60px;
  }

  &::after {
    content: '';
    position: absolute;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.04);
    bottom: -60px;
    right: 120px;
  }

  h2 {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
    position: relative;
    z-index: 1;
  }

  p {
    font-size: 14px;
    opacity: 0.85;
    position: relative;
    z-index: 1;
  }

  .quick-actions {
    display: flex;
    gap: 12px;
    position: relative;
    z-index: 1;

    .el-button {
      border-radius: var(--radius-lg);
      font-weight: 500;
      height: 40px;
      padding: 0 20px;
      transition: all var(--transition-normal);
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(255, 255, 255, 0.2);
      }
    }
  }
}

// 迷你统计
.stat-cards-mini {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  height: 100%;
}

.mini-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  transition: box-shadow var(--transition-normal), transform var(--transition-normal);

  &:hover {
    box-shadow: var(--shadow-card-hover);
    transform: translateY(-2px);
  }

  .mini-value { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .mini-label { font-size: 12px; color: var(--color-text-tertiary); margin-top: 4px; }
}

// 统计卡片
.stat-cards-row { margin-top: var(--space-4); }

.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 4px solid;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  border-left-width: 4px;
  transition: box-shadow var(--transition-normal), transform var(--transition-normal);

  &:hover {
    box-shadow: var(--shadow-card-hover);
    transform: translateY(-2px);
  }

  .stat-value { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .stat-label { font-size: 13px; color: var(--color-text-tertiary); margin-top: 4px; }
  .stat-icon { font-size: 36px; opacity: 0.2; }
}

.content-row { margin-top: var(--space-5); }
.chart { height: 260px; }

// 待办列表
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    border-color: var(--color-primary);
    background: var(--color-primary-bg);
  }
}

.todo-left { display: flex; align-items: center; gap: 12px; }
.todo-tag { min-width: 64px; text-align: center; }
.todo-info { display: flex; flex-direction: column; }
.todo-number { font-size: 14px; font-weight: 600; color: var(--color-primary); }
.todo-opponent { font-size: 12px; color: var(--color-text-tertiary); margin-top: 2px; }
.todo-right {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

// 快捷入口
.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 8px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: all var(--transition-normal);

  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(22, 119, 255, 0.12);
  }
}

.quick-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-number {
  font-family: monospace;
  font-weight: 600;
  color: var(--color-primary);
}

.amount { font-weight: 500; font-variant-numeric: tabular-nums; }
</style>
