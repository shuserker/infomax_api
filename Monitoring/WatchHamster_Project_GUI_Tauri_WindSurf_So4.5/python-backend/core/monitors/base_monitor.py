#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기본 모니터 인터페이스

모든 모니터가 상속받아야 하는 기본 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class BaseMonitor(ABC):
    """모니터 기본 클래스"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            name: 모니터 이름
            config: 설정 딕셔너리
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.last_check = None
        self.error_count = 0
        self.last_error = None

    @abstractmethod
    async def fetch_data(self) -> Dict[str, Any]:
        """데이터를 가져옵니다.
        
        Returns:
            가져온 데이터 딕셔너리
        """
        pass

    @abstractmethod
    async def parse_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터를 파싱합니다.
        
        Args:
            raw_data: 원본 데이터
            
        Returns:
            파싱된 데이터 딕셔너리
        """
        pass

    @abstractmethod
    async def check_status(self, parsed_data: Dict[str, Any]) -> bool:
        """상태를 확인합니다.
        
        Args:
            parsed_data: 파싱된 데이터
            
        Returns:
            정상 여부
        """
        pass

    async def run(self) -> Dict[str, Any]:
        """모니터를 실행합니다.
        
        Returns:
            실행 결과 딕셔너리
        """
        try:
            self.logger.info(f"Starting monitor: {self.name}")
            
            # 데이터 가져오기
            raw_data = await self.fetch_data()
            
            # 데이터 파싱
            parsed_data = await self.parse_data(raw_data)
            
            # 상태 확인
            is_healthy = await self.check_status(parsed_data)
            
            # 결과 기록
            self.last_check = datetime.utcnow()
            
            result = {
                "success": True,
                "monitor": self.name,
                "timestamp": self.last_check.isoformat(),
                "healthy": is_healthy,
                "data": parsed_data,
                "error": None
            }
            
            self.logger.info(f"Monitor {self.name} completed successfully")
            return result
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.logger.error(f"Monitor {self.name} failed: {e}", exc_info=True)
            
            return {
                "success": False,
                "monitor": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "healthy": False,
                "data": None,
                "error": str(e)
            }

    def get_status(self) -> Dict[str, Any]:
        """모니터 상태를 반환합니다."""
        return {
            "name": self.name,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_count": self.error_count,
            "last_error": self.last_error
        }
