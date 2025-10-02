#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
내장형 캐시 데이터 모니터링 시스템 (완전 독립)
kospi, exchange 데이터를 data/ 폴더에서 캐시 관리

주요 기능:
- 📊 캐시 데이터 상태 모니터링
- ⚠️ 데이터 부족 시 GUI 경고 알림 및 자동 전송
- 📅 과거 데이터 사용 시 GUI에서 명시적 표시
- 🔄 캐시 데이터 자동 갱신 및 품질 관리

Requirements: 5.3 구현
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import tkinter as tk
from tkinter import messagebox
import logging


class CacheStatus(Enum):
    """캐시 상태"""
    FRESH = "fresh"           # 신선한 데이터
    STALE = "stale"          # 오래된 데이터
    EXPIRED = "expired"       # 만료된 데이터
    MISSING = "missing"       # 데이터 없음
    CORRUPTED = "corrupted"   # 손상된 데이터


class DataType(Enum):
    """데이터 타입"""
    KOSPI = "kospi"
    EXCHANGE_RATE = "exchange_rate"
    POSCO_STOCK = "posco_stock"
    NEWS_SENTIMENT = "news_sentiment"


@dataclass
class CacheInfo:
    """캐시 정보"""
    data_type: DataType
    status: CacheStatus
    last_updated: Optional[datetime]
    age_minutes: float
    quality_score: float
    confidence: float
    size_bytes: int
    file_path: str
    warning_message: Optional[str] = None


@dataclass
class CacheAlert:
    """캐시 알림"""
    alert_type: str
    data_type: DataType
    message: str
    timestamp: datetime
    severity: str  # 'info', 'warning', 'error', 'critical'
    auto_action: Optional[str] = None


class CacheMonitor:
    """캐시 데이터 모니터링 시스템"""
    
    def __init__(self, data_dir: Optional[str] = None, gui_callback: Optional[Callable] = None):
        """캐시 모니터 초기화"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir or os.path.join(self.script_dir, "../data")
        self.gui_callback = gui_callback  # GUI 알림 콜백
        
        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 캐시 파일 경로
        self.cache_files = {
            DataType.KOSPI: os.path.join(self.data_dir, "market_data_cache.json"),
            DataType.EXCHANGE_RATE: os.path.join(self.data_dir, "market_data_cache.json"),
            DataType.POSCO_STOCK: os.path.join(self.data_dir, "market_data_cache.json"),
            DataType.NEWS_SENTIMENT: os.path.join(self.data_dir, "market_data_cache.json")
        }
        
        # 모니터링 설정
        self.monitoring_config = {
            'check_interval_seconds': 30,      # 30초마다 체크
            'fresh_threshold_minutes': 5,      # 5분 이내는 신선
            'stale_threshold_minutes': 15,     # 15분 이내는 오래됨
            'expired_threshold_minutes': 60,   # 60분 이후는 만료
            'min_quality_threshold': 0.7,      # 최소 품질 기준 70%
            'min_confidence_threshold': 0.6,   # 최소 신뢰도 기준 60%
            'auto_refresh_enabled': True,      # 자동 갱신 활성화
            'gui_alerts_enabled': True         # GUI 알림 활성화
        }
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_thread = None
        self.cache_status = {}
        self.alert_history = []
        self.last_check_time = None
        
        # 로깅 설정
        self.setup_logging()
        
        # 알림 콜백 리스트
        self.alert_callbacks = []
        
        print(f"📊 캐시 모니터 초기화 완료 (데이터 디렉토리: {self.data_dir})")
    
    def setup_logging(self):
        """로깅 설정"""
        log_dir = os.path.join(self.data_dir, "../logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "cache_monitor.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('CacheMonitor')
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            self.logger.warning("모니터링이 이미 실행 중입니다")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("🔍 캐시 모니터링 시작")
        print("🔍 캐시 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("⏹️ 캐시 모니터링 중지")
        print("⏹️ 캐시 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                self.check_cache_status()
                time.sleep(self.monitoring_config['check_interval_seconds'])
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)  # 오류 시 10초 대기
    
    def check_cache_status(self) -> Dict[DataType, CacheInfo]:
        """캐시 상태 확인"""
        self.last_check_time = datetime.now()
        current_status = {}
        
        for data_type in DataType:
            cache_info = self._analyze_cache_file(data_type)
            current_status[data_type] = cache_info
            
            # 상태 변화 감지 및 알림
            self._check_status_changes(data_type, cache_info)
        
        self.cache_status = current_status
        return current_status
    
    def _analyze_cache_file(self, data_type: DataType) -> CacheInfo:
        """개별 캐시 파일 분석"""
        file_path = self.cache_files[data_type]
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            return CacheInfo(
                data_type=data_type,
                status=CacheStatus.MISSING,
                last_updated=None,
                age_minutes=float('inf'),
                quality_score=0.0,
                confidence=0.0,
                size_bytes=0,
                file_path=file_path,
                warning_message="캐시 파일이 존재하지 않습니다"
            )
        
        try:
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return CacheInfo(
                    data_type=data_type,
                    status=CacheStatus.CORRUPTED,
                    last_updated=None,
                    age_minutes=float('inf'),
                    quality_score=0.0,
                    confidence=0.0,
                    size_bytes=0,
                    file_path=file_path,
                    warning_message="캐시 파일이 비어있습니다"
                )
            
            # JSON 파일 로드 및 분석
            with open(file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 데이터 타입별 정보 추출
            data_info = self._extract_data_info(cache_data, data_type)
            
            if not data_info:
                return CacheInfo(
                    data_type=data_type,
                    status=CacheStatus.CORRUPTED,
                    last_updated=None,
                    age_minutes=float('inf'),
                    quality_score=0.0,
                    confidence=0.0,
                    size_bytes=file_size,
                    file_path=file_path,
                    warning_message=f"{data_type.value} 데이터를 찾을 수 없습니다"
                )
            
            # 타임스탬프 분석
            last_updated = None
            age_minutes = float('inf')
            
            if 'timestamp' in data_info:
                try:
                    last_updated = datetime.fromisoformat(data_info['timestamp'])
                    age_minutes = (datetime.now() - last_updated).total_seconds() / 60
                except:
                    pass
            
            # 품질 및 신뢰도 추출
            quality_score = data_info.get('quality_score', 0.0)
            confidence = data_info.get('confidence', 0.0)
            
            # 상태 결정
            status = self._determine_cache_status(age_minutes, quality_score, confidence)
            
            # 경고 메시지 생성
            warning_message = self._generate_warning_message(status, age_minutes, quality_score, confidence)
            
            return CacheInfo(
                data_type=data_type,
                status=status,
                last_updated=last_updated,
                age_minutes=age_minutes,
                quality_score=quality_score,
                confidence=confidence,
                size_bytes=file_size,
                file_path=file_path,
                warning_message=warning_message
            )
            
        except json.JSONDecodeError:
            return CacheInfo(
                data_type=data_type,
                status=CacheStatus.CORRUPTED,
                last_updated=None,
                age_minutes=float('inf'),
                quality_score=0.0,
                confidence=0.0,
                size_bytes=file_size,
                file_path=file_path,
                warning_message="JSON 파일이 손상되었습니다"
            )
        except Exception as e:
            return CacheInfo(
                data_type=data_type,
                status=CacheStatus.CORRUPTED,
                last_updated=None,
                age_minutes=float('inf'),
                quality_score=0.0,
                confidence=0.0,
                size_bytes=0,
                file_path=file_path,
                warning_message=f"파일 분석 오류: {str(e)}"
            )
    
    def _extract_data_info(self, cache_data: Dict, data_type: DataType) -> Optional[Dict]:
        """캐시 데이터에서 특정 데이터 타입 정보 추출"""
        try:
            market_data = cache_data.get('market_data', {})
            
            if data_type == DataType.KOSPI:
                return market_data.get('kospi')
            elif data_type == DataType.EXCHANGE_RATE:
                return market_data.get('exchange_rate')
            elif data_type == DataType.POSCO_STOCK:
                return market_data.get('posco_stock')
            elif data_type == DataType.NEWS_SENTIMENT:
                return market_data.get('news_sentiment')
            
            return None
        except:
            return None
    
    def _determine_cache_status(self, age_minutes: float, quality_score: float, confidence: float) -> CacheStatus:
        """캐시 상태 결정"""
        config = self.monitoring_config
        
        # 품질이나 신뢰도가 너무 낮으면 손상된 것으로 간주
        if (quality_score < config['min_quality_threshold'] or 
            confidence < config['min_confidence_threshold']):
            return CacheStatus.CORRUPTED
        
        # 나이에 따른 상태 결정
        if age_minutes <= config['fresh_threshold_minutes']:
            return CacheStatus.FRESH
        elif age_minutes <= config['stale_threshold_minutes']:
            return CacheStatus.STALE
        elif age_minutes <= config['expired_threshold_minutes']:
            return CacheStatus.EXPIRED
        else:
            return CacheStatus.EXPIRED
    
    def _generate_warning_message(self, status: CacheStatus, age_minutes: float, 
                                quality_score: float, confidence: float) -> Optional[str]:
        """경고 메시지 생성"""
        messages = []
        
        if status == CacheStatus.STALE:
            messages.append(f"데이터가 {age_minutes:.0f}분 전 것입니다")
        elif status == CacheStatus.EXPIRED:
            messages.append(f"데이터가 {age_minutes:.0f}분 전 것으로 만료되었습니다")
        elif status == CacheStatus.MISSING:
            messages.append("데이터가 없습니다")
        elif status == CacheStatus.CORRUPTED:
            messages.append("데이터가 손상되었거나 품질이 낮습니다")
        
        if quality_score < self.monitoring_config['min_quality_threshold']:
            messages.append(f"품질이 낮습니다 ({quality_score:.1%})")
        
        if confidence < self.monitoring_config['min_confidence_threshold']:
            messages.append(f"신뢰도가 낮습니다 ({confidence:.1%})")
        
        return "; ".join(messages) if messages else None
    
    def _check_status_changes(self, data_type: DataType, cache_info: CacheInfo):
        """상태 변화 감지 및 알림"""
        previous_status = self.cache_status.get(data_type)
        
        # 이전 상태와 비교
        if previous_status and previous_status.status != cache_info.status:
            self._create_status_change_alert(data_type, previous_status.status, cache_info.status)
        
        # 경고 상황 체크
        self._check_warning_conditions(data_type, cache_info)
    
    def _create_status_change_alert(self, data_type: DataType, old_status: CacheStatus, new_status: CacheStatus):
        """상태 변화 알림 생성"""
        severity = self._get_alert_severity(new_status)
        
        alert = CacheAlert(
            alert_type="status_change",
            data_type=data_type,
            message=f"{data_type.value} 데이터 상태가 {old_status.value}에서 {new_status.value}로 변경되었습니다",
            timestamp=datetime.now(),
            severity=severity
        )
        
        self._send_alert(alert)
    
    def _check_warning_conditions(self, data_type: DataType, cache_info: CacheInfo):
        """경고 조건 확인"""
        alerts = []
        
        # 데이터 부족 경고
        if cache_info.status in [CacheStatus.MISSING, CacheStatus.EXPIRED]:
            alert = CacheAlert(
                alert_type="data_shortage",
                data_type=data_type,
                message=f"{data_type.value} 데이터가 부족합니다. 자동 갱신을 시도합니다.",
                timestamp=datetime.now(),
                severity="warning",
                auto_action="refresh_data"
            )
            alerts.append(alert)
        
        # 품질 저하 경고
        if cache_info.quality_score < self.monitoring_config['min_quality_threshold']:
            alert = CacheAlert(
                alert_type="quality_degradation",
                data_type=data_type,
                message=f"{data_type.value} 데이터 품질이 낮습니다 ({cache_info.quality_score:.1%})",
                timestamp=datetime.now(),
                severity="warning"
            )
            alerts.append(alert)
        
        # 과거 데이터 사용 경고
        if cache_info.status == CacheStatus.STALE:
            alert = CacheAlert(
                alert_type="stale_data",
                data_type=data_type,
                message=f"{data_type.value} 과거 데이터를 사용 중입니다 ({cache_info.age_minutes:.0f}분 전)",
                timestamp=datetime.now(),
                severity="info"
            )
            alerts.append(alert)
        
        # 알림 전송
        for alert in alerts:
            self._send_alert(alert)
    
    def _get_alert_severity(self, status: CacheStatus) -> str:
        """알림 심각도 결정"""
        severity_map = {
            CacheStatus.FRESH: "info",
            CacheStatus.STALE: "info",
            CacheStatus.EXPIRED: "warning",
            CacheStatus.MISSING: "error",
            CacheStatus.CORRUPTED: "critical"
        }
        return severity_map.get(status, "info")
    
    def _send_alert(self, alert: CacheAlert):
        """알림 전송"""
        # 알림 히스토리에 추가
        self.alert_history.append(alert)
        
        # 최근 100개 알림만 유지
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # 로그 기록
        self.logger.info(f"[{alert.severity.upper()}] {alert.data_type.value}: {alert.message}")
        
        # GUI 콜백 호출
        if self.gui_callback and self.monitoring_config['gui_alerts_enabled']:
            try:
                self.gui_callback(alert)
            except Exception as e:
                self.logger.error(f"GUI 콜백 오류: {e}")
        
        # 등록된 콜백들 호출
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"알림 콜백 오류: {e}")
        
        # 자동 액션 실행
        if alert.auto_action:
            self._execute_auto_action(alert)
    
    def _execute_auto_action(self, alert: CacheAlert):
        """자동 액션 실행"""
        if not self.monitoring_config['auto_refresh_enabled']:
            return
        
        if alert.auto_action == "refresh_data":
            self.logger.info(f"자동 데이터 갱신 시도: {alert.data_type.value}")
            try:
                # DynamicDataManager를 통한 자동 데이터 갱신
                self._trigger_data_refresh()
                self.logger.info(f"자동 데이터 갱신 완료: {alert.data_type.value}")
            except Exception as e:
                self.logger.error(f"자동 데이터 갱신 실패: {e}")
    
    def _trigger_data_refresh(self):
        """데이터 갱신 트리거"""
        try:
            # DynamicDataManager 임포트 및 실행
            import sys
            import os
            parent_dir = os.path.dirname(self.script_dir)
            sys.path.insert(0, os.path.join(parent_dir, "Posco_News_Mini_Final_GUI"))
            
            from dynamic_data_manager import DynamicDataManager
            
            # 데이터 매니저 생성 및 데이터 수집
            data_manager = DynamicDataManager(data_dir=self.data_dir)
            market_data = data_manager.collect_market_data()
            
            self.logger.info("DynamicDataManager를 통한 데이터 갱신 완료")
            return True
            
        except ImportError as e:
            self.logger.warning(f"DynamicDataManager 임포트 실패: {e}")
            return False
        except Exception as e:
            self.logger.error(f"데이터 갱신 중 오류: {e}")
            return False
    
    def add_alert_callback(self, callback: Callable[[CacheAlert], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[CacheAlert], None]):
        """알림 콜백 제거"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """캐시 상태 요약"""
        if not self.cache_status:
            self.check_cache_status()
        
        summary = {
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'total_data_types': len(DataType),
            'status_counts': {},
            'overall_health': 'unknown',
            'warnings': [],
            'recommendations': []
        }
        
        # 상태별 카운트
        for status in CacheStatus:
            summary['status_counts'][status.value] = 0
        
        for cache_info in self.cache_status.values():
            summary['status_counts'][cache_info.status.value] += 1
            
            if cache_info.warning_message:
                summary['warnings'].append({
                    'data_type': cache_info.data_type.value,
                    'message': cache_info.warning_message
                })
        
        # 전체 건강도 평가
        fresh_count = summary['status_counts'][CacheStatus.FRESH.value]
        total_count = len(self.cache_status)
        
        if total_count == 0:
            summary['overall_health'] = 'unknown'
        elif fresh_count == total_count:
            summary['overall_health'] = 'excellent'
        elif fresh_count >= total_count * 0.7:
            summary['overall_health'] = 'good'
        elif fresh_count >= total_count * 0.5:
            summary['overall_health'] = 'fair'
        else:
            summary['overall_health'] = 'poor'
        
        # 권장사항 생성
        if summary['status_counts'][CacheStatus.MISSING.value] > 0:
            summary['recommendations'].append("누락된 데이터를 갱신하세요")
        if summary['status_counts'][CacheStatus.EXPIRED.value] > 0:
            summary['recommendations'].append("만료된 데이터를 새로고침하세요")
        if summary['status_counts'][CacheStatus.CORRUPTED.value] > 0:
            summary['recommendations'].append("손상된 데이터를 복구하세요")
        
        return summary
    
    def get_detailed_status(self) -> Dict[DataType, CacheInfo]:
        """상세 캐시 상태 조회"""
        if not self.cache_status:
            self.check_cache_status()
        return self.cache_status.copy()
    
    def get_recent_alerts(self, limit: int = 10) -> List[CacheAlert]:
        """최근 알림 조회"""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def clear_alert_history(self):
        """알림 히스토리 초기화"""
        self.alert_history.clear()
        self.logger.info("알림 히스토리가 초기화되었습니다")
    
    def get_gui_status_text(self) -> str:
        """GUI용 상태 텍스트 생성"""
        summary = self.get_cache_summary()
        
        status_text = f"캐시 상태: {summary['overall_health']}\n"
        status_text += f"마지막 확인: {summary['last_check']}\n\n"
        
        # 데이터 타입별 상태
        for data_type, cache_info in self.get_detailed_status().items():
            status_icon = "✅" if cache_info.status == CacheStatus.FRESH else "⚠️"
            status_text += f"{status_icon} {data_type.value}: {cache_info.status.value}\n"
            
            if cache_info.warning_message:
                status_text += f"   └ {cache_info.warning_message}\n"
        
        return status_text
    
    def get_data_age_info(self) -> Dict[str, str]:
        """데이터 나이 정보 반환 (GUI 표시용)"""
        age_info = {}
        
        for data_type, cache_info in self.get_detailed_status().items():
            if cache_info.last_updated:
                age_minutes = (datetime.now() - cache_info.last_updated).total_seconds() / 60
                
                if age_minutes < 1:
                    age_text = "방금 전"
                elif age_minutes < 60:
                    age_text = f"{age_minutes:.0f}분 전"
                elif age_minutes < 1440:  # 24시간
                    age_text = f"{age_minutes/60:.1f}시간 전"
                else:
                    age_text = f"{age_minutes/1440:.1f}일 전"
                
                # 과거 데이터 표시
                if cache_info.status == CacheStatus.STALE:
                    age_text += " (과거 데이터)"
                elif cache_info.status == CacheStatus.EXPIRED:
                    age_text += " (만료된 데이터)"
                
                age_info[data_type.value] = age_text
            else:
                age_info[data_type.value] = "데이터 없음"
        
        return age_info
    
    def update_config(self, config_updates: Dict[str, Any]):
        """모니터링 설정 업데이트"""
        self.monitoring_config.update(config_updates)
        self.logger.info(f"모니터링 설정 업데이트: {config_updates}")
    
    def set(self, key: str, value: Any):
        """캐시 데이터 설정 (테스트용)"""
        # 간단한 테스트용 캐시 저장
        if not hasattr(self, '_test_cache'):
            self._test_cache = {}
        self._test_cache[key] = value
        print(f"💾 캐시 저장: {key}")
    
    def get(self, key: str) -> Any:
        """캐시 데이터 조회 (테스트용)"""
        if hasattr(self, '_test_cache') and key in self._test_cache:
            print(f"✅ 캐시 히트: {key}")
            return self._test_cache[key]
        return None
    
    def force_refresh_all(self):
        """모든 캐시 강제 새로고침"""
        self.logger.info("모든 캐시 강제 새로고침 시작")
        try:
            success = self._trigger_data_refresh()
            if success:
                self.logger.info("모든 캐시 강제 새로고침 완료")
                # 새로고침 후 상태 재확인
                self.check_cache_status()
            else:
                self.logger.warning("캐시 새로고침 실패")
            return success
        except Exception as e:
            self.logger.error(f"캐시 강제 새로고침 오류: {e}")
            return False
    
    def export_status_report(self, file_path: Optional[str] = None) -> str:
        """상태 보고서 내보내기"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.data_dir, f"cache_status_report_{timestamp}.json")
        
        # JSON 직렬화 가능한 형태로 변환
        detailed_status = {}
        for data_type, cache_info in self.get_detailed_status().items():
            cache_dict = asdict(cache_info)
            # Enum 값을 문자열로 변환
            cache_dict['data_type'] = cache_info.data_type.value
            cache_dict['status'] = cache_info.status.value
            # datetime 객체를 ISO 문자열로 변환
            if hasattr(cache_info, 'last_updated') and cache_info.last_updated:
                cache_dict['last_updated'] = cache_info.last_updated.isoformat()
            detailed_status[data_type.value] = cache_dict
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_cache_summary(),
            'detailed_status': detailed_status,
            'recent_alerts': [
                {
                    'alert_type': alert.alert_type,
                    'data_type': alert.data_type.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'severity': alert.severity,
                    'auto_action': alert.auto_action
                }
                for alert in self.get_recent_alerts(50)
            ],
            'monitoring_config': self.monitoring_config
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"상태 보고서 저장: {file_path}")
        return file_path


def create_gui_alert_handler(parent_window=None):
    """GUI 알림 핸들러 생성"""
    def handle_alert(alert: CacheAlert):
        """GUI 알림 처리"""
        try:
            if alert.severity in ['error', 'critical']:
                messagebox.showerror(
                    f"캐시 모니터 - {alert.data_type.value}",
                    alert.message,
                    parent=parent_window
                )
            elif alert.severity == 'warning':
                messagebox.showwarning(
                    f"캐시 모니터 - {alert.data_type.value}",
                    alert.message,
                    parent=parent_window
                )
            else:
                messagebox.showinfo(
                    f"캐시 모니터 - {alert.data_type.value}",
                    alert.message,
                    parent=parent_window
                )
        except Exception as e:
            print(f"GUI 알림 표시 오류: {e}")
    
    return handle_alert


# 테스트 및 데모 함수
def demo_cache_monitor():
    """캐시 모니터 데모"""
    print("🔍 캐시 모니터 데모 시작")
    
    # 캐시 모니터 생성
    monitor = CacheMonitor()
    
    # GUI 알림 핸들러 추가 (실제 GUI 없이 콘솔 출력)
    def console_alert_handler(alert: CacheAlert):
        print(f"[{alert.severity.upper()}] {alert.data_type.value}: {alert.message}")
    
    monitor.add_alert_callback(console_alert_handler)
    
    # 캐시 상태 확인
    print("\n📊 캐시 상태 확인:")
    status = monitor.check_cache_status()
    
    for data_type, cache_info in status.items():
        print(f"  {data_type.value}: {cache_info.status.value}")
        if cache_info.warning_message:
            print(f"    ⚠️ {cache_info.warning_message}")
    
    # 요약 정보 출력
    print("\n📋 캐시 요약:")
    summary = monitor.get_cache_summary()
    print(f"  전체 건강도: {summary['overall_health']}")
    print(f"  상태별 카운트: {summary['status_counts']}")
    
    if summary['warnings']:
        print("  ⚠️ 경고사항:")
        for warning in summary['warnings']:
            print(f"    - {warning['data_type']}: {warning['message']}")
    
    if summary['recommendations']:
        print("  💡 권장사항:")
        for rec in summary['recommendations']:
            print(f"    - {rec}")
    
    # 모니터링 시작 (짧은 시간)
    print("\n🔄 모니터링 시작 (10초간)...")
    monitor.start_monitoring()
    time.sleep(10)
    monitor.stop_monitoring()
    
    # 최근 알림 확인
    recent_alerts = monitor.get_recent_alerts()
    if recent_alerts:
        print(f"\n📢 최근 알림 ({len(recent_alerts)}개):")
        for alert in recent_alerts:
            print(f"  [{alert.timestamp.strftime('%H:%M:%S')}] {alert.message}")
    
    # 보고서 생성
    report_path = monitor.export_status_report()
    print(f"\n📄 상태 보고서 생성: {report_path}")
    
    print("✅ 캐시 모니터 데모 완료")


if __name__ == "__main__":
    demo_cache_monitor()