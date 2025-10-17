#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern InfoMax API Client - httpx/async/Pydantic 기반
현재 FastAPI와 완벽 호환되는 비동기 InfoMax API 클라이언트
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl
import httpx
import json

# Pydantic 모델들 (현재 시스템과 호환)
class ApiConfig(BaseModel):
    base_url: HttpUrl = "https://global-api.einfomax.co.kr/apis/posco/news"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    headers: Dict[str, str] = Field(default_factory=lambda: {
        "Content-Type": "application/json",
        "User-Agent": "WatchHamster/3.0"
    })

class NewsItem(BaseModel):
    title: str
    content: str
    timestamp: datetime
    source: str = "POSCO API"
    category: Optional[str] = None
    url: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    response_time_ms: Optional[float] = None

class ModernInfomaxClient:
    """
    현대적 InfoMax API 클라이언트
    - httpx 기반 비동기 HTTP 클라이언트
    - Pydantic 모델 사용
    - 자동 재시도 및 에러 처리
    - FastAPI와 완벽 호환
    """
    
    def __init__(self, config: Optional[ApiConfig] = None):
        self.config = config or ApiConfig()
        self.logger = logging.getLogger(__name__)
        self.client: Optional[httpx.AsyncClient] = None
        self.is_connected = False
        
    async def __aenter__(self):
        """Async context manager 진입"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager 종료"""
        await self.disconnect()
    
    async def connect(self) -> Dict[str, Any]:
        """API 클라이언트 연결"""
        try:
            self.client = httpx.AsyncClient(
                base_url=str(self.config.base_url),
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.config.headers,
                follow_redirects=True
            )
            
            # 연결 테스트
            await self.test_connection()
            self.is_connected = True
            
            self.logger.info("🔗 InfoMax API 클라이언트 연결 성공")
            return {
                "status": "connected",
                "base_url": str(self.config.base_url),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.is_connected = False
            error_msg = f"InfoMax API 연결 실패: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "connection_failed",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    async def disconnect(self):
        """API 클라이언트 연결 해제"""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.is_connected = False
        self.logger.info("🔌 InfoMax API 클라이언트 연결 해제")
    
    async def test_connection(self) -> ApiResponse:
        """연결 상태 테스트"""
        start_time = datetime.now()
        
        try:
            if not self.client:
                raise Exception("클라이언트가 초기화되지 않았습니다")
            
            # 간단한 health check 요청
            response = await self.client.get("/health", timeout=10.0)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return ApiResponse(
                    success=True,
                    data={"connection": "active", "status_code": response.status_code},
                    message="연결 테스트 성공",
                    response_time_ms=response_time
                )
            else:
                return ApiResponse(
                    success=False,
                    data={"status_code": response.status_code},
                    error=f"HTTP {response.status_code}",
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ApiResponse(
                success=False,
                data=None,
                error=str(e),
                response_time_ms=response_time
            )
    
    async def get_exchange_rate_news(self) -> ApiResponse:
        """환율 뉴스 조회"""
        return await self._fetch_news("exchange-rate", {
            "category": "exchange_rate",
            "limit": 10
        })
    
    async def get_newyork_market_news(self) -> ApiResponse:
        """뉴욕 시장 뉴스 조회"""
        return await self._fetch_news("newyork-market", {
            "market": "us",
            "category": "market_watch",
            "limit": 10
        })
    
    async def get_kospi_close_news(self) -> ApiResponse:
        """코스피 종가 뉴스 조회"""
        return await self._fetch_news("kospi-close", {
            "market": "kospi",
            "category": "market_close",
            "limit": 5
        })
    
    async def get_news_by_category(self, category: str, params: Optional[Dict] = None) -> ApiResponse:
        """카테고리별 뉴스 조회"""
        return await self._fetch_news(category, params or {})
    
    async def get_status(self) -> Dict[str, Any]:
        """클라이언트 상태 조회 (UI 호환)"""
        connection_test = await self.test_connection() if self.is_connected else None
        
        return {
            "is_connected": self.is_connected,
            "base_url": str(self.config.base_url),
            "last_test": connection_test.dict() if connection_test else None,
            "config": {
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "retry_delay": self.config.retry_delay
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Private 메서드들
    async def _fetch_news(self, endpoint: str, params: Dict[str, Any]) -> ApiResponse:
        """뉴스 데이터 조회 (내부 메서드)"""
        if not self.is_connected or not self.client:
            return ApiResponse(
                success=False,
                data=None,
                error="API 클라이언트가 연결되지 않았습니다"
            )
        
        start_time = datetime.now()
        last_error = None
        
        # 재시도 로직
        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.get(
                    f"/{endpoint}",
                    params=params,
                    timeout=self.config.timeout
                )
                
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 뉴스 데이터 파싱
                    news_items = self._parse_news_data(data, endpoint)
                    
                    return ApiResponse(
                        success=True,
                        data={
                            "news": news_items,
                            "count": len(news_items),
                            "category": endpoint,
                            "raw_data": data
                        },
                        message=f"{endpoint} 뉴스 조회 성공",
                        response_time_ms=response_time
                    )
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
            except httpx.TimeoutException:
                last_error = f"타임아웃 ({self.config.timeout}초)"
            except httpx.RequestError as e:
                last_error = f"요청 오류: {str(e)}"
            except Exception as e:
                last_error = f"예상치 못한 오류: {str(e)}"
            
            # 재시도 전 대기
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(self.config.retry_delay)
                self.logger.warning(f"재시도 {attempt + 1}/{self.config.max_retries}: {last_error}")
        
        # 모든 재시도 실패
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return ApiResponse(
            success=False,
            data=None,
            error=f"최대 재시도 횟수 초과: {last_error}",
            response_time_ms=response_time
        )
    
    def _parse_news_data(self, raw_data: Any, category: str) -> List[NewsItem]:
        """원시 뉴스 데이터를 구조화된 NewsItem으로 파싱"""
        news_items = []
        
        try:
            # API 응답 형식에 따른 파싱 로직
            if isinstance(raw_data, dict):
                if "items" in raw_data:
                    items = raw_data["items"]
                elif "news" in raw_data:
                    items = raw_data["news"]
                else:
                    items = [raw_data]  # 단일 항목
            elif isinstance(raw_data, list):
                items = raw_data
            else:
                return []
            
            for item in items:
                if isinstance(item, dict):
                    news_item = NewsItem(
                        title=item.get("title", "제목 없음"),
                        content=item.get("content", item.get("summary", "내용 없음")),
                        timestamp=self._parse_timestamp(item.get("timestamp", item.get("date"))),
                        category=category,
                        url=item.get("url"),
                        source="POSCO InfoMax API"
                    )
                    news_items.append(news_item)
            
        except Exception as e:
            self.logger.error(f"뉴스 데이터 파싱 오류: {e}")
        
        return news_items
    
    def _parse_timestamp(self, timestamp_str: Any) -> datetime:
        """타임스탬프 문자열을 datetime 객체로 변환"""
        if not timestamp_str:
            return datetime.now()
        
        try:
            if isinstance(timestamp_str, str):
                # 다양한 날짜 형식 지원
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d",
                    "%m/%d/%Y %H:%M:%S"
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except ValueError:
                        continue
            
            return datetime.now()
        except:
            return datetime.now()

# 편의 함수들
async def create_infomax_client(config: Optional[ApiConfig] = None) -> ModernInfomaxClient:
    """InfoMax 클라이언트 생성 및 연결"""
    client = ModernInfomaxClient(config)
    await client.connect()
    return client
