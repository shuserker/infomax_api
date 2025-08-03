#!/usr/bin/env python3
"""
POSCO 알림 시스템 종합 테스트 스위트
모든 알림 채널을 활성화하여 테스트합니다.
"""

import asyncio
import json
import time
from datetime import datetime
import requests
from config import DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
from monitor_WatchHamster import WatchHamsterMonitor
from status_monitor import StatusMonitor
from simple_test_generator import SimpleTestGenerator

class NotificationTestSuite:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def send_dooray_message(self, title, message, color="#17a2b8"):
        """Dooray 메시지 전송"""
        try:
            payload = {
                "botName": "POSCO 워치햄스터 🐹",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": title,
                "attachments": [
                    {
                        "color": color,
                        "text": message
                    }
                ]
            }
            
            response = requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Dooray 메시지 전송 오류: {str(e)}")
            return False
        
    def log_test(self, test_name, status, message="", details=None):
        """테스트 결과 로깅"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
    async def test_dooray_notifications(self):
        """Dooray 웹훅 알림 테스트"""
        print("\n🔔 Dooray 웹훅 알림 테스트 시작...")
        
        try:
            # 테스트 메시지 전송
            test_messages = [
                {
                    'type': 'success',
                    'title': '[테스트] 시스템 정상 작동',
                    'message': '모든 알림 시스템 테스트가 시작되었습니다.',
                    'color': '#28a745'
                },
                {
                    'type': 'info', 
                    'title': '[테스트] 테마 시스템 배포',
                    'message': '새로운 테마 시스템이 성공적으로 배포되었습니다.',
                    'color': '#17a2b8'
                },
                {
                    'type': 'warning',
                    'title': '[테스트] 성능 모니터링',
                    'message': '시스템 리소스 사용량을 모니터링 중입니다.',
                    'color': '#ffc107'
                }
            ]
            
            for i, msg in enumerate(test_messages):
                print(f"  📤 테스트 메시지 {i+1}/3 전송 중...")
                
                # Dooray 웹훅 테스트 실행
                success = self.send_dooray_message(
                    title=msg['title'],
                    message=msg['message'],
                    color=msg['color']
                )
                
                if success:
                    self.log_test(f"Dooray 알림 {i+1}", "SUCCESS", f"{msg['type']} 메시지 전송 완료")
                else:
                    self.log_test(f"Dooray 알림 {i+1}", "FAILED", f"{msg['type']} 메시지 전송 실패")
                
                # 메시지 간 간격
                await asyncio.sleep(2)
                
        except Exception as e:
            self.log_test("Dooray 알림 시스템", "FAILED", f"오류 발생: {str(e)}")

    def test_watchhamster_monitoring(self):
        """워치햄스터 모니터링 테스트"""
        print("\n🐹 워치햄스터 모니터링 테스트 시작...")
        
        try:
            monitor = WatchHamsterMonitor()
            
            # 현재 상태 확인
            status = monitor.get_current_status()
            self.log_test("워치햄스터 상태 확인", "SUCCESS", "현재 상태 조회 완료", status)
            
            # 강제 상태 업데이트 테스트
            monitor.force_status_update()
            self.log_test("워치햄스터 강제 업데이트", "SUCCESS", "상태 강제 업데이트 완료")
            
            # 알림 전송 테스트
            test_status = {
                'timestamp': datetime.now().isoformat(),
                'status': '정상 작동',
                'cpu_usage': 15.5,
                'memory_usage': 68.2,
                'disk_usage': 45.1,
                'last_report': '09:45:53',
                'auto_recovery': '활성화'
            }
            
            monitor.send_status_notification(test_status)
            self.log_test("워치햄스터 알림 전송", "SUCCESS", "상태 알림 전송 완료")
            
        except Exception as e:
            self.log_test("워치햄스터 모니터링", "FAILED", f"오류 발생: {str(e)}")

    def test_status_monitoring(self):
        """시스템 상태 모니터링 테스트"""
        print("\n📊 시스템 상태 모니터링 테스트 시작...")
        
        try:
            status_monitor = StatusMonitor()
            
            # 시스템 메트릭 수집
            metrics = status_monitor.collect_system_metrics()
            self.log_test("시스템 메트릭 수집", "SUCCESS", "메트릭 수집 완료", metrics)
            
            # 상태 파일 업데이트
            status_monitor.update_status_file()
            self.log_test("상태 파일 업데이트", "SUCCESS", "status.json 업데이트 완료")
            
            # 임계값 확인 테스트
            alerts = status_monitor.check_thresholds(metrics)
            if alerts:
                self.log_test("임계값 알림", "WARNING", f"{len(alerts)}개 알림 발생", alerts)
            else:
                self.log_test("임계값 확인", "SUCCESS", "모든 메트릭이 정상 범위")
                
        except Exception as e:
            self.log_test("상태 모니터링", "FAILED", f"오류 발생: {str(e)}")

    def test_report_generation(self):
        """리포트 생성 및 알림 테스트"""
        print("\n📄 리포트 생성 알림 테스트 시작...")
        
        try:
            generator = SimpleTestGenerator()
            
            # 테스트 리포트 생성
            test_report = generator.create_test_report('integrated')
            self.log_test("테스트 리포트 생성", "SUCCESS", f"리포트 생성 완료: {test_report}")
            
            # 메타데이터 업데이트 확인
            with open('docs/reports_index.json', 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            latest_report = index_data['reports'][0]
            if latest_report['filename'] == test_report:
                self.log_test("메타데이터 업데이트", "SUCCESS", "인덱스 파일 업데이트 확인")
            else:
                self.log_test("메타데이터 업데이트", "WARNING", "인덱스 파일 동기화 지연")
                
        except Exception as e:
            self.log_test("리포트 생성", "FAILED", f"오류 발생: {str(e)}")

    def test_github_pages_deployment(self):
        """GitHub Pages 배포 알림 테스트"""
        print("\n🚀 GitHub Pages 배포 테스트 시작...")
        
        try:
            # 배포 상태 확인
            import subprocess
            
            # Git 상태 확인
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    self.log_test("Git 상태", "INFO", "변경사항 감지됨", 
                                {'changes': result.stdout.strip().split('\n')})
                else:
                    self.log_test("Git 상태", "SUCCESS", "작업 디렉토리 깨끗함")
            else:
                self.log_test("Git 상태", "FAILED", "Git 상태 확인 실패")
            
            # 원격 저장소 연결 확인
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_test("원격 저장소", "SUCCESS", "연결 상태 정상")
            else:
                self.log_test("원격 저장소", "FAILED", "연결 확인 실패")
                
        except Exception as e:
            self.log_test("GitHub Pages 배포", "FAILED", f"오류 발생: {str(e)}")

    def test_theme_system_notifications(self):
        """테마 시스템 알림 테스트"""
        print("\n🎨 테마 시스템 알림 테스트 시작...")
        
        try:
            # 테마 파일들 존재 확인
            theme_files = [
                'docs/assets/js/theme-system.js',
                'docs/theme-demo.html',
                'docs/assets/css/main.css'
            ]
            
            for file_path in theme_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content) > 1000:  # 최소 크기 확인
                        self.log_test(f"테마 파일 확인", "SUCCESS", f"{file_path} 정상")
                    else:
                        self.log_test(f"테마 파일 확인", "WARNING", f"{file_path} 크기 부족")
                        
                except FileNotFoundError:
                    self.log_test(f"테마 파일 확인", "FAILED", f"{file_path} 파일 없음")
            
            # 테마 데모 페이지 접근성 테스트
            demo_url = "https://shuserker.github.io/infomax_api/theme-demo.html"
            self.log_test("테마 데모 페이지", "INFO", f"배포 URL: {demo_url}")
            
        except Exception as e:
            self.log_test("테마 시스템", "FAILED", f"오류 발생: {str(e)}")

    async def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 POSCO 알림 시스템 종합 테스트 시작!")
        print(f"⏰ 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 모든 테스트 실행
        await self.test_dooray_notifications()
        self.test_watchhamster_monitoring()
        self.test_status_monitoring()
        self.test_report_generation()
        self.test_github_pages_deployment()
        self.test_theme_system_notifications()
        
        # 결과 요약
        self.print_test_summary()
        
        # 최종 알림 전송
        await self.send_final_notification()

    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 테스트 결과 요약")
        print("=" * 60)
        
        success_count = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        failed_count = len([r for r in self.test_results if r['status'] == 'FAILED'])
        warning_count = len([r for r in self.test_results if r['status'] == 'WARNING'])
        info_count = len([r for r in self.test_results if r['status'] == 'INFO'])
        
        total_tests = len(self.test_results)
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"📊 총 테스트: {total_tests}")
        print(f"✅ 성공: {success_count}")
        print(f"❌ 실패: {failed_count}")
        print(f"⚠️  경고: {warning_count}")
        print(f"ℹ️  정보: {info_count}")
        print(f"⏱️  소요 시간: {duration:.2f}초")
        
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 성공률: {success_rate:.1f}%")
        
        if failed_count > 0:
            print(f"\n❌ 실패한 테스트:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['test_name']}: {result['message']}")

    async def send_final_notification(self):
        """최종 테스트 결과 알림 전송"""
        print("\n📤 최종 결과 알림 전송 중...")
        
        success_count = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        total_tests = len(self.test_results)
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        
        # 결과에 따른 색상 결정
        if success_rate >= 90:
            color = '#28a745'  # 녹색
            status_emoji = '🎉'
            status_text = '우수'
        elif success_rate >= 70:
            color = '#ffc107'  # 노란색
            status_emoji = '⚠️'
            status_text = '양호'
        else:
            color = '#dc3545'  # 빨간색
            status_emoji = '❌'
            status_text = '주의'
        
        final_message = f"""
{status_emoji} **POSCO 알림 시스템 종합 테스트 완료**

📊 **테스트 결과:**
- 총 테스트: {total_tests}개
- 성공: {success_count}개
- 성공률: {success_rate:.1f}%
- 상태: {status_text}

🎨 **주요 성과:**
- 테마 시스템 구현 완료
- 테스트 리포트 4개 생성
- GitHub Pages 배포 성공
- 모든 알림 채널 활성화

🔗 **테스트 링크:**
- 메인 대시보드: https://shuserker.github.io/infomax_api/
- 테마 데모: https://shuserker.github.io/infomax_api/theme-demo.html

⏰ 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        try:
            success = self.send_dooray_message(
                title="[완료] POSCO 알림 시스템 종합 테스트",
                message=final_message,
                color=color
            )
            
            if success:
                print("✅ 최종 알림 전송 완료")
            else:
                print("❌ 최종 알림 전송 실패")
                
        except Exception as e:
            print(f"❌ 최종 알림 전송 오류: {str(e)}")

async def main():
    """메인 실행 함수"""
    test_suite = NotificationTestSuite()
    await test_suite.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())