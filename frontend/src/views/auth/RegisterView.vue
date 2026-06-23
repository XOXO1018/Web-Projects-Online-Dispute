<template>
  <div class="register-form">
    <h2>{{ t('auth.registerTitle') }}</h2>
    <p class="subtitle">{{ t('auth.registerSubtitle') }}</p>

    <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
      <el-divider>{{ t('auth.enterpriseInfo') }}</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item :label="t('auth.creditCode')" prop="credit_code">
            <el-input v-model="form.credit_code" :placeholder="t('auth.creditCodePlaceholder')" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.enterpriseName')" prop="enterprise_name">
            <el-input v-model="form.enterprise_name" :placeholder="t('auth.enterpriseNamePlaceholder')" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.legalPerson')" prop="legal_person">
            <el-input v-model="form.legal_person" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.businessLicense')" prop="business_license">
            <el-input v-model="form.business_license" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider>{{ t('auth.contactInfo') }}</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item :label="t('auth.realName')" prop="real_name">
            <el-input v-model="form.real_name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.legalIdCard')" prop="legal_id_card">
            <el-input v-model="form.legal_id_card" :placeholder="t('auth.legalIdCardPlaceholder')" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.contactPhone')" prop="contact_phone">
            <el-input v-model="form.contact_phone" :placeholder="t('auth.contactPhonePlaceholder')" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.email')" prop="email">
            <el-input v-model="form.email" type="email" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.loginPassword')" prop="password">
            <el-input v-model="form.password" type="password" show-password :placeholder="t('auth.passwordPlaceholder2')" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="t('auth.captcha')" prop="captchaCode">
            <div class="captcha-row">
              <el-input v-model="form.captchaCode" :placeholder="t('auth.captchaPlaceholder')" />
              <img v-if="captchaImage" :src="captchaImage" @click="loadCaptcha" class="captcha-img" />
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-button type="primary" size="large" @click="handleRegister" :loading="loading" style="width:100%">
        {{ t('auth.register') }}
      </el-button>
    </el-form>

    <div class="footer-links">
      {{ t('auth.hasAccount') }}<router-link to="/auth/login">{{ t('auth.loginNow') }}</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'

const { t } = useI18n()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const captchaImage = ref('')
const captchaToken = ref('')

const form = ref({
  credit_code: '',
  enterprise_name: '',
  legal_person: '',
  legal_id_card: '',
  business_license: '',
  contact_phone: '',
  email: '',
  real_name: '',
  password: '',
  captchaCode: '',
})

const rules = {
  credit_code: [
    { required: true, message: t('auth.validation.requiredCreditCode') },
    { len: 18, message: t('auth.validation.creditCodeLength') },
  ],
  enterprise_name: [{ required: true, message: t('auth.validation.requiredEnterpriseName') }],
  legal_person: [{ required: true, message: t('auth.validation.requiredLegalPerson') }],
  business_license: [{ required: true, message: t('auth.validation.requiredBusinessLicense') }],
  real_name: [{ required: true, message: t('auth.validation.requiredRealName') }],
  email: [{ required: true, type: 'email', message: t('auth.validation.validEmail') }],
  password: [{ required: true, min: 8, message: t('auth.validation.passwordMin') }],
  captchaCode: [{ required: true, message: t('auth.validation.requiredCaptcha') }],
}

onMounted(loadCaptcha)

async function loadCaptcha() {
  try {
    const res = await authApi.getCaptcha()
    captchaImage.value = res.data.data.image
    captchaToken.value = res.data.data.captcha_id  // 对齐 demo_server 返回字段
  } catch {
    // 验证码加载失败时静默处理，用户可点击重试
  }
}

async function handleRegister() {
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      const payload = {
        ...form.value,
        captcha_id: captchaToken.value,   // 对齐 demo_server 字段名
        captcha_code: form.value.captchaCode,
      }
      await authApi.register(payload)
      ElMessage.success(t('auth.registerSuccess'))
      router.push('/auth/login')
    } finally {
      loading.value = false
      loadCaptcha()
    }
  })
}
</script>

<style lang="scss" scoped>
.register-form {
  h2 {
    font-size: 24px;
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: 6px;
  }

  .subtitle {
    color: var(--color-text-tertiary);
    margin-bottom: 28px;
    font-size: 14px;
  }
}

.captcha-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.captcha-img {
  height: 36px;
  cursor: pointer;
  border: 1px solid var(--color-border-dark);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);

  &:hover { border-color: var(--color-primary); }
}

.footer-links {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: var(--color-text-tertiary);

  a {
    color: var(--color-primary);
    font-weight: 500;
    margin-left: 4px;
  }
}
</style>
