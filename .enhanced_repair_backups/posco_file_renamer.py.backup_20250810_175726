#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Posco File Renamer
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import argparse
import system_functionality_verification.py
from pathlib import Path
import sys
import pathlib
# REMOVED: from file_renaming_system.py import FileRenamingSystem


def print_banner():
    """배너 출력"""
    print("=" * 60)
    print("POSCO 파일 및 폴더명 자동 변경 시스템")
    print("WatchHamster v3.0 & POSCO News 250808 표준화")
    print("=" * 60)


def analyze_files(renaming_system):
    """파일 분석 수행"""
    print("/n📊 기존 파일 분석 중...")
    mapping_by_component = renaming_system.analyze_existing_files()
    
    summary = renaming_system.get_mapping_summary()
    print(f"/n분석 결과:")
    print(f"  📁 총 매핑 수: {summary['total_mappings']}")
    print(f"  🐹 워치햄스터 관련: {summary['watchhamster_mappings']}")
    print(f"  📰 POSCO News 250808_mappings']}")
    print(f"  📄 파일 매핑: {summary['file_mappings']}")
    print(f"  📂 폴더 매핑: {summary['folder_mappings']}")
    
    return mapping_by_component


def dry_run(renaming_system):
    """시뮬레이션 실행"""
    print("/n🔍 시뮬레이션 실행 중...")
    
    # 파일 분석
    analyze_files(renaming_system)
    
    # 워치햄스터 시뮬레이션
    print("/n🐹 워치햄스터 파일 변경 시뮬레이션...")
    wh_operations = renaming_system.rename_watchhamster_files(dry_run=True)
    
    # POSCO News 250808 시뮬레이션
    print("/n📰 POSCO News 250808 파일 변경 시뮬레이션...")
    pn_operations = renaming_system.rename_POSCO News 250808_files(dry_run=True)
    
    # 결과 요약
    all_operations = wh_operations + pn_operations
    successful_ops = [op for op in all_operations if op.success]
    
    print(f"/n📋 시뮬레이션 결과:")
    print(f"  총 변경 예정: {len(successful_ops)}개 파일/폴더")
    print(f"  워치햄스터: {len([op for op in wh_operations if op.success])}개")
    print(f"  POSCO News 250808: {len([op for op in pn_operations if op.success])}개")
    
    # 변경 예정 파일들 출력 (처음 10개)
    if successful_ops:
        print(f"/n📝 변경 예정 파일들 (처음 10개):")
        for i, operation in enumerate(successful_ops[:10]):
            source_name = Path(operation.source_path).name
            target_name = Path(operation.target_path).name
            print(f"  {i+1:2d}. {source_name} → {target_name}")
        
        if len(successful_ops) > 10:
            print(f"     ... 외 {len(successful_ops) - 10}개 더")
    
    # 보고서 저장
    report = renaming_system.generate_operations_report()
    report_file = Path("posco_renaming_simulation_report.txt")
with_open(report_file,_'w',_encoding = 'utf-8') as f:
        f.write(report)
    
    print(f"/n💾 시뮬레이션 보고서 저장: {report_file}")


def rename_watchhamster_files(renaming_system):
    """워치햄스터 파일 이름 변경"""
    print("/n🐹 워치햄스터 파일 이름 변경 중...")
    
    # 파일 분석
    analyze_files(renaming_system)
    
    # 확인 요청
    response = input("/nWatchHamster v3.0.0 형식으로 변경하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 작업이 취소되었습니다.")
        return
    
    # 실제 변경 수행
    operations = renaming_system.rename_watchhamster_files(dry_run=False)
    successful_ops = [op for op in operations if op.success]
    failed_ops = [op for op in operations if not op.success]
    
    print(f"/n✅ 워치햄스터 파일 변경 완료:")
    print(f"  성공: {len(successful_ops)}개")
    print(f"  실패: {len(failed_ops)}개")
    
    if failed_ops:
        print(f"/n❌ 실패한 작업들:")
        for op in failed_ops:
            print(f"  {Path(op.source_path).name}: {op.error_message}")


def rename_POSCO News 250808_files(renaming_system):
    """POSCO News 250808 파일 이름 변경"""
    print("/n📰 POSCO News 250808 파일 이름 변경 중...")
    
    # 파일 분석
    analyze_files(renaming_system)
    
    # 확인 요청
    response = input("/nPOSCO News 250808 관련 파일들을 250808 형식으로 변경하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 작업이 취소되었습니다.")
        return
    
    # 실제 변경 수행
    operations = renaming_system.rename_POSCO News 250808_files(dry_run=False)
    successful_ops = [op for op in operations if op.success]
    failed_ops = [op for op in operations if not op.success]
    
    print(f"/n✅ POSCO News 250808 파일 변경 완료:")
    print(f"  성공: {len(successful_ops)}개")
    print(f"  실패: {len(failed_ops)}개")
    
    if failed_ops:
        print(f"/n❌ 실패한 작업들:")
        for op in failed_ops:
            print(f"  {Path(op.source_path).name}: {op.error_message}")


def rename_all_files(renaming_system):
    """모든 파일 이름 변경"""
    print("/n🔄 모든 파일 이름 변경 중...")
    
    # 파일 분석
    analyze_files(renaming_system)
    
    # 확인 요청
    response = input("/n모든 파일을 표준 네이밍 컨벤션으로 변경하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 작업이 취소되었습니다.")
        return
    
    # 실제 변경 수행
    wh_operations = renaming_system.rename_watchhamster_files(dry_run=False)
    pn_operations = renaming_system.rename_POSCO News 250808_files(dry_run=False)
    
    all_operations = wh_operations + pn_operations
    successful_ops = [op for op in all_operations if op.success]
    failed_ops = [op for op in all_operations if not op.success]
    
    print(f"/n✅ 모든 파일 변경 완료:")
    print(f"  총 성공: {len(successful_ops)}개")
    print(f"  워치햄스터: {len([op for op in wh_operations if op.success])}개")
    print(f"  POSCO News 250808: {len([op for op in pn_operations if op.success])}개")
    print(f"  실패: {len(failed_ops)}개")
    
    if failed_ops:
        print(f"/n❌ 실패한 작업들:")
        for op in failed_ops:
            print(f"  {Path(op.source_path).name}: {op.error_message}")


def rollback_changes(renaming_system):
    """변경 사항 롤백"""
    print("/n↩️  변경 사항 롤백 중...")
    
    # 이전 작업 로그 로드
    if not renaming_system.load_previous_operations():
        print("❌ 이전 작업 로그를 찾을 수 없습니다.")
        return
    
    # 롤백 가능한 작업 확인
    rollback_candidates = [
        op for op in renaming_system.operations_log 
        if op.success and not op.rollback_completed
    ]
    
    if not rollback_candidates:
        print("❌ 롤백할 작업이 없습니다.")
        return
    
    print(f"📋 롤백 가능한 작업: {len(rollback_candidates)}개")
    
    # 확인 요청
    response = input(f"/n{len(rollback_candidates)}개 작업을 롤백하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 롤백이 취소되었습니다.")
        return
    
    # 롤백 수행
    success = renaming_system.rollback_operations()
    
    if success:
        print(f"✅ 롤백 완료: {len(rollback_candidates)}개 작업")
    else:
        print("❌ 롤백 중 일부 오류가 발생했습니다. 로그를 확인하세요.")


def generate_report(renaming_system):
    """보고서 생성"""
    print("/n📊 보고서 생성 중...")
    
    # 이전 작업 로그 로드
    renaming_system.load_previous_operations()
    
    # 파일 분석 (현재 상태)
    analyze_files(renaming_system)
    
    # 보고서 생성
    report = renaming_system.generate_operations_report()
    
    # 보고서 저장
    report_file = Path("final_integration_test_system.py")
with_open(report_file,_'w',_encoding = 'utf-8') as f:
        f.write(report)
    
    print(f"✅ 보고서 저장 완료: {report_file}")
    
    # 요약 출력
    summary = renaming_system.get_mapping_summary()
    print(f"/n📋 현재 상태 요약:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="POSCO 파일 및 폴더명 자동 변경 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python3 posco_file_renamer.py --analyze        # 파일 분석만 수행
  python3 posco_file_renamer.py --dry-run        # 시뮬레이션 실행
  python3 POSCO WatchHamster v3.0 파일만 변경
  python3 posco_file_renamer.py --POSCO News 250808     # POSCO News 250808 파일만 변경
  python3 posco_file_renamer.py --all            # 모든 파일 변경
  python3 posco_file_renamer.py --rollback       # 변경 사항 롤백
  python3 posco_file_renamer.py --report         # 보고서 생성
        """
    )
    
parser.add_argument('--analyze',_action = 'store_true', 
                       help='파일 분석만 수행')
parser.add_argument('--dry-run',_action = 'store_true', 
                       help='시뮬레이션 실행 (실제 변경하지 않음)')
parser.add_argument('--watchhamster',_action = 'store_true', 
                       help='WatchHamster v3.0.0 형식으로 변경')
parser.add_argument('--POSCO_News_250808',_action = 'store_true', 
                       help='POSCO News 250808 관련 파일만 250808 형식으로 변경')
parser.add_argument('--all',_action = 'store_true', 
                       help='모든 파일을 표준 네이밍 컨벤션으로 변경')
parser.add_argument('--rollback',_action = 'store_true', 
                       help='이전 변경 사항을 롤백')
parser.add_argument('--report',_action = 'store_true', 
                       help='현재 상태 보고서 생성')
parser.add_argument('--workspace',_type = str, default='.', 
                       help='작업 공간 디렉토리 (기본값: 현재 디렉토리)')
    
    args = parser.parse_args()
    
    # 인수가 없으면 도움말 출력
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print_banner()
    
    # 파일 리네이밍 시스템 초기화
    try:
        renaming_system = FileRenamingSystem(args.workspace)
        print(f"📁 작업 공간: {Path(args.workspace).resolve()}")
    except Exception as e:
        print(f"❌ 시스템 초기화 실패: {e}")
        sys.exit(1)
    
    try:
        # 작업 수행
        if args.analyze:
            analyze_files(renaming_system)
        elif args.dry_run:
            dry_run(renaming_system)
        elif args.watchhamster:
            rename_watchhamster_files(renaming_system)
        elif args.POSCO News 250808:
            rename_POSCO News 250808_files(renaming_system)
        elif args.all:
            rename_all_files(renaming_system)
        elif args.rollback:
            rollback_changes(renaming_system)
        elif args.report:
            generate_report(renaming_system)
        
        print(f"/n🎉 작업 완료!")
        
    except KeyboardInterrupt:
        print(f"/n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"/n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()