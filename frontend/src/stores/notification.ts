import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notificationApi } from '@/api'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)

  async function fetchUnreadCount() {
    try {
      const res = await notificationApi.list({ page: 1, page_size: 1, unread_only: true })
      unreadCount.value = res.data.data.unread_count || 0
    } catch {}
  }

  function decrement(n = 1) {
    unreadCount.value = Math.max(0, unreadCount.value - n)
  }

  function reset() {
    unreadCount.value = 0
  }

  return { unreadCount, fetchUnreadCount, decrement, reset }
})
