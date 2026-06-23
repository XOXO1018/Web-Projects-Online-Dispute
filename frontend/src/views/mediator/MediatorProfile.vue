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
              <el-tag>{{ profileRoleLabel }}</el-tag>
            </el-form-item>
            <el-form-item :label="t('mediation.specialty')">
              <el-input v-model="form.specialty" :placeholder="t('mediator.specialtyPlaceholder')" />
            </el-form-item>
            <el-form-item :label="t('mediation.bio')">
              <el-input v-model="form.bio" type="textarea" :rows="3" :placeholder="t('mediator.bioPlaceholder')" />
            </el-form-item>
            <el-form-item :label="t('profile.language')">
              <el-select v-model="currentLang" @change="changeLanguage" style="width: 100%">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
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

        <!-- 调解员统计 -->
        <div class="page-card" style="margin-top: 16px">
          <h3>{{ t('mediator.myStats') }}</h3>
          <el-row :gutter="12" style="margin-top: 16px">
            <el-col :span="12">
              <div class="stat-box">
                <div class="stat-value">{{ mediatorData.cases_count || 0 }}</div>
                <div class="stat-label">{{ t('mediation.casesCount') }}</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="stat-box">
                <div class="stat-value">{{ mediatorData.success_rate || 0 }}%</div>
                <div class="stat-label">{{ t('mediation.successRate') }}</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="12" style="margin-top: 12px">
            <el-col :span="12">
              <div class="stat-box">
                <div class="stat-value">{{ mediatorData.rating || 0 }}</div>
                <div class="stat-label">{{ t('mediation.rating') }}</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="stat-box" :class="mediatorData.status">
                <div class="stat-value">{{ t(`admin.mediatorStatus.${mediatorData.status || 'active'}`) }}</div>
                <div class="stat-label">{{ t('common.status') }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { mediatorApi, authApi, userApi } from '@/api'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const saving = ref(false)
const changingPwd = ref(false)

const currentLang = ref(localStorage.getItem('zjfl_language') || 'zh-CN')

// 根据 specialty 推断真实角色
const profileRoleLabel = computed(() => {
  const specialty = authStore.user?.specialty || ''
  let inferredRole = authStore.user?.role || 'mediator'
  if (specialty.includes('英语') || specialty.includes('翻译') || specialty.includes('商务英语')) {
    inferredRole = 'translator'
  } else if (specialty.includes('数学') || specialty.includes('分析') || specialty.includes('数据')) {
    inferredRole = 'analyst'
  }
  return t(`profile.roles.${inferredRole}`)
})

const form = ref({
  real_name: authStore.user?.real_name || '',
  specialty: '',
  bio: '',
  language: currentLang.value,
})

const mediatorData = ref<Record<string, any>>({})

const pwdForm = ref({ old: '', new: '', confirm: '' })

onMounted(async () => {
  // 加载用户基本信息
  try {
    const res = await userApi.getMe()
    const u = res.data.data
    form.value.real_name = u.real_name || authStore.user?.real_name || ''
    form.value.language = u.language || localStorage.getItem('zjfl_language') || 'zh-CN'
    currentLang.value = form.value.language
  } catch {
    form.value.real_name = authStore.user?.real_name || ''
  }

  // 加载调解员特有信息
  try {
    const res = await mediatorApi.getMe()
    const m = res.data.data
    mediatorData.value = m
    form.value.specialty = m.specialty || ''
    form.value.bio = m.bio || ''
    if (m.name) form.value.real_name = m.name
  } catch {}
})

async function saveProfile() {
  saving.value = true
  try {
    // 更新基本信息
    await userApi.updateMe({
      real_name: form.value.real_name,
      language: form.value.language,
    })
    // 更新调解员特有信息
    await mediatorApi.updateMe({
      name: form.value.real_name,
      specialty: form.value.specialty,
      bio: form.value.bio,
    })
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
.stat-box {
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  text-align: center;
  border: 1px solid var(--color-border);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  &:hover { transform: translateY(-2px); box-shadow: var(--shadow-card); }
}
.stat-box.active {
  border-color: var(--color-success);
  background: #f6ffed;
}
.stat-box.disabled {
  border-color: var(--color-danger);
  background: #fff2f0;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0d1b2a;
  font-variant-numeric: tabular-nums;
}
.stat-box.active .stat-value { color: var(--color-success); }
.stat-box.disabled .stat-value { color: var(--color-danger); }
.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: var(--space-1);
}
</style>
