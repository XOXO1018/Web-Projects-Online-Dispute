<template>
  <el-config-provider :locale="elLocale">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import enUs from 'element-plus/dist/locale/en.mjs'

const { locale } = useI18n()
const authStore = useAuthStore()

const localeMap: Record<string, any> = { 'zh-CN': zhCn, 'en-US': enUs }
const elLocale = computed(() => localeMap[locale.value] || zhCn)

onMounted(async () => {
  // 检查 token 并恢复登录状态
  if (authStore.token) {
    await authStore.fetchCurrentUser()
  }
})
</script>
