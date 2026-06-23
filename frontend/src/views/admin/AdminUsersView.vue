<template>
  <div>
    <div class="page-card">
      <div class="list-header">
        <h3>{{ t('admin.users') }}</h3>
        <div class="filter-bar">
          <el-select v-model="filterRole" :placeholder="t('profile.role')" clearable style="width: 160px" @change="handleFilterChange">
            <el-option :label="t('admin.userRole.platform_admin')" value="platform_admin" />
            <el-option :label="t('admin.userRole.enterprise_admin')" value="enterprise_admin" />
            <el-option :label="t('admin.userRole.legal')" value="legal" />
            <el-option :label="t('admin.userRole.salesperson')" value="salesperson" />
            <el-option :label="t('admin.userRole.mediator')" value="mediator" />
            <el-option :label="t('admin.userRole.translator')" value="translator" />
            <el-option :label="t('admin.userRole.analyst')" value="analyst" />
          </el-select>
          <el-select v-model="filterStatus" :placeholder="t('common.status')" clearable style="width: 120px" @change="handleFilterChange">
            <el-option :label="t('admin.userStatus.active')" value="active" />
            <el-option :label="t('admin.userStatus.disabled')" value="disabled" />
          </el-select>
          <el-input v-model="filterKeyword" :placeholder="t('admin.searchPlaceholder')" clearable style="width: 200px" @keyup.enter="handleFilterChange" />
          <el-button type="primary" @click="handleFilterChange">{{ t('common.search') }}</el-button>
          <el-button @click="resetFilter">{{ t('common.reset') }}</el-button>
        </div>
      </div>

      <!-- 统计条（点击标签可切换筛选） -->
      <div class="user-stats">
        <div class="stat-chip clickable" :class="{ active: filterRole === '' }" @click="filterRole = ''; handleFilterChange()">
          <span>{{ t('admin.userStats.all') }}：<strong>{{ roleStats[0]?.count || 0 }}</strong></span>
        </div>
        <div
          v-for="item in roleStats.filter(s => s.role !== 'all')"
          :key="item.role"
          class="stat-chip clickable"
          :class="{ active: filterRole === item.role }"
          @click="filterRole = item.role; handleFilterChange()"
        >
          <span>{{ item.label }}：<strong>{{ item.count }}</strong></span>
        </div>
      </div>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column :label="t('admin.userStats.user')" min-width="160">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar size="small" :style="{ background: getAvatarColor(row.role) }">
                {{ (row.real_name || row.username || 'U')[0] }}
              </el-avatar>
              <div>
                <div class="user-real-name">{{ row.real_name || '-' }}</div>
                <div class="user-email">{{ row.username || row.email || '-' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('profile.role')" width="120">
          <template #default="{ row }">
            <el-tag :type="roleTagType(inferRole(row))" size="small">{{ roleMap[inferRole(row)] || row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('auth.enterpriseName')" min-width="140">
          <template #default="{ row }">
            <span>{{ row.enterprise_name || (['mediator','translator','analyst','platform_admin'].includes(inferRole(row)) ? t('admin.platformOfficial') : '-') }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? t('admin.userStatus.active') : t('admin.userStatus.disabled') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.createTime')" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">{{ t('common.detail') }}</el-button>
            <el-button
              link
              :type="row.status === 'active' ? 'danger' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? t('common.disable') : t('common.enable') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :total="total"
        :page-size="20"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @change="loadList"
      />
    </div>

    <!-- 用户详情弹窗 -->
    <el-dialog v-model="showDetail" :title="t('admin.userDetail')" width="520px">
      <el-descriptions :column="2" border v-if="detailUser">
        <el-descriptions-item label="ID">{{ detailUser.id }}</el-descriptions-item>
        <el-descriptions-item :label="t('admin.userStats.name')">{{ detailUser.real_name || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('profile.email')">{{ detailUser.username || detailUser.email || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('profile.role')">
          <el-tag :type="roleTagType(inferRole(detailUser))">{{ roleMap[inferRole(detailUser)] || detailUser.role }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('auth.enterpriseName')">{{ detailUser.enterprise_name || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.status')">
          <el-tag :type="detailUser.status === 'active' ? 'success' : 'danger'">
            {{ detailUser.status === 'active' ? t('admin.userStatus.active') : t('admin.userStatus.disabled') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.createTime')" :span="2">{{ formatDate(detailUser.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { adminApi } from '@/api'

const { t } = useI18n()
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const filterRole = ref('')
const filterStatus = ref('')
const filterKeyword = ref('')
const showDetail = ref(false)
const detailUser = ref<any>(null)

const roleMap: Record<string, string> = {
  platform_admin: '平台管理员',
  enterprise_admin: '企业管理员',
  legal: '法务',
  salesperson: '业务员',
  mediator: '调解员',
  translator: '翻译员',
  analyst: '数据分析师',
}

// 根据 specialty 推断真实角色（因为数据库 role 字段只有 mediator）
function inferRole(row: any): string {
  // 如果数据库已经有正确的 role 且不是 mediator，直接返回
  if (row.role && row.role !== 'mediator') return row.role
  // 根据 specialty 推断
  const specialty = row.specialty || row.domain || ''
  if (specialty.includes('英语') || specialty.includes('翻译') || specialty.includes('商务英语')) return 'translator'
  if (specialty.includes('数学') || specialty.includes('分析') || specialty.includes('数据')) return 'analyst'
  return 'mediator'
}

const roleTagType = (r: string) =>
  ({ platform_admin: 'danger', enterprise_admin: '', legal: 'primary', salesperson: 'success', mediator: 'warning', translator: 'info', analyst: 'success' }[r] || 'info')

const roleStats = ref([
  { role: 'all', label: t('admin.userStats.all'), count: 0, color: '#1677ff' },
  { role: 'enterprise_admin', label: t('admin.userRole.enterprise_admin'), count: 0, color: '#52c41a' },
  { role: 'legal', label: t('admin.userRole.legal'), count: 0, color: '#1677ff' },
  { role: 'salesperson', label: t('admin.userRole.salesperson'), count: 0, color: '#13c2c2' },
  { role: 'mediator', label: t('admin.userRole.mediator'), count: 0, color: '#fa8c16' },
  { role: 'translator', label: t('admin.userRole.translator'), count: 0, color: '#1677ff' },
  { role: 'analyst', label: t('admin.userRole.analyst'), count: 0, color: '#52c41a' },
])

function updateRoleStats(roleCounts: Record<string, number>) {
  const totalCount = Object.values(roleCounts).reduce((a, b) => a + b, 0)
  for (const stat of roleStats.value) {
    if (stat.role === 'all') {
      stat.count = totalCount
    } else {
      stat.count = roleCounts[stat.role] || 0
    }
  }
}

function getAvatarColor(role: string) {
  const map: Record<string, string> = {
    platform_admin: '#e63946', enterprise_admin: '#1677ff',
    legal: '#722ed1', salesperson: '#13c2c2', mediator: '#fa8c16',
    translator: '#1677ff', analyst: '#52c41a',
  }
  return map[role] || '#1677ff'
}

onMounted(loadList)

async function loadList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (filterRole.value) params.role = filterRole.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterKeyword.value) params.keyword = filterKeyword.value
    const res = await adminApi.listUsers(params)
    const responseData = res.data.data
    list.value = responseData.items || []
    total.value = responseData.total || 0
    if (responseData.role_counts) {
      updateRoleStats(responseData.role_counts)
    }
  } finally {
    loading.value = false
  }
}

function handleFilterChange() { page.value = 1; loadList() }
function resetFilter() { filterRole.value = ''; filterStatus.value = ''; filterKeyword.value = ''; page.value = 1; loadList() }
function viewDetail(row: any) { detailUser.value = row; showDetail.value = true }

async function toggleStatus(row: any) {
  const newStatus = row.status === 'active' ? 'disabled' : 'active'
  const actionText = newStatus === 'active' ? t('common.enable') : t('common.disable')
  try {
    await ElMessageBox.confirm(
      t('admin.confirmToggleUser', { name: row.real_name || row.username, action: actionText }),
      t('common.hint'),
      { type: 'warning', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await adminApi.updateUserStatus(row.id, newStatus)
    ElMessage.success(t('common.success'))
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}

function formatDate(d: string) { return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-' }
</script>

<style lang="scss" scoped>
.list-header {
  display: flex; flex-direction: column; align-items: flex-start; gap: var(--space-3); margin-bottom: var(--space-4);
  h3 { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
}
.filter-bar { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.user-stats {
  display: flex; gap: var(--space-3); margin-bottom: var(--space-4); flex-wrap: wrap;
}
.stat-chip {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--color-text-secondary);
  padding: 6px 14px; background: var(--color-bg-page); border-radius: var(--radius-md);
  border: 1px solid transparent;
  &.clickable { cursor: pointer; transition: all var(--transition-fast); }
  &.active { background: var(--color-primary-bg); color: var(--color-primary); border-color: #91caff; }
}
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-real-name { font-size: 13px; font-weight: 500; color: var(--color-text-primary); }
.user-email { font-size: 12px; color: var(--color-text-tertiary); }

:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  th.el-table__cell { background: var(--color-bg-page) !important; font-weight: 600; }
}
:deep(.el-pagination) { margin-top: var(--space-4); justify-content: flex-end; }
</style>
