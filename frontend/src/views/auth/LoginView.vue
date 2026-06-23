<template>
  <div class="login-form">
    <h2>{{ t('auth.loginTitle') }}</h2>
    <p class="subtitle">{{ t('auth.loginSubtitle') }}</p>

    <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @submit.prevent="handleLogin">
      <el-form-item :label="t('auth.email')" prop="loginField">
        <el-input v-model="form.loginField" :placeholder="t('auth.loginFieldPlaceholder')" size="large" />
      </el-form-item>

      <el-form-item :label="t('auth.password')" prop="password">
        <el-input v-model="form.password" type="password" :placeholder="t('auth.passwordPlaceholder')" size="large" show-password />
      </el-form-item>

      <el-form-item :label="t('auth.captcha')" prop="captchaCode">
        <div class="captcha-row">
          <el-input v-model="form.captchaCode" :placeholder="t('auth.captchaPlaceholder')" size="large" style="flex:1" />
          <img
            v-if="captchaImage"
            :src="captchaImage"
            @click="loadCaptcha"
            class="captcha-img"
            :title="t('auth.clickRefresh')"
          />
          <el-button v-else @click="loadCaptcha" size="large">{{ t('auth.getCaptcha') }}</el-button>
        </div>
      </el-form-item>

      <el-button type="primary" size="large" @click="handleLogin" :loading="loading" class="login-btn" native-type="submit">
        {{ t('auth.login') }}
      </el-button>
    </el-form>

    <div class="footer-links">
      <span>{{ t('auth.noAccount') }}</span>
      <router-link to="/auth/register">{{ t('auth.registerNow') }}</router-link>
    </div>

    <div class="demo-hint">
      <el-alert type="info" :closable="false" show-icon>
        <template #title>{{ t('auth.demoHint') }}</template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)
const captchaImage = ref('')
const captchaToken = ref('')

const form = ref({ loginField: '', password: '', captchaCode: '' })
const rules = {
  loginField: [{ required: true, message: t('auth.validation.requiredEmail') }],
  password: [{ required: true, message: t('auth.validation.requiredPassword') }],
  captchaCode: [{ required: true, message: t('auth.validation.requiredCaptcha') }],
}

onMounted(loadCaptcha)

async function loadCaptcha() {
  try {
    const res = await authApi.getCaptcha()
    captchaImage.value = res.data.data.image
    captchaToken.value = res.data.data.captcha_id
    form.value.captchaCode = ''
  } catch {
    ElMessage.error(t('auth.captchaLoadFailed'))
  }
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.login(
        form.value.loginField,
        form.value.password,
        captchaToken.value,
        form.value.captchaCode,
      )
      ElMessage.success(t('auth.loginSuccess'))
      // 根据角色跳转不同首页
      if (authStore.isAdmin) {
        router.push('/admin/dashboard')
      } else {
        router.push('/dashboard')
      }
    } catch {
      loadCaptcha()
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.login-form {
  h2 {
    font-size: 28px;
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: 6px;
    letter-spacing: 0.5px;
    animation: fadeInUp 0.5s ease-out;
  }

  .subtitle {
    color: var(--color-text-tertiary);
    margin-bottom: 36px;
    font-size: 14px;
    line-height: 1.5;
    animation: fadeInUp 0.5s ease-out 0.1s both;
  }
}

:deep(.el-form) {
  animation: fadeInUp 0.5s ease-out 0.2s both;
}

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-img {
  height: 40px;
  border: 1px solid var(--color-border-dark);
  border-radius: var(--radius-md);
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--transition-fast);

  &:hover {
    border-color: var(--color-primary);
    transform: scale(1.02);
    box-shadow: 0 2px 8px rgba(22, 119, 255, 0.15);
  }
}

.login-btn {
  width: 100%;
  margin-top: 12px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(22, 119, 255, 0.3);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
}

.footer-links {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--color-text-tertiary);
  animation: fadeInUp 0.5s ease-out 0.3s both;

  a {
    color: var(--color-primary);
    margin-left: 4px;
    font-weight: 500;
    transition: all var(--transition-fast);

    &:hover {
      color: var(--color-primary-light);
      text-decoration: underline;
    }
  }
}

.demo-hint {
  margin-top: 20px;
  animation: fadeInUp 0.5s ease-out 0.4s both;

  :deep(.el-alert) {
    border-radius: var(--radius-md);
    border: 1px dashed var(--color-border);
  }
}

// 动画定义
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
