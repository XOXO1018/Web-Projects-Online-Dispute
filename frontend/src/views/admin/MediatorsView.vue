<template>
  <div class="page-card">
    <div class="list-header">
      <h3>{{ t('admin.staff') }}</h3>
      <el-button type="primary" @click="showCreate = true">{{ t('admin.staffCreate') }}</el-button>
    </div>

    <!-- 人员类型筛选 -->
    <div class="staff-filter">
      <div
        v-for="type in staffTypes"
        :key="type.value"
        class="filter-chip"
        :class="{ active: filterType === type.value }"
        @click="filterType = type.value; fetchList()"
      >
        <span>{{ type.label }}</span>
        <strong>{{ type.count }}</strong>
      </div>
    </div>

    <el-table :data="filteredData" v-loading="loading" stripe>
      <el-table-column prop="real_name" :label="t('admin.mediatorForm.name')" width="120" />
      <el-table-column :label="t('admin.staffType')" width="120">
        <template #default="{ row }">
          <el-tag :type="staffTypeTag(inferStaffType(row))" size="small">{{ staffTypeLabel(inferStaffType(row)) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="email" :label="t('admin.mediatorForm.email')" width="220" show-overflow-tooltip />
      <el-table-column prop="domain" :label="t('admin.mediatorForm.domain')" min-width="100">
        <template #default="{ row }">{{ row.domain || row.specialty || '-' }}</template>
      </el-table-column>
      <el-table-column :label="t('admin.mediatorForm.rating')" width="130">
        <template #default="{ row }">
          <el-rate :model-value="row.rating" disabled allow-half />
        </template>
      </el-table-column>
      <el-table-column :label="t('mediation.successRate')" width="90">
        <template #default="{ row }">{{ row.success_rate ?? '-' }}%</template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="120">
        <template #default="{ row }">
          <el-tag :type="mediatorStatusType(row.status)" size="small">{{ mediatorStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="240" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="editStaff(row)">{{ t('common.edit') }}</el-button>
          <el-button
            v-if="row.status === 'active'"
            link type="warning"
            @click="updateStatus(row, 'vacation')"
          >{{ t('admin.mediatorStatus.vacation') }}</el-button>
          <el-button
            v-if="row.status === 'vacation'"
            link type="success"
            @click="updateStatus(row, 'active')"
          >{{ t('admin.mediatorStatus.active') }}</el-button>
          <el-button
            :link="row.status !== 'disabled'"
            :type="row.status === 'disabled' ? 'success' : 'danger'"
            @click="updateStatus(row, row.status === 'disabled' ? 'active' : 'disabled')"
          >{{ row.status === 'disabled' ? t('common.enable') : t('common.disable') }}</el-button>
          <el-button link type="danger" @click="deleteMediator(row)">{{ t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建人员弹窗 -->
    <el-dialog v-model="showCreate" :title="t('admin.staffCreateTitle')" width="520px">
      <el-form :model="createForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('admin.staffType')">
              <el-select v-model="createForm.staff_type" style="width:100%">
                <el-option :label="t('admin.staffTypes.mediator')" value="mediator" />
                <el-option :label="t('admin.staffTypes.translator')" value="translator" />
                <el-option :label="t('admin.staffTypes.analyst')" value="analyst" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.name')"><el-input v-model="createForm.real_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.email')"><el-input v-model="createForm.email" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.phone')"><el-input v-model="createForm.phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.domain')"><el-input v-model="createForm.domain" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.rating')">
              <el-rate v-model="createForm.rating" allow-half />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('admin.mediatorForm.intro')"><el-input v-model="createForm.intro" type="textarea" /></el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="doCreate" :loading="creating">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 编辑人员弹窗 -->
    <el-dialog v-model="showEdit" :title="t('admin.staffEditTitle')" width="520px">
      <el-form :model="editForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="t('admin.staffType')">
              <el-select v-model="editForm.staff_type" style="width:100%">
                <el-option :label="t('admin.staffTypes.mediator')" value="mediator" />
                <el-option :label="t('admin.staffTypes.translator')" value="translator" />
                <el-option :label="t('admin.staffTypes.analyst')" value="analyst" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.name')"><el-input v-model="editForm.real_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.email')"><el-input v-model="editForm.email" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.phone')"><el-input v-model="editForm.phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.domain')"><el-input v-model="editForm.domain" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('admin.mediatorForm.rating')">
              <el-rate v-model="editForm.rating" allow-half />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('admin.mediatorForm.intro')"><el-input v-model="editForm.intro" type="textarea" /></el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="doUpdate" :loading="updating">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'

const { t } = useI18n()
const loading = ref(false)
const list = ref<any[]>([])
const filterType = ref('')
const showCreate = ref(false)
const creating = ref(false)
const showEdit = ref(false)
const updating = ref(false)

const createForm = ref({
  real_name: '', email: '', phone: '', domain: '', intro: '',
  staff_type: 'mediator' as string, rating: 0,
})
const editForm = ref({
  id: 0, real_name: '', email: '', phone: '', domain: '', intro: '',
  staff_type: 'mediator' as string, rating: 0,
})

const staffTypes = computed(() => [
  { value: '', label: t('admin.staffTypes.all'), count: list.value.length },
  { value: 'mediator', label: t('admin.staffTypes.mediator'), count: list.value.filter(s => inferStaffType(s) === 'mediator').length },
  { value: 'translator', label: t('admin.staffTypes.translator'), count: list.value.filter(s => inferStaffType(s) === 'translator').length },
  { value: 'analyst', label: t('admin.staffTypes.analyst'), count: list.value.filter(s => inferStaffType(s) === 'analyst').length },
])

const filteredData = computed(() => {
  if (!filterType.value) return list.value
  return list.value.filter(s => s.staff_type === filterType.value)
})

// 根据专业推断人员类型
function inferStaffType(row: any): string {
  if (row.staff_type && row.staff_type !== 'mediator') return row.staff_type
  const specialty = row.domain || row.specialty || ''
  if (specialty.includes('英语') || specialty.includes('翻译') || specialty.includes('商务英语')) return 'translator'
  if (specialty.includes('数学') || specialty.includes('分析') || specialty.includes('数据')) return 'analyst'
  return 'mediator'
}

function staffTypeLabel(type: string) {
  return ({ mediator: t('admin.staffTypes.mediator'), translator: t('admin.staffTypes.translator'), analyst: t('admin.staffTypes.analyst') }[type]) || t('admin.staffTypes.mediator')
}
function staffTypeTag(type: string) {
  return ({ mediator: 'warning', translator: 'primary', analyst: 'success' }[type]) || 'warning'
}

const mediatorStatusLabel = (status: string) => ({
  active: t('admin.mediatorStatus.active'),
  vacation: t('admin.mediatorStatus.vacation'),
  disabled: t('common.disable'),
}[status] || status)

const mediatorStatusType = (status: string) => ({
  active: 'success',
  vacation: 'warning',
  disabled: 'danger',
}[status] || 'info')

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  try {
    const res = await adminApi.listMediators({ page: 1, page_size: 200 })
    const responseData = res.data.data
    const items = Array.isArray(responseData) ? responseData : (responseData?.data || [])
    list.value = items.map((item: any) => ({
      ...item,
      staff_type: item.staff_type || 'mediator',
      _editRating: item.rating || 0,
    }))
  } catch (e) {
    console.error('Failed to load staff:', e)
  } finally {
    loading.value = false
  }
}

function editStaff(row: any) {
  editForm.value = {
    id: row.id,
    real_name: row.real_name,
    email: row.email,
    phone: row.phone || '',
    domain: row.domain || '',
    intro: row.intro || '',
    staff_type: row.staff_type || 'mediator',
    rating: row.rating || 0,
  }
  showEdit.value = true
}

async function doUpdate() {
  updating.value = true
  try {
    await adminApi.updateMediator(editForm.value.id, editForm.value)
    ElMessage.success(t('common.success'))
    showEdit.value = false
    await fetchList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  } finally {
    updating.value = false
  }
}

async function doCreate() {
  creating.value = true
  try {
    const res = await adminApi.createMediator(createForm.value)
    // 后端返回的消息中包含随机生成的初始密码，需要提取并显示给管理员
    const responseMessage = res.data?.message || t('admin.mediatorCreated')
    // 尝试从消息中提取密码（格式："...初始密码为 xxx"）
    const passwordMatch = responseMessage.match(/初始密码为\s*(\S+)/)
    if (passwordMatch) {
      ElMessageBox.alert(
        `${t('admin.mediatorCreated')}\n\n${t('admin.initialPassword')}: ${passwordMatch[1]}`,
        t('admin.staffCreateTitle'),
        { type: 'success', confirmButtonText: t('common.confirm') }
      )
    } else {
      ElMessage.success(responseMessage)
    }
    showCreate.value = false
    createForm.value = { real_name: '', email: '', phone: '', domain: '', intro: '', staff_type: 'mediator', rating: 0 }
    await fetchList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  } finally {
    creating.value = false
  }
}

async function updateStatus(row: any, newStatus: string) {
  const statusLabel = mediatorStatusLabel(newStatus)
  try {
    await ElMessageBox.confirm(
      t('admin.mediatorStatus.confirmChange', { name: row.real_name, status: statusLabel }),
      t('common.hint'),
      { type: 'warning', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await adminApi.updateMediatorStatus(row.id, newStatus)
    ElMessage.success(t('common.success'))
    await fetchList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}

async function deleteMediator(row: any) {
  try {
    await ElMessageBox.confirm(
      t('admin.mediatorStatus.confirmDelete', { name: row.real_name }),
      t('common.hint'),
      { type: 'error', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await adminApi.deleteMediator(row.id)
    ElMessage.success(t('common.success'))
    await fetchList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || t('common.error'))
  }
}
</script>

<style lang="scss" scoped>
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); h3 { font-size: 15px; font-weight: 600; color: var(--color-text-primary); } }

.staff-filter {
  display: flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;
}
.filter-chip {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--color-text-secondary);
  padding: 6px 16px; background: var(--color-bg-page); border-radius: var(--radius-md);
  border: 1px solid transparent; cursor: pointer; transition: all var(--transition-fast);
  strong { color: var(--color-text-primary); }
  &:hover { border-color: var(--color-primary-light); }
  &.active { background: var(--color-primary-bg); color: var(--color-primary); border-color: #91caff; strong { color: var(--color-primary); } }
}



::deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  th.el-table__cell { background: var(--color-bg-page) !important; font-weight: 600; }
}
</style>
