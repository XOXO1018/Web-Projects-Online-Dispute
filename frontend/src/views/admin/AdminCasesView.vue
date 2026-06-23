<template>
  <div class="page-card">
    <h3>{{ t('admin.caseManagement') }}</h3>
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="filterKeyword" :placeholder="t('admin.searchPlaceholder')" clearable style="width: 220px" @keyup.enter="handleSearch">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterStatus" :placeholder="t('case.searchLabels.allStatus')" clearable style="width: 160px" @change="handleSearch">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="handleSearch">{{ t('common.search') }}</el-button>
      <el-button @click="resetFilter">{{ t('common.reset') }}</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe style="margin-top:12px">
      <el-table-column prop="case_number" :label="t('case.caseNumber')" width="200">
        <template #default="{ row }">
          <span class="case-number">{{ row.case_number }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="enterprise_name" :label="t('auth.enterpriseName')" min-width="120" />
      <el-table-column prop="opponent_name" :label="t('case.opponentName')" min-width="120" />
      <el-table-column prop="opponent_country" :label="t('case.opponentCountry')" width="100">
        <template #default="{ row }">{{ tr(`countries.${row.opponent_country || 'OTHER'}`, row.opponent_country || 'OTHER') }}</template>
      </el-table-column>
      <el-table-column :label="t('case.amount')" width="130">
        <template #default="{ row }">USD {{ Number(row.amount).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ statusMap[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.createTime')" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="viewProgress(row)">{{ t('admin.caseProgress') }}</el-button>
          <el-button link type="danger" @click="deleteCase(row)">{{ t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next"
      style="margin-top:16px; justify-content:flex-end; display:flex" @change="loadList" />

    <!-- 案件进程弹窗 -->
    <el-dialog v-model="showProgress" :title="progressTitle" width="700px">
      <div v-loading="progressLoading">
        <el-timeline v-if="timeline.length > 0">
          <el-timeline-item
            v-for="(item, idx) in timeline"
            :key="idx"
            :type="timelineType(item.type)"
            :timestamp="item.time"
            placement="top"
          >
            {{ item.event }}
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else :description="t('common.noData')" />
      </div>
      <template #footer>
        <el-button @click="showProgress = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { adminApi } from '@/api'

const { t, te } = useI18n()

function tr(key: string, fallback: string) {
  return te(key) ? t(key) : fallback
}

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const filterStatus = ref('')
const filterKeyword = ref('')
const showProgress = ref(false)
const progressTitle = ref('')
const progressLoading = ref(false)
const timeline = ref<any[]>([])

const statusMap = computed(() => ({
  negotiating: t('case.statusMap.negotiating'),
  mediating: t('case.statusMap.mediating'),
  closed_success: t('case.statusMap.closed_success'),
  closed_fail: t('case.statusMap.closed_fail'),
  closed_failed: t('case.statusMap.closed_failed'),
  closed_negotiation: t('case.statusMap.closed_negotiation'),
  closed_mediation: t('case.statusMap.closed_mediation'),
  archived: t('case.statusMap.archived'),
}))

const statusTagType = (s: string) =>
  ({ negotiating: 'primary', mediating: 'warning', closed_success: 'success', closed_negotiation: 'success', closed_mediation: 'success', closed_fail: 'danger', closed_failed: 'danger', archived: 'info' }[s] || 'info')



const timelineType = (type: string) => {
  const map: Record<string, string> = { create: 'primary', evidence: 'success', message: '', mediation: 'warning' }
  return map[type] || ''
}

onMounted(loadList)

async function loadList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (filterStatus.value) params.status = filterStatus.value
    if (filterKeyword.value) params.keyword = filterKeyword.value
    const res = await adminApi.listAllCases(params)
    list.value = res.data.data.items || []
    total.value = res.data.data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() { page.value = 1; loadList() }
function resetFilter() { filterStatus.value = ''; filterKeyword.value = ''; page.value = 1; loadList() }

async function deleteCase(row: any) {
  try {
    await ElMessageBox.confirm(
      t('admin.confirmDeleteCase', { number: row.case_number }),
      t('common.hint'),
      { type: 'error', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await adminApi.deleteCase(row.id)
    ElMessage.success(t('common.success'))
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}

async function viewProgress(row: any) {
  progressTitle.value = `${t('admin.caseProgress')} - ${row.case_number}`
  showProgress.value = true
  progressLoading.value = true
  try {
    const res = await adminApi.getCaseProgress(row.id)
    timeline.value = res.data.data.timeline || []
  } catch {
    timeline.value = []
  } finally {
    progressLoading.value = false
  }
}

function formatDate(d: string) { return d ? dayjs(d).format('YYYY-MM-DD') : '-' }
</script>
<style lang="scss" scoped>
h3 { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.filter-bar { display: flex; gap: var(--space-3); margin-top: var(--space-4); align-items: center; flex-wrap: wrap; }
.case-number { font-family: monospace; font-weight: 600; color: var(--color-primary); }

:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  th.el-table__cell { background: var(--color-bg-page) !important; font-weight: 600; }
}
:deep(.el-pagination) { margin-top: var(--space-4); justify-content: flex-end; }
</style>
