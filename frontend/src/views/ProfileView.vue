<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="page-card">
          <h3>{{ t('profile.personalInfo') }}</h3>
          <el-form :model="form" label-position="top" style="margin-top: 16px">
            <el-form-item :label="t('profile.realName')">
              <el-input v-model="form.real_name" />
            </el-form-item>
            <el-form-item :label="t('profile.email')">
              <el-input :value="authStore.user?.email" disabled />
            </el-form-item>
            <el-form-item :label="t('profile.role')">
              <el-tag>{{ t(`profile.roles.${authStore.user?.role || 'platform_admin'}`) }}</el-tag>
            </el-form-item>
            <el-form-item :label="t('profile.language')">
              <el-select v-model="currentLang" @change="changeLanguage" style="width: 100%">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('profile.emailNotify')">
              <el-switch v-model="form.notify_email" />
            </el-form-item>
            <el-form-item :label="t('profile.smsNotify')">
              <el-switch v-model="form.notify_sms" />
            </el-form-item>
            <el-button type="primary" @click="saveProfile" :loading="saving">{{ t('profile.saveSettings') }}</el-button>
          </el-form>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="page-card">
          <h3>{{ t('profile.changePassword') }}</h3>
          <el-form :model="pwdForm" label-position="top" style="margin-top: 16px">
            <el-form-item :label="t('profile.oldPassword')">
              <el-input v-model="pwdForm.old" type="password" show-password />
            </el-form-item>
            <el-form-item :label="t('profile.newPassword')">
              <el-input v-model="pwdForm.new" type="password" show-password />
            </el-form-item>
            <el-form-item :label="t('profile.confirmPassword')">
              <el-input v-model="pwdForm.confirm" type="password" show-password />
            </el-form-item>
            <el-button type="primary" @click="changePwd" :loading="changingPwd">{{ t('profile.changePwdBtn') }}</el-button>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { userApi, authApi } from '@/api'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const saving = ref(false)
const changingPwd = ref(false)

const currentLang = ref(localStorage.getItem('zjfl_language') || 'zh-CN')

const form = ref({
  real_name: authStore.user?.real_name || '',
  language: currentLang.value,
  notify_email: true,
  notify_sms: false,
})

const pwdForm = ref({ old: '', new: '', confirm: '' })

onMounted(async () => {
  try {
    const res = await userApi.getMe()
    const u = res.data.data
    form.value = {
      real_name: u.real_name || authStore.user?.real_name || '',
      language: u.language || localStorage.getItem('zjfl_language') || 'zh-CN',
      notify_email: u.notify_email ?? true,
      notify_sms: u.notify_sms ?? false,
    }
    currentLang.value = form.value.language
  } catch {
    form.value.real_name = authStore.user?.real_name || ''
  }
})

async function saveProfile() {
  saving.value = true
  try {
    await userApi.updateMe(form.value)
    ElMessage.success(t('profile.saved'))
    await authStore.fetchCurrentUser()
  } finally {
    saving.value = false
  }
}

function changeLanguage(lang: string) {
  locale.value = lang
  localStorage.setItem('zjfl_language', lang)
  document.documentElement.setAttribute('lang', lang)
  ElMessage.success(t('profile.languageChanged'))
}

async function changePwd() {
  if (pwdForm.value.new !== pwdForm.value.confirm) {
    ElMessage.error(t('profile.pwdMismatch'))
    return
  }
  changingPwd.value = true
  try {
    await authApi.changePassword({
      old_password: pwdForm.value.old,
      new_password: pwdForm.value.new,
    })
    ElMessage.success(t('profile.pwdChanged'))
    pwdForm.value = { old: '', new: '', confirm: '' }
  } finally {
    changingPwd.value = false
  }
}
</script>

<style lang="scss" scoped>
h3 { font-size: 16px; font-weight: 600; margin-bottom: 0; color: var(--color-text-primary); }
</style>
