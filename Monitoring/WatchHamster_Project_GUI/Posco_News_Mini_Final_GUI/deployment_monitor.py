#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 모니터링 시스템 (DeploymentMonitor)
POSCO 뉴스 시스템용 완전 독립 배포 모니터링 시스템

주요 기능:
- 📊 배포 각 단계별 상태 로깅 시스템
- ⏱️ 배포 소요 시간 측정 및 기록
- 📁 logs/ 폴더에 상세 로그 저장
- 🖥️ GUI에서 배포 진행 상황 실시간 표시
- 📈 배포 성능 분석 및 통계

Requirements: 5.1, 5.2 구현
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class DeploymentPhase(Enum):
    """배포 단계 열거형"""
    INITIALIZING = "initializing"
    PRE_CHECK = "pre_check"
    BACKUP = "backup"
    HTML_GENERATION = "html_generation"
    BRANCH_SWITCH = "branch_switch"
    MERGE_CHANGES = "merge_changes"
    COMMIT_CHANGES = "commit_changes"
    PUSH_REMOTE = "push_remote"
    VERIFY_PAGES = "verify_pages"
    SEND_NOTIFICATION = "send_notification"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    FAILED = "failed"


class MonitoringStatus(Enum):
    """모니터링 상태 열거형"""
    IDLE = "idle"
    MONITORING = "monitoring"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class DeploymentMetrics:
    """배포 메트릭 정보"""
    phase: DeploymentPhase
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
    
    def complete(self, success: bool = True, error_message: Optional[str] = None):
        """단계 완료 처리"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        if error_message:
            self.error_message = error_message


@dataclass
class DeploymentSession:
    """배포 세션 모니터링 정보"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    current_phase: DeploymentPhase = DeploymentPhase.INITIALIZING
    phases: Dict[str, DeploymentMetrics] = None
    overall_success: bool = False
    total_phases: int = 0
    completed_phases: int = 0
    progress_percentage: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    
    def __post_init__(self):
        if self.phases is None:
            self.phases = {}


class DeploymentMonitor:
    """배포 모니터링 시스템 클래스 (스탠드얼론)"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """배포 모니터링 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # logs 폴더 설정 (Requirements 5.1, 5.2)
        self.logs_dir = os.path.join(os.path.dirname(self.script_dir), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 로그 파일들
        self.deployment_log = os.path.join(self.logs_dir, "deployment_monitor.log")
        self.metrics_log = os.path.join(self.logs_dir, "deployment_metrics.json")
        self.performance_log = os.path.join(self.logs_dir, "deployment_performance.json")
        
        # 현재 모니터링 세션
        self.current_session: Optional[DeploymentSession] = None
        self.monitoring_status = MonitoringStatus.IDLE
        
        # GUI 콜백 함수들 (실시간 표시용)
        self.progress_callbacks: List[Callable[[str, float, Dict], None]] = []
        self.phase_callbacks: List[Callable[[DeploymentPhase, DeploymentMetrics], None]] = []
        self.completion_callbacks: List[Callable[[DeploymentSession], None]] = []
        self.error_callbacks: List[Callable[[str, Dict], None]] = []
        
        # 모니터링 설정
        self.monitoring_interval = 1.0  # 초
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.monitoring_lock = threading.Lock()
        
        # 성능 임계값 설정
        self.performance_thresholds = {
            DeploymentPhase.PRE_CHECK: 30.0,      # 30초
            DeploymentPhase.BACKUP: 60.0,         # 1분
            DeploymentPhase.HTML_GENERATION: 120.0,  # 2분
            DeploymentPhase.BRANCH_SWITCH: 45.0,  # 45초
            DeploymentPhase.MERGE_CHANGES: 90.0,  # 1.5분
            DeploymentPhase.COMMIT_CHANGES: 30.0, # 30초
            DeploymentPhase.PUSH_REMOTE: 180.0,   # 3분
            DeploymentPhase.VERIFY_PAGES: 300.0,  # 5분
            DeploymentPhase.SEND_NOTIFICATION: 30.0,  # 30초
            DeploymentPhase.CLEANUP: 30.0         # 30초
        }
        
        self.log_message("🔧 배포 모니터링 시스템 초기화 완료 (스탠드얼론)")
    
    def log_message(self, message: str, level: str = "INFO"):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        try:
            with open(self.deployment_log, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"❌ 로그 파일 쓰기 실패: {e}")
    
    def register_progress_callback(self, callback: Callable[[str, float, Dict], None]):
        """진행 상황 콜백 등록 (GUI용)"""
        self.progress_callbacks.append(callback)
    
    def register_phase_callback(self, callback: Callable[[DeploymentPhase, DeploymentMetrics], None]):
        """단계 변경 콜백 등록 (GUI용)"""
        self.phase_callbacks.append(callback)
    
    def register_completion_callback(self, callback: Callable[[DeploymentSession], None]):
        """완료 콜백 등록 (GUI용)"""
        self.completion_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable[[str, Dict], None]):
        """오류 콜백 등록 (GUI용)"""
        self.error_callbacks.append(callback)
    
    def _notify_progress(self, message: str, progress: float, details: Dict = None):
        """진행 상황 알림 (GUI 실시간 표시)"""
        if details is None:
            details = {}
        
        for callback in self.progress_callbacks:
            try:
                callback(message, progress, details)
            except Exception as e:
                self.log_message(f"❌ 진행 상황 콜백 오류: {e}", "ERROR")
    
    def _notify_phase_change(self, phase: DeploymentPhase, metrics: DeploymentMetrics):
        """단계 변경 알림"""
        for callback in self.phase_callbacks:
            try:
                callback(phase, metrics)
            except Exception as e:
                self.log_message(f"❌ 단계 변경 콜백 오류: {e}", "ERROR")
    
    def _notify_completion(self, session: DeploymentSession):
        """완료 알림"""
        for callback in self.completion_callbacks:
            try:
                callback(session)
            except Exception as e:
                self.log_message(f"❌ 완료 콜백 오류: {e}", "ERROR")
    
    def _notify_error(self, error_message: str, error_details: Dict):
        """오류 알림"""
        for callback in self.error_callbacks:
            try:
                callback(error_message, error_details)
            except Exception as e:
                self.log_message(f"❌ 오류 콜백 오류: {e}", "ERROR")
    
    def start_deployment_monitoring(self, session_id: str) -> bool:
        """배포 모니터링 시작 (Requirements 5.1)"""
        try:
            with self.monitoring_lock:
                if self.monitoring_status == MonitoringStatus.MONITORING:
                    self.log_message("⚠️ 이미 모니터링이 진행 중입니다", "WARNING")
                    return False
                
                # 새 배포 세션 생성
                self.current_session = DeploymentSession(
                    session_id=session_id,
                    start_time=time.time(),
                    total_phases=len(DeploymentPhase) - 3  # INITIALIZING, COMPLETED, FAILED 제외
                )
                
                self.monitoring_status = MonitoringStatus.MONITORING
                self.monitoring_active = True
                
                # 모니터링 스레드 시작
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    daemon=True
                )
                self.monitoring_thread.start()
                
                self.log_message(f"📊 배포 모니터링 시작: {session_id}")
                self._notify_progress(f"배포 모니터링 시작: {session_id}", 0.0)
                
                return True
                
        except Exception as e:
            error_msg = f"배포 모니터링 시작 실패: {str(e)}"
            self.log_message(f"❌ {error_msg}", "ERROR")
            self._notify_error(error_msg, {"session_id": session_id})
            return False
    
    def stop_deployment_monitoring(self, success: bool = True, error_message: Optional[str] = None):
        """배포 모니터링 중지"""
        try:
            with self.monitoring_lock:
                if self.monitoring_status != MonitoringStatus.MONITORING:
                    return
                
                self.monitoring_active = False
                
                if self.current_session:
                    # 세션 완료 처리
                    self.current_session.end_time = time.time()
                    self.current_session.total_duration = (
                        self.current_session.end_time - self.current_session.start_time
                    )
                    self.current_session.overall_success = success
                    
                    if not success and error_message:
                        self.current_session.error_count += 1
                    
                    # 최종 단계 설정
                    if success:
                        self.current_session.current_phase = DeploymentPhase.COMPLETED
                        self.current_session.progress_percentage = 100.0
                    else:
                        self.current_session.current_phase = DeploymentPhase.FAILED
                    
                    # 메트릭 저장
                    self._save_deployment_metrics(self.current_session)
                    
                    # 완료 알림
                    self._notify_completion(self.current_session)
                    
                    session_id = self.current_session.session_id
                    duration = self.current_session.total_duration
                    
                    if success:
                        self.log_message(f"✅ 배포 모니터링 완료: {session_id} (소요시간: {duration:.2f}초)")
                        self._notify_progress(f"배포 완료: {session_id}", 100.0)
                    else:
                        self.log_message(f"❌ 배포 모니터링 실패: {session_id} - {error_message}")
                        self._notify_error(f"배포 실패: {error_message}", {"session_id": session_id})
                
                self.monitoring_status = MonitoringStatus.IDLE
                
                # 모니터링 스레드 종료 대기
                if self.monitoring_thread and self.monitoring_thread.is_alive():
                    self.monitoring_thread.join(timeout=5)
                
        except Exception as e:
            self.log_message(f"❌ 배포 모니터링 중지 중 오류: {str(e)}", "ERROR")
    
    def update_deployment_phase(self, phase: DeploymentPhase, success: bool = True, 
                              error_message: Optional[str] = None, details: Dict = None):
        """배포 단계 업데이트 (Requirements 5.1, 5.2)"""
        if not self.current_session:
            self.log_message("⚠️ 활성 배포 세션이 없습니다", "WARNING")
            return
        
        try:
            # 이전 단계 완료 처리
            if self.current_session.current_phase != DeploymentPhase.INITIALIZING:
                prev_phase_key = self.current_session.current_phase.value
                if prev_phase_key in self.current_session.phases:
                    prev_metrics = self.current_session.phases[prev_phase_key]
                    if prev_metrics.end_time is None:
                        prev_metrics.complete(success, error_message)
                        
                        # 성능 임계값 확인
                        if prev_metrics.duration and prev_metrics.duration > self.performance_thresholds.get(self.current_session.current_phase, 300):
                            self.log_message(f"⚠️ 성능 임계값 초과: {self.current_session.current_phase.value} ({prev_metrics.duration:.2f}초)", "WARNING")
                            self.current_session.warning_count += 1
            
            # 새 단계 시작
            self.current_session.current_phase = phase
            phase_key = phase.value
            
            # 단계 메트릭 생성
            metrics = DeploymentMetrics(
                phase=phase,
                start_time=time.time(),
                details=details or {}
            )
            
            self.current_session.phases[phase_key] = metrics
            
            # 진행률 계산
            if phase != DeploymentPhase.FAILED:
                self.current_session.completed_phases += 1
                self.current_session.progress_percentage = (
                    self.current_session.completed_phases / self.current_session.total_phases * 100
                )
            
            # 오류 카운트 업데이트
            if not success:
                self.current_session.error_count += 1
            
            # 로그 및 알림
            phase_name = phase.value.replace('_', ' ').title()
            if success:
                self.log_message(f"📍 배포 단계 시작: {phase_name}")
                self._notify_progress(
                    f"{phase_name} 진행 중...", 
                    self.current_session.progress_percentage,
                    {"phase": phase.value, "details": details}
                )
            else:
                self.log_message(f"❌ 배포 단계 실패: {phase_name} - {error_message}", "ERROR")
                self._notify_error(f"{phase_name} 실패: {error_message}", {"phase": phase.value})
            
            # 단계 변경 알림
            self._notify_phase_change(phase, metrics)
            
        except Exception as e:
            error_msg = f"배포 단계 업데이트 중 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}", "ERROR")
            self._notify_error(error_msg, {"phase": phase.value if phase else "unknown"})
    
    def _monitoring_loop(self):
        """모니터링 루프 (백그라운드 실행)"""
        try:
            while self.monitoring_active and self.current_session:
                # 현재 단계 모니터링
                current_phase = self.current_session.current_phase
                
                if current_phase.value in self.current_session.phases:
                    metrics = self.current_session.phases[current_phase.value]
                    
                    # 실행 시간 계산
                    if metrics.end_time is None:
                        current_duration = time.time() - metrics.start_time
                        
                        # 성능 임계값 경고
                        threshold = self.performance_thresholds.get(current_phase, 300)
                        if current_duration > threshold * 0.8:  # 80% 도달 시 경고
                            warning_msg = f"⚠️ {current_phase.value} 단계 실행 시간 주의: {current_duration:.1f}초"
                            self.log_message(warning_msg, "WARNING")
                            self.current_session.warning_count += 1
                
                # 전체 배포 시간 모니터링
                total_duration = time.time() - self.current_session.start_time
                if total_duration > 1800:  # 30분 초과 시 경고
                    self.log_message(f"⚠️ 전체 배포 시간 초과: {total_duration:.1f}초", "WARNING")
                
                time.sleep(self.monitoring_interval)
                
        except Exception as e:
            self.log_message(f"❌ 모니터링 루프 오류: {str(e)}", "ERROR")
    
    def _save_deployment_metrics(self, session: DeploymentSession):
        """배포 메트릭 저장 (logs 폴더에 기록)"""
        try:
            # 메트릭 데이터 준비
            metrics_data = {
                "session_id": session.session_id,
                "timestamp": datetime.now().isoformat(),
                "start_time": session.start_time,
                "end_time": session.end_time,
                "total_duration": session.total_duration,
                "overall_success": session.overall_success,
                "progress_percentage": session.progress_percentage,
                "completed_phases": session.completed_phases,
                "total_phases": session.total_phases,
                "error_count": session.error_count,
                "warning_count": session.warning_count,
                "phases": {}
            }
            
            # 각 단계별 메트릭 추가
            for phase_key, metrics in session.phases.items():
                metrics_data["phases"][phase_key] = {
                    "phase": metrics.phase.value,
                    "start_time": metrics.start_time,
                    "end_time": metrics.end_time,
                    "duration": metrics.duration,
                    "success": metrics.success,
                    "error_message": metrics.error_message,
                    "details": metrics.details
                }
            
            # 기존 메트릭 로드
            existing_metrics = []
            if os.path.exists(self.metrics_log):
                with open(self.metrics_log, 'r', encoding='utf-8') as f:
                    existing_metrics = json.load(f)
            
            # 새 메트릭 추가
            existing_metrics.append(metrics_data)
            
            # 최근 100개 세션만 유지
            if len(existing_metrics) > 100:
                existing_metrics = existing_metrics[-100:]
            
            # 파일에 저장
            with open(self.metrics_log, 'w', encoding='utf-8') as f:
                json.dump(existing_metrics, f, ensure_ascii=False, indent=2)
            
            # 성능 분석 데이터 업데이트
            self._update_performance_analysis(session)
            
            self.log_message(f"💾 배포 메트릭 저장 완료: {session.session_id}")
            
        except Exception as e:
            self.log_message(f"❌ 배포 메트릭 저장 실패: {str(e)}", "ERROR")
    
    def _update_performance_analysis(self, session: DeploymentSession):
        """성능 분석 데이터 업데이트"""
        try:
            # 기존 성능 데이터 로드
            performance_data = {"summary": {}, "phase_averages": {}, "trends": []}
            if os.path.exists(self.performance_log):
                with open(self.performance_log, 'r', encoding='utf-8') as f:
                    performance_data = json.load(f)
            
            # 현재 세션 데이터 추가
            session_summary = {
                "session_id": session.session_id,
                "timestamp": datetime.now().isoformat(),
                "total_duration": session.total_duration,
                "success": session.overall_success,
                "error_count": session.error_count,
                "warning_count": session.warning_count,
                "phase_durations": {}
            }
            
            # 각 단계별 소요 시간 기록
            for phase_key, metrics in session.phases.items():
                if metrics.duration:
                    session_summary["phase_durations"][phase_key] = metrics.duration
            
            # 트렌드 데이터에 추가
            performance_data["trends"].append(session_summary)
            
            # 최근 50개 세션만 유지
            if len(performance_data["trends"]) > 50:
                performance_data["trends"] = performance_data["trends"][-50:]
            
            # 단계별 평균 시간 계산
            phase_totals = {}
            phase_counts = {}
            
            for trend in performance_data["trends"]:
                for phase, duration in trend.get("phase_durations", {}).items():
                    if phase not in phase_totals:
                        phase_totals[phase] = 0
                        phase_counts[phase] = 0
                    phase_totals[phase] += duration
                    phase_counts[phase] += 1
            
            # 평균 계산
            for phase in phase_totals:
                if phase_counts[phase] > 0:
                    performance_data["phase_averages"][phase] = phase_totals[phase] / phase_counts[phase]
            
            # 전체 요약 통계
            recent_sessions = performance_data["trends"][-10:]  # 최근 10개 세션
            if recent_sessions:
                total_durations = [s["total_duration"] for s in recent_sessions if s["total_duration"]]
                success_count = sum(1 for s in recent_sessions if s["success"])
                
                performance_data["summary"] = {
                    "recent_sessions_count": len(recent_sessions),
                    "average_duration": sum(total_durations) / len(total_durations) if total_durations else 0,
                    "success_rate": success_count / len(recent_sessions) * 100,
                    "last_updated": datetime.now().isoformat()
                }
            
            # 파일에 저장
            with open(self.performance_log, 'w', encoding='utf-8') as f:
                json.dump(performance_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.log_message(f"❌ 성능 분석 데이터 업데이트 실패: {str(e)}", "ERROR")
    
    def get_current_deployment_status(self) -> Optional[Dict[str, Any]]:
        """현재 배포 상태 조회 (GUI용)"""
        if not self.current_session:
            return None
        
        try:
            current_time = time.time()
            current_phase_duration = None
            
            # 현재 단계 실행 시간 계산
            if self.current_session.current_phase.value in self.current_session.phases:
                current_metrics = self.current_session.phases[self.current_session.current_phase.value]
                if current_metrics.end_time is None:
                    current_phase_duration = current_time - current_metrics.start_time
            
            return {
                "session_id": self.current_session.session_id,
                "current_phase": self.current_session.current_phase.value,
                "progress_percentage": self.current_session.progress_percentage,
                "total_duration": current_time - self.current_session.start_time,
                "current_phase_duration": current_phase_duration,
                "completed_phases": self.current_session.completed_phases,
                "total_phases": self.current_session.total_phases,
                "error_count": self.current_session.error_count,
                "warning_count": self.current_session.warning_count,
                "monitoring_status": self.monitoring_status.value
            }
            
        except Exception as e:
            self.log_message(f"❌ 현재 배포 상태 조회 실패: {str(e)}", "ERROR")
            return None
    
    def get_deployment_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """배포 히스토리 조회"""
        try:
            if not os.path.exists(self.metrics_log):
                return []
            
            with open(self.metrics_log, 'r', encoding='utf-8') as f:
                all_metrics = json.load(f)
            
            # 최신순으로 정렬하여 반환
            return sorted(all_metrics, key=lambda x: x.get('start_time', 0), reverse=True)[:limit]
            
        except Exception as e:
            self.log_message(f"❌ 배포 히스토리 조회 실패: {str(e)}", "ERROR")
            return []
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """성능 통계 조회"""
        try:
            if not os.path.exists(self.performance_log):
                return {"summary": {}, "phase_averages": {}, "trends": []}
            
            with open(self.performance_log, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.log_message(f"❌ 성능 통계 조회 실패: {str(e)}", "ERROR")
            return {"summary": {}, "phase_averages": {}, "trends": []}
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """오래된 로그 파일 정리"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            
            # 메트릭 로그 정리
            if os.path.exists(self.metrics_log):
                with open(self.metrics_log, 'r', encoding='utf-8') as f:
                    all_metrics = json.load(f)
                
                # 최근 데이터만 유지
                recent_metrics = [
                    m for m in all_metrics 
                    if m.get('start_time', 0) > cutoff_time
                ]
                
                if len(recent_metrics) != len(all_metrics):
                    with open(self.metrics_log, 'w', encoding='utf-8') as f:
                        json.dump(recent_metrics, f, ensure_ascii=False, indent=2)
                    
                    removed_count = len(all_metrics) - len(recent_metrics)
                    self.log_message(f"🧹 오래된 메트릭 {removed_count}개 정리 완료")
            
            # 성능 로그 정리
            if os.path.exists(self.performance_log):
                with open(self.performance_log, 'r', encoding='utf-8') as f:
                    performance_data = json.load(f)
                
                # 트렌드 데이터 정리
                if "trends" in performance_data:
                    original_count = len(performance_data["trends"])
                    performance_data["trends"] = [
                        t for t in performance_data["trends"]
                        if datetime.fromisoformat(t["timestamp"]).timestamp() > cutoff_time
                    ]
                    
                    if len(performance_data["trends"]) != original_count:
                        with open(self.performance_log, 'w', encoding='utf-8') as f:
                            json.dump(performance_data, f, ensure_ascii=False, indent=2)
                        
                        removed_count = original_count - len(performance_data["trends"])
                        self.log_message(f"🧹 오래된 성능 데이터 {removed_count}개 정리 완료")
            
        except Exception as e:
            self.log_message(f"❌ 로그 정리 중 오류: {str(e)}", "ERROR")


# 편의 함수들
def create_deployment_monitor(base_dir: Optional[str] = None) -> DeploymentMonitor:
    """배포 모니터 인스턴스 생성"""
    return DeploymentMonitor(base_dir)


def get_deployment_phase_from_string(phase_str: str) -> Optional[DeploymentPhase]:
    """문자열에서 배포 단계 열거형 변환"""
    try:
        return DeploymentPhase(phase_str.lower())
    except ValueError:
        return None


if __name__ == "__main__":
    # 테스트 코드
    print("🔧 배포 모니터링 시스템 테스트")
    
    monitor = create_deployment_monitor()
    
    # 테스트 세션 시작
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if monitor.start_deployment_monitoring(session_id):
        print(f"✅ 모니터링 시작: {session_id}")
        
        # 테스트 단계들 실행
        test_phases = [
            DeploymentPhase.PRE_CHECK,
            DeploymentPhase.HTML_GENERATION,
            DeploymentPhase.BRANCH_SWITCH,
            DeploymentPhase.PUSH_REMOTE
        ]
        
        for phase in test_phases:
            monitor.update_deployment_phase(phase, success=True, details={"test": True})
            time.sleep(1)  # 1초 대기
        
        # 모니터링 중지
        monitor.stop_deployment_monitoring(success=True)
        print("✅ 테스트 완료")
        
        # 상태 조회 테스트
        history = monitor.get_deployment_history(5)
        print(f"📊 히스토리 조회: {len(history)}개 세션")
        
        stats = monitor.get_performance_statistics()
        print(f"📈 성능 통계: {stats.get('summary', {})}")
    
    else:
        print("❌ 모니터링 시작 실패")