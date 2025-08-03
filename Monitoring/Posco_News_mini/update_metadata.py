#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
리포트 메타데이터 업데이트 스크립트

기존 리포트들의 메타데이터를 일괄 업데이트하고
대시보드 데이터를 최신 상태로 유지합니다.

사용법:
    python update_metadata.py          # 전체 스캔 및 업데이트
    python update_metadata.py --stats  # 통계만 출력
    python update_metadata.py --clean  # 존재하지 않는 파일 정리

작성자: AI Assistant
최종 수정: 2025-08-02
"""

import argparse
import sys
from pathlib import Path

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from reports.metadata_manager import metadata_manager

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='리포트 메타데이터 관리')
    parser.add_argument('--stats', action='store_true', help='통계 정보만 출력')
    parser.add_argument('--clean', action='store_true', help='존재하지 않는 파일 정리')
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 출력')
    
    args = parser.parse_args()
    
    print("🔄 POSCO 리포트 메타데이터 관리 시스템")
    print("=" * 50)
    
    if args.stats:
        # 통계 정보만 출력
        show_statistics()
    elif args.clean:
        # 정리 작업
        clean_metadata()
    else:
        # 전체 업데이트
        update_all_metadata(args.verbose)

def show_statistics():
    """통계 정보 출력"""
    print("📊 현재 리포트 통계")
    print("-" * 30)
    
    stats = metadata_manager.get_report_stats()
    
    print(f"총 리포트 수: {stats.get('total_reports', 0)}개")
    print(f"마지막 업데이트: {stats.get('last_update', 'N/A')}")
    
    print("\n📈 타입별 분포:")
    type_dist = stats.get('type_distribution', {})
    for report_type, count in type_dist.items():
        type_name = get_type_display_name(report_type)
        print(f"  - {type_name}: {count}개")
    
    print("\n📋 최근 리포트 (5개):")
    recent_reports = stats.get('recent_reports', [])
    for i, report in enumerate(recent_reports, 1):
        print(f"  {i}. {report.get('title', 'N/A')} ({report.get('date', 'N/A')})")

def get_type_display_name(report_type):
    """리포트 타입 표시명 반환"""
    type_names = {
        'integrated': '통합리포트',
        'exchange-rate': '서환마감',
        'kospi-close': '증시마감',
        'newyork-market-watch': '뉴욕마켓워치'
    }
    return type_names.get(report_type, report_type)

def clean_metadata():
    """존재하지 않는 파일의 메타데이터 정리"""
    print("🧹 메타데이터 정리 작업 시작")
    print("-" * 30)
    
    try:
        metadata = metadata_manager._load_metadata()
        reports_dir = metadata_manager.reports_dir
        
        removed_count = 0
        valid_reports = []
        
        for report in metadata['reports']:
            filename = report.get('filename', '')
            file_path = reports_dir / filename
            
            if file_path.exists():
                valid_reports.append(report)
            else:
                print(f"❌ 파일 없음: {filename}")
                removed_count += 1
        
        if removed_count > 0:
            metadata['reports'] = valid_reports
            metadata['totalReports'] = len(valid_reports)
            metadata_manager._save_metadata(metadata)
            print(f"✅ {removed_count}개의 무효한 메타데이터를 제거했습니다.")
        else:
            print("✅ 모든 메타데이터가 유효합니다.")
            
    except Exception as e:
        print(f"❌ 정리 작업 실패: {e}")

def update_all_metadata(verbose=False):
    """전체 메타데이터 업데이트"""
    print("🔄 전체 메타데이터 업데이트 시작")
    print("-" * 30)
    
    try:
        # 기존 통계
        old_stats = metadata_manager.get_report_stats()
        old_count = old_stats.get('total_reports', 0)
        
        # 전체 스캔 및 업데이트
        updated_count = metadata_manager.scan_and_update_all()
        
        # 새로운 통계
        new_stats = metadata_manager.get_report_stats()
        new_count = new_stats.get('total_reports', 0)
        
        print(f"✅ 업데이트 완료!")
        print(f"   - 처리된 파일: {updated_count}개")
        print(f"   - 이전 리포트 수: {old_count}개")
        print(f"   - 현재 리포트 수: {new_count}개")
        print(f"   - 신규 추가: {max(0, new_count - old_count)}개")
        
        if verbose:
            print("\n📊 상세 통계:")
            show_statistics()
            
    except Exception as e:
        print(f"❌ 업데이트 실패: {e}")
        sys.exit(1)

def check_system_health():
    """시스템 상태 체크"""
    print("🔍 시스템 상태 체크")
    print("-" * 30)
    
    issues = []
    
    # 필수 디렉토리 체크
    required_dirs = [
        metadata_manager.reports_dir,
        metadata_manager.docs_dir
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            issues.append(f"필수 디렉토리 없음: {dir_path}")
    
    # 필수 파일 체크
    required_files = [
        metadata_manager.metadata_file,
        metadata_manager.status_file
    ]
    
    for file_path in required_files:
        if not file_path.exists():
            issues.append(f"필수 파일 없음: {file_path}")
    
    if issues:
        print("❌ 발견된 문제:")
        for issue in issues:
            print(f"   - {issue}")
        
        print("\n🔧 자동 복구 시도...")
        try:
            metadata_manager._ensure_metadata_files()
            print("✅ 복구 완료")
        except Exception as e:
            print(f"❌ 복구 실패: {e}")
    else:
        print("✅ 시스템 상태 양호")

if __name__ == "__main__":
    try:
        # 시스템 상태 체크
        check_system_health()
        print()
        
        # 메인 실행
        main()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)