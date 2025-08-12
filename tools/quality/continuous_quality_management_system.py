#!/usr/bin/env python3
"""
POSCO 시스템 지속적 품질 관리 시스템
Continuous Quality Management System for POSCO System
"""

import os
import sys
import json
import time
import psutil
import subprocess
import threading
import schedule
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import yaml
import sqlite3
from collections import defaultdict, deque

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quality_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QualityMetric:
    """품질 메트릭 데이터 클래스"""
    name: str
    value: float
    threshold: float
    status: str  # 'pass', 'warning', 'fail'
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

@dataclass
class PipelineStage:
    """파이프라인 단계 데이터 클래스"""
    name: str
    status: str  # 'pending', 'running', 'success', 'failed'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    logs: List[str] = None
    artifacts: List[str] = None

    def __post_init__(self):
        if self.logs is None:
            self.logs = []
        if self.artifacts is None:
            self.artifacts = []

class ContinuousQualityManager:
    """지속적 품질 관리 통합 시스템"""
    
    def __init__(self):
        self.dashboard = QualityMonitoringDashboard()
        self.health_system = HealthCheckSystem(self.dashboard)
        self._setup_default_health_checks()
        
    def _setup_default_health_checks(self):
        """기본 건강성 체크 설정"""
        
        def system_resource_check():
            """시스템 리소스 체크"""
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('.').percent
            
            healthy = (cpu_percent < 80 and 
                      memory_percent < 85 and 
                      disk_percent < 90)
            
            return {
                'healthy': healthy,
                'message': f"CPU: {cpu_percent:.1f}%, 메모리: {memory_percent:.1f}%, 디스크: {disk_percent:.1f}%",
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent
                }
            }
        
        self.health_system.register_health_check("system_resources", system_resource_check, 15)
    
    def start_continuous_monitoring(self):
        """지속적 모니터링 시작"""
        logger.info("🚀 지속적 품질 관리 시스템 시작")
        self.health_system.start_scheduler()
        self._collect_initial_metrics()
        logger.info("✅ 지속적 품질 관리 시스템 시작 완료")
    
    def stop_continuous_monitoring(self):
        """지속적 모니터링 중지"""
        logger.info("🛑 지속적 품질 관리 시스템 중지")
        self.health_system.stop_scheduler()
    
    def _collect_initial_metrics(self):
        """초기 메트릭 수집"""
        try:
            cpu_metric = QualityMetric(
                name="system_cpu_usage",
                value=psutil.cpu_percent(interval=1),
                threshold=80.0,
                status='pass',
                timestamp=datetime.now()
            )
            self.dashboard.record_metric(cpu_metric)
            
            memory_metric = QualityMetric(
                name="system_memory_usage",
                value=psutil.virtual_memory().percent,
                threshold=85.0,
                status='pass',
                timestamp=datetime.now()
            )
            self.dashboard.record_metric(memory_metric)
            
        except Exception as e:
            logger.error(f"초기 메트릭 수집 오류: {e}")
    
    def generate_quality_report(self) -> str:
        """품질 보고서 생성"""
        report_time = datetime.now()
        
        current_metrics = self.dashboard.get_current_metrics()
        health_status = self.health_system.get_health_status()
        
        report = f"""
# POSCO 시스템 품질 보고서
생성 시간: {report_time.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 현재 품질 메트릭
"""
        
        for metric_name, metric in current_metrics.items():
            status_emoji = "✅" if metric.status == 'pass' else "⚠️" if metric.status == 'warning' else "❌"
            report += f"- {status_emoji} **{metric.name}**: {metric.value:.2f} (임계값: {metric.threshold:.2f})\n"
        
        report += f"""
## 🏥 시스템 건강성 상태
전체 상태: {'✅ 정상' if health_status['overall_healthy'] else '❌ 문제 있음'}

## 📈 요약
- 총 메트릭 수: {len(current_metrics)}
- 건강성 체크 수: {len(health_status['checks'])}
- 전체 시스템 상태: {'정상' if health_status['overall_healthy'] else '주의 필요'}

---
*이 보고서는 자동으로 생성되었습니다.*
"""
        
        return report

class QualityMonitoringDashboard:
    """품질 모니터링 대시보드"""
    
    def __init__(self, db_path: str = "quality_metrics.db"):
        self.db_path = db_path
        self.metrics_history = deque(maxlen=1000)
        self._init_database()
        
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric: QualityMetric):
        """메트릭 기록"""
        self.metrics_history.append(metric)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quality_metrics (name, value, threshold, status, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metric.name,
            metric.value,
            metric.threshold,
            metric.status,
            metric.timestamp.isoformat(),
            json.dumps(metric.details) if metric.details else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_current_metrics(self) -> Dict[str, QualityMetric]:
        """현재 메트릭 조회"""
        current_metrics = {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, value, threshold, status, timestamp, details
            FROM quality_metrics
            WHERE timestamp = (
                SELECT MAX(timestamp) 
                FROM quality_metrics AS qm2 
                WHERE qm2.name = quality_metrics.name
            )
        ''')
        
        for row in cursor.fetchall():
            name, value, threshold, status, timestamp, details = row
            current_metrics[name] = QualityMetric(
                name=name,
                value=value,
                threshold=threshold,
                status=status,
                timestamp=datetime.fromisoformat(timestamp),
                details=json.loads(details) if details else None
            )
        
        conn.close()
        return current_metrics

class HealthCheckSystem:
    """정기적 건강성 체크 시스템"""
    
    def __init__(self, dashboard: QualityMonitoringDashboard):
        self.dashboard = dashboard
        self.health_checks = []
        self.scheduler_running = False
        self.scheduler_thread = None
        
    def register_health_check(self, name: str, check_function, interval_minutes: int = 30):
        """건강성 체크 등록"""
        self.health_checks.append({
            'name': name,
            'function': check_function,
            'interval': interval_minutes,
            'last_run': None,
            'last_result': None
        })
        
        schedule.every(interval_minutes).minutes.do(
            self._run_health_check, name, check_function
        )
    
    def _run_health_check(self, name: str, check_function):
        """개별 건강성 체크 실행"""
        try:
            logger.info(f"🏥 건강성 체크 실행: {name}")
            
            start_time = time.time()
            result = check_function()
            duration = time.time() - start_time
            
            status = 'pass' if result.get('healthy', False) else 'fail'
            
            metric = QualityMetric(
                name=f"health_check_{name}",
                value=1.0 if result.get('healthy', False) else 0.0,
                threshold=1.0,
                status=status,
                timestamp=datetime.now(),
                details={
                    'duration': duration,
                    'details': result.get('details', {}),
                    'recommendations': result.get('recommendations', [])
                }
            )
            
            self.dashboard.record_metric(metric)
            
            for check in self.health_checks:
                if check['name'] == name:
                    check['last_run'] = datetime.now()
                    check['last_result'] = result
                    break
            
        except Exception as e:
            logger.error(f"❌ 건강성 체크 오류 ({name}): {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        
        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("📅 건강성 체크 스케줄러 시작")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("📅 건강성 체크 스케줄러 중지")
    
    def get_health_status(self) -> Dict[str, Any]:
        """전체 건강성 상태 조회"""
        status = {
            'overall_healthy': True,
            'checks': [],
            'last_update': datetime.now().isoformat()
        }
        
        for check in self.health_checks:
            check_status = {
                'name': check['name'],
                'last_run': check['last_run'].isoformat() if check['last_run'] else None,
                'healthy': check['last_result'].get('healthy', False) if check['last_result'] else None,
                'message': check['last_result'].get('message', '') if check['last_result'] else '',
                'interval_minutes': check['interval']
            }
            
            status['checks'].append(check_status)
            
            if not check_status['healthy']:
                status['overall_healthy'] = False
        
        return status

if __name__ == "__main__":
    manager = ContinuousQualityManager()
    print("✅ 지속적 품질 관리 시스템 초기화 완료")

    def generate_dashboard_html(self) -> str:
        """HTML 대시보드 생성"""
        current_metrics = self.get_current_metrics()
        
        html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>POSCO 시스템 품질 대시보드</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; }
        .metric-card.pass { border-left: 5px solid #27ae60; }
        .metric-card.warning { border-left: 5px solid #f39c12; }
        .metric-card.fail { border-left: 5px solid #e74c3c; }
        .metric-value { font-size: 2em; font-weight: bold; }
        .metric-name { color: #666; margin-bottom: 10px; }
        .timestamp { color: #999; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 POSCO 시스템 품질 대시보드</h1>
        <p>실시간 품질 메트릭 및 시스템 상태</p>
    </div>
    
    <div class="metrics-grid">
        {metrics_cards}
    </div>
    
    <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
        <p><strong>마지막 업데이트:</strong> {last_update}</p>
        <p><strong>총 메트릭 수:</strong> {total_metrics}</p>
    </div>
</body>
</html>
        '''
        
        metrics_cards = ""
        for metric in current_metrics.values():
            card_html = f'''
        <div class="metric-card {metric.status}">
            <div class="metric-name">{metric.name}</div>
            <div class="metric-value">{metric.value:.2f}</div>
            <div>임계값: {metric.threshold:.2f}</div>
            <div class="timestamp">{metric.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
            '''
            metrics_cards += card_html
        
        return html_template.format(
            metrics_cards=metrics_cards,
            last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_metrics=len(current_metrics)
        )
