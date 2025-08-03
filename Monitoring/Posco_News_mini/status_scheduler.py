#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상태 모니터링 스케줄러

정기적으로 시스템 상태를 수집하고 업데이트하는 스케줄러입니다.
백그라운드에서 실행되며 대시보드 데이터를 최신 상태로 유지합니다.

주요 기능:
- 정기적인 상태 수집 (5분 간격)
- 메타데이터 자동 업데이트 (30분 간격)
- 오류 발생 시 알림
- 로그 관리

작성자: AI Assistant
최종 수정: 2025-08-02
"""

import schedule
import time
import logging
import sys
from datetime import datetime
from pathlib import Path
import threading
import signal

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from status_monitor import status_monitor
from reports.metadata_manager import metadata_manager

class StatusScheduler:
    """상태 모니터링 스케줄러 클래스"""
    
    def __init__(self):
        self.running = False
        self.setup_logging()
        
        # 종료 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """로깅 설정"""
        log_dir = current_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 로그 파일 설정
        log_file = log_dir / f'status_scheduler_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, signum, frame):
        """종료 신호 처리"""
        self.logger.info(f"종료 신호 수신: {signum}")
        self.stop()
    
    def update_status_job(self):
        """상태 업데이트 작업"""
        try:
            self.logger.info("🔄 상태 업데이트 시작")
            status_data = status_monitor.collect_all_status()
            
            # 오류 체크
            errors = status_data.get('systemStatus', {}).get('errors', [])
            if errors:
                self.logger.warning(f"시스템 오류 감지: {len(errors)}개")
                for error in errors:
                    self.logger.warning(f"  - {error}")
            
            self.logger.info("✅ 상태 업데이트 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 상태 업데이트 실패: {e}")
    
    def update_metadata_job(self):
        """메타데이터 업데이트 작업"""
        try:
            self.logger.info("📊 메타데이터 업데이트 시작")
            updated_count = metadata_manager.scan_and_update_all()
            self.logger.info(f"✅ 메타데이터 업데이트 완료: {updated_count}개 파일 처리")
            
        except Exception as e:
            self.logger.error(f"❌ 메타데이터 업데이트 실패: {e}")
    
    def cleanup_logs_job(self):
        """로그 정리 작업 (7일 이상 된 로그 삭제)"""
        try:
            log_dir = current_dir / 'logs'
            if not log_dir.exists():
                return
            
            current_time = time.time()
            deleted_count = 0
            
            for log_file in log_dir.glob('*.log'):
                # 7일 이상 된 파일 삭제
                if current_time - log_file.stat().st_mtime > 7 * 24 * 3600:
                    log_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                self.logger.info(f"🧹 오래된 로그 파일 {deleted_count}개 삭제")
                
        except Exception as e:
            self.logger.error(f"❌ 로그 정리 실패: {e}")
    
    def health_check_job(self):
        """시스템 헬스 체크"""
        try:
            self.logger.info("🔍 시스템 헬스 체크")
            
            # 필수 파일 존재 확인
            required_files = [
                current_dir.parent.parent / 'docs' / 'reports_index.json',
                current_dir.parent.parent / 'docs' / 'status.json'
            ]
            
            missing_files = []
            for file_path in required_files:
                if not file_path.exists():
                    missing_files.append(str(file_path))
            
            if missing_files:
                self.logger.warning(f"필수 파일 누락: {missing_files}")
                # 자동 복구 시도
                try:
                    metadata_manager._ensure_metadata_files()
                    self.logger.info("✅ 누락된 파일 자동 복구 완료")
                except Exception as e:
                    self.logger.error(f"❌ 파일 복구 실패: {e}")
            
            # 디스크 공간 체크
            import shutil
            total, used, free = shutil.disk_usage(current_dir)
            free_percent = (free / total) * 100
            
            if free_percent < 10:
                self.logger.warning(f"디스크 공간 부족: {free_percent:.1f}% 남음")
            
            self.logger.info("✅ 헬스 체크 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 헬스 체크 실패: {e}")
    
    def setup_schedule(self):
        """스케줄 설정"""
        # 상태 업데이트: 5분마다
        schedule.every(5).minutes.do(self.update_status_job)
        
        # 메타데이터 업데이트: 30분마다
        schedule.every(30).minutes.do(self.update_metadata_job)
        
        # 로그 정리: 매일 자정
        schedule.every().day.at("00:00").do(self.cleanup_logs_job)
        
        # 헬스 체크: 1시간마다
        schedule.every().hour.do(self.health_check_job)
        
        self.logger.info("📅 스케줄 설정 완료")
        self.logger.info("  - 상태 업데이트: 5분마다")
        self.logger.info("  - 메타데이터 업데이트: 30분마다")
        self.logger.info("  - 로그 정리: 매일 자정")
        self.logger.info("  - 헬스 체크: 1시간마다")
    
    def start(self):
        """스케줄러 시작"""
        if self.running:
            self.logger.warning("스케줄러가 이미 실행 중입니다.")
            return
        
        self.running = True
        self.setup_schedule()
        
        self.logger.info("🚀 상태 모니터링 스케줄러 시작")
        
        # 초기 실행
        self.logger.info("🔄 초기 상태 수집 실행")
        self.update_status_job()
        self.update_metadata_job()
        
        # 스케줄 실행 루프
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"❌ 스케줄러 실행 오류: {e}")
        finally:
            self.logger.info("⏹️ 스케줄러 종료")
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        self.logger.info("🛑 스케줄러 중지 요청")
    
    def run_once(self):
        """한 번만 실행"""
        self.logger.info("🔄 일회성 상태 수집 실행")
        self.update_status_job()
        self.update_metadata_job()
        self.health_check_job()
        self.logger.info("✅ 일회성 실행 완료")

def run_scheduler_daemon():
    """데몬 모드로 스케줄러 실행"""
    scheduler = StatusScheduler()
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.logger.info("⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        scheduler.logger.error(f"❌ 예상치 못한 오류: {e}")
    finally:
        scheduler.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='POSCO 리포트 상태 모니터링 스케줄러')
    parser.add_argument('--daemon', '-d', action='store_true', help='데몬 모드로 실행')
    parser.add_argument('--once', action='store_true', help='한 번만 실행')
    
    args = parser.parse_args()
    
    scheduler = StatusScheduler()
    
    if args.once:
        # 한 번만 실행
        scheduler.run_once()
    elif args.daemon:
        # 데몬 모드
        run_scheduler_daemon()
    else:
        # 일반 모드 (포그라운드)
        try:
            scheduler.start()
        except KeyboardInterrupt:
            print("\n⚠️ 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            sys.exit(1)