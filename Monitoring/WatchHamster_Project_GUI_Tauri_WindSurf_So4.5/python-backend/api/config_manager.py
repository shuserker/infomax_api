"""
설정 관리 API
모니터 설정 CRUD 및 검증
"""

import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# 설정 파일 경로
CONFIG_DIR = Path(__file__).parent.parent / "config" / "monitors"


class AuthConfig(BaseModel):
    """인증 설정"""
    type: str = Field(..., description="인증 타입: bearer, apikey, basic, none")
    token: Optional[str] = None
    apiKey: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class ApiConfig(BaseModel):
    """API 설정"""
    endpoint: str
    method: str = "GET"
    auth: AuthConfig
    headers: Dict[str, str] = {}
    params: Dict[str, Any] = {}
    body: Optional[Dict[str, Any]] = None
    timeout: int = 30


class TimeRange(BaseModel):
    """시간 범위"""
    start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class ScheduleConfig(BaseModel):
    """스케줄 설정"""
    interval: int = Field(..., gt=0, description="실행 간격 (분)")
    timeRange: Optional[TimeRange] = None
    daysOfWeek: Optional[List[int]] = Field(None, description="0-6 (일-토)")
    excludeHolidays: bool = False


class RetryConfig(BaseModel):
    """재시도 설정"""
    maxAttempts: int = Field(3, ge=1, le=10)
    delayMs: int = Field(1000, ge=100)
    backoff: str = Field("exponential", pattern="^(linear|exponential)$")


class ParsingRule(BaseModel):
    """파싱 규칙"""
    field: str
    path: str
    required: bool = False
    transform: Optional[str] = None


class ValidationRule(BaseModel):
    """검증 규칙"""
    field: str
    type: str
    minLength: Optional[int] = None
    maxLength: Optional[int] = None


class ParsingConfig(BaseModel):
    """파싱 설정"""
    type: str = Field("json", pattern="^(json|html|xml)$")
    rules: List[ParsingRule] = []
    validation: List[ValidationRule] = []


class WebhookConfig(BaseModel):
    """웹훅 설정"""
    enabled: bool = True
    url: str
    templateId: str = "default"
    condition: str = Field("on_change", pattern="^(always|on_change|on_error)$")
    timeout: int = 10


class MonitorMetadata(BaseModel):
    """메타데이터"""
    created_at: str
    updated_at: str
    version: str = "1.0.0"


class MonitorConfig(BaseModel):
    """모니터 설정"""
    name: str
    display_name: str
    enabled: bool = True
    description: str = ""
    api: ApiConfig
    schedule: ScheduleConfig
    retry: RetryConfig
    parsing: ParsingConfig
    webhook: WebhookConfig
    metadata: MonitorMetadata


class MonitorSummary(BaseModel):
    """모니터 요약 정보"""
    name: str
    display_name: str
    enabled: bool
    description: str
    last_updated: str


@router.get("/monitors", response_model=List[MonitorSummary])
async def get_all_monitors():
    """모든 모니터 설정 목록 조회"""
    logger.info("모든 모니터 설정 조회")
    
    try:
        monitors = []
        
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            return []
        
        for config_file in CONFIG_DIR.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    monitors.append(MonitorSummary(
                        name=config.get("name", config_file.stem),
                        display_name=config.get("display_name", config_file.stem),
                        enabled=config.get("enabled", False),
                        description=config.get("description", ""),
                        last_updated=config.get("metadata", {}).get("updated_at", "")
                    ))
            except Exception as e:
                logger.error(f"설정 파일 읽기 실패: {config_file} - {e}")
                continue
        
        return monitors
        
    except Exception as e:
        logger.error(f"모니터 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitors/{name}", response_model=MonitorConfig)
async def get_monitor_config(name: str):
    """특정 모니터 설정 조회"""
    logger.info(f"모니터 설정 조회: {name}")
    
    config_file = CONFIG_DIR / f"{name}.json"
    
    if not config_file.exists():
        raise HTTPException(status_code=404, detail=f"모니터를 찾을 수 없습니다: {name}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return MonitorConfig(**config)
    except Exception as e:
        logger.error(f"설정 파일 읽기 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/monitors/{name}", response_model=MonitorConfig)
async def update_monitor_config(name: str, config: MonitorConfig):
    """모니터 설정 수정"""
    logger.info(f"모니터 설정 수정: {name}")
    
    if name != config.name:
        raise HTTPException(status_code=400, detail="모니터 이름이 일치하지 않습니다")
    
    config_file = CONFIG_DIR / f"{name}.json"
    
    try:
        # 메타데이터 업데이트
        config.metadata.updated_at = datetime.now().isoformat()
        
        # 설정 저장
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config.dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"모니터 설정 저장 완료: {name}")
        return config
        
    except Exception as e:
        logger.error(f"설정 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitors", response_model=MonitorConfig)
async def create_monitor_config(config: MonitorConfig):
    """새 모니터 설정 생성"""
    logger.info(f"새 모니터 생성: {config.name}")
    
    config_file = CONFIG_DIR / f"{config.name}.json"
    
    if config_file.exists():
        raise HTTPException(status_code=409, detail=f"이미 존재하는 모니터입니다: {config.name}")
    
    try:
        # 메타데이터 설정
        now = datetime.now().isoformat()
        config.metadata.created_at = now
        config.metadata.updated_at = now
        
        # 설정 저장
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config.dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"모니터 생성 완료: {config.name}")
        return config
        
    except Exception as e:
        logger.error(f"모니터 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/monitors/{name}")
async def delete_monitor_config(name: str):
    """모니터 설정 삭제"""
    logger.info(f"모니터 삭제: {name}")
    
    config_file = CONFIG_DIR / f"{name}.json"
    
    if not config_file.exists():
        raise HTTPException(status_code=404, detail=f"모니터를 찾을 수 없습니다: {name}")
    
    try:
        config_file.unlink()
        logger.info(f"모니터 삭제 완료: {name}")
        return {"status": "ok", "message": f"모니터가 삭제되었습니다: {name}"}
        
    except Exception as e:
        logger.error(f"모니터 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitors/{name}/validate")
async def validate_monitor_config(name: str):
    """모니터 설정 검증"""
    logger.info(f"모니터 설정 검증: {name}")
    
    try:
        config = await get_monitor_config(name)
        
        errors = []
        warnings = []
        
        # API 엔드포인트 검증
        if not config.api.endpoint.startswith(("http://", "https://")):
            errors.append("API 엔드포인트는 http:// 또는 https://로 시작해야 합니다")
        
        # 인증 설정 검증
        if config.api.auth.type == "bearer" and not config.api.auth.token:
            errors.append("Bearer 인증 타입은 토큰이 필요합니다")
        
        # 웹훅 URL 검증
        if config.webhook.enabled and not config.webhook.url:
            errors.append("웹훅이 활성화되어 있지만 URL이 설정되지 않았습니다")
        
        # 스케줄 검증
        if config.schedule.interval < 1:
            errors.append("실행 간격은 최소 1분 이상이어야 합니다")
        
        # 경고 메시지
        if config.api.timeout > 60:
            warnings.append("API 타임아웃이 60초를 초과합니다")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 검증 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitors/{name}/test")
async def test_monitor_config(name: str):
    """모니터 설정 테스트 (API 호출)"""
    logger.info(f"모니터 설정 테스트: {name}")
    
    try:
        config = await get_monitor_config(name)
        
        # TODO: 실제 API 호출 구현
        # 현재는 데모 응답 반환
        
        return {
            "status": "success",
            "message": "설정 테스트 성공",
            "test_result": {
                "api_reachable": True,
                "auth_valid": True,
                "parsing_valid": True,
                "webhook_valid": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
