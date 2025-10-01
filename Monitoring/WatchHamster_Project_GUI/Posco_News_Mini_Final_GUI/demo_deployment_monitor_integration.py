#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 모니터링 시스템 통합 데모
DeploymentMonitor를 기존 배포 시스템과 통합하는 방법을 보여주는 데모

주요 기능:
- IntegratedDeploymentSystem과 DeploymentMonitor 연동
- GUI 콜백을 통한 실시간 진행 상황 표시
- 배포 각 단계별 상세 모니터링
- 성능 메트릭 수집 및 분석
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, Any

# 현재 스크립트의 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from deployment_monitor import DeploymentMonitor, DeploymentPhase
    # 기존 시스템들 (실제 환경에서는 이미 구현되어 있음)
    # from integrated_deployment_system import IntegratedDeploymentSystem
    # from git_deployment_manager import GitDeploymentManager
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class DeploymentMonitorIntegration:
    """배포 모니터링 시스템 통합 클래스"""
    
    def __init__(self):
        """통합 시스템 초기화"""
        self.monitor = DeploymentMonitor()
        
        # GUI 상태 (실제 GUI에서는 tkinter 위젯들)
        self.gui_status = {
            "current_phase": "대기 중",
            "progress": 0.0,
            "message": "배포 대기 중...",
            "session_id": None,
            "start_time": None,
            "errors": [],
            "warnings": []
        }
        
        # 콜백 등록
        self.setup_callbacks()
        
        print("🔧 배포 모니터링 통합 시스템 초기화 완료")
    
    def setup_callbacks(self):
        """GUI 콜백 설정"""
        
        def progress_callback(message: str, progress: float, details: Dict):
            """진행 상황 업데이트 콜백 (GUI용)"""
            self.gui_status["message"] = message
            self.gui_status["progress"] = progress
            
            # 실제 GUI에서는 여기서 위젯 업데이트
            print(f"📊 진행률: {progress:.1f}% - {message}")
            
            if details:
                print(f"   세부사항: {details}")
        
        def phase_callback(phase: DeploymentPhase, metrics):
            """단계 변경 콜백 (GUI용)"""
            phase_name = phase.value.replace('_', ' ').title()
            self.gui_status["current_phase"] = phase_name
            
            # 실제 GUI에서는 여기서 단계 표시 위젯 업데이트
            print(f"🔄 단계 변경: {phase_name}")
            
            if metrics.details:
                print(f"   메트릭: 시작시간 {datetime.fromtimestamp(metrics.start_time).strftime('%H:%M:%S')}")
        
        def completion_callback(session):
            """완료 콜백 (GUI용)"""
            duration = session.total_duration or 0
            success_msg = "성공" if session.overall_success else "실패"
            
            self.gui_status["message"] = f"배포 {success_msg} (소요시간: {duration:.1f}초)"
            self.gui_status["progress"] = 100.0
            
            # 실제 GUI에서는 여기서 완료 다이얼로그 표시
            print(f"✅ 배포 완료: {session.session_id}")
            print(f"   소요시간: {duration:.1f}초")
            print(f"   완료 단계: {session.completed_phases}/{session.total_phases}")
            print(f"   오류 수: {session.error_count}")
            print(f"   경고 수: {session.warning_count}")
        
        def error_callback(error_message: str, error_details: Dict):
            """오류 콜백 (GUI용)"""
            self.gui_status["errors"].append({
                "message": error_message,
                "details": error_details,
                "timestamp": datetime.now().isoformat()
            })
            
            # 실제 GUI에서는 여기서 오류 다이얼로그 표시
            print(f"❌ 오류 발생: {error_message}")
            if error_details:
                print(f"   세부사항: {error_details}")
        
        # 콜백 등록
        self.monitor.register_progress_callback(progress_callback)
        self.monitor.register_phase_callback(phase_callback)
        self.monitor.register_completion_callback(completion_callback)
        self.monitor.register_error_callback(error_callback)
    
    def simulate_integrated_deployment(self, test_data: Dict[str, Any]):
        """통합 배포 시뮬레이션 (실제 IntegratedDeploymentSystem 연동)"""
        session_id = f"integrated_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🚀 통합 배포 시작: {session_id}")
        print("=" * 60)
        
        try:
            # 1. 배포 모니터링 시작
            if not self.monitor.start_deployment_monitoring(session_id):
                print("❌ 모니터링 시작 실패")
                return False
            
            self.gui_status["session_id"] = session_id
            self.gui_status["start_time"] = datetime.now()
            
            # 2. 배포 단계들 시뮬레이션
            deployment_phases = [
                (DeploymentPhase.PRE_CHECK, "배포 전 상태 확인", 2.0),
                (DeploymentPhase.BACKUP, "백업 생성", 3.0),
                (DeploymentPhase.HTML_GENERATION, "HTML 리포트 생성", 5.0),
                (DeploymentPhase.BRANCH_SWITCH, "브랜치 전환", 3.0),
                (DeploymentPhase.MERGE_CHANGES, "변경사항 병합", 4.0),
                (DeploymentPhase.COMMIT_CHANGES, "변경사항 커밋", 2.0),
                (DeploymentPhase.PUSH_REMOTE, "원격 저장소 푸시", 8.0),
                (DeploymentPhase.VERIFY_PAGES, "GitHub Pages 확인", 10.0),
                (DeploymentPhase.SEND_NOTIFICATION, "알림 전송", 2.0),
                (DeploymentPhase.CLEANUP, "정리 작업", 1.0)
            ]
            
            for phase, description, duration in deployment_phases:
                # 단계 시작
                self.monitor.update_deployment_phase(
                    phase, 
                    success=True, 
                    details={
                        "description": description,
                        "estimated_duration": duration,
                        "test_data": test_data.get("phase_data", {})
                    }
                )
                
                # 실제 작업 시뮬레이션
                print(f"⏳ {description} 진행 중...")
                
                # 진행률 시뮬레이션
                steps = 10
                for step in range(steps):
                    time.sleep(duration / steps)
                    step_progress = (step + 1) / steps * 100
                    
                    # 중간 진행 상황 업데이트 (실제로는 각 시스템에서 호출)
                    current_status = self.monitor.get_current_deployment_status()
                    if current_status:
                        overall_progress = current_status["progress_percentage"]
                        self.monitor._notify_progress(
                            f"{description} ({step_progress:.0f}%)",
                            overall_progress,
                            {"step": step + 1, "total_steps": steps}
                        )
                
                print(f"✅ {description} 완료")
            
            # 3. 배포 완료
            self.monitor.stop_deployment_monitoring(success=True)
            
            print("=" * 60)
            print("🎉 통합 배포 성공 완료!")
            
            return True
            
        except Exception as e:
            error_msg = f"통합 배포 중 오류: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 오류 발생 시 모니터링 중지
            self.monitor.stop_deployment_monitoring(success=False, error_message=error_msg)
            
            return False
    
    def show_deployment_dashboard(self):
        """배포 대시보드 표시 (GUI 시뮬레이션)"""
        print("\n📊 배포 대시보드")
        print("=" * 40)
        
        # 현재 상태
        current_status = self.monitor.get_current_deployment_status()
        if current_status:
            print("🔄 현재 배포 진행 중:")
            print(f"   세션 ID: {current_status['session_id']}")
            print(f"   현재 단계: {current_status['current_phase']}")
            print(f"   진행률: {current_status['progress_percentage']:.1f}%")
            print(f"   소요시간: {current_status['total_duration']:.1f}초")
            print(f"   완료 단계: {current_status['completed_phases']}/{current_status['total_phases']}")
        else:
            print("💤 현재 진행 중인 배포 없음")
        
        # 최근 배포 히스토리
        print("\n📈 최근 배포 히스토리:")
        history = self.monitor.get_deployment_history(5)
        
        if history:
            for i, session in enumerate(history, 1):
                status = "✅ 성공" if session.get("overall_success") else "❌ 실패"
                duration = session.get("total_duration", 0)
                timestamp = datetime.fromtimestamp(session.get("start_time", 0)).strftime("%m-%d %H:%M")
                
                print(f"   {i}. {session['session_id']} - {status} ({duration:.1f}초) [{timestamp}]")
        else:
            print("   히스토리 없음")
        
        # 성능 통계
        print("\n📊 성능 통계:")
        stats = self.monitor.get_performance_statistics()
        
        summary = stats.get("summary", {})
        if summary:
            print(f"   최근 세션 수: {summary.get('recent_sessions_count', 0)}")
            print(f"   평균 소요시간: {summary.get('average_duration', 0):.1f}초")
            print(f"   성공률: {summary.get('success_rate', 0):.1f}%")
        else:
            print("   통계 데이터 없음")
        
        # 단계별 평균 시간
        phase_averages = stats.get("phase_averages", {})
        if phase_averages:
            print("\n⏱️ 단계별 평균 소요시간:")
            for phase, avg_time in phase_averages.items():
                phase_name = phase.replace('_', ' ').title()
                print(f"   {phase_name}: {avg_time:.1f}초")
    
    def cleanup_old_data(self):
        """오래된 데이터 정리"""
        print("\n🧹 오래된 로그 데이터 정리 중...")
        self.monitor.cleanup_old_logs(days_to_keep=7)  # 7일간 데이터 유지
        print("✅ 데이터 정리 완료")


def main():
    """메인 데모 함수"""
    print("🎯 배포 모니터링 시스템 통합 데모")
    print("=" * 60)
    
    # 통합 시스템 초기화
    integration = DeploymentMonitorIntegration()
    
    # 테스트 데이터
    test_data = {
        "html_content": "<html><body>Test Report</body></html>",
        "branch_target": "publish",
        "webhook_url": "https://example.com/webhook",
        "phase_data": {
            "test_mode": True,
            "demo_version": "1.0.0"
        }
    }
    
    try:
        # 1. 통합 배포 실행
        print("\n1️⃣ 통합 배포 실행")
        success = integration.simulate_integrated_deployment(test_data)
        
        if success:
            print("\n✅ 배포 성공!")
        else:
            print("\n❌ 배포 실패!")
        
        # 2. 대시보드 표시
        print("\n2️⃣ 배포 대시보드")
        integration.show_deployment_dashboard()
        
        # 3. 추가 배포 시뮬레이션 (빠른 배포)
        print("\n3️⃣ 빠른 배포 테스트")
        quick_data = {**test_data, "quick_mode": True}
        
        # 빠른 배포 (일부 단계만)
        session_id = f"quick_deploy_{datetime.now().strftime('%H%M%S')}"
        integration.monitor.start_deployment_monitoring(session_id)
        
        quick_phases = [
            DeploymentPhase.PRE_CHECK,
            DeploymentPhase.HTML_GENERATION,
            DeploymentPhase.PUSH_REMOTE
        ]
        
        for phase in quick_phases:
            integration.monitor.update_deployment_phase(phase, success=True)
            time.sleep(0.5)
        
        integration.monitor.stop_deployment_monitoring(success=True)
        
        # 4. 최종 대시보드
        print("\n4️⃣ 최종 대시보드")
        integration.show_deployment_dashboard()
        
        # 5. 데이터 정리
        integration.cleanup_old_data()
        
        print("\n🎉 데모 완료!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
        integration.monitor.stop_deployment_monitoring(success=False, error_message="사용자 중단")
    
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {str(e)}")
        integration.monitor.stop_deployment_monitoring(success=False, error_message=str(e))


if __name__ == "__main__":
    main()