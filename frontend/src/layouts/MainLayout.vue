<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo" @click="router.push('/dashboard')">
        <img src="/logo.jpg" alt="智链解纷" class="logo-img" />
        <span v-if="!isCollapsed" class="logo-text">{{ t('auth.loginTitle') }}</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapsed"
        router
        background-color="#001529"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <template #title>{{ t('nav.dashboard') }}</template>
        </el-menu-item>
        <el-menu-item index="/cases">
          <el-icon><Folder /></el-icon>
          <template #title>{{ t('nav.cases') }}</template>
        </el-menu-item>
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <template #title>
            <span class="nav-notif-wrapper">
              {{ t('nav.notifications') }}
              <span v-if="unreadCount > 0" class="notif-dot">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </span>
          </template>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <template #title>{{ t('nav.profile') }}</template>
        </el-menu-item>
      </el-menu>
      <!-- 侧边栏底部 -->
      <div v-if="!isCollapsed" class="sidebar-footer">
        <div class="ent-info">
          <el-icon size="16"><OfficeBuilding /></el-icon>
          <span class="ent-name">{{ authStore.user?.enterprise_name || t('dashboard.enterpriseInfo') }}</span>
        </div>
      </div>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-button text @click="isCollapsed = !isCollapsed" class="collapse-btn">
            <el-icon size="20"><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <!-- 语言切换快捷按钮 -->
          <el-button text size="small" @click="toggleLanguage" class="lang-btn">
            🌐 {{ locale === 'zh-CN' ? 'EN' : '中' }}
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">{{ t('nav.dashboard') }}</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-button text @click="router.push('/notifications')">
              <el-icon size="20"><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar size="small" :style="{ background: '#1677ff' }">
                {{ authStore.user?.real_name?.[0] || 'U' }}
              </el-avatar>
              <span class="user-name">{{ authStore.user?.real_name }}</span>
              <el-tag size="small" type="info" class="role-tag">{{ roleLabel }}</el-tag>
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
        <!-- 强制修改密码弹窗 -->
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
import { useNotificationStore } from '@/stores/notification'
import { notificationApi, authApi } from '@/api'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const isCollapsed = ref(false)
const unreadCount = computed(() => notificationStore.unreadCount)
const showChangePassword = ref(false)
const pwdForm = ref({ newPassword: '', confirmPassword: '' })
const pwdLoading = ref(false)

const currentRoute = computed(() => route.path)
const currentTitle = computed(() => {
  const key = String(route.meta.title || '')
  return key.startsWith('nav.') || key.startsWith('case.') || key.startsWith('admin.') || key.startsWith('mediation.')
    ? t(key) : key
})

const roleLabel = computed(() => {
  return t(`profile.roles.${authStore.user?.role || 'enterprise_admin'}`)
})

function toggleLanguage() {
  const newLang = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
  locale.value = newLang
  localStorage.setItem('zjfl_language', newLang)
  document.documentElement.setAttribute('lang', newLang)
}

onMounted(async () => {
  notificationStore.fetchUnreadCount()
  if (authStore.user?.must_change_password) {
    showChangePassword.value = true
  }
  setInterval(() => notificationStore.fetchUnreadCount(), 30000)
})

const pwdOldPassword = ref('')

async function doChangePassword() {
  if (!pwdOldPassword.value) {
    ElMessage.error(t('profile.pwdMismatch'))
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

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    ElMessageBox.confirm(
      t('nav.logoutConfirm'),
      t('common.hint'),
      {
        type: 'warning',
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
      }
    ).then(() => {
      authStore.logout()
    })
  } else if (cmd === 'profile') {
    router.push('/profile')
  } else if (cmd === 'change-password') {
    pwdForm.value = { newPassword: '', confirmPassword: '' }
    showChangePassword.value = true
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: var(--color-admin-sidebar);
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
      height: 44px;
      line-height: 44px;
      transition: all var(--transition-fast);

      &:hover {
        background: rgba(255, 255, 255, 0.06) !important;
      }

      &.is-active {
        background: rgba(22, 119, 255, 0.15) !important;
        color: #fff;
        position: relative;

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 20px;
          background: var(--color-primary);
          border-radius: 0 3px 3px 0;
        }
      }
    }
  }
}

.logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  padding: 0 12px;
  flex-shrink: 0;

  .logo-img {
    width: 40px;
    height: 40px;
    object-fit: cover;
    flex-shrink: 0;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.2);
  }

  .logo-text {
    color: white;
    font-size: 15px;
    font-weight: 700;
    white-space: nowrap;
    letter-spacing: 1px;
    line-height: 1.4;
  }
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);

  .ent-info {
    display: flex;
    align-items: center;
    gap: 6px;
    color: rgba(255, 255, 255, 0.35);
    font-size: 12px;
  }

  .ent-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.header {
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  height: var(--header-height);
  box-shadow: none;
  z-index: 10;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-btn {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);

  &:hover {
    color: var(--color-primary);
    background: var(--color-primary-bg);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);

  &:hover { background: var(--color-bg-hover); }
}

.user-name {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.role-tag { margin-left: -4px; }

.main-content {
  background: var(--color-bg-page);
  overflow-y: auto;
  padding: var(--space-6);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 侧边栏消息角标与文字并排 */
.nav-notif-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  .notif-dot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    height: 18px;
    padding: 0 5px;
    font-size: 11px;
    font-weight: 600;
    line-height: 1;
    color: #fff;
    background: #f56c6c;
    border-radius: var(--radius-full);
  }
}

/* 顶部栏消息角标定位 */
.header-right {
  :deep(.el-badge__content) {
    top: -4px;
    right: 2px;
  }
}
</style>
