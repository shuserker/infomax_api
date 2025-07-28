#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
POSCO 뉴스 AI 분석 시스템 CLI 도구
전체 기능을 명령줄에서 사용할 수 있는 통합 CLI
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import PoscoNewsMonitor, DoorayNotifier, PoscoNewsAPIClient
from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL

class PoscoCLI:
    def __init__(self):
        self.monitor = None
        self.api_client = None
        self.notifier = None
        
    def setup_components(self):
        """컴포넌트 초기화"""
        try:
            self.api_client = PoscoNewsAPIClient(API_CONFIG)
            self.notifier = DoorayNotifier(DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, self.api_client)
            self.monitor = PoscoNewsMonitor(DOORAY_WEBHOOK_URL)
            return True
        except Exception as e:
            print(f"❌ 컴포넌트 초기화 실패: {e}")
            return False
    
    def status(self, args):
        """현재 상태 확인"""
        print("📊 POSCO 뉴스 모니터링 상태 확인 중...")
        
        if not self.setup_components():
            return
        
        try:
            # API 연결 테스트
            print("🔗 API 연결 테스트 중...")
            if self.api_client.test_connection():
                print("✅ API 연결 성공")
            else:
                print("❌ API 연결 실패")
                return
            
            # 현재 데이터 가져오기
            current_data = self.api_client.get_news_data()
            if not current_data:
                print("⚠️ 현재 뉴스 데이터가 없습니다.")
                return
            
            # 상태 정보 생성
            processor = self.monitor.data_processor
            status_info = processor.get_status_info(current_data)
            
            # 상태 출력
            print("\n" + "="*50)
            print("📈 POSCO 뉴스 모니터링 상태")
            print("="*50)
            
            for news_type, info in status_info.items():
                print(f"\n📰 {info['display_name']}")
                print(f"   상태: {info['status']}")
                print(f"   최신 뉴스: {info['latest_news']}")
                print(f"   발행 시간: {info['publish_time']}")
                print(f"   예상 발행: {info['expected_time']}")
            
            print(f"\n🕐 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ 상태 확인 실패: {e}")
    
    def monitor_start(self, args):
        """모니터링 시작"""
        print("🚀 POSCO 뉴스 모니터링 시작...")
        
        if not self.setup_components():
            return
        
        try:
            interval = args.interval if args.interval else 60
            print(f"⏰ 모니터링 간격: {interval}분")
            
            if args.smart:
                print("🧠 스마트 모니터링 모드 활성화")
                self.monitor.start_smart_monitoring()
            else:
                print("🔄 기본 모니터링 모드 활성화")
                self.monitor.start_monitoring(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ 모니터링 중지됨")
        except Exception as e:
            print(f"❌ 모니터링 시작 실패: {e}")
    
    def analyze(self, args):
        """분석 실행"""
        print("🧠 POSCO 뉴스 AI 분석 실행...")
        
        if not self.setup_components():
            return
        
        try:
            days_back = args.days if args.days else 30
            print(f"📊 분석 범위: 최근 {days_back}일")
            
            if args.simple:
                print("📋 간단 분석 모드")
                self.monitor.execute_detailed_daily_summary()
            elif args.advanced:
                print("🔬 고급 분석 모드")
                self.monitor.execute_advanced_analysis(days_back)
            else:
                print("📊 기본 분석 모드")
                self.monitor.send_daily_summary()
                
            print("✅ 분석 완료")
            
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
    
    def deploy(self, args):
        """배포 실행"""
        print("🚀 배포 프로세스 시작...")
        
        if not self.setup_components():
            return
        
        try:
            # 1. 분석 리포트 생성
            print("📊 분석 리포트 생성 중...")
            self.monitor.execute_advanced_analysis(30)
            
            # 2. Git 상태 확인
            print("🔍 Git 상태 확인 중...")
            os.system("git status")
            
            # 3. 변경사항 커밋
            print("💾 변경사항 커밋 중...")
            commit_message = args.message if args.message else f"🚀 자동 배포: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            os.system(f'git add . && git commit -m "{commit_message}"')
            
            # 4. GitHub에 푸시
            print("📤 GitHub에 푸시 중...")
            os.system("git push origin main")
            
            print("✅ 배포 완료!")
            print("🌐 대시보드 URL: https://shuserker.github.io/infomax_api/")
            
        except Exception as e:
            print(f"❌ 배포 실패: {e}")
    
    def test(self, args):
        """테스트 실행"""
        print("🧪 테스트 실행...")
        
        if not self.setup_components():
            return
        
        try:
            # API 연결 테스트
            print("🔗 API 연결 테스트...")
            if self.api_client.test_connection():
                print("✅ API 연결 성공")
            else:
                print("❌ API 연결 실패")
            
            # 웹훅 테스트
            print("📡 웹훅 테스트...")
            test_message = f"🧪 CLI 테스트 메시지 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if self.notifier.send_notification(test_message):
                print("✅ 웹훅 전송 성공")
            else:
                print("❌ 웹훅 전송 실패")
            
            # 데이터 가져오기 테스트
            print("📊 데이터 가져오기 테스트...")
            current_data = self.api_client.get_news_data()
            if current_data:
                print(f"✅ 데이터 가져오기 성공 ({len(current_data)}개 뉴스 타입)")
            else:
                print("❌ 데이터 가져오기 실패")
                
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
    
    def config(self, args):
        """설정 관리"""
        if args.show:
            print("⚙️ 현재 설정:")
            print(f"   API URL: {API_CONFIG.get('url', 'N/A')}")
            print(f"   웹훅 URL: {DOORAY_WEBHOOK_URL}")
            print(f"   봇 이미지: {BOT_PROFILE_IMAGE_URL}")
        
        if args.validate:
            print("🔍 설정 유효성 검사...")
            if self.setup_components():
                print("✅ 설정 유효")
            else:
                print("❌ 설정 오류")
    
    def logs(self, args):
        """로그 확인"""
        print("📋 로그 확인...")
        
        log_file = "posco_monitor.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if args.lines:
                    lines = lines[-args.lines:]
                for line in lines:
                    print(line.rstrip())
        else:
            print("📝 로그 파일이 없습니다.")
    
    def dashboard(self, args):
        """대시보드 정보"""
        print("📊 대시보드 정보:")
        print("🌐 URL: https://shuserker.github.io/infomax_api/")
        print("📱 PWA 설치 가능")
        print("🎨 다크/라이트 테마 지원")
        print("🔄 실시간 업데이트")
        
        # 최신 리포트 확인
        reports_dir = Path("docs/reports")
        if reports_dir.exists():
            html_files = list(reports_dir.glob("*.html"))
            if html_files:
                latest_file = max(html_files, key=lambda x: x.stat().st_mtime)
                print(f"📄 최신 리포트: {latest_file.name}")
                print(f"🕐 생성 시간: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")
    
    def report(self, args):
        """리포트 관리"""
        if args.list:
            print("📋 리포트 목록:")
            reports_dir = Path("docs/reports")
            if reports_dir.exists():
                html_files = list(reports_dir.glob("*.html"))
                if html_files:
                    # 날짜별로 그룹화
                    reports_by_date = {}
                    for file in html_files:
                        date = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d')
                        if date not in reports_by_date:
                            reports_by_date[date] = []
                        reports_by_date[date].append(file)
                    
                    for date in sorted(reports_by_date.keys(), reverse=True):
                        print(f"\n📅 {date}:")
                        for file in reports_by_date[date]:
                            size = file.stat().st_size / 1024  # KB
                            print(f"   📄 {file.name} ({size:.1f}KB)")
                else:
                    print("   📝 리포트가 없습니다.")
            else:
                print("   📁 리포트 디렉토리가 없습니다.")
        
        if args.clean:
            print("🧹 오래된 리포트 정리 중...")
            reports_dir = Path("docs/reports")
            if reports_dir.exists():
                html_files = list(reports_dir.glob("*.html"))
                if html_files:
                    # 7일 이상 된 파일 삭제
                    cutoff_time = time.time() - (7 * 24 * 60 * 60)
                    deleted_count = 0
                    for file in html_files:
                        if file.stat().st_mtime < cutoff_time:
                            file.unlink()
                            deleted_count += 1
                    print(f"✅ {deleted_count}개 파일 삭제됨")
                else:
                    print("📝 삭제할 파일이 없습니다.")
    
    def backup(self, args):
        """백업 관리"""
        if args.create:
            print("💾 백업 생성 중...")
            backup_dir = Path("backup")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"posco_backup_{timestamp}"
            backup_path = backup_dir / backup_name
            backup_path.mkdir()
            
            # 중요 파일들 복사
            import shutil
            files_to_backup = [
                "config.py",
                "core/__init__.py",
                "requirements.txt",
                "docs/dashboard_data.json"
            ]
            
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    shutil.copy2(file_path, backup_path)
            
            print(f"✅ 백업 완료: {backup_path}")
        
        if args.list:
            print("📋 백업 목록:")
            backup_dir = Path("backup")
            if backup_dir.exists():
                backups = list(backup_dir.iterdir())
                if backups:
                    for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
                        size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file()) / 1024
                        print(f"   📁 {backup.name} ({size:.1f}KB)")
                else:
                    print("   📝 백업이 없습니다.")
            else:
                print("   📁 백업 디렉토리가 없습니다.")
    
    def health(self, args):
        """시스템 상태 점검"""
        print("🏥 시스템 상태 점검 중...")
        
        checks = []
        
        # 1. Python 버전 확인
        import platform
        python_version = platform.python_version()
        checks.append(("Python 버전", python_version, "3.8+"))
        
        # 2. 필수 패키지 확인
        required_packages = ['requests', 'textblob', 'numpy', 'pandas']
        for package in required_packages:
            try:
                __import__(package)
                checks.append((f"{package} 패키지", "설치됨", "필수"))
            except ImportError:
                checks.append((f"{package} 패키지", "미설치", "필수"))
        
        # 3. 설정 파일 확인
        config_files = ['config.py', 'core/__init__.py']
        for file in config_files:
            if os.path.exists(file):
                checks.append((f"{file} 파일", "존재함", "필수"))
            else:
                checks.append((f"{file} 파일", "없음", "필수"))
        
        # 4. 디렉토리 확인
        directories = ['docs', 'reports', 'docs/reports']
        for dir_path in directories:
            if os.path.exists(dir_path):
                checks.append((f"{dir_path} 디렉토리", "존재함", "필수"))
            else:
                checks.append((f"{dir_path} 디렉토리", "없음", "필수"))
        
        # 결과 출력
        print("\n" + "="*60)
        print("📊 시스템 상태 점검 결과")
        print("="*60)
        
        all_good = True
        for item, status, requirement in checks:
            if "없음" in status or "미설치" in status:
                print(f"❌ {item}: {status} ({requirement})")
                all_good = False
            else:
                print(f"✅ {item}: {status}")
        
        print("\n" + "="*60)
        if all_good:
            print("🎉 모든 점검이 통과되었습니다!")
        else:
            print("⚠️ 일부 문제가 발견되었습니다. 위 항목들을 확인해주세요.")
        
        return all_good

def main():
    parser = argparse.ArgumentParser(
        description="POSCO 뉴스 AI 분석 시스템 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s status                    # 현재 상태 확인
  %(prog)s monitor --smart          # 스마트 모니터링 시작
  %(prog)s analyze --advanced       # 고급 분석 실행
  %(prog)s deploy                   # 배포 실행
  %(prog)s test                     # 테스트 실행
  %(prog)s config --show            # 설정 확인
  %(prog)s logs --lines 50          # 최근 50줄 로그 확인
  %(prog)s dashboard                # 대시보드 정보
  %(prog)s report --list            # 리포트 목록 확인
  %(prog)s report --clean           # 오래된 리포트 정리
  %(prog)s backup --create          # 백업 생성
  %(prog)s backup --list            # 백업 목록 확인
  %(prog)s health                   # 시스템 상태 점검
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # status 명령어
    status_parser = subparsers.add_parser('status', help='현재 상태 확인')
    
    # monitor 명령어
    monitor_parser = subparsers.add_parser('monitor', help='모니터링 시작')
    monitor_parser.add_argument('--interval', type=int, help='모니터링 간격 (분)')
    monitor_parser.add_argument('--smart', action='store_true', help='스마트 모니터링 모드')
    
    # analyze 명령어
    analyze_parser = subparsers.add_parser('analyze', help='분석 실행')
    analyze_parser.add_argument('--days', type=int, help='분석할 일수 (기본값: 30)')
    analyze_parser.add_argument('--simple', action='store_true', help='간단 분석')
    analyze_parser.add_argument('--advanced', action='store_true', help='고급 분석')
    
    # deploy 명령어
    deploy_parser = subparsers.add_parser('deploy', help='배포 실행')
    deploy_parser.add_argument('--message', help='커밋 메시지')
    
    # test 명령어
    test_parser = subparsers.add_parser('test', help='테스트 실행')
    
    # config 명령어
    config_parser = subparsers.add_parser('config', help='설정 관리')
    config_parser.add_argument('--show', action='store_true', help='현재 설정 표시')
    config_parser.add_argument('--validate', action='store_true', help='설정 유효성 검사')
    
    # logs 명령어
    logs_parser = subparsers.add_parser('logs', help='로그 확인')
    logs_parser.add_argument('--lines', type=int, help='표시할 줄 수')
    
    # dashboard 명령어
    dashboard_parser = subparsers.add_parser('dashboard', help='대시보드 정보')
    
    # report 명령어
    report_parser = subparsers.add_parser('report', help='리포트 관리')
    report_parser.add_argument('--list', action='store_true', help='리포트 목록 표시')
    report_parser.add_argument('--clean', action='store_true', help='오래된 리포트 정리')
    
    # backup 명령어
    backup_parser = subparsers.add_parser('backup', help='백업 관리')
    backup_parser.add_argument('--create', action='store_true', help='백업 생성')
    backup_parser.add_argument('--list', action='store_true', help='백업 목록 표시')
    
    # health 명령어
    health_parser = subparsers.add_parser('health', help='시스템 상태 점검')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PoscoCLI()
    
    # 명령어 실행
    if args.command == 'status':
        cli.status(args)
    elif args.command == 'monitor':
        cli.monitor_start(args)
    elif args.command == 'analyze':
        cli.analyze(args)
    elif args.command == 'deploy':
        cli.deploy(args)
    elif args.command == 'test':
        cli.test(args)
    elif args.command == 'config':
        cli.config(args)
    elif args.command == 'logs':
        cli.logs(args)
    elif args.command == 'dashboard':
        cli.dashboard(args)
    elif args.command == 'report':
        cli.report(args)
    elif args.command == 'backup':
        cli.backup(args)
    elif args.command == 'health':
        cli.health(args)

if __name__ == "__main__":
    main() 