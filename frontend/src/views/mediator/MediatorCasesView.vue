<template>
  <div>
    <!-- 搜索栏 -->
    <div class="page-card" style="margin-bottom: 16px;">
      <el-form :inline="true" :model="query" @submit.prevent="handleSearch">
        <el-form-item :label="t('case.searchLabels.caseNumber')">
          <el-input v-model="query.keyword" :placeholder="t('case.searchLabels.searchPlaceholder')" clearable />
        </el-form-item>
        <el-form-item :label="t('case.searchLabels.status')">
          <el-select v-model="query.status" :placeholder="t('case.searchLabels.allStatus')" clearable style="width: 160px">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit">{{ t('common.search') }}</el-button>
          <el-button @click="resetQuery">{{ t('common.reset') }}</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 案件列表 -->
    <div class="page-card">
      <div class="list-header">
        <h3>{{ t('mediator.assignedCases') }} <el-tag type="info">{{ total }} {{ t('common.pieces') }}</el-tag></h3>
      </div>

      <el-table :data="cases" v-loading="loading" stripe style="margin-top: 12px">
        <el-table-column prop="case_number" :label="t('case.caseNumber')" width="200">
          <template #default="{ row }">
            <span class="case-number">{{ row.case_number }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="opponent_name" :label="t('case.opponentName')" min-width="150" />
        <el-table-column prop="opponent_country" :label="t('case.opponentCountry')" width="110">
          <template #default="{ row }">{{ tr(`countries.${row.opponent_country || 'OTHER'}`, row.opponent_country || 'OTHER') }}</template>
        </el-table-column>
        <el-table-column :label="t('case.contractType')" width="120">
          <template #default="{ row }">{{ tr(`case.contractTypes.${row.contract_type}`, row.contract_type) }}</template>
        </el-table-column>
        <el-table-column :label="t('case.amountUsd')" width="140" align="right">
          <template #default="{ row }">
            <span class="amount">$ {{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="120">
          <template #default="{ row }">
            <span :class="['status-tag', row.status]">{{ tr(`case.statusMap.${row.status}`, row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.createTime')" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">{{ t('common.detail') }}</el-button>
            <el-button link type="warning" @click="goNegotiation(row)">{{ t('mediator.enterNegotiation') }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        :total="total"
        :page-size="20"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end; display: flex;"
        @current-change="loadCases"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import { mediatorApi } from '@/api'

const { t, te } = useI18n()
const router = useRouter()
const loading = ref(false)
const cases = ref<any[]>([])
const total = ref(0)

function tr(key: string, fallback: string) {
  return te(key) ? t(key) : fallback
}

const statusMap = computed(() => ({
  negotiating: t('case.statusMap.negotiating'), mediating: t('case.statusMap.mediating'),
  closed_success: t('case.statusMap.closed_success'),
  closed_negotiation: t('case.statusMap.closed_negotiation'), closed_mediation: t('case.statusMap.closed_mediation'),
  closed_fail: t('case.statusMap.closed_fail'), closed_failed: t('case.statusMap.closed_failed'),
  archived: t('case.statusMap.archived'),
}))

const query = ref({
  keyword: '',
  status: '',
  page: 1,
})

onMounted(loadCases)

async function loadCases() {
  loading.value = true
  try {
    const params: any = { page: query.value.page, page_size: 20 }
    if (query.value.keyword) params.keyword = query.value.keyword
    if (query.value.status) params.status = query.value.status
    const res = await mediatorApi.getMyCases(params)
    cases.value = res.data.data.items || []
    total.value = res.data.data.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() { query.value.page = 1; loadCases() }
function resetQuery() {
  query.value = { keyword: '', status: '', page: 1 }
  loadCases()
}
function goDetail(row: any) { router.push(`/mediator/cases/${row.id}`) }
function goNegotiation(row: any) { router.push(`/mediator/cases/${row.id}/negotiation`) }
function formatMoney(v: number) { return Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) }
function formatDate(d: string) { return d ? dayjs(d).format('YYYY-MM-DD') : '-' }
</script>

<style lang="scss" scoped>
.list-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4);
  h3 { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: var(--space-2); color: var(--color-text-primary); }
}
.case-number { font-family: monospace; font-weight: 600; color: var(--color-mediator); }
.amount { font-weight: 500; color: var(--color-text-secondary); }

:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  th.el-table__cell { background: var(--color-bg-page) !important; font-weight: 600; }
}
:deep(.el-pagination) { margin-top: var(--space-4); justify-content: flex-end; }
</style>
