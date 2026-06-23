import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'Login', component: () => import('@/views/auth/LoginView.vue') },
      { path: 'register', name: 'Register', component: () => import('@/views/auth/RegisterView.vue') },
    ],
  },

  // ===================== 管理员后台（独立布局） =====================
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['platform_admin'] },
    children: [
      { path: '', redirect: 'dashboard' },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/AdminDashboard.vue'),
        meta: { title: 'admin.dashboard' },
      },
      {
        path: 'enterprises',
        name: 'AdminEnterprises',
        component: () => import('@/views/admin/EnterprisesView.vue'),
        meta: { title: 'admin.enterprises' },
      },
      {
        path: 'mediators',
        name: 'AdminMediators',
        component: () => import('@/views/admin/MediatorsView.vue'),
        meta: { title: 'admin.mediators' },
      },
      {
        path: 'cases',
        name: 'AdminCases',
        component: () => import('@/views/admin/AdminCasesView.vue'),
        meta: { title: 'admin.cases' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/AdminUsersView.vue'),
        meta: { title: 'admin.users' },
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/AdminSettingsView.vue'),
        meta: { title: 'admin.settings' },
      },
    ],
  },

  // ===================== 调解员平台（独立布局） =====================
  {
    path: '/mediator',
    component: () => import('@/layouts/MediatorLayout.vue'),
    meta: { requiresAuth: true, roles: ['mediator'] },
    children: [
      { path: '', redirect: 'dashboard' },
      {
        path: 'dashboard',
        name: 'MediatorDashboard',
        component: () => import('@/views/mediator/MediatorDashboard.vue'),
        meta: { title: 'nav.dashboard' },
      },
      {
        path: 'cases',
        name: 'MediatorCases',
        component: () => import('@/views/mediator/MediatorCasesView.vue'),
        meta: { title: 'mediator.myCases' },
      },
      {
        path: 'cases/create',
        name: 'MediatorCaseCreate',
        component: () => import('@/views/cases/CaseCreateView.vue'),
        meta: { title: 'case.create' },
      },
      {
        path: 'cases/:id',
        name: 'MediatorCaseDetail',
        component: () => import('@/views/mediator/MediatorCaseDetail.vue'),
        meta: { title: 'case.caseInfo' },
      },
      {
        path: 'cases/:id/negotiation',
        name: 'MediatorNegotiation',
        component: () => import('@/views/mediator/MediatorNegotiationView.vue'),
        meta: { title: 'nav.negotiation' },
      },
      {
        path: 'cases/:id/mediation',
        name: 'MediatorMediation',
        component: () => import('@/views/mediation/MediationView.vue'),
        meta: { title: 'nav.mediation' },
      },
      {
        path: 'schedule',
        name: 'MediatorSchedule',
        component: () => import('@/views/mediator/MediatorScheduleView.vue'),
        meta: { title: 'mediator.scheduleMeeting' },
      },
      {
        path: 'mediation-workspace',
        name: 'MediatorMediationWorkspace',
        component: () => import('@/views/mediator/MediatorMediationWorkspace.vue'),
        meta: { title: 'mediator.mediationWorkspace' },
      },
      {
        path: 'meeting/:channelName',
        name: 'MediatorMeeting',
        component: () => import('@/views/mediation/MeetingRoomView.vue'),
        meta: { title: 'admin.meetingRoom' },
      },
      {
        path: 'notifications',
        name: 'MediatorNotifications',
        component: () => import('@/views/NotificationsView.vue'),
        meta: { title: 'nav.notifications' },
      },
      {
        path: 'profile',
        name: 'MediatorProfile',
        component: () => import('@/views/mediator/MediatorProfile.vue'),
        meta: { title: 'nav.profile' },
      },
    ],
  },

  // ===================== 企业用户平台（独立布局） =====================
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, roles: ['enterprise_admin', 'legal', 'salesperson'] },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: 'nav.dashboard' },
      },
      {
        path: 'cases',
        name: 'Cases',
        component: () => import('@/views/cases/CaseListView.vue'),
        meta: { title: 'nav.cases' },
      },
      {
        path: 'cases/create',
        name: 'CaseCreate',
        component: () => import('@/views/cases/CaseCreateView.vue'),
        meta: { title: 'case.create' },
      },
      {
        path: 'cases/:id',
        name: 'CaseDetail',
        component: () => import('@/views/cases/CaseDetailView.vue'),
        meta: { title: 'case.caseInfo' },
      },
      {
        path: 'cases/:id/negotiation',
        name: 'Negotiation',
        component: () => import('@/views/negotiation/NegotiationView.vue'),
        meta: { title: 'nav.negotiation' },
      },
      {
        path: 'cases/:id/mediation',
        name: 'Mediation',
        component: () => import('@/views/mediation/MediationView.vue'),
        meta: { title: 'nav.mediation' },
      },
      {
        path: 'meeting/:channelName',
        name: 'Meeting',
        component: () => import('@/views/mediation/MeetingRoomView.vue'),
        meta: { title: 'admin.meetingRoom' },
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('@/views/NotificationsView.vue'),
        meta: { title: 'nav.notifications' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { title: 'nav.profile' },
      },
    ],
  },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  NProgress.start()
  const authStore = useAuthStore()

  // 有 token 但 user 尚未加载（如刷新页面），先恢复用户信息
  if (authStore.token && !authStore.user) {
    await authStore.fetchCurrentUser()
  }

  // 需要登录但未登录 → 跳转登录
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 角色权限检查
  if (to.meta.roles && authStore.user) {
    const roles = to.meta.roles as string[]
    if (!roles.includes(authStore.user.role)) {
      // 管理员访问企业页面 → 跳管理后台，调解员访问企业页面 → 跳调解员工作台，企业用户访问管理后台 → 跳工作台
      if (authStore.user.role === 'platform_admin') next('/admin/dashboard')
      else if (authStore.user.role === 'mediator') next('/mediator/dashboard')
      else next('/dashboard')
      return
    }
  }

  // 已登录用户访问登录/注册页 → 跳对应首页
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isLoggedIn) {
    if (authStore.isAdmin) next('/admin/dashboard')
    else if (authStore.user?.role === 'mediator') next('/mediator/dashboard')
    else next('/dashboard')
    return
  }

  // 根路径重定向
  if (to.path === '/' && authStore.isLoggedIn) {
    if (authStore.isAdmin) next('/admin/dashboard')
    else if (authStore.user?.role === 'mediator') next('/mediator/dashboard')
    else next('/dashboard')
    return
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
