<template>
  <div class="case-detail" v-loading="loading">
    <template v-if="caseData">
      <!-- 头部信息 -->
      <div class="page-card case-header">
        <div class="case-meta">
          <h2 class="case-number">{{ caseData.case_number }}</h2>
          <span :class="['status-tag', caseData.status]">{{ tr(`case.statusMap.${caseData.status}`, caseData.status) }}</span>
        </div>
        <div class="case-actions">
          <el-button v-if="canStartNegotiation" type="primary" @click="showNegotiationDialog = true">
            {{ t('case.startNegotiation') }}
          </el-button>
          <el-button v-if="canApplyMediation" type="warning" @click="showMediationDialog = true">
            {{ t('case.applyMediation') }}
          </el-button>
          <el-button @click="router.push(`/cases/${caseData.id}/negotiation`)">{{ t('case.enterNegotiation') }}</el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <!-- 基本信息 -->
        <el-col :span="14">
          <div class="page-card">
            <h3 class="section-title">{{ t('case.caseInfo') }}</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="t('case.caseNumber')">{{ caseData.case_number }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.caseStatus')">
                <span :class="['status-tag', caseData.status]">{{ tr(`case.statusMap.${caseData.status}`, caseData.status) }}</span>
              </el-descriptions-item>
              <el-descriptions-item :label="t('case.opponentName')">{{ caseData.opponent_name }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.opponentCountry')">{{ tr(`countries.${caseData.opponent_country || 'OTHER'}`, caseData.opponent_country || 'OTHER') }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.contractType')">{{ tr(`case.contractTypes.${caseData.contract_type}`, caseData.contract_type) }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.expectedMethod')">{{ tr(`case.methods.${caseData.expected_method}`, caseData.expected_method) }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.amount')">
                <strong style="color:#e63946">USD {{ formatMoney(caseData.amount) }}</strong>
              </el-descriptions-item>
              <el-descriptions-item :label="t('common.createTime')">{{ formatDate(caseData.created_at) }}</el-descriptions-item>
              <el-descriptions-item :label="t('case.disputeDesc')" :span="2">{{ caseData.dispute_desc }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 证据列表 -->
          <div class="page-card" style="margin-top: 16px">
            <div class="section-header">
              <h3 class="section-title">{{ t('case.evidenceFiles') }}</h3>
              <el-button size="small" @click="showUploadDialog = true">
                <el-icon><Upload /></el-icon> {{ t('case.uploadEvidence') }}
              </el-button>
            </div>
            <el-table :data="evidences" v-loading="evLoading" size="small">
              <el-table-column prop="file_name" :label="t('case.fileName')" />
              <el-table-column :label="t('case.evidenceType')" width="100">
                <template #default="{ row }">{{ tr(`case.evidenceTypes.${row.evidence_type}`, row.evidence_type) }}</template>
              </el-table-column>
              <el-table-column :label="t('case.storageVoucher')" width="160">
                <template #default="{ row }">
                  <el-tooltip :content="row.storage_voucher">
                    <span class="voucher-code">{{ row.storage_voucher?.slice(0, 12) }}...</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column :label="t('common.uploadTime')" width="140">
                <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
              </el-table-column>
              <el-table-column :label="t('common.actions')" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" @click="previewFile(row)">{{ t('common.preview') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <!-- 时间轴 -->
        <el-col :span="10">
          <div class="page-card timeline-card">
            <h3 class="section-title">{{ t('case.caseTimeline') }}</h3>
            <div class="timeline">
              <div v-for="(item, idx) in caseData.timeline" :key="idx" class="timeline-item">
                <div class="tl-action">{{ item.action || item.event }}</div>
                <div class="tl-meta">{{ item.operator }} · {{ formatDate(item.time) }}</div>
              </div>
            </div>
            <el-empty v-if="!caseData.timeline?.length" :description="t('case.noTimeline')" :image-size="60" />
          </div>
        </el-col>
      </el-row>
    </template>

    <!-- 上传证据对话框 -->
    <el-dialog v-model="showUploadDialog" :title="t('case.uploadDialogTitle')" width="500px">
      <el-form label-position="top">
        <el-form-item :label="t('case.evidenceType')">
          <el-select v-model="uploadForm.evidence_type" :placeholder="t('common.select')" style="width:100%">
            <el-option v-for="(v, k) in evidenceTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('case.selectFile')">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            multiple
            :limit="10"
            accept=".pdf,.jpg,.jpeg,.png,.xlsx,.docx"
            :on-change="handleFileChange"
          >
            <el-button size="small" type="primary">{{ t('case.selectFile') }}</el-button>
            <template #tip>
              <div class="upload-tip">{{ t('case.uploadTip') }}</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="doUpload" :loading="uploading">{{ t('common.upload') }}</el-button>
      </template>
    </el-dialog>

    <!-- 发起协商对话框 -->
    <el-dialog v-model="showNegotiationDialog" :title="t('case.startNegotiation')" width="440px">
      <el-form label-position="top">
        <el-form-item :label="t('case.opponentEmail')">
          <el-input v-model="negotiationEmail" :placeholder="t('case.opponentEmailPlaceholder')" />
        </el-form-item>
        <el-alert type="info" :closable="false" :title="t('case.systemInviteHint')" />
      </el-form>
      <template #footer>
        <el-button @click="showNegotiationDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="doStartNegotiation" :loading="actionLoading">{{ t('case.confirmStart') }}</el-button>
      </template>
    </el-dialog>

    <!-- 申请调解对话框 -->
    <el-dialog v-model="showMediationDialog" :title="t('case.applyMediation')" width="500px">
      <el-form label-position="top">
        <el-form-item :label="t('case.mediationDemand')">
          <el-input v-model="mediationDemand" type="textarea" :rows="4" :placeholder="t('case.mediationDemandPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMediationDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" @click="doApplyMediation" :loading="actionLoading">{{ t('case.submitApplication') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { caseApi, evidenceApi, negotiationApi, mediationApi } from '@/api'

const { t, te } = useI18n()

/** 安全翻译：key 不存在时直接返回原始值，而不是显示 key 本身 */
function tr(key: string, fallback: string) {
  return te(key) ? t(key) : fallback
}
const router = useRouter()
const route = useRoute()
const caseId = Number(route.params.id)

const loading = ref(false)
const evLoading = ref(false)
const caseData = ref<any>(null)
const evidences = ref<any[]>([])
const showUploadDialog = ref(false)
const showNegotiationDialog = ref(false)
const showMediationDialog = ref(false)
const uploading = ref(false)
const actionLoading = ref(false)
const negotiationEmail = ref('')
const mediationDemand = ref('')
const uploadFiles = ref<File[]>([])
const uploadForm = ref({ evidence_type: 'contract' })

const evidenceTypeMap = computed(() => ({
  contract: t('case.evidenceTypes.contract'), bill_of_lading: t('case.evidenceTypes.bill_of_lading'),
  customs: t('case.evidenceTypes.customs'), invoice: t('case.evidenceTypes.invoice'),
  chat_record: t('case.evidenceTypes.chat_record'), other: t('case.evidenceTypes.other'),
}))

const canStartNegotiation = computed(() =>
  caseData.value?.status === 'negotiating' && !caseData.value.negotiation_started_at
)
const canApplyMediation = computed(() =>
  caseData.value?.status === 'negotiating' && caseData.value.negotiation_started_at
)

onMounted(async () => {
  await loadCase()
  await loadEvidences()
})

async function loadCase() {
  loading.value = true
  try {
    const res = await caseApi.getDetail(caseId)
    caseData.value = res.data.data
  } finally {
    loading.value = false
  }
}

async function loadEvidences() {
  evLoading.value = true
  try {
    const res = await evidenceApi.list(caseId)
    evidences.value = res.data.data || []
  } finally {
    evLoading.value = false
  }
}

function handleFileChange(file: any, fileList: any[]) {
  uploadFiles.value = fileList.map((f: any) => f.raw)
}

async function doUpload() {
  if (!uploadFiles.value.length) return ElMessage.warning(t('case.warnings.selectFile'))
  uploading.value = true
  try {
    const formData = new FormData()
    uploadFiles.value.forEach(f => formData.append('files', f))
    formData.append('evidence_type', uploadForm.value.evidence_type)
    await evidenceApi.upload(caseId, formData)
    ElMessage.success(t('case.success.evidenceUploaded'))
    showUploadDialog.value = false
    await loadEvidences()
    await loadCase()
  } finally {
    uploading.value = false
  }
}

async function doStartNegotiation() {
  if (!negotiationEmail.value) return ElMessage.warning(t('case.warnings.inputEmail'))
  actionLoading.value = true
  try {
    await negotiationApi.start({ case_id: caseId, opponent_email: negotiationEmail.value })
    ElMessage.success(t('case.success.negotiationStarted'))
    showNegotiationDialog.value = false
    await loadCase()
  } finally {
    actionLoading.value = false
  }
}

async function doApplyMediation() {
  if (!mediationDemand.value) return ElMessage.warning(t('case.warnings.inputDemand'))
  actionLoading.value = true
  try {
    await mediationApi.apply({ case_id: caseId, demand_text: mediationDemand.value })
    ElMessage.success(t('case.success.mediationApplied'))
    showMediationDialog.value = false
    await loadCase()
    router.push(`/cases/${caseId}/mediation`)
  } finally {
    actionLoading.value = false
  }
}

function previewFile(file: any) {
  window.open(file.file_url, '_blank')
}
function formatMoney(v: number) { return Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) }
function formatDate(d: string) { return d ? dayjs(d).format('MM-DD HH:mm') : '-' }
</script>

<style lang="scss" scoped>
.case-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-4);
}
.case-meta { display: flex; align-items: center; gap: 12px; }
.case-number { font-size: 20px; font-weight: 700; color: var(--color-primary); }
.case-actions { display: flex; gap: var(--space-2); }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: var(--space-4); color: var(--color-text-primary); }
.section-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
}

:deep(.el-descriptions) {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.timeline-card { height: fit-content; }
.timeline { padding: var(--space-2) 0; }
.timeline-item {
  position: relative;
  padding-left: 20px;
  padding-bottom: var(--space-4);
  &::before {
    content: ''; position: absolute; left: 5px; top: 10px; bottom: -2px;
    width: 2px; background: var(--color-border);
  }
  &::after {
    content: ''; position: absolute; left: 1px; top: 6px;
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--color-primary); border: 2px solid var(--color-bg-card);
    box-shadow: 0 0 0 2px var(--color-primary);
  }
  &:last-child::before { display: none; }
  .tl-action { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
  .tl-meta { font-size: 12px; color: var(--color-text-tertiary); }
}
.voucher-code { font-family: monospace; font-size: 12px; color: var(--color-success); }
.upload-tip { font-size: 12px; color: var(--color-text-tertiary); margin-top: var(--space-1); }
</style>
