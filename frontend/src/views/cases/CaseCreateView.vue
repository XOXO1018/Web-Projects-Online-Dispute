<template>
  <div class="case-create">
    <div class="page-card">
      <h3>{{ t('case.create') }}</h3>
      <p class="subtitle">{{ t('case.createHint') }}</p>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" style="margin-top: 24px">
        <el-divider>{{ t('case.opponentInfo') }}</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="t('case.opponentName')" prop="opponent_name">
              <el-input v-model="form.opponent_name" :placeholder="t('case.opponentNamePlaceholder')" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('case.opponentCountry')" prop="opponent_country">
              <el-select v-model="form.opponent_country" :placeholder="t('case.selectCountry')" style="width:100%">
                <el-option v-for="c in aseanCountries" :key="c.code" :label="t(`countries.${c.code}`)" :value="c.code" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>{{ t('case.contractInfo') }}</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="t('case.contractType')" prop="contract_type">
              <el-select v-model="form.contract_type" style="width:100%">
                <el-option :label="t('case.contractTypes.goods_sale')" value="goods_sale" />
                <el-option :label="t('case.contractTypes.cross_border_ecom')" value="cross_border_ecom" />
                <el-option :label="t('case.contractTypes.logistics')" value="logistics" />
                <el-option :label="t('case.contractTypes.other')" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('case.contractDate')" prop="contract_date">
              <el-date-picker v-model="form.contract_date" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('case.incidentDate')" prop="incident_date">
              <el-date-picker v-model="form.incident_date" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('case.amount')" prop="amount">
              <el-input-number v-model="form.amount" :min="1" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('case.expectedMethod')" prop="expected_method">
              <el-select v-model="form.expected_method" style="width:100%">
                <el-option :label="t('case.methods.negotiation')" value="negotiation" />
                <el-option :label="t('case.methods.mediation')" value="mediation" />
                <el-option :label="t('case.methods.arbitration')" value="arbitration" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>{{ t('case.disputeInfo') }}</el-divider>
        <el-form-item :label="t('case.disputeDesc')" prop="dispute_desc">
          <el-input
            v-model="form.dispute_desc"
            type="textarea"
            :rows="5"
            :placeholder="t('case.disputeDescPlaceholder')"
          />
        </el-form-item>

        <div style="text-align: right; margin-top: 16px">
          <el-button @click="router.back()">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="loading">{{ t('case.submitCreate') }}</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { caseApi } from '@/api'

const { t } = useI18n()
const router = useRouter()
const formRef = ref()
const loading = ref(false)

const aseanCountries = [
  { code: 'VN' }, { code: 'TH' },
  { code: 'ID' }, { code: 'MY' },
  { code: 'PH' }, { code: 'SG' },
  { code: 'MM' }, { code: 'KH' },
  { code: 'LA' }, { code: 'BN' },
  { code: 'OTHER' },
]

const form = ref({
  opponent_name: '',
  opponent_country: '',
  contract_type: 'goods_sale',
  amount: 10000,
  dispute_desc: '',
  contract_date: null as any,
  incident_date: null as any,
  expected_method: 'negotiation',
})

const rules = {
  opponent_name: [{ required: true, message: t('case.validation.requiredOpponentName') }],
  opponent_country: [{ required: true, message: t('case.validation.requiredOpponentCountry') }],
  contract_type: [{ required: true, message: t('case.validation.requiredContractType') }],
  amount: [{ required: true, message: t('case.validation.requiredAmount') }],
  dispute_desc: [{ required: true, message: t('case.validation.requiredDisputeDesc') }],
  contract_date: [{ required: true, message: t('case.validation.requiredContractDate') }],
  incident_date: [{ required: true, message: t('case.validation.requiredIncidentDate') }],
  expected_method: [{ required: true, message: t('case.validation.requiredMethod') }],
}

async function handleSubmit() {
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await caseApi.create({
        ...form.value,
        contract_date: new Date(form.value.contract_date).toISOString(),
        incident_date: new Date(form.value.incident_date).toISOString(),
      })
      ElMessage.success(t('case.createSuccess'))
      router.push(`/cases/${res.data.data.id}`)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.case-create { max-width: 100%; }
h3 { font-size: 20px; font-weight: 700; color: var(--color-text-primary); }
.subtitle { color: var(--color-text-tertiary); font-size: 14px; margin-top: var(--space-1); }

:deep(.el-divider__text) {
  font-weight: 600;
  color: var(--color-text-primary);
}
</style>
