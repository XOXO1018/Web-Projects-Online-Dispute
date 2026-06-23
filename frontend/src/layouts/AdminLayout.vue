<template>
  <el-container class="admin-layout">
    <!-- 管理员侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="admin-sidebar">
      <div class="logo" @click="router.push('/admin/dashboard')">
        <img src="/logo.jpg" alt="智链解纷" class="logo-img" />
        <span v-if="!isCollapsed" class="logo-text">{{ t('admin.title') }}</span>
      </div>
      <div v-if="!isCollapsed" class="platform-label">{{ t('auth.loginSubtitle') }}</div>

      <el-menu
        :default-active="adminCurrentRoute"
        :collapse="isCollapsed"
        router
        background-color="#0d1b2a"
        text-color="rgba(255,255,255,0.6)"
        active-text-color="#fff"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>{{ t('admin.dashboard') }}</template>
        </el-menu-item>

        <el-menu-item index="/admin/enterprises">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>{{ t('admin.enterprises') }}</template>
        </el-menu-item>

        <el-menu-item index="/admin/mediators">
          <el-icon><Avatar /></el-icon>
          <template #title>{{ t('admin.staff') }}</template>
        </el-menu-item>

        <el-menu-item index="/admin/cases">
          <el-icon><Folder /></el-icon>
          <template #title>{{ t('admin.cases') }}</template>
        </el-menu-item>

        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>{{ t('admin.users') }}</template>
        </el-menu-item>

        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <template #title>{{ t('admin.settings') }}</template>
        </el-menu-item>
      </el-menu>

      <!-- 底部：返回前台 -->
      <div class="sidebar-bottom">
        <el-button
          v-if="isCollapsed"
          text
          style="color: rgba(255,255,255,0.5)"
          @click="router.push('/dashboard')"
        >
          <el-icon size="18"><House /></el-icon>
        </el-button>
        <el-button v-else text style="color: rgba(255,255,255,0.5); width: 100%" @click="router.push('/dashboard')">
          <el-icon><House /></el-icon>
          <span style="margin-left: 8px">{{ t('nav.backToFront') }}</span>
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <!-- 管理员顶部栏 -->
      <el-header class="admin-header">
        <div class="header-left">
          <el-button text @click="isCollapsed = !isCollapsed" class="collapse-btn">
            <el-icon size="20"><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">{{ t('admin.title') }}</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="danger" effect="dark" size="small">
            <el-icon style="margin-right:4px"><Shield /></el-icon> {{ t('admin.roleName') }}
          </el-tag>
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar size="small" :style="{ background: '#e63946' }">
                {{ authStore.user?.real_name?.[0] || 'A' }}
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
                  <el-icon><Lock /></el-icon> {{ t('nav.changePassword') }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> {{ t('nav.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 管理员主内容区 -->
      <el-main class="admin-content">
        <!-- 修改密码弹窗 -->
        <el-dialog v-model="showChangePassword" :title="t('nav.changePassword')" :close-on-click-modal="false" width="420px">
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t, locale } = useI18n()

const isCollapsed = ref(false)
const showChangePassword = ref(false)
const pwdForm = ref({ newPassword: '', confirmPassword: '' })
const pwdLoading = ref(false)

const adminCurrentRoute = computed(() => route.path)
const currentTitle = computed(() => String(route.meta.title || ''))

onMounted(async () => {
  if (authStore.user?.must_change_password) {
    showChangePassword.value = true
  }
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
.admin-layout {
  height: 100vh;
  overflow: hidden;
}
.admin-sidebar {
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
        background: rgba(22, 119, 255, 0.15) !important;
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 60%;
          background: var(--color-primary);
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
.admin-header {
  height: var(--header-height);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: none;
}
.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
  &:hover { background: var(--color-bg-page); }
}
.user-name { font-size: 14px; color: var(--color-text-primary); }
.admin-content {
  background: var(--color-bg-page);
  overflow-y: auto;
  padding: var(--space-6);
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
