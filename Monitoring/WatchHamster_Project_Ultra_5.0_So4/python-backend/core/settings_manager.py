"""
설정 파일 관리 시스템
JSON 형식 설정 파일 읽기/쓰기, 설정 검증 및 기본값 처리, 즉시 저장 메커니즘
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from pydantic import BaseModel, ValidationError
import asyncio
import aiofiles
from threading import Lock

from models.settings import (
    AppSettings, 
    SettingsValidationResult, 
    SettingsValidationError,
    SettingsValidationWarning,
    SettingsChange,
    SettingsExport,
    SettingsImportResult,
    SettingsImportOptions
)

logger = logging.getLogger(__name__)

class SettingsManager:
    """설정 파일 관리 시스템"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.settings_file = self.config_dir / "settings.json"
        self.backup_dir = self.config_dir / "backups"
        self.temp_dir = self.config_dir / "temp"
        
        # 스레드 안전성을 위한 락
        self._lock = Lock()
        
        # 현재 설정 캐시
        self._current_settings: Optional[AppSettings] = None
        self._last_modified: Optional[datetime] = None
        
        # 변경 감지를 위한 콜백
        self._change_callbacks: List[callable] = []
        
        # 자동 저장 설정
        self._auto_save_enabled = True
        self._auto_save_delay = 1.0  # 1초 후 저장
        self._pending_save_task: Optional[asyncio.Task] = None
        
        # 초기화
        self._ensure_directories()
        self._load_default_settings()
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"설정 디렉토리 생성 완료: {self.config_dir}")
        except Exception as e:
            logger.error(f"설정 디렉토리 생성 실패: {e}")
            raise
    
    def _load_default_settings(self):
        """기본 설정 로드"""
        try:
            # 환경변수에서 기본값 로드
            default_data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "api": {
                    "infomax_api": {
                        "base_url": os.getenv("INFOMAX_API_URL", "https://global-api.einfomax.co.kr/apis/posco/news"),
                        "timeout": int(os.getenv("API_TIMEOUT", "30")),
                        "retry_attempts": int(os.getenv("API_RETRY_ATTEMPTS", "3")),
                        "retry_delay": int(os.getenv("API_RETRY_DELAY", "5")),
                        "rate_limit": {},
                        "headers": {},
                        "auth": {"type": "none"}
                    },
                    "backend_api": {
                        "base_url": os.getenv("BACKEND_API_URL", "http://localhost:8000"),
                        "timeout": int(os.getenv("BACKEND_TIMEOUT", "30")),
                        "retry_attempts": int(os.getenv("BACKEND_RETRY_ATTEMPTS", "3")),
                        "websocket_url": os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws"),
                        "websocket_reconnect": {
                            "enabled": True,
                            "max_attempts": 10,
                            "delay": 5000
                        }
                    }
                },
                "ui": {
                    "theme": "light",
                    "language": "ko",
                    "posco_branding": True,
                    "animations": True,
                    "sound_notifications": False,
                    "auto_refresh": {"enabled": True, "interval": 5000},
                    "dashboard": {
                        "layout": "grid",
                        "show_charts": True,
                        "chart_update_interval": 5000,
                        "max_recent_alerts": 10
                    },
                    "tables": {
                        "page_size": 20,
                        "show_pagination": True,
                        "sortable_columns": True,
                        "filterable_columns": True
                    },
                    "notifications": {
                        "enabled": True,
                        "position": "top-right",
                        "duration": 5000,
                        "max_visible": 5,
                        "sound": False
                    }
                },
                "logging": {
                    "level": "INFO",
                    "max_entries": 10000,
                    "retention_days": 30,
                    "auto_cleanup": True,
                    "file_logging": {
                        "enabled": True,
                        "file_path": None,
                        "max_file_size": 100,
                        "max_files": 10,
                        "rotation": "daily"
                    },
                    "remote_logging": {
                        "enabled": False,
                        "endpoint": None,
                        "api_key": None,
                        "batch_size": 100,
                        "flush_interval": 30000
                    },
                    "filters": {
                        "exclude_components": [],
                        "exclude_levels": [],
                        "include_only": None
                    }
                },
                "security": {
                    "encryption": {
                        "enabled": False,
                        "algorithm": "AES-256",
                        "key_rotation": {}
                    },
                    "session": {
                        "timeout": 3600,
                        "auto_logout": True,
                        "concurrent_sessions": 1
                    },
                    "api_security": {
                        "rate_limiting": True,
                        "ip_whitelist": None,
                        "require_https": True,
                        "cors_origins": []
                    },
                    "data_protection": {
                        "mask_sensitive_data": True,
                        "audit_logging": True,
                        "data_retention_days": 365
                    }
                },
                "backup": {
                    "enabled": False,
                    "auto_backup": {
                        "enabled": False,
                        "interval": "daily",
                        "time": "02:00",
                        "max_backups": 7
                    },
                    "backup_location": {
                        "type": "local",
                        "path": str(self.backup_dir),
                        "credentials": None
                    },
                    "backup_content": {
                        "settings": True,
                        "logs": False,
                        "data": True,
                        "git_state": True,
                        "user_data": True
                    },
                    "compression": {
                        "enabled": True,
                        "algorithm": "gzip",
                        "level": 6
                    },
                    "encryption": {
                        "enabled": False,
                        "password_protected": False
                    }
                }
            }
            
            # 웹훅 URL 환경변수에서 로드
            webhook_data = {
                "posco_webhook_url": os.getenv("POSCO_WEBHOOK_URL", ""),
                "watchhamster_webhook_url": os.getenv("WATCHHAMSTER_WEBHOOK_URL", ""),
                "timeout": int(os.getenv("WEBHOOK_TIMEOUT", "10")),
                "retry_attempts": int(os.getenv("WEBHOOK_RETRY_ATTEMPTS", "3"))
            }
            default_data["webhook"] = webhook_data
            
            self._default_settings = AppSettings(**default_data)
            logger.info("기본 설정 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 설정 로드 실패: {e}")
            raise
    
    async def load_settings(self, force_reload: bool = False) -> AppSettings:
        """설정 파일 로드"""
        with self._lock:
            try:
                # 캐시된 설정이 있고 파일이 변경되지 않았으면 캐시 반환
                if not force_reload and self._current_settings and self._is_file_unchanged():
                    return self._current_settings
                
                if self.settings_file.exists():
                    # 파일에서 설정 로드
                    async with aiofiles.open(self.settings_file, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        settings_data = json.loads(content)
                    
                    # 설정 객체 생성
                    self._current_settings = AppSettings(**settings_data)
                    self._last_modified = datetime.fromtimestamp(self.settings_file.stat().st_mtime)
                    
                    logger.info("설정 파일 로드 완료")
                else:
                    # 파일이 없으면 기본 설정 사용
                    self._current_settings = self._default_settings.copy(deep=True)
                    await self.save_settings(self._current_settings)
                    logger.info("기본 설정으로 초기화")
                
                return self._current_settings
                
            except json.JSONDecodeError as e:
                logger.error(f"설정 파일 JSON 파싱 오류: {e}")
                await self._handle_corrupted_settings()
                return self._current_settings
            except ValidationError as e:
                logger.error(f"설정 데이터 검증 오류: {e}")
                await self._handle_invalid_settings(e)
                return self._current_settings
            except Exception as e:
                logger.error(f"설정 로드 실패: {e}")
                # 오류 시 기본 설정 반환
                self._current_settings = self._default_settings.copy(deep=True)
                return self._current_settings
    
    def _is_file_unchanged(self) -> bool:
        """파일이 변경되지 않았는지 확인"""
        try:
            if not self.settings_file.exists():
                return False
            
            current_modified = datetime.fromtimestamp(self.settings_file.stat().st_mtime)
            return self._last_modified and current_modified <= self._last_modified
        except Exception:
            return False
    
    async def _handle_corrupted_settings(self):
        """손상된 설정 파일 처리"""
        try:
            # 손상된 파일 백업
            corrupted_backup = self.backup_dir / f"corrupted_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(self.settings_file, corrupted_backup)
            logger.warning(f"손상된 설정 파일 백업: {corrupted_backup}")
            
            # 기본 설정으로 복원
            self._current_settings = self._default_settings.copy(deep=True)
            await self.save_settings(self._current_settings)
            
            logger.info("손상된 설정 파일을 기본값으로 복원")
            
        except Exception as e:
            logger.error(f"손상된 설정 파일 처리 실패: {e}")
    
    async def _handle_invalid_settings(self, validation_error: ValidationError):
        """유효하지 않은 설정 처리"""
        try:
            # 유효하지 않은 설정 백업
            invalid_backup = self.backup_dir / f"invalid_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(self.settings_file, invalid_backup)
            logger.warning(f"유효하지 않은 설정 파일 백업: {invalid_backup}")
            
            # 기본 설정으로 복원
            self._current_settings = self._default_settings.copy(deep=True)
            await self.save_settings(self._current_settings)
            
            logger.info(f"유효하지 않은 설정 파일을 기본값으로 복원: {validation_error}")
            
        except Exception as e:
            logger.error(f"유효하지 않은 설정 파일 처리 실패: {e}")
    
    async def save_settings(self, settings: AppSettings, create_backup: bool = True) -> bool:
        """설정 파일 저장"""
        with self._lock:
            try:
                # 백업 생성
                if create_backup and self.settings_file.exists():
                    await self._create_backup()
                
                # 설정 업데이트
                settings.last_updated = datetime.now()
                
                # 임시 파일에 먼저 저장 (원자적 쓰기)
                temp_file = self.temp_dir / f"settings_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
                    content = json.dumps(
                        settings.dict(), 
                        indent=2, 
                        ensure_ascii=False, 
                        default=str
                    )
                    await f.write(content)
                
                # 임시 파일을 실제 파일로 이동 (원자적 연산)
                shutil.move(str(temp_file), str(self.settings_file))
                
                # 캐시 업데이트
                self._current_settings = settings
                self._last_modified = datetime.now()
                
                logger.info("설정 파일 저장 완료")
                
                # 변경 콜백 호출
                await self._notify_change_callbacks(settings)
                
                return True
                
            except Exception as e:
                logger.error(f"설정 저장 실패: {e}")
                # 임시 파일 정리
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except:
                    pass
                return False
    
    async def _create_backup(self) -> str:
        """설정 백업 생성"""
        try:
            backup_filename = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(self.settings_file, backup_path)
            
            # 오래된 백업 정리 (최대 50개 유지)
            await self._cleanup_old_backups(max_backups=50)
            
            logger.info(f"설정 백업 생성: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"설정 백업 생성 실패: {e}")
            raise
    
    async def _cleanup_old_backups(self, max_backups: int = 50):
        """오래된 백업 파일 정리"""
        try:
            backup_files = list(self.backup_dir.glob("settings_backup_*.json"))
            
            if len(backup_files) > max_backups:
                # 생성 시간 순으로 정렬
                backup_files.sort(key=lambda x: x.stat().st_ctime)
                
                # 오래된 파일 삭제
                for old_backup in backup_files[:-max_backups]:
                    old_backup.unlink()
                    logger.debug(f"오래된 백업 파일 삭제: {old_backup.name}")
                
                logger.info(f"오래된 백업 파일 {len(backup_files) - max_backups}개 정리 완료")
                
        except Exception as e:
            logger.error(f"백업 파일 정리 실패: {e}")
    
    async def update_settings(self, updates: Dict[str, Any], reason: Optional[str] = None) -> Tuple[AppSettings, List[SettingsChange]]:
        """설정 업데이트"""
        try:
            current = await self.load_settings()
            changes = []
            
            # 변경사항 추적
            for field_path, new_value in updates.items():
                old_value = self._get_nested_value(current.dict(), field_path)
                
                if old_value != new_value:
                    change = SettingsChange(
                        id=f"change_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        field_path=field_path,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by="system",
                        changed_at=datetime.now(),
                        reason=reason,
                        auto_applied=True
                    )
                    changes.append(change)
            
            # 설정 업데이트 적용
            updated_data = current.dict()
            for field_path, new_value in updates.items():
                self._set_nested_value(updated_data, field_path, new_value)
            
            # 새 설정 객체 생성
            updated_settings = AppSettings(**updated_data)
            
            # 검증
            validation_result = await self.validate_settings(updated_settings)
            if not validation_result.valid:
                raise ValueError(f"설정 검증 실패: {validation_result.errors}")
            
            # 저장
            if await self.save_settings(updated_settings):
                logger.info(f"설정 업데이트 완료: {len(changes)}개 변경")
                return updated_settings, changes
            else:
                raise RuntimeError("설정 저장 실패")
                
        except Exception as e:
            logger.error(f"설정 업데이트 실패: {e}")
            raise
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """중첩된 딕셔너리에서 값 가져오기"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """중첩된 딕셔너리에 값 설정"""
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    async def validate_settings(self, settings: AppSettings) -> SettingsValidationResult:
        """설정 유효성 검증"""
        errors = []
        warnings = []
        
        try:
            # API 설정 검증
            api_settings = settings.api
            
            # INFOMAX API URL 검증
            if not api_settings.infomax_api.base_url.startswith(('http://', 'https://')):
                errors.append(SettingsValidationError(
                    field_path="api.infomax_api.base_url",
                    message="API URL은 http:// 또는 https://로 시작해야 합니다",
                    severity="error"
                ))
            
            # 타임아웃 값 검증
            if api_settings.infomax_api.timeout < 5 or api_settings.infomax_api.timeout > 120:
                errors.append(SettingsValidationError(
                    field_path="api.infomax_api.timeout",
                    message="API 타임아웃은 5-120초 사이여야 합니다",
                    severity="error"
                ))
            
            # 웹훅 설정 검증 (있는 경우)
            if hasattr(settings, 'webhook') and settings.webhook:
                webhook_settings = settings.webhook
                
                # 웹훅 URL 검증
                for webhook_name, webhook_url in [
                    ("posco_webhook_url", getattr(webhook_settings, 'posco_webhook_url', '')),
                    ("watchhamster_webhook_url", getattr(webhook_settings, 'watchhamster_webhook_url', ''))
                ]:
                    if webhook_url and not webhook_url.startswith('https://'):
                        errors.append(SettingsValidationError(
                            field_path=f"webhook.{webhook_name}",
                            message="웹훅 URL은 https://로 시작해야 합니다",
                            severity="error"
                        ))
            
            # UI 설정 검증
            ui_settings = settings.ui
            
            # 자동 새로고침 간격 검증
            if ui_settings.auto_refresh.interval < 1000:
                warnings.append(SettingsValidationWarning(
                    field_path="ui.auto_refresh.interval",
                    message="자동 새로고침 간격이 너무 짧습니다 (1초 미만)"
                ))
            
            # 로깅 설정 검증
            logging_settings = settings.logging
            
            # 로그 보존 기간 검증
            if logging_settings.retention_days > 365:
                warnings.append(SettingsValidationWarning(
                    field_path="logging.retention_days",
                    message="로그 보존 기간이 1년을 초과합니다"
                ))
            
            # 보안 설정 검증
            security_settings = settings.security
            
            # 세션 타임아웃 검증
            if security_settings.session.timeout < 300:
                warnings.append(SettingsValidationWarning(
                    field_path="security.session.timeout",
                    message="세션 타임아웃이 너무 짧습니다 (5분 미만)"
                ))
            
            is_valid = len(errors) == 0
            
            logger.info(f"설정 검증 완료: 유효={is_valid}, 오류={len(errors)}개, 경고={len(warnings)}개")
            
            return SettingsValidationResult(
                valid=is_valid,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"설정 검증 중 오류: {e}")
            return SettingsValidationResult(
                valid=False,
                errors=[SettingsValidationError(
                    field_path="",
                    message=f"검증 중 오류 발생: {str(e)}",
                    severity="error"
                )],
                warnings=[]
            )
    
    async def reset_settings(self, sections: Optional[List[str]] = None) -> Tuple[AppSettings, str]:
        """설정 초기화"""
        try:
            # 현재 설정 백업
            backup_filename = await self._create_backup()
            
            if sections:
                # 특정 섹션만 초기화
                current = await self.load_settings()
                current_data = current.dict()
                default_data = self._default_settings.dict()
                
                for section in sections:
                    if section in default_data:
                        current_data[section] = default_data[section]
                
                reset_settings = AppSettings(**current_data)
            else:
                # 전체 초기화
                reset_settings = self._default_settings.copy(deep=True)
            
            # 저장
            if await self.save_settings(reset_settings):
                logger.info(f"설정 초기화 완료: {sections or '전체'}")
                return reset_settings, backup_filename
            else:
                raise RuntimeError("설정 저장 실패")
                
        except Exception as e:
            logger.error(f"설정 초기화 실패: {e}")
            raise
    
    def add_change_callback(self, callback: callable):
        """설정 변경 콜백 추가"""
        self._change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: callable):
        """설정 변경 콜백 제거"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    async def _notify_change_callbacks(self, settings: AppSettings):
        """설정 변경 콜백 호출"""
        for callback in self._change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(settings)
                else:
                    callback(settings)
            except Exception as e:
                logger.error(f"설정 변경 콜백 호출 실패: {e}")
    
    async def enable_auto_save(self, delay: float = 1.0):
        """자동 저장 활성화"""
        self._auto_save_enabled = True
        self._auto_save_delay = delay
        logger.info(f"자동 저장 활성화: {delay}초 지연")
    
    def disable_auto_save(self):
        """자동 저장 비활성화"""
        self._auto_save_enabled = False
        if self._pending_save_task:
            self._pending_save_task.cancel()
        logger.info("자동 저장 비활성화")
    
    async def schedule_auto_save(self, settings: AppSettings):
        """자동 저장 예약"""
        if not self._auto_save_enabled:
            return
        
        # 기존 예약된 저장 취소
        if self._pending_save_task:
            self._pending_save_task.cancel()
        
        # 새로운 저장 예약
        self._pending_save_task = asyncio.create_task(
            self._delayed_save(settings)
        )
    
    async def _delayed_save(self, settings: AppSettings):
        """지연된 저장 실행"""
        try:
            await asyncio.sleep(self._auto_save_delay)
            await self.save_settings(settings)
        except asyncio.CancelledError:
            logger.debug("자동 저장 취소됨")
        except Exception as e:
            logger.error(f"자동 저장 실패: {e}")
    
    def get_current_settings(self) -> Optional[AppSettings]:
        """현재 캐시된 설정 반환"""
        return self._current_settings
    
    def get_default_settings(self) -> AppSettings:
        """기본 설정 반환"""
        return self._default_settings.copy(deep=True)
    
    async def get_settings_info(self) -> Dict[str, Any]:
        """설정 파일 정보 조회"""
        try:
            info = {
                "settings_file": str(self.settings_file),
                "exists": self.settings_file.exists(),
                "size": 0,
                "last_modified": None,
                "backup_count": 0,
                "is_valid": False
            }
            
            if self.settings_file.exists():
                stat = self.settings_file.stat()
                info["size"] = stat.st_size
                info["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # 유효성 검증
                try:
                    settings = await self.load_settings()
                    validation_result = await self.validate_settings(settings)
                    info["is_valid"] = validation_result.valid
                except:
                    info["is_valid"] = False
            
            # 백업 파일 개수
            backup_files = list(self.backup_dir.glob("settings_backup_*.json"))
            info["backup_count"] = len(backup_files)
            
            return info
            
        except Exception as e:
            logger.error(f"설정 정보 조회 실패: {e}")
            return {}

# 전역 설정 관리자 인스턴스
_settings_manager: Optional[SettingsManager] = None

def get_settings_manager() -> SettingsManager:
    """설정 관리자 인스턴스 반환"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

async def initialize_settings_manager(config_dir: str = "config") -> SettingsManager:
    """설정 관리자 초기화"""
    global _settings_manager
    _settings_manager = SettingsManager(config_dir)
    
    # 초기 설정 로드
    await _settings_manager.load_settings()
    
    logger.info("설정 관리자 초기화 완료")
    return _settings_manager