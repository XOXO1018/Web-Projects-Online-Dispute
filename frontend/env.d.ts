/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 全局组件类型声明
declare module '@element-plus/icons-vue' {
  import type { DefineComponent } from 'vue'
  const icons: Record<string, DefineComponent<{}, {}, any>>
  export default icons
}
