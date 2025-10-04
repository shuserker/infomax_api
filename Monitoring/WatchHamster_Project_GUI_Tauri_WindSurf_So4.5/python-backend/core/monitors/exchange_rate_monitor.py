#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서환마감 모니터

기존 WatchHamster_Project의 ExchangeRateParser를 활용
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


class ExchangeRateMonitor(BaseMonitor):
    """서환마감 모니터"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("exchange-rate", config)
        
        # 기존 파서 임포트 시도
        try:
            from core.exchange_rate_parser import ExchangeRateParser
            self.parser = ExchangeRateParser()
            self.logger.info("ExchangeRateParser loaded successfully")
        except ImportError as e:
            self.logger.warning(f"Could not import ExchangeRateParser: {e}")
            self.parser = None

    async def fetch_data(self) -> Dict[str, Any]:
        """서환마감 데이터 가져오기"""
        self.logger.info("Fetching exchange rate data...")
        
        await asyncio.sleep(0.5)  # API 호출 시뮬레이션
        
        return {
            "title": "원달러 환율, 1,330원대 안정",
            "content": "달러 강세 진정, 원화 소폭 강세",
            "date": "2025-10-04",
            "time": "15:30",
            "raw_html": "<html>...</html>"
        }

    async def parse_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 파싱"""
        self.logger.info("Parsing exchange rate data...")
        
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
            "market_situation": "안정",
            "usd_krw_rate": {
                "rate": 1330.5,
                "change": -2.5,
                "change_percent": -0.19
            },
            "major_currencies": [
                {"currency_pair": "JPY/KRW", "rate": 900.2, "change_percent": 0.1},
                {"currency_pair": "EUR/KRW", "rate": 1450.8, "change_percent": -0.3}
            ],
            "summary": "달러 강세 진정, 원화 소폭 강세"
        }

    async def check_status(self, parsed_data: Dict[str, Any]) -> bool:
        """상태 확인"""
        if not parsed_data:
            return False
        
        required_fields = ["title", "market_situation"]
        return all(field in parsed_data for field in required_fields)


# 편의 함수
def create_monitor(config: Dict[str, Any] = None) -> ExchangeRateMonitor:
    """모니터 인스턴스 생성"""
    return ExchangeRateMonitor(config)
