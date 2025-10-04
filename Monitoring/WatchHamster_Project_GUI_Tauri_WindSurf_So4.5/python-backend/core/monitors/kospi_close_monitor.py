#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
증시마감 모니터

기존 WatchHamster_Project의 KospiCloseParser를 활용
"""

import sys
from pathlib import Path
from typing import Dict, Any
import asyncio

# 기존 WatchHamster_Project 경로 추가
watchhamster_project = Path(__file__).parents[5] / "WatchHamster_Project"
if watchhamster_project.exists():
    sys.path.insert(0, str(watchhamster_project))

from .base_monitor import BaseMonitor


class KospiCloseMonitor(BaseMonitor):
    """증시마감 모니터"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("kospi-close", config)
        
        # 기존 파서 임포트 시도
        try:
            from core.kospi_close_parser import KospiCloseParser
            self.parser = KospiCloseParser()
            self.logger.info("KospiCloseParser loaded successfully")
        except ImportError as e:
            self.logger.warning(f"Could not import KospiCloseParser: {e}")
            self.parser = None

    async def fetch_data(self) -> Dict[str, Any]:
        """증시마감 데이터 가져오기"""
        self.logger.info("Fetching KOSPI close data...")
        
        await asyncio.sleep(0.5)  # API 호출 시뮬레이션
        
        return {
            "title": "코스피, 외국인 매수에 2,600선 회복",
            "content": "코스피 2,650포인트, 코스닥 900포인트 기록",
            "date": "2025-10-04",
            "time": "15:30",
            "raw_html": "<html>...</html>"
        }

    async def parse_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 파싱"""
        self.logger.info("Parsing KOSPI close data...")
        
        if self.parser:
            try:
                # 기존 파서 사용
                # parsed = self.parser.parse(raw_data)
                # return parsed.__dict__
                pass
            except Exception as e:
                self.logger.error(f"Parser error: {e}")
        
        # 간단한 파싱 (데모)
        return {
            "title": raw_data.get("title", ""),
            "market_situation": "상승",
            "main_indices": [
                {"name": "코스피", "value": 2650, "change_percent": 0.8},
                {"name": "코스닥", "value": 900, "change_percent": 1.2}
            ],
            "top_gainers": [
                {"name": "삼성전자", "change_percent": 2.5},
                {"name": "SK하이닉스", "change_percent": 3.1}
            ],
            "summary": "외국인 매수세로 상승 마감"
        }

    async def check_status(self, parsed_data: Dict[str, Any]) -> bool:
        """상태 확인"""
        if not parsed_data:
            return False
        
        required_fields = ["title", "market_situation"]
        return all(field in parsed_data for field in required_fields)


# 편의 함수
def create_monitor(config: Dict[str, Any] = None) -> KospiCloseMonitor:
    """모니터 인스턴스 생성"""
    return KospiCloseMonitor(config)
