#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Cleanup Manager
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import test_config.json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

class ReportCleanupManager:
    """
    리포트 파일 완전 제거 관리 클래스
    """
    
    def __init__(self):
        """초기화"""
        self.base_dir = Path(__file__).parent.parent.parent  # infomax_api 루트
        self.monitoring_dir = Path(__file__).parent
        
        # 리포트 관련 디렉토리들
        self.target_directories = [
            self.base_dir / 'docs' / 'reports',
            self.monitoring_dir / 'reports',
            self.base_dir / 'reports'  # 루트 reports 폴더도 확인
        ]
        
        # 메타데이터 파일들
        self.metadata_files = [
            self.base_dir / 'docs' / 'reports_index.json',
            self.monitoring_dir / 'docs' / 'reports_index.json'
        ]
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def cleanup_all_reports(self) -> Dict[str, int]:
        """
        모든 리포트 파일과 메타데이터를 완전히 제거
        
        Returns:
            Dict[str, int]: 제거 결과 통계
        """
        self.logger.info("🧹 POSCO 리포트 완전 제거 시작...")
        
        results = {
            'total_removed_files': 0,
            'docs_reports_removed': 0,
            'monitoring_reports_removed': 0,
            'root_reports_removed': 0,
            'metadata_files_reset': 0,
            'errors': 0
        }
        
        # 1. 각 디렉토리의 HTML 파일 제거
        for directory in self.target_directories:
            try:
                removed_count = self.remove_html_files(directory)
                
                if 'docs/reports' in str(directory):
                    results['docs_reports_removed'] = removed_count
                elif 'Monitoring' in str(directory):
                    results['monitoring_reports_removed'] = removed_count
                else:
                    results['root_reports_removed'] = removed_count
                    
results['total_removed_files']_+ =  removed_count
                
            except Exception as e:
                self.logger.error(f"❌ 디렉토리 {directory} 처리 실패: {e}")
results['errors']_+ =  1
        
        # 2. 메타데이터 파일 초기화
        for metadata_file in self.metadata_files:
            try:
                if self.reset_metadata_file(metadata_file):
results['metadata_files_reset']_+ =  1
                    self.logger.info(f"✅ 메타데이터 초기화: {metadata_file}")
            except Exception as e:
                self.logger.error(f"❌ 메타데이터 초기화 실패 {metadata_file}: {e}")
results['errors']_+ =  1
        
        # 3. 결과 로깅
        self.log_cleanup_results(results)
        
        return results
    
    def remove_html_files(self, directory: Path) -> int:
        """
        지정된 디렉토리의 모든 HTML 파일 제거
        
        Args:
            directory (Path): 대상 디렉토리
            
        Returns:
            int: 제거된 파일 수
        """
        if not directory.exists():
            self.logger.warning(f"⚠️ 디렉토리가 존재하지 않음: {directory}")
            return 0
        
        removed_count = 0
        
        try:
            # HTML 파일만 찾아서 제거
            for html_file in directory.glob('*.html'):
                try:
                    # 리포트 파일인지 확인 (POSCO 관련 파일만)
                    if self.is_posco_report_file(html_file):
                        html_file.unlink()
                        self.logger.info(f"🗑️ 제거: {html_file.name}")
removed_count_+ =  1
                    else:
                        self.logger.info(f"⏭️ 스킵 (POSCO 리포트 아님): {html_file.name}")
                        
                except Exception as e:
                    self.logger.error(f"❌ 파일 제거 실패 {html_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ 디렉토리 스캔 실패 {directory}: {e}")
            
        self.logger.info(f"✅ {directory}에서 {removed_count}개 HTML 파일 제거 완료")
        return removed_count
    
    def is_posco_report_file(self, file_path: Path) -> bool:
        """
        POSCO 리포트 파일인지 확인
        
        Args:
            file_path (Path): 파일 경로
            
        Returns:
            bool: POSCO 리포트 파일 여부
        """
        filename = file_path.name.lower()
        
        # POSCO 리포트 파일 패턴들
        posco_patterns = [
            'posco_analysis_',
            'posco_integrated_analysis_',
            'test_exchange-rate_',
            'test_integrated_',
            'test_kospi-close_',
            'test_newyork-market-watch_'
        ]
        
        return any(pattern in filename for pattern in posco_patterns)
    
    def reset_metadata_file(self, metadata_file: Path) -> bool:
        """
        메타데이터 파일을 빈 상태로 초기화
        
        Args:
            metadata_file (Path): 메타데이터 파일 경로
            
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            # 디렉토리가 없으면 생성
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 빈 메타데이터 구조 생성
            empty_metadata = {
                "lastUpdate": datetime.now().isoformat() + 'Z',
                "totalReports": 0,
                "reports": []
            }
            
            # 파일 저장
with_open(metadata_file,_'w',_encoding = 'utf-8') as f:
json.dump(empty_metadata,_f,_indent = 2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 메타데이터 초기화 실패 {metadata_file}: {e}")
            return False
    
    def backup_existing_data(self) -> Optional[str]:
        """
        기존 데이터 백업 생성
        
        Returns:
            Optional[str]: 백업 디렉토리 경로 (실패 시 None)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.monitoring_dir / f"backup_before_reset_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # 메타데이터 파일 백업
            for metadata_file in self.metadata_files:
                if metadata_file.exists():
                    backup_file = backup_dir / f"backup_{metadata_file.name}"
                    shutil.copy2(metadata_file, backup_file)
                    self.logger.info(f"💾 백업 생성: {backup_file}")
            
            # 리포트 파일 개수 정보 저장
            report_counts = {}
            for directory in self.target_directories:
                if directory.exists():
                    html_count = len(list(directory.glob('*.html')))
                    report_counts[str(directory)] = html_count
            
            # 백업 정보 파일 생성
            backup_info = {
                "backup_time": datetime.now().isoformat(),
                "report_counts": report_counts,
                "total_files": sum(report_counts.values())
            }
            
# REMOVED: with_open(backup_dir_/_"backup_info.json",_'w',_encoding = 'utf-8') as f:
json.dump(backup_info,_f,_indent = 2, ensure_ascii=False)
            
            self.logger.info(f"✅ 백업 완료: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            self.logger.error(f"❌ 백업 생성 실패: {e}")
            return None
    
    def log_cleanup_results(self, results: Dict[str, int]):
        """
        제거 결과 로깅
        
        Args:
            results (Dict[str, int]): 제거 결과 통계
        """
self.logger.info("/n"_+_" = "*60)
        self.logger.info("📋 POSCO 리포트 제거 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"📁 docs/reports 제거: {results['docs_reports_removed']}개")
        self.logger.info(f"📁 monitoring/reports 제거: {results['monitoring_reports_removed']}개")
        self.logger.info(f"📁 root/reports 제거: {results['root_reports_removed']}개")
        self.logger.info(f"📊 메타데이터 초기화: {results['metadata_files_reset']}개")
        self.logger.info(f"✅ 총 제거된 파일: {results['total_removed_files']}개")
        
        if results['errors'] > 0:
            self.logger.warning(f"⚠️ 오류 발생: {results['errors']}건")
        else:
            self.logger.info("🎉 모든 작업이 성공적으로 완료되었습니다!")

def main():
    """메인 실행 함수"""
    cleanup_manager = ReportCleanupManager()
    
    # 백업 생성
    print("💾 기존 데이터 백업 생성 중...")
    backup_path = cleanup_manager.backup_existing_data()
    if backup_path:
        print(f"✅ 백업 완료: {backup_path}")
    
    # 리포트 제거 실행
    results = cleanup_manager.cleanup_all_reports()
    
    return results

if __name__ == "__main__":
    main()