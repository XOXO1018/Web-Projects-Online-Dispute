<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="mediator-sidebar">
      <div class="logo" @click="router.push('/mediator/dashboard')">
        <img src="/logo.jpg" alt="智链解纷" class="logo-img" />
        <span v-if="!isCollapsed" class="logo-text">{{ t('auth.loginTitle') }}</span>
      </div>
      <div v-if="!isCollapsed" class="platform-label">{{ t('dashboard.roleName.mediator') }}</div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
        background-color="#0d1b2a"
        text-color="rgba(255,255,255,0.6)"
        active-text-color="#fff"
      >
        <el-menu-item index="/mediator/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>{{ t('nav.dashboard') }}</template>
        </el-menu-item>

        <el-sub-menu index="cases-group">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>{{ t('nav.cases') }}</span>
          </template>
          <el-menu-item index="/mediator/cases">
            <el-icon><List /></el-icon>
            <template #title>{{ t('mediator.myCases') }}</template>
          </el-menu-item>
          <el-menu-item index="/mediator/schedule">
            <el-icon><Calendar /></el-icon>
            <template #title>{{ t('mediator.scheduleMeeting') }}</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/mediator/mediation-workspace">
          <el-icon><VideoCamera /></el-icon>
          <template #title>{{ t('mediator.mediationWorkspace') }}</template>
        </el-menu-item>

        <el-menu-item index="/mediator/notifications">
          <el-icon><Bell /></el-icon>
          <template #title>
            <span class="nav-notif-wrapper">
              {{ t('nav.notifications') }}
              <span v-if="unreadCount > 0" class="notif-dot">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </span>
          </template>
        </el-menu-item>
        <el-menu-item index="/mediator/profile">
          <el-icon><User /></el-icon>
          <template #title>{{ t('nav.profile') }}</template>
        </el-menu-item>
      </el-menu>

      <!-- 底部：返回前台 -->
      <div class="sidebar-bottom">
        <el-button
          v-if="isCollapsed"
          text
          style="color: rgba(255,255,255,0.5)"
          @click="router.push('/mediator/dashboard')"
        >
          <el-icon size="18"><House /></el-icon>
        </el-button>
        <el-button v-else text style="color: rgba(255,255,255,0.5); width: 100%" @click="router.push('/mediator/dashboard')">
          <el-icon><House /></el-icon>
          <span style="margin-left: 8px">{{ t('mediator.workspace') }}</span>
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="mediator-header">
        <div class="header-left">
          <el-button text @click="isCollapsed = !isCollapsed" class="collapse-btn">
            <el-icon size="20"><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/mediator/dashboard' }">{{ t('dashboard.roleName.mediator') }}</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="warning" effect="dark" size="small">
            <el-icon style="margin-right:4px"><Avatar /></el-icon> {{ roleLabel }}
          </el-tag>
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-button text @click="router.push('/mediator/notifications')">
              <el-icon size="20"><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar size="small" :style="{ background: '#fa8c16' }">
                {{ authStore.user?.real_name?.[0] || 'M' }}
              </el-avatar>
              <span class="user-name">{{ authStore.user?.real_name }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> {{ t('nav.profile') }}
                </el-dropdown-item>
                <el-dropdown-item command="change-password">
                  <el-icon><Lock /></el-icon> {{ t('profile.changePassword') }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> {{ t('nav.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <!-- 修改密码弹窗 -->
        <el-dialog v-model="showChangePassword" :title="t('profile.changePassword')" :close-on-click-modal="false" width="420px">
          <el-form :model="pwdForm" label-position="top">
            <el-form-item :label="t('profile.oldPassword') || '旧密码'">
              <el-input v-model="pwdOldPassword" type="password" show-password :placeholder="'请输入当前密码'" />
            </el-form-item>
            <el-form-item :label="t('profile.newPassword')">
              <el-input v-model="pwdForm.newPassword" type="password" show-password :placeholder="'至少8位'" />
            </el-form-item>
            <el-form-item :label="t('profile.confirmPassword')">
              <el-input v-model="pwdForm.confirmPassword" type="password" show-password />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showChangePassword = false">{{ t('common.cancel') }}</el-button>
            <el-button type="primary" @click="doChangePassword" :loading="pwdLoading">{{ t('common.confirm') }}</el-button>
          </template>
        </el-dialog>

        <router-view v-slot="{ Component }">
          <transition name="fade">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { notificationApi, authApi } from '@/api'
import { List, Calendar } from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const unreadCount = ref(0)
const showChangePassword = ref(false)
const pwdForm = ref({ newPassword: '', confirmPassword: '' })
const pwdOldPassword = ref('')
const pwdLoading = ref(false)

const activeMenu = computed(() => {
  // 案件详情 / 协商 / 调解 / 会议 等子路由都高亮父级
  const p = route.path
  if (p.startsWith('/mediator/cases/') && p.includes('/mediation')) return '/mediator/mediation-workspace'
  if (p.startsWith('/mediator/cases/') || p.startsWith('/mediator/schedule')) return '/mediator/cases'
  if (p.startsWith('/mediator/meeting')) return '/mediator/mediation-workspace'
  return p
})
const currentTitle = computed(() => {
  const key = String(route.meta.title || '')
  // 包含所有可能出现的 i18n 命名空间前缀
  const knownPrefixes = ['nav.', 'case.', 'admin.', 'mediation.', 'mediator.', 'profile.', 'dashboard.', 'common.']
  return knownPrefixes.some(p => key.startsWith(p)) ? t(key) : key
})

// 根据 specialty 推断真实角色类型
const inferredRole = computed(() => {
  const specialty = authStore.user?.specialty || ''
  if (specialty.includes('英语') || specialty.includes('翻译') || specialty.includes('商务英语')) {
    return 'translator'
  }
  if (specialty.includes('数学') || specialty.includes('分析') || specialty.includes('数据')) {
    return 'analyst'
  }
  return authStore.user?.role || 'mediator'
})

const roleLabel = computed(() => {
  return t(`profile.roles.${inferredRole.value}`)
})

function toggleLanguage() {
  const newLang = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
  locale.value = newLang
  localStorage.setItem('zjfl_language', newLang)
  document.documentElement.setAttribute('lang', newLang)
}

onMounted(async () => {
  loadUnreadCount()
  setInterval(loadUnreadCount, 30000)
})

async function loadUnreadCount() {
  try {
    const res = await notificationApi.list({ page: 1, page_size: 1, unread_only: true })
    unreadCount.value = res.data.data.unread_count || 0
  } catch {}
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    ElMessageBox.confirm(
      t('nav.logoutConfirm'), t('common.hint'),
      { type: 'warning', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    ).then(() => { authStore.logout() })
  } else if (cmd === 'profile') {
    router.push('/mediator/profile')
  } else if (cmd === 'change-password') {
    pwdForm.value = { newPassword: '', confirmPassword: '' }
    pwdOldPassword.value = ''
    showChangePassword.value = true
  }
}

async function doChangePassword() {
  if (!pwdOldPassword.value) {
    ElMessage.error(t('profile.oldPassword') || '请输入旧密码')
    return
  }
  if (pwdForm.value.newPassword !== pwdForm.value.confirmPassword) {
    ElMessage.error(t('profile.pwdMismatch'))
    return
  }
  if (pwdForm.value.newPassword.length < 8) {
    ElMessage.error(t('profile.pwdTooShort') || '密码至少8位')
    return
  }
  pwdLoading.value = true
  try {
    await authApi.changePassword({
      old_password: pwdOldPassword.value,
      new_password: pwdForm.value.newPassword,
    })
    ElMessage.success(t('profile.pwdChanged'))
    showChangePassword.value = false
    pwdOldPassword.value = ''
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
.main-layout { height: 100vh; overflow: hidden; }
.mediator-sidebar {
  background: #0d1b2a;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  .el-menu {
    border-right: none;
    flex: 1;
    .el-menu-item {
      margin: 2px 8px;
      border-radius: var(--radius-md);
      transition: all var(--transition-fast);
      &.is-active {
        background: rgba(250, 140, 22, 0.15) !important;
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 60%;
          background: var(--color-mediator);
          border-radius: 0 3px 3px 0;
        }
      }
    }
  }
}
.logo {
  height: auto;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  padding: 16px 12px 6px;
  .logo-img {
    width: 42px;
    height: 42px;
    object-fit: cover;
    flex-shrink: 0;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.25);
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
  }
  .logo-text {
    color: white;
    font-size: 15px;
    font-weight: 700;
    white-space: nowrap;
    line-height: 1.4;
  }
}
.platform-label {
  text-align: center;
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  padding: 0 16px 10px;
  line-height: 1.4;
}
.sidebar-bottom {
  padding: 8px 0;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.mediator-header {
  height: var(--header-height);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: none;
}
.header-left, .header-right { display: flex; align-items: center; gap: 16px; }
.user-info {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 8px; border-radius: var(--radius-md);
  transition: background var(--transition-fast);
  &:hover { background: var(--color-bg-page); }
}
.user-name { font-size: 14px; color: var(--color-text-primary); }
.main-content { background: var(--color-bg-page); overflow-y: auto; padding: var(--space-6); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.nav-notif-wrapper {
  display: inline-flex; align-items: center; gap: 8px;
  .notif-dot {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 18px; height: 18px; padding: 0 5px;
    font-size: 11px; font-weight: 600; line-height: 1;
    color: var(--color-bg-card); background: var(--color-danger); border-radius: 9px;
  }
}
.header-right {
  :deep(.el-badge__content) { top: -4px; right: 2px; }
}
</style>
