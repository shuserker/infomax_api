#!/usr/bin/env python3
"""
POSCO 시스템 지속적 품질 관리 시작 스크립트
Startup Script for Continuous Quality Management System

이 스크립트는 지속적 품질 관리 시스템을 시작하고 관리합니다.
"""

import os
import sys
import time
import signal
import argparse
from datetime import datetime
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from continuous_quality_management_system import ContinuousQualityManager
except ImportError as e:
    print(f"❌ 품질 관리 시스템 모듈을 찾을 수 없습니다: {e}")
    print("continuous_quality_management_system.py 파일이 존재하는지 확인하세요.")
    sys.exit(1)

class QualityManagementService:
    """품질 관리 서비스 클래스"""
    
    def __init__(self):
        self.quality_manager = None
        self.running = False
        self.start_time = None
        
    def start(self, mode='monitor', duration=3600):
        """서비스 시작"""
        print("🚀 POSCO 시스템 지속적 품질 관리 서비스 시작")
        print("=" * 60)
        
        try:
            # 품질 관리자 초기화
            print("📋 품질 관리 시스템 초기화 중...")
            self.quality_manager = ContinuousQualityManager()
            
            self.start_time = datetime.now()
            self.running = True
            
            if mode == 'monitor':
                self._run_monitoring_mode(duration)
            elif mode == 'pipeline':
                self._run_pipeline_mode()
            elif mode == 'dashboard':
                self._run_dashboard_mode()
            elif mode == 'report':
                self._run_report_mode()
            else:
                print(f"❌ 알 수 없는 모드: {mode}")
                return False
                
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ 사용자에 의해 중단됨")
            self.stop()
            return True
        except Exception as e:
            print(f"❌ 서비스 시작 중 오류: {e}")
            return False
    
    def _run_monitoring_mode(self, duration):
        """모니터링 모드 실행"""
        print(f"📊 지속적 모니터링 모드 시작 (지속 시간: {duration}초)")
        
        # 지속적 모니터링 시작
        self.quality_manager.start_continuous_monitoring()
        
        print("✅ 모니터링 시스템 시작 완료")
        print("\n📈 실시간 상태:")
        print("-" * 40)
        
        try:
            elapsed = 0
            while elapsed < duration and self.running:
                # 5초마다 상태 업데이트
                time.sleep(5)
                elapsed += 5
                
                # 진행률 표시
                progress = (elapsed / duration) * 100
                remaining = duration - elapsed
                
                print(f"\r⏱️  진행률: {progress:.1f}% | 남은 시간: {remaining}초", end="", flush=True)
                
                # 30초마다 상세 상태 출력
                if elapsed % 30 == 0:
                    print()  # 새 줄
                    self._print_current_status()
                    
        except KeyboardInterrupt:
            print("\n⏹️ 모니터링 중단됨")
        finally:
            self.quality_manager.stop_continuous_monitoring()
            print("\n✅ 모니터링 시스템 정상 종료")
    
    def _run_pipeline_mode(self):
        """파이프라인 모드 실행"""
        print("🔄 CI/CD 파이프라인 실행 모드")
        
        success = self.quality_manager.run_quality_pipeline()
        
        if success:
            print("✅ 파이프라인 성공 완료")
        else:
            print("❌ 파이프라인 실패")
            sys.exit(1)
    
    def _run_dashboard_mode(self):
        """대시보드 모드 실행"""
        print("📈 대시보드 생성 모드")
        
        # 현재 상태 수집
        self.quality_manager._collect_initial_metrics()
        
        # 대시보드 HTML 생성
        html_content = self.quality_manager.dashboard.generate_dashboard_html()
        
        dashboard_file = f"quality_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 대시보드 생성 완료: {dashboard_file}")
        
        # 브라우저에서 열기 시도
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(dashboard_file)}")
            print("🌐 브라우저에서 대시보드를 열었습니다.")
        except Exception:
            print("💡 브라우저에서 대시보드 파일을 직접 열어보세요.")
    
    def _run_report_mode(self):
        """보고서 모드 실행"""
        print("📋 품질 보고서 생성 모드")
        
        # 현재 상태 수집
        self.quality_manager._collect_initial_metrics()
        
        # 보고서 생성
        report_content = self.quality_manager.generate_quality_report()
        
        report_file = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 품질 보고서 생성 완료: {report_file}")
        print("\n" + "="*60)
        print(report_content)
    
    def _print_current_status(self):
        """현재 상태 출력"""
        try:
            # 건강성 상태 조회
            health_status = self.quality_manager.health_system.get_health_status()
            
            overall_status = "✅ 정상" if health_status['overall_healthy'] else "⚠️ 주의"
            print(f"🏥 전체 시스템 상태: {overall_status}")
            
            # 각 건강성 체크 상태
            for check in health_status['checks']:
                status_emoji = "✅" if check['healthy'] else "❌"
                print(f"   {status_emoji} {check['name']}: {check['message']}")
                
        except Exception as e:
            print(f"⚠️ 상태 조회 중 오류: {e}")
    
    def stop(self):
        """서비스 중지"""
        print("\n🛑 품질 관리 서비스 중지 중...")
        
        self.running = False
        
        if self.quality_manager:
            self.quality_manager.stop_continuous_monitoring()
        
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"⏱️ 총 실행 시간: {duration}")
        
        print("✅ 서비스 정상 종료")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    print(f"\n📡 시그널 수신: {signum}")
    service.stop()
    sys.exit(0)

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='POSCO 시스템 지속적 품질 관리 서비스',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python start_quality_management.py --mode monitor --duration 3600
  python start_quality_management.py --mode pipeline
  python start_quality_management.py --mode dashboard
  python start_quality_management.py --mode report
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['monitor', 'pipeline', 'dashboard', 'report'],
        default='monitor',
        help='실행 모드 선택 (기본값: monitor)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=3600,
        help='모니터링 지속 시간 (초, 기본값: 3600)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )
    
    args = parser.parse_args()
    
    # 로깅 레벨 설정
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 서비스 시작
    global service
    service = QualityManagementService()
    
    print(f"🎯 모드: {args.mode}")
    if args.mode == 'monitor':
        print(f"⏱️ 지속 시간: {args.duration}초")
    print()
    
    success = service.start(args.mode, args.duration)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()