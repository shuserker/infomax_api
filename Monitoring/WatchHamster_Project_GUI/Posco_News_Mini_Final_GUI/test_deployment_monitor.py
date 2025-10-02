#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 모니터링 시스템 테스트
DeploymentMonitor 클래스의 기능을 검증하는 테스트 스크립트

테스트 항목:
- 배포 모니터링 시작/중지
- 단계별 상태 업데이트
- 로그 파일 생성 및 저장
- GUI 콜백 시스템
- 성능 메트릭 수집
"""

import os
import sys
import time
import json
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from deployment_monitor import DeploymentMonitor, DeploymentPhase, MonitoringStatus
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class TestDeploymentMonitor:
    """배포 모니터링 시스템 테스트 클래스"""
    
    def __init__(self):
        self.monitor = None
        self.test_results = []
        self.callback_messages = []
    
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """테스트 결과 기록"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_monitor_initialization(self):
        """모니터 초기화 테스트"""
        try:
            self.monitor = DeploymentMonitor()
            
            # 기본 속성 확인
            assert hasattr(self.monitor, 'logs_dir'), "logs_dir 속성 없음"
            assert hasattr(self.monitor, 'deployment_log'), "deployment_log 속성 없음"
            assert hasattr(self.monitor, 'metrics_log'), "metrics_log 속성 없음"
            assert hasattr(self.monitor, 'monitoring_status'), "monitoring_status 속성 없음"
            
            # 로그 디렉토리 생성 확인
            assert os.path.exists(self.monitor.logs_dir), "logs 디렉토리가 생성되지 않음"
            
            # 초기 상태 확인
            assert self.monitor.monitoring_status == MonitoringStatus.IDLE, "초기 상태가 IDLE이 아님"
            assert self.monitor.current_session is None, "초기 세션이 None이 아님"
            
            self.log_test_result("모니터 초기화", True)
            
        except Exception as e:
            self.log_test_result("모니터 초기화", False, str(e))
    
    def test_callback_registration(self):
        """콜백 등록 테스트"""
        try:
            # 테스트 콜백 함수들
            def progress_callback(message, progress, details):
                self.callback_messages.append(f"PROGRESS: {message} ({progress}%)")
            
            def phase_callback(phase, metrics):
                self.callback_messages.append(f"PHASE: {phase.value}")
            
            def completion_callback(session):
                self.callback_messages.append(f"COMPLETION: {session.session_id}")
            
            def error_callback(error_msg, details):
                self.callback_messages.append(f"ERROR: {error_msg}")
            
            # 콜백 등록
            self.monitor.register_progress_callback(progress_callback)
            self.monitor.register_phase_callback(phase_callback)
            self.monitor.register_completion_callback(completion_callback)
            self.monitor.register_error_callback(error_callback)
            
            # 콜백 리스트 확인
            assert len(self.monitor.progress_callbacks) == 1, "진행 상황 콜백 등록 실패"
            assert len(self.monitor.phase_callbacks) == 1, "단계 콜백 등록 실패"
            assert len(self.monitor.completion_callbacks) == 1, "완료 콜백 등록 실패"
            assert len(self.monitor.error_callbacks) == 1, "오류 콜백 등록 실패"
            
            self.log_test_result("콜백 등록", True)
            
        except Exception as e:
            self.log_test_result("콜백 등록", False, str(e))
    
    def test_deployment_monitoring_lifecycle(self):
        """배포 모니터링 생명주기 테스트"""
        try:
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 1. 모니터링 시작
            start_result = self.monitor.start_deployment_monitoring(session_id)
            assert start_result, "모니터링 시작 실패"
            assert self.monitor.monitoring_status == MonitoringStatus.MONITORING, "모니터링 상태가 MONITORING이 아님"
            assert self.monitor.current_session is not None, "현재 세션이 None"
            assert self.monitor.current_session.session_id == session_id, "세션 ID 불일치"
            
            # 2. 단계별 업데이트
            test_phases = [
                DeploymentPhase.PRE_CHECK,
                DeploymentPhase.HTML_GENERATION,
                DeploymentPhase.BRANCH_SWITCH,
                DeploymentPhase.PUSH_REMOTE
            ]
            
            for i, phase in enumerate(test_phases):
                self.monitor.update_deployment_phase(
                    phase, 
                    success=True, 
                    details={"test_step": i + 1}
                )
                time.sleep(0.1)  # 짧은 대기
                
                # 현재 단계 확인
                assert self.monitor.current_session.current_phase == phase, f"현재 단계가 {phase}가 아님"
                assert phase.value in self.monitor.current_session.phases, f"{phase.value} 메트릭이 없음"
            
            # 3. 현재 상태 조회
            current_status = self.monitor.get_current_deployment_status()
            assert current_status is not None, "현재 상태 조회 실패"
            assert current_status["session_id"] == session_id, "상태 조회 세션 ID 불일치"
            assert current_status["completed_phases"] > 0, "완료된 단계가 0개"
            
            # 4. 모니터링 중지
            self.monitor.stop_deployment_monitoring(success=True)
            assert self.monitor.monitoring_status == MonitoringStatus.IDLE, "모니터링 상태가 IDLE이 아님"
            assert self.monitor.current_session.overall_success, "전체 성공 상태가 False"
            
            self.log_test_result("배포 모니터링 생명주기", True)
            
        except Exception as e:
            self.log_test_result("배포 모니터링 생명주기", False, str(e))
    
    def test_log_file_creation(self):
        """로그 파일 생성 테스트"""
        try:
            # 로그 파일들이 생성되었는지 확인
            log_files = [
                self.monitor.deployment_log,
                self.monitor.metrics_log,
                self.monitor.performance_log
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    # 파일 크기 확인 (0보다 커야 함)
                    file_size = os.path.getsize(log_file)
                    assert file_size > 0, f"{log_file} 파일이 비어있음"
                    
                    # JSON 파일인 경우 유효성 확인
                    if log_file.endswith('.json'):
                        with open(log_file, 'r', encoding='utf-8') as f:
                            json.load(f)  # JSON 파싱 테스트
            
            # 로그 디렉토리 내용 확인
            logs_dir_contents = os.listdir(self.monitor.logs_dir)
            assert len(logs_dir_contents) > 0, "logs 디렉토리가 비어있음"
            
            self.log_test_result("로그 파일 생성", True)
            
        except Exception as e:
            self.log_test_result("로그 파일 생성", False, str(e))
    
    def test_callback_system(self):
        """콜백 시스템 테스트"""
        try:
            # 콜백 메시지 초기화
            self.callback_messages.clear()
            
            # 새 세션으로 테스트
            session_id = f"callback_test_{datetime.now().strftime('%H%M%S')}"
            
            self.monitor.start_deployment_monitoring(session_id)
            
            # 단계 업데이트로 콜백 트리거
            self.monitor.update_deployment_phase(DeploymentPhase.PRE_CHECK, success=True)
            time.sleep(0.1)
            
            self.monitor.stop_deployment_monitoring(success=True)
            
            # 콜백 메시지 확인
            assert len(self.callback_messages) > 0, "콜백 메시지가 없음"
            
            # 특정 콜백 타입들이 호출되었는지 확인
            progress_messages = [msg for msg in self.callback_messages if msg.startswith("PROGRESS:")]
            phase_messages = [msg for msg in self.callback_messages if msg.startswith("PHASE:")]
            completion_messages = [msg for msg in self.callback_messages if msg.startswith("COMPLETION:")]
            
            assert len(progress_messages) > 0, "진행 상황 콜백이 호출되지 않음"
            assert len(phase_messages) > 0, "단계 콜백이 호출되지 않음"
            assert len(completion_messages) > 0, "완료 콜백이 호출되지 않음"
            
            self.log_test_result("콜백 시스템", True)
            
        except Exception as e:
            self.log_test_result("콜백 시스템", False, str(e))
    
    def test_performance_metrics(self):
        """성능 메트릭 테스트"""
        try:
            # 성능 통계 조회
            stats = self.monitor.get_performance_statistics()
            assert isinstance(stats, dict), "성능 통계가 딕셔너리가 아님"
            assert "summary" in stats, "성능 통계에 summary가 없음"
            assert "phase_averages" in stats, "성능 통계에 phase_averages가 없음"
            assert "trends" in stats, "성능 통계에 trends가 없음"
            
            # 배포 히스토리 조회
            history = self.monitor.get_deployment_history(10)
            assert isinstance(history, list), "배포 히스토리가 리스트가 아님"
            
            # 최근 테스트로 인한 히스토리가 있어야 함
            if len(history) > 0:
                latest_session = history[0]
                assert "session_id" in latest_session, "히스토리에 session_id가 없음"
                assert "total_duration" in latest_session, "히스토리에 total_duration이 없음"
                assert "phases" in latest_session, "히스토리에 phases가 없음"
            
            self.log_test_result("성능 메트릭", True)
            
        except Exception as e:
            self.log_test_result("성능 메트릭", False, str(e))
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        try:
            # 중복 모니터링 시작 테스트
            session_id1 = "error_test_1"
            session_id2 = "error_test_2"
            
            # 첫 번째 세션 시작
            result1 = self.monitor.start_deployment_monitoring(session_id1)
            assert result1, "첫 번째 세션 시작 실패"
            
            # 두 번째 세션 시작 (실패해야 함)
            result2 = self.monitor.start_deployment_monitoring(session_id2)
            assert not result2, "중복 세션 시작이 성공함 (실패해야 함)"
            
            # 첫 번째 세션 정리
            self.monitor.stop_deployment_monitoring(success=True)
            
            # 세션 없이 단계 업데이트 테스트
            self.monitor.current_session = None
            self.monitor.update_deployment_phase(DeploymentPhase.PRE_CHECK)
            # 오류가 발생해도 예외가 발생하지 않아야 함
            
            self.log_test_result("오류 처리", True)
            
        except Exception as e:
            self.log_test_result("오류 처리", False, str(e))
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 배포 모니터링 시스템 테스트 시작")
        print("=" * 50)
        
        # 테스트 실행
        self.test_monitor_initialization()
        self.test_callback_registration()
        self.test_deployment_monitoring_lifecycle()
        self.test_log_file_creation()
        self.test_callback_system()
        self.test_performance_metrics()
        self.test_error_handling()
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"전체 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # 콜백 메시지 출력
        if self.callback_messages:
            print(f"\n📢 콜백 메시지 ({len(self.callback_messages)}개):")
            for msg in self.callback_messages[-5:]:  # 최근 5개만 표시
                print(f"  {msg}")
        
        print("\n✅ 테스트 완료")
        return failed_tests == 0


def main():
    """메인 함수"""
    tester = TestDeploymentMonitor()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 모든 테스트가 성공했습니다!")
        return 0
    else:
        print("\n💥 일부 테스트가 실패했습니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())