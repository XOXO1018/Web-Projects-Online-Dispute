import { api } from './http'

// 认证相关
export const authApi = {
  getCaptcha: () => api.get('/api/v1/captcha/image'),
  login: (data: any) => api.post('/api/v1/auth/login', data),
  register: (data: any) => api.post('/api/v1/auth/register', data),
  logout: () => api.post('/api/v1/auth/logout'),
  changePassword: (data: any) => api.post('/api/v1/auth/change-password', data),
}

// 用户相关（/api/v1/auth/me 兼容 demo_server 和生产端）
export const userApi = {
  getMe: () => api.get('/api/v1/auth/me'),
  updateMe: (data: any) => api.put('/api/v1/users/me', data),
  sendSignCode: () => api.get('/api/v1/users/send-sign-code'),
}

// 企业相关
export const enterpriseApi = {
  getMyEnterprise: () => api.get('/api/v1/enterprises/my'),
}

// 案件相关
export const caseApi = {
  create: (data: any) => api.post('/api/v1/cases', data),
  list: (params: any) => api.get('/api/v1/cases', { params }),
  getDetail: (id: number) => api.get(`/api/v1/cases/${id}`),
  archive: (id: number) => api.put(`/api/v1/cases/${id}/archive`),
  updateStatus: (id: number, data: any) => api.put(`/api/v1/cases/${id}/status`, data),
  // 使用专门的统计接口，不再硬编码案件ID
  statistics: () => api.get('/api/v1/cases/stats'),
}

// 证据相关（路径与 demo_server 对齐：/api/v1/cases/{case_id}/evidence）
export const evidenceApi = {
  upload: (caseId: number, formData: FormData) =>
    api.post(`/api/v1/cases/${caseId}/evidence`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  list: (caseId: number) => api.get(`/api/v1/cases/${caseId}/evidence`),
  delete: (caseId: number, evidenceId: number) =>
    api.delete(`/api/v1/cases/${caseId}/evidence/${evidenceId}`),
}

// 协商相关（消息路径对齐：/api/v1/cases/{case_id}/messages）
export const negotiationApi = {
  start: (data: any) => api.post('/api/v1/negotiation/start', data),
  getMessages: (caseId: number, params?: any) =>
    api.get(`/api/v1/cases/${caseId}/messages`, { params }),
  sendMessage: (caseId: number, data: any) =>
    api.post(`/api/v1/cases/${caseId}/messages`, data),
  confirmResult: (data: any) => api.post('/api/v1/negotiation/confirm-result', data),
  signMemo: (data: any) => api.post('/api/v1/negotiation/sign-memo', data),
}

// 文件上传相关（协商室图片/文件）
export const uploadApi = {
  uploadImage: (formData: FormData) =>
    api.post('/api/v1/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  uploadFile: (formData: FormData) =>
    api.post('/api/v1/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}

// 调解相关（推荐调解员路径对齐：/api/v1/mediators/recommend/{case_id}）
export const mediationApi = {
  apply: (data: any) => api.post('/api/v1/mediation/apply', data),
  recommendMediators: (caseId: number) =>
    api.get(`/api/v1/mediators/recommend/${caseId}`),
  selectMediator: (data: any) => api.post('/api/v1/mediation/select-mediator', data),
  scheduleMeeting: (data: any) => api.post('/api/v1/mediation/schedule-meeting', data),
  getMeetingToken: (meetingId: number) => api.get(`/api/v1/mediation/meetings/${meetingId}/token`),
  submitOpinion: (data: any) => api.post('/api/v1/mediation/opinion', data),
  signAgreement: (agreementId: number, smsCode: string) =>
    api.post(`/api/v1/mediation/agreements/${agreementId}/sign`, null, {
      params: { sms_code: smsCode },
    }),
  exportMaterials: (caseId: number) => api.get(`/api/v1/mediation/export/${caseId}`),
  mediatorIntervene: (data: { case_id: number; mediator_id: number }) =>
    api.post('/api/v1/negotiation/mediator-intervene', data),
}

// 在线状态
export const onlineApi = {
  checkStatus: () => api.get('/api/v1/users/online-status'),
}

// 调解员相关
export const mediatorApi = {
  getMe: () => api.get('/api/v1/mediators/me'),
  updateMe: (data: any) => api.put('/api/v1/mediators/me', data),
  getMyCases: (params: any) => api.get('/api/v1/mediators/my-cases', { params }),
  getMyMeetings: () => api.get('/api/v1/mediator/meetings'),
}

// 案件会议
export const meetingApi = {
  getCaseMeetings: (caseId: number) => api.get(`/api/v1/cases/${caseId}/meetings`),
}

// 通知相关（使用 PATCH 与 demo_server 对齐）
export const notificationApi = {
  list: (params?: any) => api.get('/api/v1/notifications', { params }),
  markRead: (id: number) => api.patch(`/api/v1/notifications/${id}/read`),
  markAllRead: () => api.patch('/api/v1/notifications/read-all'),
}

// 管理后台
export const adminApi = {
  dashboard: () => api.get('/api/v1/admin/dashboard'),
  listEnterprises: (params: any) => api.get('/api/v1/admin/enterprises', { params }),
  auditEnterprise: (id: number, action: string) =>
    api.post(`/api/v1/admin/enterprises/${id}/audit`, { action }),
  listMediators: (params: any) => api.get('/api/v1/admin/mediators', { params }),
  createMediator: (data: any) => api.post('/api/v1/admin/mediators', data),
  deleteMediator: (id: number) => api.delete(`/api/v1/admin/mediators/${id}`),
  updateMediatorStatus: (id: number, status: string) =>
    api.put(`/api/v1/admin/mediators/${id}/status`, { status }),
  updateMediator: (id: number, data: any) =>
    api.put(`/api/v1/admin/mediators/${id}`, data),
  listAllCases: (params: any) => api.get('/api/v1/admin/cases', { params }),
  deleteCase: (id: number) => api.delete(`/api/v1/admin/cases/${id}`),
  getCaseProgress: (id: number) => api.get(`/api/v1/cases/${id}/progress`),
  listUsers: (params: any) => api.get('/api/v1/admin/users', { params }),
  updateUserStatus: (id: number, status: string) =>
    api.put(`/api/v1/admin/users/${id}/status`, { status }),
}

// 案件笔记
export const caseNoteApi = {
  list: (caseId: number) => api.get(`/api/v1/cases/${caseId}/notes`),
  create: (caseId: number, data: any) => api.post(`/api/v1/cases/${caseId}/notes`, data),
  delete: (caseId: number, noteId: number) => api.delete(`/api/v1/cases/${caseId}/notes/${noteId}`),
}

// 案件状态管理
export const caseStatusApi = {
  update: (caseId: number, data: any) =>
    api.put(`/api/v1/cases/${caseId}/status`, data),
}
