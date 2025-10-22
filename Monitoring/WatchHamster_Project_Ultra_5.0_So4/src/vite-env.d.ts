/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly DEV: boolean
  readonly PROD: boolean
  // 필요한 다른 환경 변수들 추가
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}