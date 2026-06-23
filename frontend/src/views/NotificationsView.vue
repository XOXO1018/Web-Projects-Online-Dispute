<template>
  <div>
    <div class="page-card">
      <div class="list-header">
        <h3>{{ t('notification.title') }}</h3>
        <el-button @click="markAllRead" :loading="marking">{{ t('notification.markAllRead') }}</el-button>
      </div>
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="t('notification.all')" name="all" />
        <el-tab-pane :label="t('notification.unread')" name="unread" />
      </el-tabs>
      <el-table :data="notifications" v-loading="loading">
        <el-table-column width="40">
          <template #default="{ row }">
            <span v-if="!row.is_read" class="unread-dot"></span>
          </template>
        </el-table-column>
        <el-table-column prop="title" :label="t('common.title')" min-width="200">
          <template #default="{ row }">
            <span :class="{ 'font-bold': !row.is_read }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="content" :label="t('common.content')" min-width="300" show-overflow-tooltip />
        <el-table-column :label="t('common.time')" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="120">
          <template #default="{ row }">
            <el-button v-if="!row.is_read" link type="primary" @click="markRead(row)">{{ t('notification.markRead') }}</el-button>
            <el-button v-if="row.related_case_id" link type="primary" @click="goCase(row)">{{ t('notification.viewCase') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @change="loadNotifications"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { notificationApi } from '@/api'
import { useNotificationStore } from '@/stores/notification'

const { t } = useI18n()
const router = useRouter()
const notificationStore = useNotificationStore()
const loading = ref(false)
const marking = ref(false)
const activeTab = ref('all')
const notifications = ref<any[]>([])
const total = ref(0)
const page = ref(1)

watch(activeTab, () => { page.value = 1; loadNotifications() })
onMounted(loadNotifications)

async function loadNotifications() {
  loading.value = true
  try {
    const res = await notificationApi.list({
      page: page.value, page_size: 20,
      unread_only: activeTab.value === 'unread',
    })
    notifications.value = res.data.data.items || []
    total.value = res.data.data.total || 0
  } finally {
    loading.value = false
  }
}

async function markRead(row: any) {
  await notificationApi.markRead(row.id)
  row.is_read = true
  // 立即减少未读数
  notificationStore.decrement(1)
  // 如果在未读 tab 下，重新加载列表以移除已读项
  if (activeTab.value === 'unread') {
    loadNotifications()
  }
}

async function markAllRead() {
  marking.value = true
  try {
    await notificationApi.markAllRead()
    // 立即清零未读数
    notificationStore.reset()
    await loadNotifications()
    ElMessage.success(t('notification.allMarked'))
  } finally {
    marking.value = false
  }
}

function goCase(row: any) {
  if (row.related_case_id) router.push(`/cases/${row.related_case_id}`)
}

function formatDate(d: string) {
  return d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-'
}
</script>

<style lang="scss" scoped>
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2); h3 { font-size: 16px; font-weight: 600; color: var(--color-text-primary); } }
.unread-dot { display: inline-block; width: 8px; height: 8px; background: var(--color-primary); border-radius: 50%; }
.font-bold { font-weight: 600; }

:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  th.el-table__cell { background: var(--color-bg-page) !important; font-weight: 600; }
}
:deep(.el-pagination) { margin-top: var(--space-4); justify-content: flex-end; }
</style>
