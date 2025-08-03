#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 리포트 시스템 레거시 파일 정리기

통합 리포트 시스템으로 전환 후 더 이상 사용하지 않는 레거시 파일들을 정리
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

class LegacyFileCleaner:
    """레거시 파일 정리 클래스"""
    
    def __init__(self):
        self.monitoring_dir = Path(__file__).parent
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 삭제할 레거시 파일들
        self.legacy_files = [
            # 비활성화된 개별 모니터 스크립트들
            'exchange_monitor.py.disabled',
            'kospi_monitor.py.disabled', 
            'newyork_monitor.py.disabled',
            'master_news_monitor.py.disabled',
            'run_monitor.py.disabled',
            
            # 개별 리포트 생성 관련 파일들
            'reports/html_report_generator.py',  # 개별 리포트 생성기
            
            # 테스트 파일들 (통합 리포트 테스트로 대체됨)
            'test_report_generator.py',
            'simple_test_generator.py',
            'simple_notification_test.py',
            'notification_test_suite.py',
            'test_dooray_webhook.py',
            'investigate_dooray_buttons.py',
            
            # 히스토리컬 리포트 생성기 (통합 리포트 빌더로 대체됨)
            'historical_report_generator.py',
            
            # 상태 모니터링 (통합 시스템으로 대체됨)
            'status_monitor.py',
            'status_scheduler.py',
            'update_metadata.py',  # metadata_reset_manager로 대체됨
            
            # 기타 레거시 파일들
            'reports_index.json',  # 로컬 인덱스 (docs/reports_index.json 사용)
            'WatchHamster.log',    # 로그 파일
        ]
        
        # 삭제할 레거시 디렉토리들
        self.legacy_directories = [
            'cleanup_backup',  # 이전 정리 백업들
            'archive',         # 아카이브 파일들
            '.github',         # GitHub 설정 (메인에서 관리)
            'scripts',         # 개별 스크립트들
        ]
        
        # 백업 디렉토리들 (날짜별로 생성된 것들)
        self.backup_pattern_dirs = [
            'backup_before_reset_*'
        ]
    
    def clean_legacy_files(self) -> Dict[str, int]:
        """레거시 파일들 정리"""
        self.logger.info("🧹 레거시 파일 정리 시작...")
        
        results = {
            'files_removed': 0,
            'directories_removed': 0,
            'backup_dirs_removed': 0,
            'total_size_freed': 0,
            'errors': 0
        }
        
        # 1. 개별 파일들 삭제
        for file_path in self.legacy_files:
            full_path = self.monitoring_dir / file_path
            try:
                if full_path.exists():
                    if full_path.is_file():
                        size = full_path.stat().st_size
                        full_path.unlink()
                        results['files_removed'] += 1
                        results['total_size_freed'] += size
                        self.logger.info(f"🗑️ 파일 삭제: {file_path}")
                    else:
                        self.logger.warning(f"⚠️ 파일이 아님: {file_path}")
            except Exception as e:
                self.logger.error(f"❌ 파일 삭제 실패 {file_path}: {e}")
                results['errors'] += 1
        
        # 2. 레거시 디렉토리들 삭제
        for dir_path in self.legacy_directories:
            full_path = self.monitoring_dir / dir_path
            try:
                if full_path.exists() and full_path.is_dir():
                    shutil.rmtree(full_path)
                    results['directories_removed'] += 1
                    self.logger.info(f"📁 디렉토리 삭제: {dir_path}")
            except Exception as e:
                self.logger.error(f"❌ 디렉토리 삭제 실패 {dir_path}: {e}")
                results['errors'] += 1
        
        # 3. 백업 디렉토리들 삭제 (패턴 매칭)
        for pattern in self.backup_pattern_dirs:
            try:
                backup_dirs = list(self.monitoring_dir.glob(pattern))
                for backup_dir in backup_dirs:
                    if backup_dir.is_dir():
                        shutil.rmtree(backup_dir)
                        results['backup_dirs_removed'] += 1
                        self.logger.info(f"💾 백업 디렉토리 삭제: {backup_dir.name}")
            except Exception as e:
                self.logger.error(f"❌ 백업 디렉토리 삭제 실패 {pattern}: {e}")
                results['errors'] += 1
        
        # 결과 로깅
        self.log_cleanup_results(results)
        
        return results
    
    def create_cleanup_summary(self) -> str:
        """정리 작업 요약 생성"""
        summary = f"""
# POSCO 리포트 시스템 레거시 파일 정리 완료

## 정리 일시
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 정리된 파일 목록

### 비활성화된 모니터 스크립트
- exchange_monitor.py.disabled
- kospi_monitor.py.disabled  
- newyork_monitor.py.disabled
- master_news_monitor.py.disabled
- run_monitor.py.disabled

### 개별 리포트 생성 관련
- reports/html_report_generator.py

### 테스트 파일들
- test_report_generator.py
- simple_test_generator.py
- simple_notification_test.py
- notification_test_suite.py
- test_dooray_webhook.py
- investigate_dooray_buttons.py

### 기타 레거시 파일들
- historical_report_generator.py
- status_monitor.py
- status_scheduler.py
- update_metadata.py
- reports_index.json
- WatchHamster.log

### 정리된 디렉토리
- cleanup_backup/
- archive/
- .github/
- scripts/
- backup_before_reset_* (모든 백업 디렉토리)

## 현재 활성 파일들

### 통합 리포트 시스템
- integrated_report_scheduler.py (메인 스케줄러)
- reports/integrated_report_generator.py (통합 리포트 생성기)
- integrated_report_builder.py (날짜별 리포트 빌더)

### 시스템 관리
- metadata_reset_manager.py (메타데이터 관리)
- report_cleanup_manager.py (리포트 정리)
- legacy_system_disabler.py (레거시 시스템 비활성화)
- completion_notifier.py (완료 알림)

### 메인 실행 스크립트
- posco_report_system_reset.py (전체 시스템 재구축)

### 설정 및 유틸리티
- config.py (시스템 설정)
- base_monitor.py (기본 모니터 클래스)
- github_pages_deployer.py (GitHub Pages 배포)
- monitor_WatchHamster.py (워치햄스터 시스템)

### 문서
- INTEGRATED_REPORT_SYSTEM_GUIDE.md (사용자 가이드)
- REPORT_ACCESS_GUIDE.md (접근 가이드)

## 정리 완료
통합 리포트 시스템으로 완전 전환되었습니다.
        """.strip()
        
        return summary
    
    def save_cleanup_summary(self, summary: str):
        """정리 요약을 파일로 저장"""
        try:
            summary_file = self.monitoring_dir / 'LEGACY_CLEANUP_SUMMARY.md'
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            self.logger.info(f"📋 정리 요약 저장: {summary_file}")
        except Exception as e:
            self.logger.error(f"❌ 정리 요약 저장 실패: {e}")
    
    def log_cleanup_results(self, results: Dict[str, int]):
        """정리 결과 로깅"""
        self.logger.info("\n" + "="*60)
        self.logger.info("📋 레거시 파일 정리 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"🗑️ 삭제된 파일: {results['files_removed']}개")
        self.logger.info(f"📁 삭제된 디렉토리: {results['directories_removed']}개")
        self.logger.info(f"💾 삭제된 백업 디렉토리: {results['backup_dirs_removed']}개")
        self.logger.info(f"💽 확보된 용량: {results['total_size_freed']:,} bytes")
        
        if results['errors'] > 0:
            self.logger.warning(f"⚠️ 오류 발생: {results['errors']}건")
        else:
            self.logger.info("🎉 모든 정리 작업이 성공적으로 완료되었습니다!")

def main():
    """메인 실행 함수"""
    cleaner = LegacyFileCleaner()
    
    print("🧹 POSCO 리포트 시스템 레거시 파일 정리를 시작합니다...")
    print("⚠️ 이 작업은 더 이상 사용하지 않는 파일들을 영구 삭제합니다.")
    print()
    
    # 사용자 확인
    try:
        confirm = input("계속 진행하시겠습니까? (yes/no): ").lower().strip()
        if confirm not in ['yes', 'y']:
            print("❌ 작업이 취소되었습니다.")
            return False
    except KeyboardInterrupt:
        print("\n❌ 작업이 중단되었습니다.")
        return False
    
    # 레거시 파일 정리 실행
    results = cleaner.clean_legacy_files()
    
    # 정리 요약 생성 및 저장
    summary = cleaner.create_cleanup_summary()
    cleaner.save_cleanup_summary(summary)
    
    # 결과 반환
    if results['errors'] == 0:
        print("\n🎉 레거시 파일 정리가 성공적으로 완료되었습니다!")
        print(f"📊 총 {results['files_removed']}개 파일, {results['directories_removed']}개 디렉토리 정리")
        return True
    else:
        print(f"\n⚠️ 정리 중 {results['errors']}개 오류가 발생했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)