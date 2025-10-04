#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 최적화 시스템 (포팅)
기존 WatchHamster 성능 최적화 로직을 FastAPI 서비스로 포팅

주요 기능:
- 시스템 성능 분석 및 최적화 권장사항 제공
- CPU, 메모리, 디스크 사용률 모니터링
- 성능 이슈 감지 및 자동 복구 제안
"""

import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import asyncio
import json
import os

logger = logging.getLogger(__name__)

class OptimizationCategory(Enum):
    """최적화 카테고리"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    CONFIGURATION = "configuration"

class OptimizationPriority(Enum):
    """최적화 우선순위"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OptimizationRecommendation:
    """최적화 권장사항"""
    id: str
    category: OptimizationCategory
    priority: OptimizationPriority
    title: str
    description: str
    impact_description: str
    implementation_steps: List[str]
    estimated_improvement: str
    risk_level: str
    created_at: datetime
    applied: bool = False
    applied_at: Optional[datetime] = None

@dataclass
class PerformanceIssue:
    """성능 이슈"""
    issue_type: str
    severity: str
    description: str
    affected_components: List[str]
    metrics: Dict[str, float]
    detected_at: datetime
    recommendations: List[str]

class PerformanceOptimizer:
    """성능 최적화 시스템"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """성능 최적화 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.logger = logger
        
        # 최적화 권장사항 저장소
        self.recommendations: List[OptimizationRecommendation] = []
        self.applied_optimizations: List[str] = []
        
        # 성능 임계값
        self.thresholds = {
            'cpu_high': 70.0,
            'cpu_critical': 85.0,
            'memory_high': 75.0,
            'memory_critical': 90.0,
            'disk_high': 80.0,
            'disk_critical': 95.0,
            'response_time_slow': 3.0,
            'response_time_critical': 10.0,
            'process_count_high': 15,
            'process_count_critical': 25
        }
        
        self.logger.info("🔧 PerformanceOptimizer 초기화 완료")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """현재 성능 메트릭 조회"""
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
            
            # 네트워크 IO
            network_io = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_mb': memory_available_mb,
                'disk_usage_percent': disk_usage_percent,
                'process_count': process_count,
                'network_io': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            }
        except Exception as e:
            self.logger.error(f"성능 메트릭 조회 실패: {e}")
            return {}
    
    async def analyze_system_performance(self, performance_data: Dict[str, Any]) -> List[PerformanceIssue]:
        """시스템 성능 분석 및 이슈 식별"""
        try:
            issues = []
            current_time = datetime.now()
            
            # CPU 사용률 분석
            cpu_percent = performance_data.get('cpu_percent', 0)
            if cpu_percent > self.thresholds['cpu_critical']:
                issues.append(PerformanceIssue(
                    issue_type="cpu_critical",
                    severity="critical",
                    description=f"CPU 사용률이 임계 수준입니다 ({cpu_percent:.1f}%)",
                    affected_components=["system", "all_processes"],
                    metrics={"cpu_percent": cpu_percent},
                    detected_at=current_time,
                    recommendations=["cpu_optimization", "process_reduction"]
                ))
            elif cpu_percent > self.thresholds['cpu_high']:
                issues.append(PerformanceIssue(
                    issue_type="cpu_high",
                    severity="warning",
                    description=f"CPU 사용률이 높습니다 ({cpu_percent:.1f}%)",
                    affected_components=["system"],
                    metrics={"cpu_percent": cpu_percent},
                    detected_at=current_time,
                    recommendations=["cpu_monitoring", "process_optimization"]
                ))
            
            # 메모리 사용률 분석
            memory_percent = performance_data.get('memory_percent', 0)
            if memory_percent > self.thresholds['memory_critical']:
                issues.append(PerformanceIssue(
                    issue_type="memory_critical",
                    severity="critical",
                    description=f"메모리 사용률이 임계 수준입니다 ({memory_percent:.1f}%)",
                    affected_components=["system", "all_processes"],
                    metrics={"memory_percent": memory_percent},
                    detected_at=current_time,
                    recommendations=["memory_cleanup", "cache_optimization"]
                ))
            elif memory_percent > self.thresholds['memory_high']:
                issues.append(PerformanceIssue(
                    issue_type="memory_high",
                    severity="warning",
                    description=f"메모리 사용률이 높습니다 ({memory_percent:.1f}%)",
                    affected_components=["system"],
                    metrics={"memory_percent": memory_percent},
                    detected_at=current_time,
                    recommendations=["memory_monitoring", "log_cleanup"]
                ))
            
            # 디스크 사용률 분석
            disk_percent = performance_data.get('disk_usage_percent', 0)
            if disk_percent > self.thresholds['disk_critical']:
                issues.append(PerformanceIssue(
                    issue_type="disk_critical",
                    severity="critical",
                    description=f"디스크 사용률이 임계 수준입니다 ({disk_percent:.1f}%)",
                    affected_components=["storage", "logging"],
                    metrics={"disk_percent": disk_percent},
                    detected_at=current_time,
                    recommendations=["disk_cleanup", "log_rotation"]
                ))
            elif disk_percent > self.thresholds['disk_high']:
                issues.append(PerformanceIssue(
                    issue_type="disk_high",
                    severity="warning",
                    description=f"디스크 사용률이 높습니다 ({disk_percent:.1f}%)",
                    affected_components=["storage"],
                    metrics={"disk_percent": disk_percent},
                    detected_at=current_time,
                    recommendations=["disk_monitoring", "file_cleanup"]
                ))
            
            return issues
            
        except Exception as e:
            self.logger.error(f"성능 분석 실패: {e}")
            return []
    
    async def generate_optimization_recommendations(self, issues: List[PerformanceIssue]) -> List[OptimizationRecommendation]:
        """최적화 권장사항 생성"""
        try:
            recommendations = []
            
            for issue in issues:
                if issue.issue_type.startswith("cpu"):
                    recommendations.append(OptimizationRecommendation(
                        id=f"cpu_opt_{datetime.now().timestamp()}",
                        category=OptimizationCategory.CPU,
                        priority=OptimizationPriority.HIGH if issue.severity == "critical" else OptimizationPriority.MEDIUM,
                        title="CPU 사용률 최적화",
                        description="높은 CPU 사용률을 개선하기 위한 최적화",
                        impact_description="시스템 응답성 향상 및 안정성 개선",
                        implementation_steps=[
                            "불필요한 프로세스 종료",
                            "백그라운드 작업 최적화",
                            "CPU 집약적 작업 스케줄링 조정"
                        ],
                        estimated_improvement="CPU 사용률 10-20% 감소 예상",
                        risk_level="낮음",
                        created_at=datetime.now()
                    ))
                
                elif issue.issue_type.startswith("memory"):
                    recommendations.append(OptimizationRecommendation(
                        id=f"memory_opt_{datetime.now().timestamp()}",
                        category=OptimizationCategory.MEMORY,
                        priority=OptimizationPriority.HIGH if issue.severity == "critical" else OptimizationPriority.MEDIUM,
                        title="메모리 사용률 최적화",
                        description="높은 메모리 사용률을 개선하기 위한 최적화",
                        impact_description="메모리 부족 현상 방지 및 성능 향상",
                        implementation_steps=[
                            "메모리 누수 프로세스 식별 및 정리",
                            "캐시 데이터 정리",
                            "불필요한 서비스 중지"
                        ],
                        estimated_improvement="메모리 사용률 15-25% 감소 예상",
                        risk_level="낮음",
                        created_at=datetime.now()
                    ))
                
                elif issue.issue_type.startswith("disk"):
                    recommendations.append(OptimizationRecommendation(
                        id=f"disk_opt_{datetime.now().timestamp()}",
                        category=OptimizationCategory.DISK,
                        priority=OptimizationPriority.HIGH if issue.severity == "critical" else OptimizationPriority.MEDIUM,
                        title="디스크 공간 최적화",
                        description="높은 디스크 사용률을 개선하기 위한 최적화",
                        impact_description="디스크 공간 확보 및 I/O 성능 향상",
                        implementation_steps=[
                            "임시 파일 정리",
                            "로그 파일 로테이션",
                            "불필요한 파일 삭제"
                        ],
                        estimated_improvement="디스크 공간 10-30% 확보 예상",
                        risk_level="낮음",
                        created_at=datetime.now()
                    ))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"최적화 권장사항 생성 실패: {e}")
            return []
    
    async def get_optimization_summary(self) -> Dict[str, Any]:
        """최적화 요약 정보 조회"""
        try:
            return {
                'total_recommendations': len(self.recommendations),
                'applied_optimizations': len(self.applied_optimizations),
                'pending_recommendations': len([r for r in self.recommendations if not r.applied]),
                'critical_issues': len([r for r in self.recommendations if r.priority == OptimizationPriority.CRITICAL]),
                'last_analysis': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"최적화 요약 조회 실패: {e}")
            return {}

# 싱글톤 인스턴스
_performance_optimizer_instance = None

def get_performance_optimizer(base_dir: Optional[str] = None) -> PerformanceOptimizer:
    """성능 최적화 시스템 싱글톤 인스턴스 반환"""
    global _performance_optimizer_instance
    if _performance_optimizer_instance is None:
        _performance_optimizer_instance = PerformanceOptimizer(base_dir)
    return _performance_optimizer_instance