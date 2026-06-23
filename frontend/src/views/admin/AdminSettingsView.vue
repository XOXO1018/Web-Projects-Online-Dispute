<template>
  <div>
    <el-row :gutter="20">
      <!-- 基础设置 -->
      <el-col :span="12">
        <div class="page-card">
          <h3>⚙ {{ t('admin.settingsSections.basic') }}</h3>
          <el-form label-position="top" style="margin-top: 16px">
            <el-form-item :label="t('admin.settingsLabels.platformName')">
              <el-input v-model="settings.platform_name" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.platformDesc')">
              <el-input v-model="settings.platform_desc" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.defaultLanguage')">
              <el-select v-model="settings.default_language" style="width: 100%">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en" />
                <el-option label="Tiếng Việt" value="vi" />
                <el-option label="ภาษาไทย" value="th" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.demoMode')">
              <el-switch v-model="settings.demo_mode" :active-text="t('admin.settingsSections.demoModeOn')" :inactive-text="t('admin.settingsSections.demoModeOff')" />
              <div class="setting-hint">{{ t('admin.settingsHints.demoMode') }}</div>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- 安全设置 -->
      <el-col :span="12">
        <div class="page-card">
          <h3>🔒 {{ t('admin.settingsSections.security') }}</h3>
          <el-form label-position="top" style="margin-top: 16px">
            <el-form-item :label="t('admin.settingsLabels.tokenExpireDays')">
              <el-input-number v-model="settings.token_expire_days" :min="1" :max="90" style="width: 100%" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.refreshTokenExpireDays')">
              <el-input-number v-model="settings.refresh_token_expire_days" :min="7" :max="365" style="width: 100%" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.captchaExpireSeconds')">
              <el-input-number v-model="settings.captcha_expire_seconds" :min="30" :max="300" :step="30" style="width: 100%" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.requireAudit')">
              <el-switch v-model="settings.require_audit" :active-text="t('admin.settingsSections.demoModeOn')" :inactive-text="t('admin.settingsSections.demoModeOff')" />
              <div class="setting-hint">{{ t('admin.settingsHints.requireAudit') }}</div>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 调解设置 -->
      <el-col :span="12">
        <div class="page-card">
          <h3>⚖ {{ t('admin.settingsSections.mediation') }}</h3>
          <el-form label-position="top" style="margin-top: 16px">
            <el-form-item :label="t('admin.settingsLabels.recommendMediatorCount')">
              <el-input-number v-model="settings.recommend_mediator_count" :min="1" :max="10" style="width: 100%" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.meetingMaxDuration')">
              <el-input-number v-model="settings.meeting_max_duration" :min="30" :max="480" :step="30" style="width: 100%" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.demoSignCode')">
              <el-input v-model="settings.demo_sign_code" style="width: 200px" />
              <div class="setting-hint">{{ t('admin.settingsHints.demoSignCode') }}</div>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- 通知设置 -->
      <el-col :span="12">
        <div class="page-card">
          <h3>📬 {{ t('admin.settingsSections.notify') }}</h3>
          <el-form label-position="top" style="margin-top: 16px">
            <el-form-item :label="t('admin.settingsLabels.emailNotify')">
              <el-switch v-model="settings.email_notify" :active-text="t('admin.settingsSections.demoModeOn')" :inactive-text="t('admin.settingsSections.demoModeOff')" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.smsNotify')">
              <el-switch v-model="settings.sms_notify" :active-text="t('admin.settingsSections.demoModeOn')" :inactive-text="t('admin.settingsSections.demoModeOff')" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.inAppNotify')">
              <el-switch v-model="settings.in_app_notify" :active-text="t('admin.settingsSections.demoModeOn')" :inactive-text="t('admin.settingsSections.demoModeOff')" />
            </el-form-item>
            <el-form-item :label="t('admin.settingsLabels.notifyRefreshInterval')">
              <el-input-number v-model="settings.notify_refresh_interval" :min="10" :max="120" :step="10" style="width: 100%" />
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>

    <div style="text-align: right; margin-top: 20px">
      <el-button @click="resetSettings">{{ t('admin.settingsActions.resetDefault') }}</el-button>
      <el-button type="primary" @click="saveSettings" :loading="saving">{{ t('admin.settingsActions.saveSettings') }}</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api'

const { t, locale } = useI18n()
const saving = ref(false)

const settings = reactive({
  platform_name: '智链解纷',
  platform_desc: '中国-东盟跨境商事纠纷在线解决平台',
  default_language: localStorage.getItem('zjfl_language') || 'zh-CN',
  demo_mode: true,
  token_expire_days: 7,
  refresh_token_expire_days: 30,
  captcha_expire_seconds: 120,
  require_audit: false,
  recommend_mediator_count: 3,
  meeting_max_duration: 120,
  demo_sign_code: '123456',
  email_notify: true,
  sms_notify: false,
  in_app_notify: true,
  notify_refresh_interval: 30,
})

const defaults = { ...settings }

// 语言变更时实时切换全局语言
watch(() => settings.default_language, (newLang) => {
  const lang = newLang === 'en' ? 'en-US' : 'zh-CN'
  locale.value = lang
  localStorage.setItem('zjfl_language', lang)
  document.documentElement.setAttribute('lang', lang)
  // 同时更新用户偏好
  userApi.updateMe({ language: lang }).catch(() => {})
})

function resetSettings() {
  ElMessageBox.confirm(t('admin.settingsActions.resetDefaultConfirm'), t('common.hint'), {
    type: 'warning',
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
  }).then(() => {
    Object.assign(settings, defaults)
    ElMessage.success(t('admin.settingsActions.resetSuccess'))
  })
}

function saveSettings() {
  saving.value = true
  const lang = settings.default_language === 'en' ? 'en-US' : 'zh-CN'
  locale.value = lang
  localStorage.setItem('zjfl_language', lang)
  document.documentElement.setAttribute('lang', lang)
  userApi.updateMe({ language: lang }).catch(() => {})
  setTimeout(() => {
    saving.value = false
    ElMessage.success(t('admin.settingsActions.saveSuccess'))
  }, 800)
}
</script>

<style lang="scss" scoped>
h3 { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.setting-hint {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: var(--space-1);
  line-height: 1.6;
}
</style>
