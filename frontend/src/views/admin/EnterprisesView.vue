<template>
  <div class="page-card">
    <div class="list-header">
      <h3>{{ t('admin.enterprises') }}</h3>
    </div>
    <div class="filter-bar">
      <el-input v-model="filterKeyword" :placeholder="t('admin.searchPlaceholder')" clearable style="width: 240px" @keyup.enter="handleSearch">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterStatus" :placeholder="t('admin.actions.audit') + ' ' + t('common.status')" clearable style="width: 160px" @change="handleSearch">
        <el-option :label="t('admin.enterpriseAudit.pending')" value="pending" />
        <el-option :label="t('admin.enterpriseAudit.approved')" value="approved" />
        <el-option :label="t('admin.enterpriseAudit.rejected')" value="rejected" />
      </el-select>
      <el-button type="primary" @click="handleSearch">{{ t('common.search') }}</el-button>
      <el-button @click="resetFilter">{{ t('common.reset') }}</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="credit_code" :label="t('auth.creditCode')" width="200">
        <template #default="{ row }">
          <span class="mono-text">{{ row.credit_code }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" :label="t('auth.enterpriseName')" min-width="160" />
      <el-table-column prop="legal_person" :label="t('auth.legalPerson')" width="120" />
      <el-table-column prop="contact_phone" :label="t('auth.contactPhone')" width="140" />
      <el-table-column :label="t('admin.actions.audit')" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.audit_status)">{{ statusMap[row.audit_status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.createTime')" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="160" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.audit_status === 'pending'" link type="success" @click="audit(row.id, 'approve')">{{ t('admin.actions.approve') }}</el-button>
          <el-button v-if="row.audit_status === 'pending'" link type="danger" @click="audit(row.id, 'reject')">{{ t('admin.actions.reject') }}</el-button>
          <span v-if="row.audit_status !== 'pending'" style="color: #8c8c8c; font-size: 12px">-</span>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total, prev, pager, next"
      style="margin-top:16px; justify-content:flex-end; display:flex" @change="loadList" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'
import dayjs from 'dayjs'

const { t } = useI18n()
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const filterStatus = ref('')
const filterKeyword = ref('')

const statusMap = computed(() => ({
  pending: t('admin.enterpriseAudit.pending'),
  approved: t('admin.enterpriseAudit.approved'),
  rejected: t('admin.enterpriseAudit.rejected'),
}))
const statusTagType = (s: string) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info')

onMounted(loadList)

async function loadList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (filterStatus.value) params.audit_status = filterStatus.value
    if (filterKeyword.value) params.keyword = filterKeyword.value
    const res = await adminApi.listEnterprises(params)
    list.value = res.data.data.items || []
    total.value = res.data.data.total || 0
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; loadList() }
function resetFilter() { filterStatus.value = ''; filterKeyword.value = ''; page.value = 1; loadList() }

async function audit(id: number, action: string) {
  const actionText = action === 'approve' ? t('admin.actions.approve') : t('admin.actions.reject')
  try {
    await ElMessageBox.confirm(
      t('admin.confirmAudit', { action: actionText }),
      t('common.hint'),
      { type: 'warning', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await adminApi.auditEnterprise(id, action)
    ElMessage.success(t('common.success'))
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}

function formatDate(d: string) { return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-' }
</script>

<style lang="scss" scoped>
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); h3 { font-size: 15px; font-weight: 600; color: var(--color-text-primary); } }
.filter-bar { display: flex; gap: var(--space-3); margin-bottom: var(--space-4); align-items: center; flex-wrap: wrap; }
.mono-text { font-family: monospace; font-size: 12px; color: var(--color-text-secondary); }

:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  th.el-table__cell { background: var(--color-bg-page) !important; font-weight: 600; }
}
:deep(.el-pagination) { margin-top: var(--space-4); justify-content: flex-end; }
</style>
