#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitor
POSCO 모니터링 시스템

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import psutil
import .comprehensive_repair_backup/realtime_news_monitor.py.backup_20250809_181657
import test_config.json
import posco_news_250808_monitor.log
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import statistics
from collections import deque, defaultdict

class PerformanceLevel(Enum):
    """성능 수준 열거형"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"

class MetricType(Enum):
    """메트릭 타입 열거형"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    PROCESS_COUNT = "process_count"
    SYSTEM_LOAD = "system_load"

@dataclass
class PerformanceMetric:
    """성능 메트릭 데이터 클래스"""
    timestamp: datetime
    metric_type: MetricType
    value: float
process_name:_Optional[str] =  None
operation_name:_Optional[str] =  None
additional_data:_Optional[Dict[str,_Any]] =  None

@dataclass
class SystemPerformanceSnapshot:
    """시스템 성능 스냅샷"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    process_count: int
    active_processes: List[str]
system_load_avg:_Optional[Tuple[float,_float,_float]] =  None
network_io:_Optional[Dict[str,_int]] =  None

@dataclass
class ProcessPerformanceData:
    """프로세스별 성능 데이터"""
    process_name: str
    pid: int
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: datetime
    num_threads: int
io_counters:_Optional[Dict[str,_int]] =  None

@dataclass
class PerformanceComparison:
    """v1/v2 성능 비교 결과"""
    comparison_time: datetime
    v1_metrics: Dict[str, float]
    v2_metrics: Dict[str, float]
    improvement_percentage: Dict[str, float]
    recommendations: List[str]

class PerformanceMonitor:
    """
    POSCO WatchHamster v3.0.0 성능 모니터링 시스템
    
    시스템 리소스 사용량을 실시간으로 추적하고,
    성능 최적화를 위한 분석 및 권장사항을 제공합니다.
    """
    
    def __init__(self, script_dir: str, monitoring_interval: int = 60):
        """
        PerformanceMonitor 초기화
        
        Args:
            script_dir (str): 스크립트 디렉토리 경로
            monitoring_interval (int): 모니터링 간격 (초)
        """
        self.script_dir = script_dir
        self.monitoring_interval = monitoring_interval
        self.logger = logging.getLogger(__name__)
        
        # 성능 데이터 저장소
self.metrics_history:_deque =  deque(maxlen=1440)  # 24시간 분량 (1분 간격)
self.process_metrics:_Dict[str,_deque] =  defaultdict(lambda: deque(maxlen=60))  # 1시간 분량
self.response_times:_Dict[str,_deque] =  defaultdict(lambda: deque(maxlen=100))  # 최근 100회
        
        # 성능 임계값 설정
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'response_time_warning': 5.0,  # 5초
            'response_time_critical': 10.0,  # 10초
            'process_count_warning': 20,
            'process_count_critical': 30
        }
        
        # 모니터링 상태
        self.is_monitoring = False
        self.monitoring_thread = None
        self.start_time = datetime.now()
        
        # 성능 통계
        self.total_measurements = 0
        self.alert_count = 0
        self.last_optimization_check = datetime.now()
        
        # v1/v2 비교 데이터
        self.v1_baseline = None
        self.v2_performance_data = {}
        
        self.logger.info("📊 PerformanceMonitor 초기화 완료")
    
    def start_monitoring(self):
        """성능 모니터링 시작"""
        if self.is_monitoring:
            self.logger.warning("성능 모니터링이 이미 실행 중입니다")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info(f"📊 성능 모니터링 시작 (간격: {self.monitoring_interval}초)")
    
    def stop_monitoring(self):
        """성능 모니터링 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("📊 성능 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 메인 루프"""
        while self.is_monitoring:
            try:
                # 시스템 성능 스냅샷 수집
                snapshot = self._collect_system_snapshot()
                self.metrics_history.append(snapshot)
                
                # 프로세스별 성능 데이터 수집
                self._collect_process_metrics()
                
                # 성능 분석 및 알림 체크
                self._analyze_performance()
                
self.total_measurements_+ =  1
                
                # 다음 측정까지 대기
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"성능 모니터링 중 오류 발생: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_snapshot(self) -> SystemPerformanceSnapshot:
        """시스템 성능 스냅샷 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # 프로세스 수
            process_count = len(psutil.pids())
            
            # 활성 프로세스 목록 (워치햄스터 관련)
            active_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('posco' in cmd.lower() or 'watchhamster' in cmd.lower() 
                                                   for cmd in proc.info['cmdline']):
                        active_processes.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 시스템 로드 (Linux/macOS만)
            system_load_avg = None
            try:
                if hasattr(os, 'getloadavg'):
                    system_load_avg = os.getloadavg()
            except (OSError, AttributeError):
                pass
            
            # 네트워크 I/O
            network_io = None
            try:
                net_io = psutil.net_io_counters()
                if net_io:
                    network_io = {
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv,
                        'packets_sent': net_io.packets_sent,
                        'packets_recv': net_io.packets_recv
                    }
            except Exception:
                pass
            
            return SystemPerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                process_count=process_count,
                active_processes=active_processes,
                system_load_avg=system_load_avg,
                network_io=network_io
            )
            
        except Exception as e:
            self.logger.error(f"시스템 스냅샷 수집 실패: {e}")
            # 기본값으로 빈 스냅샷 반환
            return SystemPerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                process_count=0,
                active_processes=[]
            )
    
    def _collect_process_metrics(self):
        """프로세스별 성능 메트릭 수집"""
        try:
            current_time = datetime.now()
            
            # 워치햄스터 관련 프로세스 찾기
            watchhamster_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 
                                           'memory_percent', 'memory_info', 'status', 
                                           'create_time', 'num_threads']):
                try:
                    if not proc.info['cmdline']:
                        continue
                    
                    # 워치햄스터 관련 프로세스 식별
                    cmdline_str = ' '.join(proc.info['cmdline']).lower()
                    if any(keyword in cmdline_str for keyword in 
                          ['posco', 'watchhamster', 'monitor_watchhamster', 
                           'POSCO News 250808_monitor', 
                           'integrated_report_scheduler']):
                        
                        # I/O 카운터 수집 (가능한 경우)
                        io_counters = None
                        try:
                            io_info = proc.io_counters()
                            if io_info:
                                io_counters = {
                                    'read_count': io_info.read_count,
                                    'write_count': io_info.write_count,
                                    'read_bytes': io_info.read_bytes,
                                    'write_bytes': io_info.write_bytes
                                }
                        except (psutil.AccessDenied, AttributeError):
                            pass
                        
                        process_data = ProcessPerformanceData(
                            process_name=proc.info['name'],
                            pid=proc.info['pid'],
                            cpu_percent=proc.info['cpu_percent'] or 0.0,
                            memory_percent=proc.info['memory_percent'] or 0.0,
                            memory_mb=(proc.info['memory_info'].rss / (1024 * 1024)) if proc.info['memory_info'] else 0.0,
                            status=proc.info['status'],
                            create_time=datetime.fromtimestamp(proc.info['create_time']),
                            num_threads=proc.info['num_threads'] or 0,
                            io_counters=io_counters
                        )
                        
                        watchhamster_processes.append(process_data)
                        
                        # 프로세스별 히스토리에 추가
                        process_key = f"{proc.info['name']}_{proc.info['pid']}"
                        self.process_metrics[process_key].append(process_data)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 수집된 프로세스 수 로그
            if watchhamster_processes:
                self.logger.debug(f"프로세스 메트릭 수집 완료: {len(watchhamster_processes)}개 프로세스")
            
        except Exception as e:
            self.logger.error(f"프로세스 메트릭 수집 실패: {e}")
    
    def _analyze_performance(self):
        """성능 분석 및 알림 체크"""
        try:
            if not self.metrics_history:
                return
            
            latest_snapshot = self.metrics_history[-1]
            
            # CPU 사용률 체크
            if latest_snapshot.cpu_percent > self.thresholds['cpu_critical']:
                self._trigger_performance_alert(
                    MetricType.CPU_USAGE, 
                    latest_snapshot.cpu_percent, 
                    PerformanceLevel.CRITICAL
                )
            elif latest_snapshot.cpu_percent > self.thresholds['cpu_warning']:
                self._trigger_performance_alert(
                    MetricType.CPU_USAGE, 
                    latest_snapshot.cpu_percent, 
                    PerformanceLevel.WARNING
                )
            
            # 메모리 사용률 체크
            if latest_snapshot.memory_percent > self.thresholds['memory_critical']:
                self._trigger_performance_alert(
                    MetricType.MEMORY_USAGE, 
                    latest_snapshot.memory_percent, 
                    PerformanceLevel.CRITICAL
                )
            elif latest_snapshot.memory_percent > self.thresholds['memory_warning']:
                self._trigger_performance_alert(
                    MetricType.MEMORY_USAGE, 
                    latest_snapshot.memory_percent, 
                    PerformanceLevel.WARNING
                )
            
            # 프로세스 수 체크
            if latest_snapshot.process_count > self.thresholds['process_count_critical']:
                self._trigger_performance_alert(
                    MetricType.PROCESS_COUNT, 
                    latest_snapshot.process_count, 
                    PerformanceLevel.CRITICAL
                )
            elif latest_snapshot.process_count > self.thresholds['process_count_warning']:
                self._trigger_performance_alert(
                    MetricType.PROCESS_COUNT, 
                    latest_snapshot.process_count, 
                    PerformanceLevel.WARNING
                )
            
            # 최적화 권장사항 체크 (1시간마다)
            if datetime.now() - self.last_optimization_check > timedelta(hours=1):
                self._check_optimization_opportunities()
                self.last_optimization_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"성능 분석 중 오류 발생: {e}")
    
    def _trigger_performance_alert(self, metric_type: MetricType, value: float, level: PerformanceLevel):
        """성능 알림 트리거"""
        try:
self.alert_count_+ =  1
            
            alert_message = self._generate_alert_message(metric_type, value, level)
            
            # 로그 기록
            if level == PerformanceLevel.CRITICAL:
                self.logger.critical(alert_message)
            elif level == PerformanceLevel.WARNING:
                self.logger.warning(alert_message)
            else:
                self.logger.info(alert_message)
            
            # 알림 히스토리에 기록
            alert_record = {
                'timestamp': datetime.now().isoformat(),
                'metric_type': metric_type.value,
                'value': value,
                'level': level.value,
                'message': alert_message
            }
            
            # 알림 히스토리 파일에 저장
            self._save_alert_to_history(alert_record)
            
        except Exception as e:
            self.logger.error(f"성능 알림 트리거 실패: {e}")
    
    def _generate_alert_message(self, metric_type: MetricType, value: float, level: PerformanceLevel) -> str:
        """알림 메시지 생성"""
        level_emoji = {
            PerformanceLevel.WARNING: "⚠️",
            PerformanceLevel.CRITICAL: "🚨"
        }
        
        metric_names = {
            MetricType.CPU_USAGE: "CPU 사용률",
            MetricType.MEMORY_USAGE: "메모리 사용률",
            MetricType.PROCESS_COUNT: "프로세스 수"
        }
        
        emoji = level_emoji.get(level, "ℹ️")
        metric_name = metric_names.get(metric_type, str(metric_type.value))
        
        if metric_type in [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]:
            return f"{emoji} {metric_name} {level.value.upper()}: {value:.1f}%"
        else:
            return f"{emoji} {metric_name} {level.value.upper()}: {value}"
    
    def _save_alert_to_history(self, alert_record: Dict[str, Any]):
        """알림 히스토리 저장"""
        try:
            history_file = os.path.join(self.script_dir, 'performance_alerts.json')
            
            # 기존 히스토리 로드
            alerts_history = []
            if os.path.exists(history_file):
                try:
with_open(history_file,_'r',_encoding = 'utf-8') as f:
                        alerts_history = json.load(f)
                except Exception:
                    alerts_history = []
            
            # 새 알림 추가
            alerts_history.append(alert_record)
            
            # 최근 1000개만 유지
            if len(alerts_history) > 1000:
                alerts_history = alerts_history[-1000:]
            
            # 파일에 저장
with_open(history_file,_'w',_encoding = 'utf-8') as f:
json.dump(alerts_history,_f,_ensure_ascii = False, indent=2)
            
        except Exception as e:
            self.logger.error(f"알림 히스토리 저장 실패: {e}")
    
    def _check_optimization_opportunities(self):
        """최적화 기회 체크"""
        try:
            recommendations = []
            
            if len(self.metrics_history) < 10:
                return recommendations
            
            # 최근 10분간 평균 계산
            recent_snapshots = list(self.metrics_history)[-10:]
            avg_cpu = statistics.mean([s.cpu_percent for s in recent_snapshots])
            avg_memory = statistics.mean([s.memory_percent for s in recent_snapshots])
            
            # CPU 최적화 권장사항
            if avg_cpu > 60:
                recommendations.append("CPU 사용률이 높습니다. 불필요한 프로세스를 종료하거나 모니터링 간격을 늘려보세요.")
            
            # 메모리 최적화 권장사항
            if avg_memory > 70:
                recommendations.append("메모리 사용률이 높습니다. 로그 파일 정리나 캐시 크기 조정을 고려해보세요.")
            
            # 프로세스 수 최적화
            avg_process_count = statistics.mean([s.process_count for s in recent_snapshots])
            if avg_process_count > 15:
                recommendations.append("실행 중인 프로세스가 많습니다. 불필요한 모니터링 프로세스를 비활성화해보세요.")
            
            # 권장사항이 있으면 로그에 기록
            if recommendations:
                self.logger.info("🔧 성능 최적화 권장사항:")
                for i, rec in enumerate(recommendations, 1):
                    self.logger.info(f"  {i}. {rec}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"최적화 기회 체크 실패: {e}")
            return []
    
    def measure_operation_time(self, operation_name: str):
        """
        작업 시간 측정을 위한 컨텍스트 매니저
        
        Usage:
            with performance_monitor.measure_operation_time("process_start"):
                # 시간을 측정할 작업
                pass
        """
        return OperationTimer(self, operation_name)
    
    def record_response_time(self, operation_name: str, response_time: float):
        """
        응답 시간 기록
        
        Args:
            operation_name (str): 작업 이름
            response_time (float): 응답 시간 (초)
        """
        try:
            self.response_times[operation_name].append(response_time)
            
            # 응답 시간 임계값 체크
            if response_time > self.thresholds['response_time_critical']:
                self._trigger_performance_alert(
                    MetricType.RESPONSE_TIME, 
                    response_time, 
                    PerformanceLevel.CRITICAL
                )
            elif response_time > self.thresholds['response_time_warning']:
                self._trigger_performance_alert(
                    MetricType.RESPONSE_TIME, 
                    response_time, 
                    PerformanceLevel.WARNING
                )
            
self.logger.debug(f"응답_시간_기록:_{operation_name} =  {response_time:.2f}초")
            
        except Exception as e:
            self.logger.error(f"응답 시간 기록 실패: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보 조회"""
        try:
            if not self.metrics_history:
                return {'error': '성능 데이터가 없습니다'}
            
            # 최근 데이터 기반 요약
            recent_snapshots = list(self.metrics_history)[-10:] if len(self.metrics_history) >= 10 else list(self.metrics_history)
            latest_snapshot = self.metrics_history[-1]
            
            # 평균 계산
            avg_cpu = statistics.mean([s.cpu_percent for s in recent_snapshots])
            avg_memory = statistics.mean([s.memory_percent for s in recent_snapshots])
            avg_process_count = statistics.mean([s.process_count for s in recent_snapshots])
            
            # 응답 시간 통계
            response_time_stats = {}
            for operation, times in self.response_times.items():
                if times:
                    response_time_stats[operation] = {
                        'avg': statistics.mean(times),
                        'min': min(times),
                        'max': max(times),
                        'count': len(times)
                    }
            
            # 가동 시간 계산
            uptime = datetime.now() - self.start_time
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime).split('.')[0],  # 소수점 제거
                'monitoring_status': 'active' if self.is_monitoring else 'inactive',
                'total_measurements': self.total_measurements,
                'alert_count': self.alert_count,
                
                # 현재 상태
                'current': {
                    'cpu_percent': latest_snapshot.cpu_percent,
                    'memory_percent': latest_snapshot.memory_percent,
                    'memory_available_mb': latest_snapshot.memory_available_mb,
                    'disk_usage_percent': latest_snapshot.disk_usage_percent,
                    'process_count': latest_snapshot.process_count,
                    'active_processes': latest_snapshot.active_processes
                },
                
                # 평균 (최근 10분)
                'averages': {
                    'cpu_percent': round(avg_cpu, 2),
                    'memory_percent': round(avg_memory, 2),
                    'process_count': round(avg_process_count, 1)
                },
                
                # 응답 시간 통계
                'response_times': response_time_stats,
                
                # 성능 수준 평가
                'performance_level': self._evaluate_performance_level(avg_cpu, avg_memory),
                
                # 시스템 로드 (가능한 경우)
                'system_load': latest_snapshot.system_load_avg,
                
                # 네트워크 I/O (가능한 경우)
                'network_io': latest_snapshot.network_io
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"성능 요약 조회 실패: {e}")
            return {'error': f'성능 요약 조회 실패: {e}'}
    
    def _evaluate_performance_level(self, avg_cpu: float, avg_memory: float) -> str:
        """성능 수준 평가"""
        if avg_cpu > 80 or avg_memory > 85:
            return PerformanceLevel.CRITICAL.value
        elif avg_cpu > 60 or avg_memory > 70:
            return PerformanceLevel.WARNING.value
        elif avg_cpu > 40 or avg_memory > 50:
            return PerformanceLevel.GOOD.value
        else:
            return PerformanceLevel.EXCELLENT.value
    
    def compare_with_baseline(self, baseline_data: Dict[str, Any]) -> PerformanceComparison:
        """
        기준선과 성능 비교
        
        Args:
            baseline_data (Dict): v1 시스템의 기준선 데이터
            
        Returns:
            PerformanceComparison: 비교 결과
        """
        try:
            current_summary = self.get_performance_summary()
            
            if 'error' in current_summary:
                raise ValueError(current_summary['error'])
            
            # v2 메트릭 추출
            v2_metrics = {
                'cpu_percent': current_summary['averages']['cpu_percent'],
                'memory_percent': current_summary['averages']['memory_percent'],
                'process_count': current_summary['averages']['process_count'],
                'response_time_avg': 0.0  # 기본값
            }
            
            # 평균 응답 시간 계산
            if current_summary['response_times']:
                response_times = [stats['avg'] for stats in current_summary['response_times'].values()]
                v2_metrics['response_time_avg'] = statistics.mean(response_times)
            
            # v1 메트릭 (기준선)
            v1_metrics = baseline_data
            
            # 개선율 계산
            improvement_percentage = {}
            recommendations = []
            
            for metric, v2_value in v2_metrics.items():
                if metric in v1_metrics:
                    v1_value = v1_metrics[metric]
                    if v1_value > 0:
                        # 낮을수록 좋은 메트릭들 (CPU, 메모리, 응답시간)
                        if metric in ['cpu_percent', 'memory_percent', 'response_time_avg']:
                            improvement = ((v1_value - v2_value) / v1_value) * 100
                        else:  # 높을수록 좋은 메트릭들
                            improvement = ((v2_value - v1_value) / v1_value) * 100
                        
                        improvement_percentage[metric] = round(improvement, 2)
                        
                        # 권장사항 생성
                        if improvement < -10:  # 10% 이상 악화
                            recommendations.append(f"{metric} 성능이 {abs(improvement):.1f}% 악화되었습니다. 최적화가 필요합니다.")
                        elif improvement > 10:  # 10% 이상 개선
                            recommendations.append(f"{metric} 성능이 {improvement:.1f}% 개선되었습니다.")
            
            # 전반적인 권장사항
            if not recommendations:
                recommendations.append("전반적인 성능이 안정적입니다.")
            
            return PerformanceComparison(
                comparison_time=datetime.now(),
                v1_metrics=v1_metrics,
                v2_metrics=v2_metrics,
                improvement_percentage=improvement_percentage,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"성능 비교 실패: {e}")
            return PerformanceComparison(
                comparison_time=datetime.now(),
                v1_metrics={},
                v2_metrics={},
                improvement_percentage={},
                recommendations=[f"성능 비교 실패: {e}"]
            )
    
    def set_v1_baseline(self, baseline_data: Dict[str, Any]):
        """v1 시스템 기준선 설정"""
        self.v1_baseline = baseline_data
        self.logger.info("v1 시스템 기준선 설정 완료")
    
    def get_v1_v2_comparison(self) -> Optional[PerformanceComparison]:
        """v1과 v2 시스템 성능 비교"""
        if not self.v1_baseline:
            self.logger.warning("v1 기준선이 설정되지 않았습니다")
            return None
        
        return self.compare_with_baseline(self.v1_baseline)
    
    def export_performance_data(self, filepath: str = None) -> str:
        """성능 데이터 내보내기"""
        try:
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(self.script_dir, f'performance_alerts.json')
            
            # 내보낼 데이터 준비
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'monitoring_period': {
                    'start': self.start_time.isoformat(),
                    'end': datetime.now().isoformat(),
                    'duration_seconds': (datetime.now() - self.start_time).total_seconds()
                },
                'summary': self.get_performance_summary(),
                'metrics_history': [asdict(snapshot) for snapshot in list(self.metrics_history)],
                'alert_count': self.alert_count,
                'total_measurements': self.total_measurements,
                'thresholds': self.thresholds
            }
            
            # JSON 직렬화를 위한 datetime 변환
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            # 파일에 저장
with_open(filepath,_'w',_encoding = 'utf-8') as f:
json.dump(export_data,_f,_ensure_ascii = False, indent=2, default=json_serializer)
            
            self.logger.info(f"성능 데이터 내보내기 완료: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"성능 데이터 내보내기 실패: {e}")
            return ""
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """알림 통계 조회 (NotificationManager 호환성)"""
        return {
            'total_notifications': self.alert_count,
            'failed_notifications': 0,  # 성능 모니터는 실패 추적 안함
            'last_notification': datetime.now() if self.alert_count > 0 else None
        }


class OperationTimer:
    """작업 시간 측정을 위한 컨텍스트 매니저"""
    
    def __init__(self, performance_monitor: PerformanceMonitor, operation_name: str):
        self.performance_monitor = performance_monitor
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            response_time = time.time() - self.start_time
            self.performance_monitor.record_response_time(self.operation_name, response_time)


class PerformanceComparator:
    """
    v1과 v2 시스템 간 성능 비교 도구
    
    두 시스템의 성능 메트릭을 비교하고 분석 결과를 제공합니다.
    """
    
    def __init__(self, script_dir: str):
        self.script_dir = script_dir
        self.logger = logging.getLogger(__name__)
        
        # 비교 결과 저장소
        self.comparison_history = []
        
        self.logger.info("📊 PerformanceComparator 초기화 완료")
    
    def collect_v1_baseline(self) -> Dict[str, Any]:
        """
        v1 시스템의 기준선 성능 데이터 수집
        
        Returns:
            Dict: v1 시스템 성능 기준선
        """
        try:
            self.logger.info("📊 v1 시스템 기준선 수집 시작...")
            
            # v1 시스템 프로세스 식별 및 성능 측정
            v1_processes = []
            total_cpu = 0.0
            total_memory = 0.0
            
            # 기존 워치햄스터 프로세스 찾기
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    if not proc.info['cmdline']:
                        continue
                    
                    cmdline_str = ' '.join(proc.info['cmdline']).lower()
                    
                    # v1 시스템 프로세스 식별 (v2 제외)
                    if ('monitor_watchhamster' in cmdline_str or 
                        'posco_main_notifier' in cmdline_str or
                        'realtime_news_monitor' in cmdline_str) and 'v2' not in cmdline_str:
                        
                        cpu_percent = proc.info['cpu_percent'] or 0.0
                        memory_percent = proc.info['memory_percent'] or 0.0
                        
                        v1_processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent
                        })
                        
total_cpu_+ =  cpu_percent
total_memory_+ =  memory_percent
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 시스템 전체 성능 측정
            system_cpu = psutil.cpu_percent(interval=1)
            system_memory = psutil.virtual_memory().percent
            
            baseline = {
                'timestamp': datetime.now().isoformat(),
                'system_type': 'v1',
                'cpu_percent': total_cpu,
                'memory_percent': total_memory,
                'system_cpu_percent': system_cpu,
                'system_memory_percent': system_memory,
                'process_count': len(v1_processes),
                'processes': v1_processes,
                'response_time_avg': 3.0  # v1 시스템 예상 응답시간
            }
            
            self.logger.info(f"v1 기준선 수집 완료: CPU {total_cpu:.1f}%, 메모리 {total_memory:.1f}%, 프로세스 {len(v1_processes)}개")
            
            return baseline
            
        except Exception as e:
            self.logger.error(f"v1 기준선 수집 실패: {e}")
            return {}
    
    def generate_comparison_report(self, v1_data: Dict[str, Any], v2_data: Dict[str, Any]) -> str:
        """
        v1/v2 성능 비교 보고서 생성
        
        Args:
            v1_data (Dict): v1 시스템 데이터
            v2_data (Dict): v2 시스템 데이터
            
        Returns:
            str: 비교 보고서 텍스트
        """
        try:
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("🔍 POSCO WatchHamster v3.0.0 성능 비교 보고서")
            report_lines.append("=" * 60)
            report_lines.append(f"📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # 시스템 정보
            report_lines.append("📊 시스템 정보")
            report_lines.append("-" * 30)
            report_lines.append(f"v1 시스템 - 프로세스 수: {v1_data.get('process_count', 0)}개")
            report_lines.append(f"v2 시스템 - 프로세스 수: {v2_data.get('process_count', 0)}개")
            report_lines.append("")
            
            # 성능 메트릭 비교
            report_lines.append("⚡ 성능 메트릭 비교")
            report_lines.append("-" * 30)
            
            metrics = [
                ('CPU 사용률', 'cpu_percent', '%'),
                ('메모리 사용률', 'memory_percent', '%'),
                ('평균 응답시간', 'response_time_avg', '초')
            ]
            
            for metric_name, metric_key, unit in metrics:
                v1_value = v1_data.get(metric_key, 0)
                v2_value = v2_data.get(metric_key, 0)
                
                if v1_value > 0:
                    improvement = ((v1_value - v2_value) / v1_value) * 100
                    improvement_text = f"({improvement:+.1f}%)"
                    
                    if improvement > 5:
                        status = "✅ 개선"
                    elif improvement < -5:
                        status = "⚠️ 악화"
                    else:
                        status = "➖ 유사"
                else:
                    improvement_text = ""
                    status = "➖ 비교불가"
                
                report_lines.append(f"{metric_name:12}: v1 {v1_value:.1f}{unit} → v2 {v2_value:.1f}{unit} {improvement_text} {status}")
            
            report_lines.append("")
            
            # 권장사항
            report_lines.append("💡 권장사항")
            report_lines.append("-" * 30)
            
            recommendations = []
            
            # CPU 사용률 분석
            cpu_improvement = ((v1_data.get('cpu_percent', 0) - v2_data.get('cpu_percent', 0)) / max(v1_data.get('cpu_percent', 1), 1)) * 100
            if cpu_improvement > 10:
                recommendations.append("✅ v2 시스템의 CPU 효율성이 크게 개선되었습니다.")
            elif cpu_improvement < -10:
                recommendations.append("⚠️ v2 시스템의 CPU 사용률이 증가했습니다. 최적화를 검토해보세요.")
            
            # 메모리 사용률 분석
            memory_improvement = ((v1_data.get('memory_percent', 0) - v2_data.get('memory_percent', 0)) / max(v1_data.get('memory_percent', 1), 1)) * 100
            if memory_improvement > 10:
                recommendations.append("✅ v2 시스템의 메모리 효율성이 개선되었습니다.")
            elif memory_improvement < -10:
                recommendations.append("⚠️ v2 시스템의 메모리 사용량이 증가했습니다. 메모리 누수를 확인해보세요.")
            
            # 응답시간 분석
            response_improvement = ((v1_data.get('response_time_avg', 0) - v2_data.get('response_time_avg', 0)) / max(v1_data.get('response_time_avg', 1), 1)) * 100
            if response_improvement > 20:
                recommendations.append("✅ v2 시스템의 응답속도가 크게 향상되었습니다.")
            elif response_improvement < -20:
                recommendations.append("⚠️ v2 시스템의 응답속도가 저하되었습니다. 성능 튜닝이 필요합니다.")
            
            if not recommendations:
                recommendations.append("📊 전반적인 성능이 안정적으로 유지되고 있습니다.")
            
            for rec in recommendations:
                report_lines.append(f"• {rec}")
            
            report_lines.append("")
            report_lines.append("=" * 60)
            
            return "/n".join(report_lines)
            
        except Exception as e:
            self.logger.error(f"비교 보고서 생성 실패: {e}")
            return f"비교 보고서 생성 실패: {e}"
    
    def save_comparison_report(self, report_text: str, filename: str = None) -> str:
        """비교 보고서 파일 저장"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_performance_monitoring.py"
            
            filepath = os.path.join(self.script_dir, filename)
            
with_open(filepath,_'w',_encoding = 'utf-8') as f:
                f.write(report_text)
            
            self.logger.info(f"비교 보고서 저장 완료: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"비교 보고서 저장 실패: {e}")
            return ""