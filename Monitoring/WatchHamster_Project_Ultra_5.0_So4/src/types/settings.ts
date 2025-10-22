/**
 * 설정 관련 타입 정의
 * 애플리케이션 전체 설정을 위한 타입들
 */

import { z } from 'zod'
import { NewsSettings } from './news'
import { SystemSettings } from './system'
import { WebhookSettings } from './webhook'

// ===== 기본 설정 타입 =====
export type ThemeMode = 'light' | 'dark' | 'auto'
export type Language = 'ko' | 'en'
export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'

// ===== API 설정 스키마 =====
export const ApiSettingsSchema = z.object({
  infomax_api: z.object({
    base_url: z.string().url(),
    timeout: z.number().min(5).max(120), // seconds
    retry_attempts: z.number().min(0).max(10),
    retry_delay: z.number().min(1).max(30), // seconds
    rate_limit: z.object({
      enabled: z.boolean(),
      requests_per_minute: z.number().min(1).max(1000),
    }),
    headers: z.record(z.string(), z.string()).optional(),
    auth: z.object({
      type: z.enum(['none', 'api_key', 'bearer']),
      api_key: z.string().optional(),
      token: z.string().optional(),
      header_name: z.string().optional(),
    }),
  }),
  backend_api: z.object({
    base_url: z.string().url(),
    timeout: z.number().min(5).max(60),
    retry_attempts: z.number().min(0).max(5),
    websocket_url: z.string().url(),
    websocket_reconnect: z.object({
      enabled: z.boolean(),
      max_attempts: z.number().min(1).max(20),
      delay: z.number().min(1000).max(30000), // milliseconds
    }),
  }),
})

// ===== UI 설정 스키마 =====
export const UiSettingsSchema = z.object({
  theme: z.enum(['light', 'dark', 'auto']),
  language: z.enum(['ko', 'en']),
  posco_branding: z.boolean(),
  animations: z.boolean(),
  sound_notifications: z.boolean(),
  auto_refresh: z.object({
    enabled: z.boolean(),
    interval: z.number().min(1000).max(300000), // 1초 ~ 5분
  }),
  dashboard: z.object({
    layout: z.enum(['grid', 'list', 'compact']),
    show_charts: z.boolean(),
    chart_update_interval: z.number().min(1000).max(60000),
    max_recent_alerts: z.number().min(5).max(100),
  }),
  tables: z.object({
    page_size: z.number().min(10).max(100),
    show_pagination: z.boolean(),
    sortable_columns: z.boolean(),
    filterable_columns: z.boolean(),
  }),
  notifications: z.object({
    enabled: z.boolean(),
    position: z.enum(['top-right', 'top-left', 'bottom-right', 'bottom-left']),
    duration: z.number().min(1000).max(30000), // milliseconds
    max_visible: z.number().min(1).max(10),
    sound: z.boolean(),
  }),
})

// ===== 로깅 설정 스키마 =====
export const LoggingSettingsSchema = z.object({
  level: z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']),
  max_entries: z.number().min(100).max(50000),
  retention_days: z.number().min(1).max(365),
  auto_cleanup: z.boolean(),
  file_logging: z.object({
    enabled: z.boolean(),
    file_path: z.string().optional(),
    max_file_size: z.number().min(1).max(1000), // MB
    max_files: z.number().min(1).max(50),
    rotation: z.enum(['daily', 'weekly', 'size-based']),
  }),
  remote_logging: z.object({
    enabled: z.boolean(),
    endpoint: z.string().url().optional(),
    api_key: z.string().optional(),
    batch_size: z.number().min(1).max(1000),
    flush_interval: z.number().min(1000).max(60000), // milliseconds
  }),
  filters: z.object({
    exclude_components: z.array(z.string()),
    exclude_levels: z.array(z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])),
    include_only: z.array(z.string()).optional(),
  }),
})

// ===== 보안 설정 스키마 =====
export const SecuritySettingsSchema = z.object({
  encryption: z.object({
    enabled: z.boolean(),
    algorithm: z.enum(['AES-256', 'AES-128']),
    key_rotation: z.object({
      enabled: z.boolean(),
      interval_days: z.number().min(1).max(365),
    }),
  }),
  session: z.object({
    timeout: z.number().min(300).max(86400), // 5분 ~ 24시간
    auto_logout: z.boolean(),
    concurrent_sessions: z.number().min(1).max(10),
  }),
  api_security: z.object({
    rate_limiting: z.boolean(),
    ip_whitelist: z.array(z.string()).optional(),
    require_https: z.boolean(),
    cors_origins: z.array(z.string()),
  }),
  data_protection: z.object({
    mask_sensitive_data: z.boolean(),
    audit_logging: z.boolean(),
    data_retention_days: z.number().min(1).max(2555), // 7년
  }),
})

// ===== 백업 설정 스키마 =====
export const BackupSettingsSchema = z.object({
  enabled: z.boolean(),
  auto_backup: z.object({
    enabled: z.boolean(),
    interval: z.enum(['daily', 'weekly', 'monthly']),
    time: z.string(), // HH:MM 형식
    max_backups: z.number().min(1).max(100),
  }),
  backup_location: z.object({
    type: z.enum(['local', 'cloud', 'network']),
    path: z.string(),
    credentials: z.record(z.string(), z.string()).optional(),
  }),
  backup_content: z.object({
    settings: z.boolean(),
    logs: z.boolean(),
    data: z.boolean(),
    git_state: z.boolean(),
    user_data: z.boolean(),
  }),
  compression: z.object({
    enabled: z.boolean(),
    algorithm: z.enum(['gzip', 'zip', 'tar.gz']),
    level: z.number().min(1).max(9),
  }),
  encryption: z.object({
    enabled: z.boolean(),
    password_protected: z.boolean(),
  }),
})

// ===== 전체 애플리케이션 설정 스키마 =====
export const AppSettingsSchema = z.object({
  version: z.string(),
  last_updated: z.string(),
  api: ApiSettingsSchema,
  ui: UiSettingsSchema,
  logging: LoggingSettingsSchema,
  security: SecuritySettingsSchema,
  backup: BackupSettingsSchema,
  news: z.any(), // NewsSettings 타입 참조
  system: z.any(), // SystemSettings 타입 참조
  webhook: z.any(), // WebhookSettings 타입 참조
})

// ===== 타입 추출 =====
export type ApiSettings = z.infer<typeof ApiSettingsSchema>
export type UiSettings = z.infer<typeof UiSettingsSchema>
export type LoggingSettings = z.infer<typeof LoggingSettingsSchema>
export type SecuritySettings = z.infer<typeof SecuritySettingsSchema>
export type BackupSettings = z.infer<typeof BackupSettingsSchema>
export type AppSettings = z.infer<typeof AppSettingsSchema>

// ===== 설정 그룹 타입 =====
export interface SettingsGroup {
  id: string
  name: string
  description: string
  icon?: string
  sections: SettingsSection[]
}

export interface SettingsSection {
  id: string
  name: string
  description?: string
  fields: SettingsField[]
}

export interface SettingsField {
  id: string
  name: string
  description?: string
  type: 'text' | 'number' | 'boolean' | 'select' | 'multiselect' | 'textarea' | 'password' | 'url' | 'email' | 'time' | 'date'
  value: any
  default_value: any
  required?: boolean
  validation?: {
    min?: number
    max?: number
    pattern?: string
    custom?: (value: any) => boolean | string
  }
  options?: Array<{
    label: string
    value: any
    description?: string
  }>
  dependencies?: Array<{
    field_id: string
    condition: 'equals' | 'not_equals' | 'greater_than' | 'less_than'
    value: any
  }>
  sensitive?: boolean // 민감한 정보 (비밀번호 등)
}

// ===== 설정 변경 이력 타입 =====
export interface SettingsChange {
  id: string
  field_path: string
  old_value: any
  new_value: any
  changed_by: string
  changed_at: string
  reason?: string
  auto_applied: boolean
}

export interface SettingsChangeHistory {
  changes: SettingsChange[]
  total: number
  page: number
  size: number
}

// ===== 설정 검증 타입 =====
export interface SettingsValidationResult {
  valid: boolean
  errors: Array<{
    field_path: string
    message: string
    severity: 'error' | 'warning'
  }>
  warnings: Array<{
    field_path: string
    message: string
  }>
}

// ===== 설정 내보내기/가져오기 타입 =====
export interface SettingsExport {
  version: string
  exported_at: string
  exported_by: string
  settings: Partial<AppSettings>
  metadata: {
    app_version: string
    platform: string
    hostname: string
  }
}

export interface SettingsImport {
  file: File
  options: {
    merge: boolean // true: 기존 설정과 병합, false: 완전 교체
    validate: boolean
    backup_before_import: boolean
    sections: string[] // 가져올 섹션 선택
  }
}

export interface SettingsImportResult {
  success: boolean
  imported_sections: string[]
  skipped_sections: string[]
  errors: string[]
  warnings: string[]
  backup_id?: string
}

// ===== 설정 기본값 타입 =====
export interface DefaultSettings {
  api: ApiSettings
  ui: UiSettings
  logging: LoggingSettings
  security: SecuritySettings
  backup: BackupSettings
  news: NewsSettings
  system: SystemSettings
  webhook: WebhookSettings
}

// ===== API 요청/응답 타입 =====
export interface GetSettingsRequest {
  sections?: string[]
  include_sensitive?: boolean
}

export interface GetSettingsResponse {
  settings: AppSettings
  last_updated: string
  version: string
}

export interface UpdateSettingsRequest {
  settings: Partial<AppSettings>
  reason?: string
  validate_only?: boolean
}

export interface UpdateSettingsResponse {
  settings: AppSettings
  validation_result: SettingsValidationResult
  applied_changes: SettingsChange[]
  restart_required: boolean
}

export interface ResetSettingsRequest {
  sections?: string[]
  confirm: boolean
}

export interface ResetSettingsResponse {
  reset_sections: string[]
  backup_id: string
  restart_required: boolean
}

export interface ExportSettingsRequest {
  sections?: string[]
  include_sensitive?: boolean
  format?: 'json' | 'yaml'
}

export interface ExportSettingsResponse {
  export_data: SettingsExport
  download_url: string
  expires_at: string
}

export interface ImportSettingsRequest {
  import_data: SettingsExport
  options: SettingsImport['options']
}

export interface ImportSettingsResponse {
  result: SettingsImportResult
  restart_required: boolean
}

// ===== 설정 컴포넌트 Props 타입 =====
export interface SettingsFormProps {
  settings: AppSettings
  onSettingsChange: (settings: Partial<AppSettings>) => void
  onSave: () => void
  onReset: (sections?: string[]) => void
  onExport: () => void
  onImport: (file: File, options: SettingsImport['options']) => void
  loading?: boolean
  validation?: SettingsValidationResult
}

export interface SettingsSectionProps {
  section: SettingsSection
  values: Record<string, any>
  onChange: (fieldId: string, value: any) => void
  errors?: Record<string, string>
  disabled?: boolean
}

export interface SettingsFieldProps {
  field: SettingsField
  value: any
  onChange: (value: any) => void
  error?: string
  disabled?: boolean
}

export interface SettingsSearchProps {
  onSearch: (query: string) => void
  onFilterChange: (filters: SettingsFilter) => void
  results?: SettingsSearchResult[]
}

// ===== 설정 검색 타입 =====
export interface SettingsFilter {
  sections?: string[]
  types?: SettingsField['type'][]
  modified_only?: boolean
  has_errors?: boolean
}

export interface SettingsSearchResult {
  field_path: string
  field_name: string
  section_name: string
  description?: string
  current_value: any
  match_score: number
}

// ===== 설정 마이그레이션 타입 =====
export interface SettingsMigration {
  from_version: string
  to_version: string
  migrations: Array<{
    field_path: string
    action: 'rename' | 'move' | 'transform' | 'remove'
    new_path?: string
    transformer?: (value: any) => any
  }>
}

export interface SettingsMigrationResult {
  success: boolean
  migrated_fields: string[]
  removed_fields: string[]
  errors: string[]
  backup_id: string
}

// ===== 설정 동기화 타입 =====
export interface SettingsSync {
  enabled: boolean
  remote_url?: string
  sync_interval: number // minutes
  last_sync: string | null
  conflicts: SettingsConflict[]
}

export interface SettingsConflict {
  field_path: string
  local_value: any
  remote_value: any
  last_modified_local: string
  last_modified_remote: string
  resolution: 'local' | 'remote' | 'manual' | 'pending'
}

// ===== 설정 템플릿 타입 =====
export interface SettingsTemplate {
  id: string
  name: string
  description: string
  category: 'development' | 'production' | 'testing' | 'custom'
  settings: Partial<AppSettings>
  created_at: string
  created_by: string
  is_system: boolean
}

export interface ApplyTemplateRequest {
  template_id: string
  sections?: string[]
  merge: boolean
}

export interface ApplyTemplateResponse {
  applied_sections: string[]
  conflicts: SettingsConflict[]
  backup_id: string
  restart_required: boolean
}