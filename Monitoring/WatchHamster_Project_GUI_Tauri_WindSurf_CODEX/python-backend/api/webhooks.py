"""
웹훅 관리 API 엔드포인트
포팅된 웹훅 시스템 및 메시지 템플릿 엔진과 연동
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl
import httpx

# 포팅된 웹훅 시스템 임포트
from core.webhook_system import WebhookSystem, MessageType, MessagePriority

logger = logging.getLogger(__name__)
router = APIRouter()

# 전역 웹훅 시스템 인스턴스
_webhook_system = None

def get_webhook_system():
    """웹훅 시스템 인스턴스 반환"""
    global _webhook_system
    if _webhook_system is None:
        _webhook_system = WebhookSystem()
    return _webhook_system

# 데이터 모델
class WebhookPayload(BaseModel):
    url: HttpUrl
    message: str
    webhook_type: str = "discord"  # discord, slack, generic
    template_id: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

class WebhookTemplate(BaseModel):
    id: str
    name: str
    description: str
    webhook_type: str
    template: str
    variables: List[str]
    created_at: datetime
    updated_at: datetime

class WebhookHistory(BaseModel):
    id: str
    url: str
    message: str
    webhook_type: str
    status: str  # success, failed, pending
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    sent_at: datetime

# 임시 데이터 저장소
webhook_templates = [
    WebhookTemplate(
        id="posco_news_alert",
        name="POSCO 뉴스 알림",
        description="POSCO 뉴스 업데이트 알림 템플릿",
        webhook_type="discord",
        template="🏢 **POSCO 뉴스 업데이트**\n\n📰 **제목**: {title}\n🔗 **링크**: {url}\n⏰ **시간**: {timestamp}",
        variables=["title", "url", "timestamp"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    WebhookTemplate(
        id="system_error_alert",
        name="시스템 오류 알림",
        description="시스템 오류 발생 시 알림 템플릿",
        webhook_type="discord",
        template="🚨 **시스템 오류 발생**\n\n❌ **서비스**: {service_name}\n📝 **오류**: {error_message}\n⏰ **시간**: {timestamp}",
        variables=["service_name", "error_message", "timestamp"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    WebhookTemplate(
        id="deployment_success",
        name="배포 성공 알림",
        description="배포 성공 시 알림 템플릿",
        webhook_type="slack",
        template="✅ *배포 완료*\n\n• *브랜치*: {branch}\n• *커밋*: {commit_hash}\n• *시간*: {timestamp}",
        variables=["branch", "commit_hash", "timestamp"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

webhook_history = []

@router.post("/send")
async def send_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """웹훅 전송"""
    logger.info(f"웹훅 전송 요청: {payload.webhook_type} to {payload.url}")
    
    # 템플릿 사용 시 메시지 생성
    final_message = payload.message
    if payload.template_id:
        template = next((t for t in webhook_templates if t.id == payload.template_id), None)
        if template:
            try:
                final_message = template.template.format(**(payload.variables or {}))
            except KeyError as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"템플릿 변수가 누락되었습니다: {e}"
                )
    
    # 히스토리 엔트리 생성
    history_entry = WebhookHistory(
        id=f"webhook_{len(webhook_history) + 1}",
        url=str(payload.url),
        message=final_message,
        webhook_type=payload.webhook_type,
        status="pending",
        sent_at=datetime.now()
    )
    webhook_history.append(history_entry)
    
    # 백그라운드에서 웹훅 전송
    background_tasks.add_task(
        _send_webhook_task, 
        history_entry.id, 
        str(payload.url), 
        final_message, 
        payload.webhook_type
    )
    
    return {
        "message": "웹훅 전송이 시작되었습니다",
        "webhook_id": history_entry.id
    }

@router.get("/templates", response_model=List[WebhookTemplate])
async def get_webhook_templates():
    """웹훅 템플릿 목록 조회"""
    logger.info("웹훅 템플릿 목록 조회 요청")
    return webhook_templates

@router.get("/templates/{template_id}", response_model=WebhookTemplate)
async def get_webhook_template(template_id: str):
    """특정 웹훅 템플릿 조회"""
    logger.info(f"웹훅 템플릿 조회: {template_id}")
    
    template = next((t for t in webhook_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    return template

class WebhookTemplateCreate(BaseModel):
    name: str
    description: str
    webhook_type: str
    template: str

def extract_template_variables(template_text: str) -> List[str]:
    """템플릿에서 변수 추출 ({{변수명}} 형태)"""
    import re
    pattern = r'\{\{(\w+)\}\}'
    variables = re.findall(pattern, template_text)
    return list(set(variables))  # 중복 제거

@router.post("/templates", response_model=WebhookTemplate)
async def create_webhook_template(template_data: WebhookTemplateCreate):
    """새 웹훅 템플릿 생성"""
    logger.info(f"웹훅 템플릿 생성: {template_data.name}")
    
    # 고유 ID 생성
    import uuid
    template_id = str(uuid.uuid4())
    
    # 템플릿에서 변수 자동 추출
    variables = extract_template_variables(template_data.template)
    
    template = WebhookTemplate(
        id=template_id,
        name=template_data.name,
        description=template_data.description,
        webhook_type=template_data.webhook_type,
        template=template_data.template,
        variables=variables,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    webhook_templates.append(template)
    
    return template

@router.put("/templates/{template_id}", response_model=WebhookTemplate)
async def update_webhook_template(template_id: str, template_data: WebhookTemplateCreate):
    """웹훅 템플릿 수정"""
    logger.info(f"웹훅 템플릿 수정: {template_id}")
    
    template_index = next(
        (i for i, t in enumerate(webhook_templates) if t.id == template_id), 
        None
    )
    
    if template_index is None:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    # 기존 템플릿 정보 유지
    existing_template = webhook_templates[template_index]
    
    # 템플릿에서 변수 자동 추출
    variables = extract_template_variables(template_data.template)
    
    updated_template = WebhookTemplate(
        id=template_id,
        name=template_data.name,
        description=template_data.description,
        webhook_type=template_data.webhook_type,
        template=template_data.template,
        variables=variables,
        created_at=existing_template.created_at,
        updated_at=datetime.now()
    )
    
    webhook_templates[template_index] = updated_template
    
    return updated_template

@router.delete("/templates/{template_id}")
async def delete_webhook_template(template_id: str):
    """웹훅 템플릿 삭제"""
    logger.info(f"웹훅 템플릿 삭제: {template_id}")
    
    template_index = next(
        (i for i, t in enumerate(webhook_templates) if t.id == template_id), 
        None
    )
    
    if template_index is None:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    deleted_template = webhook_templates.pop(template_index)
    
    return {"message": f"템플릿 '{deleted_template.name}'이 삭제되었습니다"}

@router.get("/history", response_model=List[WebhookHistory])
async def get_webhook_history(limit: int = 50):
    """웹훅 전송 히스토리 조회"""
    logger.info(f"웹훅 히스토리 조회 요청 (limit: {limit})")
    
    # 최근 N개 히스토리 반환 (최신순)
    recent_history = webhook_history[-limit:][::-1]
    
    return recent_history

@router.get("/history/{webhook_id}", response_model=WebhookHistory)
async def get_webhook_status(webhook_id: str):
    """특정 웹훅 전송 상태 조회"""
    logger.info(f"웹훅 상태 조회: {webhook_id}")
    
    history_entry = next((h for h in webhook_history if h.id == webhook_id), None)
    if not history_entry:
        raise HTTPException(status_code=404, detail="웹훅 히스토리를 찾을 수 없습니다")
    
    return history_entry

# 백그라운드 작업 함수
async def _send_webhook_task(webhook_id: str, url: str, message: str, webhook_type: str):
    """웹훅 전송 백그라운드 작업"""
    logger.info(f"웹훅 전송 작업 실행: {webhook_id}")
    
    # 히스토리 엔트리 찾기
    history_entry = next((h for h in webhook_history if h.id == webhook_id), None)
    if not history_entry:
        logger.error(f"웹훅 히스토리를 찾을 수 없습니다: {webhook_id}")
        return
    
    try:
        # 웹훅 타입에 따른 페이로드 구성
        if webhook_type == "discord":
            payload = {"content": message}
        elif webhook_type == "slack":
            payload = {"text": message}
        else:
            payload = {"message": message}
        
        # HTTP 요청 전송
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            # 결과 업데이트
            history_entry.status = "success" if response.is_success else "failed"
            history_entry.response_code = response.status_code
            
            if not response.is_success:
                history_entry.error_message = f"HTTP {response.status_code}: {response.text}"
            
            logger.info(f"웹훅 전송 완료: {webhook_id} (상태: {response.status_code})")
            
    except Exception as e:
        # 오류 처리
        history_entry.status = "failed"
        history_entry.error_message = str(e)
        logger.error(f"웹훅 전송 실패: {webhook_id} - {e}")

# 포팅된 웹훅 시스템을 사용하는 새로운 엔드포인트들

class EnhancedWebhookRequest(BaseModel):
    message_type: str  # deployment_success, deployment_failure, system_status, error_alert
    data: Dict[str, Any]
    webhook_url: Optional[str] = None

@router.post("/enhanced/send")
async def send_enhanced_webhook(request: EnhancedWebhookRequest, 
                               webhook_system = Depends(get_webhook_system)):
    """포팅된 메시지 템플릿 엔진을 사용한 웹훅 전송"""
    logger.info(f"향상된 웹훅 전송 요청: {request.message_type}")
    
    try:
        # 메시지 타입 매핑
        message_type_mapping = {
            "deployment_success": MessageType.DEPLOYMENT_SUCCESS,
            "deployment_failure": MessageType.DEPLOYMENT_FAILURE,
            "deployment_start": MessageType.DEPLOYMENT_START,
            "system_status": MessageType.SYSTEM_STATUS,
            "error_alert": MessageType.ERROR_ALERT,
            "maintenance": MessageType.MAINTENANCE
        }
        
        message_type = message_type_mapping.get(request.message_type)
        if not message_type:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 메시지 타입: {request.message_type}"
            )
        
        # 웹훅 전송
        result = await webhook_system.send_message(
            message_type, 
            request.data, 
            request.webhook_url
        )
        
        return result
        
    except Exception as e:
        logger.error(f"향상된 웹훅 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced/deployment/success")
async def send_deployment_success_webhook(data: Dict[str, Any], 
                                        webhook_system = Depends(get_webhook_system)):
    """배포 성공 웹훅 전송"""
    logger.info("배포 성공 웹훅 전송 요청")
    
    try:
        result = await webhook_system.send_deployment_success(data)
        return result
    except Exception as e:
        logger.error(f"배포 성공 웹훅 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced/deployment/failure")
async def send_deployment_failure_webhook(data: Dict[str, Any], 
                                        webhook_system = Depends(get_webhook_system)):
    """배포 실패 웹훅 전송"""
    logger.info("배포 실패 웹훅 전송 요청")
    
    try:
        result = await webhook_system.send_deployment_failure(data)
        return result
    except Exception as e:
        logger.error(f"배포 실패 웹훅 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced/system/status")
async def send_system_status_webhook(data: Dict[str, Any], 
                                   webhook_system = Depends(get_webhook_system)):
    """시스템 상태 웹훅 전송"""
    logger.info("시스템 상태 웹훅 전송 요청")
    
    try:
        result = await webhook_system.send_system_status(data)
        return result
    except Exception as e:
        logger.error(f"시스템 상태 웹훅 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced/error/alert")
async def send_error_alert_webhook(data: Dict[str, Any], 
                                 webhook_system = Depends(get_webhook_system)):
    """오류 알림 웹훅 전송"""
    logger.info("오류 알림 웹훅 전송 요청")
    
    try:
        result = await webhook_system.send_error_alert(data)
        return result
    except Exception as e:
        logger.error(f"오류 알림 웹훅 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enhanced/history")
async def get_enhanced_webhook_history(limit: int = 50, 
                                     webhook_system = Depends(get_webhook_system)):
    """향상된 웹훅 전송 히스토리 조회"""
    logger.info(f"향상된 웹훅 히스토리 조회 요청 (limit: {limit})")
    
    try:
        history = webhook_system.get_message_history(limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"웹훅 히스토리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enhanced/statistics")
async def get_webhook_statistics(webhook_system = Depends(get_webhook_system)):
    """웹훅 전송 통계 조회"""
    logger.info("웹훅 전송 통계 조회 요청")
    
    try:
        stats = webhook_system.get_send_statistics()
        return stats
    except Exception as e:
        logger.error(f"웹훅 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced/test")
async def test_enhanced_webhook(webhook_url: str, 
                              webhook_system = Depends(get_webhook_system)):
    """향상된 웹훅 연결 테스트"""
    logger.info(f"향상된 웹훅 연결 테스트: {webhook_url}")
    
    try:
        result = await webhook_system.test_webhook_connection(webhook_url)
        return result
    except Exception as e:
        logger.error(f"웹훅 연결 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/enhanced/config")
async def update_webhook_config(webhook_type: str, webhook_url: str, 
                              webhook_system = Depends(get_webhook_system)):
    """웹훅 설정 업데이트"""
    logger.info(f"웹훅 설정 업데이트: {webhook_type}")
    
    try:
        webhook_system.update_webhook_url(webhook_type, webhook_url)
        return {"message": f"웹훅 URL이 업데이트되었습니다: {webhook_type}"}
    except Exception as e:
        logger.error(f"웹훅 설정 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))