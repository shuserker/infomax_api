"""
설정 백업/복원 시스템
설정 내보내기/가져오기, 자동 복구 로직
"""

import json
import logging
import os
import shutil
import zipfile
import gzip
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import asyncio
import aiofiles
from pydantic import ValidationError

from models.settings import (
    AppSettings,
    SettingsExport,
    SettingsExportMetadata,
    SettingsImportOptions,
    SettingsImportResult,
    SettingsValidationResult
)

logger = logging.getLogger(__name__)

class SettingsBackupManager:
    """설정 백업/복원 관리자"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.backup_dir = self.config_dir / "backups"
        self.export_dir = self.config_dir / "exports"
        self.temp_dir = self.config_dir / "temp"
        
        # 디렉토리 생성
        self._ensure_directories()
        
        # 지원되는 압축 형식
        self.compression_formats = {
            'gzip': self._compress_gzip,
            'zip': self._compress_zip,
            'none': self._compress_none
        }
        
        self.decompression_formats = {
            'gzip': self._decompress_gzip,
            'zip': self._decompress_zip,
            'none': self._decompress_none
        }
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.export_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            logger.info("백업 디렉토리 생성 완료")
        except Exception as e:
            logger.error(f"백업 디렉토리 생성 실패: {e}")
            raise
    
    async def export_settings(
        self,
        settings: AppSettings,
        sections: Optional[List[str]] = None,
        include_sensitive: bool = False,
        format_type: str = "json",
        compression: str = "none",
        password: Optional[str] = None
    ) -> SettingsExport:
        """설정 내보내기"""
        try:
            # 내보낼 설정 데이터 준비
            settings_data = settings.dict()
            
            # 특정 섹션만 내보내기
            if sections:
                filtered_data = {}
                for section in sections:
                    if section in settings_data:
                        filtered_data[section] = settings_data[section]
                settings_data = filtered_data
            
            # 민감한 정보 제거
            if not include_sensitive:
                settings_data = self._remove_sensitive_data(settings_data)
            
            # 메타데이터 생성
            metadata = SettingsExportMetadata(
                app_version=settings.version,
                platform=os.name,
                hostname=os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            )
            
            # 내보내기 객체 생성
            export_data = SettingsExport(
                version="1.0.0",
                exported_at=datetime.now(),
                exported_by="system",
                settings=settings_data,
                metadata=metadata
            )
            
            logger.info(f"설정 내보내기 완료: {len(sections or settings_data.keys())}개 섹션")
            return export_data
            
        except Exception as e:
            logger.error(f"설정 내보내기 실패: {e}")
            raise
    
    def _remove_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """민감한 데이터 제거"""
        sensitive_fields = [
            'api_key', 'token', 'password', 'secret', 'credential',
            'webhook_url', 'private_key', 'auth_token'
        ]
        
        def remove_sensitive_recursive(obj):
            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    # 키 이름에 민감한 단어가 포함되어 있으면 제거
                    if any(sensitive in key.lower() for sensitive in sensitive_fields):
                        result[key] = "[REDACTED]"
                    else:
                        result[key] = remove_sensitive_recursive(value)
                return result
            elif isinstance(obj, list):
                return [remove_sensitive_recursive(item) for item in obj]
            else:
                return obj
        
        return remove_sensitive_recursive(data)
    
    async def save_export_to_file(
        self,
        export_data: SettingsExport,
        filename: Optional[str] = None,
        compression: str = "none",
        password: Optional[str] = None
    ) -> str:
        """내보내기 데이터를 파일로 저장"""
        try:
            # 파일명 생성
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"watchhamster_settings_export_{timestamp}.json"
            
            # 파일 경로
            export_path = self.export_dir / filename
            
            # JSON 데이터 생성
            json_data = json.dumps(
                export_data.dict(),
                indent=2,
                ensure_ascii=False,
                default=str
            )
            
            # 압축 적용
            if compression in self.compression_formats:
                compressed_data = await self.compression_formats[compression](json_data.encode('utf-8'))
                
                # 압축된 파일 저장
                if compression != 'none':
                    export_path = export_path.with_suffix(f'.json.{compression}')
                
                async with aiofiles.open(export_path, 'wb') as f:
                    await f.write(compressed_data)
            else:
                # 일반 JSON 파일 저장
                async with aiofiles.open(export_path, 'w', encoding='utf-8') as f:
                    await f.write(json_data)
            
            logger.info(f"설정 내보내기 파일 저장: {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"내보내기 파일 저장 실패: {e}")
            raise
    
    async def import_settings_from_file(
        self,
        file_path: Union[str, Path],
        options: SettingsImportOptions
    ) -> SettingsImportResult:
        """파일에서 설정 가져오기"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
            # 파일 읽기 및 압축 해제
            content = await self._read_and_decompress_file(file_path)
            
            # JSON 파싱
            import_data = json.loads(content)
            export_obj = SettingsExport(**import_data)
            
            # 설정 가져오기 실행
            return await self.import_settings(export_obj, options)
            
        except Exception as e:
            logger.error(f"파일에서 설정 가져오기 실패: {e}")
            return SettingsImportResult(
                success=False,
                imported_sections=[],
                skipped_sections=[],
                errors=[str(e)],
                warnings=[],
                backup_id=None
            )
    
    async def _read_and_decompress_file(self, file_path: Path) -> str:
        """파일 읽기 및 압축 해제"""
        try:
            # 파일 확장자로 압축 형식 판단
            if file_path.suffix == '.gz':
                compression = 'gzip'
            elif file_path.suffix == '.zip':
                compression = 'zip'
            else:
                compression = 'none'
            
            # 파일 읽기
            async with aiofiles.open(file_path, 'rb') as f:
                compressed_data = await f.read()
            
            # 압축 해제
            if compression in self.decompression_formats:
                decompressed_data = await self.decompression_formats[compression](compressed_data)
                return decompressed_data.decode('utf-8')
            else:
                return compressed_data.decode('utf-8')
                
        except Exception as e:
            logger.error(f"파일 읽기/압축 해제 실패: {e}")
            raise
    
    async def import_settings(
        self,
        export_data: SettingsExport,
        options: SettingsImportOptions
    ) -> SettingsImportResult:
        """설정 가져오기"""
        try:
            from .settings_manager import get_settings_manager
            settings_manager = get_settings_manager()
            
            imported_sections = []
            skipped_sections = []
            errors = []
            warnings = []
            backup_id = None
            
            # 가져오기 전 백업 생성
            if options.backup_before_import:
                current_settings = await settings_manager.load_settings()
                backup_filename = await self._create_import_backup(current_settings)
                backup_id = backup_filename
            
            # 현재 설정 로드
            if options.merge:
                current_settings = await settings_manager.load_settings()
                current_data = current_settings.dict()
            else:
                current_data = {}
            
            # 가져올 섹션 결정
            sections_to_import = options.sections if options.sections else list(export_data.settings.keys())
            
            # 각 섹션 가져오기
            for section in sections_to_import:
                try:
                    if section in export_data.settings:
                        current_data[section] = export_data.settings[section]
                        imported_sections.append(section)
                        logger.debug(f"섹션 가져오기 완료: {section}")
                    else:
                        skipped_sections.append(section)
                        warnings.append(f"섹션을 찾을 수 없습니다: {section}")
                        
                except Exception as e:
                    errors.append(f"섹션 {section} 가져오기 실패: {str(e)}")
                    skipped_sections.append(section)
            
            # 새 설정 객체 생성 및 검증
            if imported_sections:
                try:
                    new_settings = AppSettings(**current_data)
                    
                    if options.validate:
                        validation_result = await settings_manager.validate_settings(new_settings)
                        if not validation_result.valid:
                            for error in validation_result.errors:
                                errors.append(f"검증 오류: {error.message}")
                        for warning in validation_result.warnings:
                            warnings.append(f"검증 경고: {warning.message}")
                    
                    # 설정 저장
                    if not errors:
                        await settings_manager.save_settings(new_settings)
                        logger.info(f"설정 가져오기 완료: {len(imported_sections)}개 섹션")
                    
                except ValidationError as e:
                    errors.append(f"설정 검증 실패: {str(e)}")
                except Exception as e:
                    errors.append(f"설정 저장 실패: {str(e)}")
            
            success = len(errors) == 0 and len(imported_sections) > 0
            
            return SettingsImportResult(
                success=success,
                imported_sections=imported_sections,
                skipped_sections=skipped_sections,
                errors=errors,
                warnings=warnings,
                backup_id=backup_id
            )
            
        except Exception as e:
            logger.error(f"설정 가져오기 실패: {e}")
            return SettingsImportResult(
                success=False,
                imported_sections=[],
                skipped_sections=[],
                errors=[str(e)],
                warnings=[],
                backup_id=backup_id
            )
    
    async def _create_import_backup(self, settings: AppSettings) -> str:
        """가져오기 전 백업 생성"""
        try:
            backup_filename = f"settings_before_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.backup_dir / backup_filename
            
            async with aiofiles.open(backup_path, 'w', encoding='utf-8') as f:
                content = json.dumps(
                    settings.dict(),
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
                await f.write(content)
            
            logger.info(f"가져오기 전 백업 생성: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"가져오기 전 백업 생성 실패: {e}")
            raise
    
    async def auto_recovery(self, settings_file: Path) -> bool:
        """설정 파일 자동 복구"""
        try:
            logger.info("설정 파일 자동 복구 시작")
            
            # 최신 백업 파일 찾기
            backup_files = list(self.backup_dir.glob("settings_backup_*.json"))
            
            if not backup_files:
                logger.warning("복구할 백업 파일이 없습니다")
                return False
            
            # 최신 백업 파일 선택
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            
            # 손상된 파일 백업
            if settings_file.exists():
                corrupted_backup = self.backup_dir / f"corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(settings_file, corrupted_backup)
                logger.info(f"손상된 파일 백업: {corrupted_backup}")
            
            # 백업에서 복구
            shutil.copy2(latest_backup, settings_file)
            
            # 복구된 설정 검증
            async with aiofiles.open(settings_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                settings_data = json.loads(content)
                AppSettings(**settings_data)  # 검증
            
            logger.info(f"설정 파일 자동 복구 완료: {latest_backup.name}")
            return True
            
        except Exception as e:
            logger.error(f"설정 파일 자동 복구 실패: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """백업 파일 목록 조회"""
        try:
            backups = []
            
            # 백업 파일 검색
            backup_patterns = [
                "settings_backup_*.json",
                "settings_before_import_*.json",
                "corrupted_*.json"
            ]
            
            for pattern in backup_patterns:
                for backup_file in self.backup_dir.glob(pattern):
                    stat = backup_file.stat()
                    
                    # 백업 타입 결정
                    if "before_import" in backup_file.name:
                        backup_type = "import_backup"
                    elif "corrupted" in backup_file.name:
                        backup_type = "corrupted_backup"
                    else:
                        backup_type = "regular_backup"
                    
                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "type": backup_type,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime)
                    })
            
            # 최신 순으로 정렬
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
            logger.info(f"백업 파일 목록 조회: {len(backups)}개")
            return backups
            
        except Exception as e:
            logger.error(f"백업 파일 목록 조회 실패: {e}")
            return []
    
    async def restore_from_backup(self, backup_filename: str) -> bool:
        """백업에서 복원"""
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_filename}")
            
            from .settings_manager import get_settings_manager
            settings_manager = get_settings_manager()
            
            # 백업 파일 검증
            async with aiofiles.open(backup_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                settings_data = json.loads(content)
                restored_settings = AppSettings(**settings_data)
            
            # 현재 설정 백업
            current_settings = await settings_manager.load_settings()
            current_backup = await self._create_restore_backup(current_settings)
            
            # 복원 실행
            await settings_manager.save_settings(restored_settings)
            
            logger.info(f"백업에서 복원 완료: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"백업에서 복원 실패: {e}")
            return False
    
    async def _create_restore_backup(self, settings: AppSettings) -> str:
        """복원 전 백업 생성"""
        try:
            backup_filename = f"settings_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.backup_dir / backup_filename
            
            async with aiofiles.open(backup_path, 'w', encoding='utf-8') as f:
                content = json.dumps(
                    settings.dict(),
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
                await f.write(content)
            
            logger.info(f"복원 전 백업 생성: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"복원 전 백업 생성 실패: {e}")
            raise
    
    async def cleanup_old_backups(self, max_backups: int = 50, max_age_days: int = 90):
        """오래된 백업 파일 정리"""
        try:
            backup_files = list(self.backup_dir.glob("*.json"))
            
            # 나이별 정리
            cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 3600)
            old_files = [f for f in backup_files if f.stat().st_ctime < cutoff_date]
            
            # 개수별 정리
            if len(backup_files) > max_backups:
                backup_files.sort(key=lambda x: x.stat().st_ctime)
                old_files.extend(backup_files[:-max_backups])
            
            # 중복 제거
            old_files = list(set(old_files))
            
            # 파일 삭제
            deleted_count = 0
            for old_file in old_files:
                try:
                    old_file.unlink()
                    deleted_count += 1
                    logger.debug(f"오래된 백업 파일 삭제: {old_file.name}")
                except Exception as e:
                    logger.warning(f"백업 파일 삭제 실패: {old_file.name}, {e}")
            
            logger.info(f"오래된 백업 파일 정리 완료: {deleted_count}개 삭제")
            return deleted_count
            
        except Exception as e:
            logger.error(f"백업 파일 정리 실패: {e}")
            return 0
    
    # 압축/압축 해제 메서드들
    async def _compress_gzip(self, data: bytes) -> bytes:
        """GZIP 압축"""
        return gzip.compress(data)
    
    async def _compress_zip(self, data: bytes) -> bytes:
        """ZIP 압축"""
        import io
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('settings.json', data)
        return buffer.getvalue()
    
    async def _compress_none(self, data: bytes) -> bytes:
        """압축 없음"""
        return data
    
    async def _decompress_gzip(self, data: bytes) -> bytes:
        """GZIP 압축 해제"""
        return gzip.decompress(data)
    
    async def _decompress_zip(self, data: bytes) -> bytes:
        """ZIP 압축 해제"""
        import io
        buffer = io.BytesIO(data)
        with zipfile.ZipFile(buffer, 'r') as zf:
            return zf.read('settings.json')
    
    async def _decompress_none(self, data: bytes) -> bytes:
        """압축 해제 없음"""
        return data

# 전역 백업 관리자 인스턴스
_backup_manager: Optional[SettingsBackupManager] = None

def get_backup_manager() -> SettingsBackupManager:
    """백업 관리자 인스턴스 반환"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = SettingsBackupManager()
    return _backup_manager