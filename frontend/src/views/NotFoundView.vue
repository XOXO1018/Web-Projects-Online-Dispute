<template>
  <div class="not-found">
    <el-result icon="404" :title="t('notFound.title')" :sub-title="t('notFound.subtitle')">
      <template #extra>
        <el-button type="primary" @click="router.push('/dashboard')">{{ t('notFound.backHome') }}</el-button>
      </template>
    </el-result>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
</script>
<style lang="scss" scoped>
.not-found {
  display: flex; align-items: center; justify-content: center;
  height: 100vh;
  background: var(--color-bg-page);
}
</style>
