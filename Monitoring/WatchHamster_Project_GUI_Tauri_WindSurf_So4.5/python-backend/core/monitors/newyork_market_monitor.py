#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴욕마켓워치 모니터

기존 WatchHamster_Project의 NewYorkMarketParser를 활용
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


class NewYorkMarketMonitor(BaseMonitor):
    """뉴욕마켓워치 모니터"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("newyork-market-watch", config)
        
        # 기존 파서 임포트 시도
        try:
            from core.newyork_market_parser import NewYorkMarketParser
            self.parser = NewYorkMarketParser()
            self.logger.info("NewYorkMarketParser loaded successfully")
        except ImportError as e:
            self.logger.warning(f"Could not import NewYorkMarketParser: {e}")
            self.parser = None

    async def fetch_data(self) -> Dict[str, Any]:
        """뉴욕마켓워치 데이터 가져오기"""
        # TODO: 실제 API 호출 구현
        # 현재는 데모 데이터 반환
        self.logger.info("Fetching New York market data...")
        
        await asyncio.sleep(0.5)  # API 호출 시뮬레이션
        
        return {
            "title": "뉴욕증시, 기술주 강세에 상승 마감",
            "content": "다우 35,000포인트, 나스닥 14,500포인트 기록",
            "date": "2025-10-04",
            "time": "05:00",
            "raw_html": "<html>...</html>"
        }

    async def parse_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 파싱"""
        self.logger.info("Parsing New York market data...")
        
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
            "major_indices": [
                {"name": "다우", "value": 35000, "change_percent": 0.5},
                {"name": "나스닥", "value": 14500, "change_percent": 0.8},
                {"name": "S&P500", "value": 4500, "change_percent": 0.6}
            ],
            "summary": "기술주 강세로 상승 마감"
        }

    async def check_status(self, parsed_data: Dict[str, Any]) -> bool:
        """상태 확인"""
        # 데이터가 정상적으로 파싱되었는지 확인
        if not parsed_data:
            return False
        
        required_fields = ["title", "market_situation"]
        return all(field in parsed_data for field in required_fields)


# 편의 함수
def create_monitor(config: Dict[str, Any] = None) -> NewYorkMarketMonitor:
    """모니터 인스턴스 생성"""
    return NewYorkMarketMonitor(config)
