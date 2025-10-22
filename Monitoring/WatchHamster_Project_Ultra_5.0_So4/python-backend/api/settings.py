"""
설정 관리 API 엔드포인트
시스템 설정 조회, 업데이트, 내보내기, 가져오기, 초기화 기능
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.settings_manager import get_settings_manager, initialize_settings_manager
from core.settings_backup import get_backup_manager
from models.settings import (
    AppSettings,
    SettingsValidationResult,
    SettingsChange,
    SettingsExport,
    SettingsImportOptions,
    SettingsImportResult,
    UpdateSettingsRequest,
    UpdateSettingsResponse,
    GetSettingsResponse,
    ExportSettingsRequest,
    ExportSettingsResponse,
    ImportSettingsRequest,
    ImportSettingsResponse,
    ResetSettingsRequest,
    ResetSettingsResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# 설정 관리자 인스턴스
settings_manager = None
backup_manager = None

async def get_managers():
    """설정 관리자들 초기화 및 반환"""
    global settings_manager, backup_manager
    if settings_manager is None:
        settings_manager = await initialize_settings_manager()
    if backup_manager is None:
        backup_manager = get_backup_manager()
    return settings_manager, backup_manager

# 헬퍼 함수들
async def notify_settings_change(change_type: str, data: Dict[str, Any]):
    """설정 변경 WebSocket 알림"""
    try:
        from api.websocket import manager
        await manager.broadcast_json({
            "type": change_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.warning(f"설정 변경 WebSocket 알림 실패: {e}")

@router.get("/", response_model=GetSettingsResponse)
async def get_settings(sections: Optional[str] = None, include_sensitive: bool = False):
    """현재 설정 조회"""
    logger.info("설정 조회 요청")
    
    try:
        settings_mgr, _ = await get_managers()
        settings = await settings_mgr.load_settings()
        
        return GetSettingsResponse(
            settings=settings,
            last_updated=settings.last_updated,
            version=settings.version
        )
        
    except Exception as e:
        logger.error(f"설정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 조회 중 오류가 발생했습니다")

@router.put("/", response_model=UpdateSettingsResponse)
async def update_settings(request: UpdateSettingsRequest):
    """설정 업데이트"""
    logger.info("설정 업데이트 요청")
    
    try:
        settings_mgr, _ = await get_managers()
        
        # 설정 업데이트 실행
        updated_settings, changes = await settings_mgr.update_settings(
            request.settings,
            reason=request.reason
        )
        
        # 검증 수행
        validation_result = await settings_mgr.validate_settings(updated_settings)
        
        # 검증만 수행하는 경우
        if request.validate_only:
            return UpdateSettingsResponse(
                settings=updated_settings,
                validation_result=validation_result,
                applied_changes=[],
                restart_required=False
            )
        
        # 검증 실패 시 오류 반환
        if not validation_result.valid:
            raise HTTPException(
                status_code=400, 
                detail=f"설정이 유효하지 않습니다: {[e.message for e in validation_result.errors]}"
            )
        
        # 재시작 필요 여부 판단
        restart_required = any(
            change.field_path.startswith(('api.', 'security.', 'logging.'))
            for change in changes
        )
        
        logger.info(f"설정 업데이트 완료: {len(changes)}개 변경")
        
        # WebSocket 알림
        await notify_settings_change("settings_updated", {
            "message": "시스템 설정이 업데이트되었습니다",
            "changes_count": len(changes),
            "restart_required": restart_required
        })
        
        return UpdateSettingsResponse(
            settings=updated_settings,
            validation_result=validation_result,
            applied_changes=changes,
            restart_required=restart_required
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 업데이트 중 오류가 발생했습니다")

@router.post("/export", response_model=ExportSettingsResponse)
async def export_settings(request: ExportSettingsRequest):
    """설정 내보내기"""
    logger.info("설정 내보내기 요청")
    
    try:
        settings_mgr, backup_mgr = await get_managers()
        
        # 현재 설정 로드
        settings = await settings_mgr.load_settings()
        
        # 설정 내보내기
        export_data = await backup_mgr.export_settings(
            settings=settings,
            sections=request.sections,
            include_sensitive=request.include_sensitive,
            format_type=request.format,
            compression="none"
        )
        
        # 파일로 저장
        export_path = await backup_mgr.save_export_to_file(
            export_data=export_data,
            compression="none"
        )
        
        # 다운로드 URL 생성 (실제 구현에서는 임시 URL 생성)
        download_url = f"/api/settings/download/{Path(export_path).name}"
        expires_at = datetime.now().replace(hour=23, minute=59, second=59)
        
        logger.info(f"설정 내보내기 완료: {Path(export_path).name}")
        
        return ExportSettingsResponse(
            export_data=export_data,
            download_url=download_url,
            expires_at=expires_at
        )
        
    except Exception as e:
        logger.error(f"설정 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 내보내기 중 오류가 발생했습니다")

@router.get("/download/{filename}")
async def download_export_file(filename: str):
    """내보내기 파일 다운로드"""
    try:
        _, backup_mgr = await get_managers()
        export_path = backup_mgr.export_dir / filename
        
        if not export_path.exists():
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        return FileResponse(
            path=export_path,
            filename=filename,
            media_type='application/json'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail="파일 다운로드 중 오류가 발생했습니다")

@router.post("/import", response_model=ImportSettingsResponse)
async def import_settings(
    file: UploadFile = File(...),
    merge: bool = True,
    validate: bool = True,
    backup_before_import: bool = True,
    sections: Optional[str] = None
):
    """설정 가져오기"""
    logger.info(f"설정 가져오기 요청: {file.filename}")
    
    try:
        # 파일 형식 검증
        if not file.filename.endswith(('.json', '.json.gz', '.json.zip')):
            raise HTTPException(status_code=400, detail="JSON 파일만 지원됩니다")
        
        settings_mgr, backup_mgr = await get_managers()
        
        # 임시 파일로 저장
        temp_path = backup_mgr.temp_dir / f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # 가져오기 옵션 설정
        import_options = SettingsImportOptions(
            merge=merge,
            validate=validate,
            backup_before_import=backup_before_import,
            sections=sections.split(',') if sections else []
        )
        
        # 설정 가져오기 실행
        result = await backup_mgr.import_settings_from_file(temp_path, import_options)
        
        # 임시 파일 정리
        try:
            temp_path.unlink()
        except:
            pass
        
        # 재시작 필요 여부 판단
        restart_required = len(result.imported_sections) > 0 and any(
            section in ['api', 'security', 'logging'] 
            for section in result.imported_sections
        )
        
        logger.info(f"설정 가져오기 완료: {len(result.imported_sections)}개 섹션")
        
        # WebSocket 알림
        if result.success:
            await notify_settings_change("settings_imported", {
                "message": f"설정이 {file.filename}에서 가져와졌습니다",
                "filename": file.filename,
                "imported_sections": result.imported_sections
            })
        
        return ImportSettingsResponse(
            result=result,
            restart_required=restart_required
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 가져오기 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 가져오기 중 오류가 발생했습니다")

@router.post("/reset", response_model=ResetSettingsResponse)
async def reset_settings(request: ResetSettingsRequest):
    """설정 기본값 복원"""
    logger.info("설정 기본값 복원 요청")
    
    try:
        if not request.confirm:
            raise HTTPException(status_code=400, detail="설정 초기화를 확인해주세요")
        
        settings_mgr, _ = await get_managers()
        
        # 설정 초기화 실행
        reset_settings_obj, backup_id = await settings_mgr.reset_settings(request.sections)
        
        # 재시작 필요 여부 판단
        restart_required = not request.sections or any(
            section in ['api', 'security', 'logging'] 
            for section in (request.sections or ['api', 'ui', 'logging', 'security', 'backup'])
        )
        
        reset_sections = request.sections or ['api', 'ui', 'logging', 'security', 'backup']
        
        logger.info(f"설정 기본값 복원 완료: {len(reset_sections)}개 섹션")
        
        # WebSocket 알림
        await notify_settings_change("settings_reset", {
            "message": "설정이 기본값으로 복원되었습니다",
            "reset_sections": reset_sections,
            "backup_id": backup_id
        })
        
        return ResetSettingsResponse(
            reset_sections=reset_sections,
            backup_id=backup_id,
            restart_required=restart_required
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 기본값 복원 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 기본값 복원 중 오류가 발생했습니다")

@router.get("/validate", response_model=SettingsValidationResult)
async def validate_current_settings():
    """현재 설정 유효성 검증"""
    logger.info("설정 유효성 검증 요청")
    
    try:
        settings_mgr, _ = await get_managers()
        settings = await settings_mgr.load_settings()
        validation_result = await settings_mgr.validate_settings(settings)
        
        return validation_result
        
    except Exception as e:
        logger.error(f"설정 유효성 검증 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 유효성 검증 중 오류가 발생했습니다")

@router.get("/backups")
async def list_setting_backups():
    """설정 백업 목록 조회"""
    logger.info("설정 백업 목록 조회 요청")
    
    try:
        _, backup_mgr = await get_managers()
        backups = await backup_mgr.list_backups()
        
        return {
            "backups": backups,
            "total_count": len(backups)
        }
        
    except Exception as e:
        logger.error(f"설정 백업 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 백업 목록 조회 중 오류가 발생했습니다")

@router.get("/backups/{filename}")
async def download_backup(filename: str):
    """설정 백업 파일 다운로드"""
    logger.info(f"설정 백업 다운로드 요청: {filename}")
    
    try:
        _, backup_mgr = await get_managers()
        backup_path = backup_mgr.backup_dir / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="백업 파일을 찾을 수 없습니다")
        
        return FileResponse(
            path=backup_path,
            filename=filename,
            media_type='application/json'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 백업 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 백업 다운로드 중 오류가 발생했습니다")

@router.post("/backups/{filename}/restore")
async def restore_from_backup(filename: str):
    """백업에서 설정 복원"""
    logger.info(f"백업에서 설정 복원 요청: {filename}")
    
    try:
        _, backup_mgr = await get_managers()
        
        success = await backup_mgr.restore_from_backup(filename)
        
        if not success:
            raise HTTPException(status_code=500, detail="백업에서 복원에 실패했습니다")
        
        logger.info(f"백업에서 설정 복원 완료: {filename}")
        
        # WebSocket 알림
        await notify_settings_change("settings_restored", {
            "message": f"설정이 백업 {filename}에서 복원되었습니다",
            "backup_filename": filename
        })
        
        return {
            "message": "백업에서 설정이 성공적으로 복원되었습니다",
            "backup_filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"백업에서 설정 복원 실패: {e}")
        raise HTTPException(status_code=500, detail="백업에서 설정 복원 중 오류가 발생했습니다")

@router.get("/info")
async def get_settings_info():
    """설정 파일 정보 조회"""
    logger.info("설정 파일 정보 조회 요청")
    
    try:
        settings_mgr, _ = await get_managers()
        info = await settings_mgr.get_settings_info()
        
        return info
        
    except Exception as e:
        logger.error(f"설정 파일 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="설정 파일 정보 조회 중 오류가 발생했습니다")

@router.post("/cleanup")
async def cleanup_old_backups(
    background_tasks: BackgroundTasks,
    max_backups: int = 50,
    max_age_days: int = 90
):
    """오래된 백업 파일 정리"""
    logger.info("백업 파일 정리 요청")
    
    try:
        _, backup_mgr = await get_managers()
        
        # 백그라운드에서 정리 작업 실행
        background_tasks.add_task(
            backup_mgr.cleanup_old_backups,
            max_backups=max_backups,
            max_age_days=max_age_days
        )
        
        return {
            "message": "백업 파일 정리 작업이 시작되었습니다",
            "max_backups": max_backups,
            "max_age_days": max_age_days
        }
        
    except Exception as e:
        logger.error(f"백업 파일 정리 실패: {e}")
        raise HTTPException(status_code=500, detail="백업 파일 정리 중 오류가 발생했습니다")

# 설정 초기화 함수 (서버 시작 시 호출)
async def initialize_settings():
    """설정 시스템 초기화"""
    logger.info("설정 시스템 초기화")
    
    try:
        # 설정 관리자 초기화
        await get_managers()
        
        logger.info("설정 시스템 초기화 완료")
        
    except Exception as e:
        logger.error(f"설정 시스템 초기화 실패: {e}")

# 현재 설정 가져오기 헬퍼 함수
async def get_current_settings() -> AppSettings:
    """현재 설정 반환"""
    settings_mgr, _ = await get_managers()
    return await settings_mgr.load_settings()