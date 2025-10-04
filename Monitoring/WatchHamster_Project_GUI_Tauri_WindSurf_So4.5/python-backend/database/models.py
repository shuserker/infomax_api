"""
데이터베이스 모델
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Company(BaseModel):
    """회사 모델"""
    id: str = Field(..., description="회사 ID (영문 소문자, 하이픈)")
    name: str = Field(..., description="회사명")
    display_name: str = Field(..., description="표시명 (한글)")
    logo_url: Optional[str] = Field(None, description="로고 URL")
    is_active: bool = Field(True, description="활성 상태")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "posco",
                "name": "POSCO",
                "display_name": "포스코",
                "logo_url": "https://example.com/logo.png",
                "is_active": True
            }
        }


class WebhookConfig(BaseModel):
    """웹훅 설정 모델"""
    id: Optional[str] = None
    company_id: str = Field(..., description="회사 ID")
    channel_name: str = Field(..., description="채널 이름 (news_main, watchhamster)")
    webhook_url: str = Field(..., description="Dooray 웹훅 URL")
    bot_name: str = Field(..., description="BOT 이름")
    bot_icon: str = Field(..., description="BOT 아이콘 URL")
    is_active: bool = Field(True, description="활성 상태")
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "posco",
                "channel_name": "news_main",
                "webhook_url": "https://infomax.dooray.com/services/.../...",
                "bot_name": "POSCO 뉴스 📊",
                "bot_icon": "https://example.com/icon.png",
                "is_active": True
            }
        }


class APIConfig(BaseModel):
    """API 설정 모델"""
    id: Optional[str] = None
    company_id: str = Field(..., description="회사 ID")
    api_name: str = Field(..., description="API 이름")
    api_url: str = Field(..., description="API URL")
    api_token: Optional[str] = Field(None, description="API 토큰")
    config: Optional[Dict[str, Any]] = Field(None, description="추가 설정")
    is_active: bool = Field(True, description="활성 상태")
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "posco",
                "api_name": "news_api",
                "api_url": "https://global-api.einfomax.co.kr/apis/posco/news",
                "api_token": "YOUR_TOKEN",
                "config": {
                    "endpoints": {
                        "newyork": "/newyork-market-watch",
                        "kospi": "/kospi-close",
                        "exchange": "/exchange-rate"
                    }
                },
                "is_active": True
            }
        }


class WebhookLog(BaseModel):
    """웹훅 로그 모델"""
    id: str
    company_id: str = Field(..., description="회사 ID")
    timestamp: str
    message_type: str
    bot_type: str
    priority: str
    endpoint: str
    status: str
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    full_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CompanyCreate(BaseModel):
    """회사 생성 요청"""
    id: str
    name: str
    display_name: str
    logo_url: Optional[str] = None
    webhooks: Dict[str, Dict[str, str]] = Field(..., description="웹훅 설정")
    api_config: Dict[str, Any] = Field(..., description="API 설정")
    message_types: List[str] = Field(..., description="사용할 메시지 타입")
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "company2",
                "name": "Company2",
                "display_name": "회사2",
                "logo_url": "https://company2.com/logo.png",
                "webhooks": {
                    "news_main": {
                        "url": "https://company2.dooray.com/services/.../...",
                        "bot_name": "회사2 뉴스 📊",
                        "bot_icon": "https://company2.com/icon.png"
                    },
                    "watchhamster": {
                        "url": "https://company2.dooray.com/services/.../...",
                        "bot_name": "회사2 워치햄스터 🎯",
                        "bot_icon": "https://company2.com/icon.png"
                    }
                },
                "api_config": {
                    "news_api": {
                        "url": "https://api.company2.com/news",
                        "token": "YOUR_TOKEN"
                    }
                },
                "message_types": [
                    "business_day_comparison",
                    "delay_notification",
                    "daily_report"
                ],
                "is_active": True
            }
        }


class CompanyUpdate(BaseModel):
    """회사 수정 요청"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyDetail(BaseModel):
    """회사 상세 정보"""
    company: Dict[str, Any]
    webhooks: List[Dict[str, Any]]
    api_configs: List[Dict[str, Any]]
    stats: Dict[str, Any]
    last_activity: Optional[str] = None
