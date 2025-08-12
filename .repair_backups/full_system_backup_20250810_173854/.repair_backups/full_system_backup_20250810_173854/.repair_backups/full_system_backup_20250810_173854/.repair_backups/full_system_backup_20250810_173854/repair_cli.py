#!/usr/bin/env python3
"""
POSCO 시스템 수리 CLI 도구
Command Line Interface for POSCO System Repair

이 CLI 도구는 POSCO 시스템의 자동화된 수리 기능을 쉽게 사용할 수 있게 해줍니다.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

from automated_repair_system import AutomatedRepairSystem


def print_banner():
    """배너 출력"""
    print("""
🔧 POSCO 시스템 자동화된 수리 도구 CLI v1.0
================================================
Python 구문 오류, Import 문제, 파일 참조 오류를 자동으로 수정합니다.
""")


def diagnose_command(args):
    """진단 명령 실행"""
    print("🔍 POSCO 시스템 진단을 시작합니다...")
    
    repair_system = AutomatedRepairSystem()
    results = repair_system.run_full_diagnosis()
    
    # 결과 출력
    print("\n📊 진단 결과:")
    print(f"  구문 오류: {len(results['syntax_errors'])}개")
    print(f"  Import 문제: {len(results['import_problems'])}개")
    print(f"  깨진 파일 참조: {len(results['broken_references'])}개")
    
    if args.detailed:
        print("\n📝 상세 결과:")
        
        if results['syntax_errors']:
            print("\n  구문 오류 상세:")
            for error in results['syntax_errors'][:10]:  # 최대 10개만 표시
                print(f"    - {error['file_path']}:{error['line_number']} - {error['error_message']}")
            if len(results['syntax_errors']) > 10:
                print(f"    ... 및 {len(results['syntax_errors']) - 10}개 더")
        
        if results['import_problems']:
            print("\n  Import 문제 상세:")
            for problem in results['import_problems'][:10]:
                print(f"    - {problem}")
            if len(results['import_problems']) > 10:
                print(f"    ... 및 {len(results['import_problems']) - 10}개 더")
        
        if results['broken_references']:
            print("\n  깨진 파일 참조 상세:")
            for ref in results['broken_references'][:10]:
                print(f"    - {ref['source_file']}:{ref['line_number']} - {ref['referenced_path']}")
            if len(results['broken_references']) > 10:
                print(f"    ... 및 {len(results['broken_references']) - 10}개 더")
    
    if args.save_report:
        report_file = f"diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 상세 보고서가 저장되었습니다: {report_file}")
    
    print(f"\n✅ 진단 완료! 백업이 생성되었습니다: {results['backup_created']}")


def repair_command(args):
    """수리 명령 실행"""
    print("🔧 POSCO 시스템 자동 수리를 시작합니다...")
    
    if not args.force:
        response = input("⚠️  이 작업은 파일을 수정합니다. 계속하시겠습니까? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("수리 작업이 취소되었습니다.")
            return
    
    repair_system = AutomatedRepairSystem()
    
    # 진단 먼저 실행
    if not args.skip_diagnosis:
        print("1️⃣ 진단 실행 중...")
        diagnosis_results = repair_system.run_full_diagnosis()
        
        total_issues = (len(diagnosis_results['syntax_errors']) + 
                       len(diagnosis_results['import_problems']) + 
                       len(diagnosis_results['broken_references']))
        
        if total_issues == 0:
            print("✅ 문제가 발견되지 않았습니다. 수리가 필요하지 않습니다.")
            return
        
        print(f"   발견된 문제: {total_issues}개")
    
    # 수리 실행
    print("2️⃣ 자동 수리 실행 중...")
    repair_results = repair_system.run_automated_repair()
    
    # 검증 실행
    print("3️⃣ 수리 결과 검증 중...")
    verification_results = repair_system.verify_repairs()
    
    # 결과 출력
    print("\n📊 수리 결과:")
    print(f"  처리된 파일: {repair_results['total_files_processed']}개")
    print(f"  성공한 수리: {repair_results['successful_repairs']}개")
    print(f"  실패한 수리: {repair_results['failed_repairs']}개")
    print(f"  전체 성공률: {verification_results['overall_success_rate']:.1f}%")
    
    if verification_results['overall_success_rate'] >= 95:
        print("\n🎉 수리 목표 달성! (95% 이상)")
    else:
        print(f"\n⚠️  추가 수리가 필요할 수 있습니다.")
    
    if args.save_report:
        report_file = f"repair_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        combined_results = {
            "repair_results": repair_results,
            "verification_results": verification_results
        }
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(combined_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 수리 보고서가 저장되었습니다: {report_file}")


def verify_command(args):
    """검증 명령 실행"""
    print("✅ POSCO 시스템 검증을 시작합니다...")
    
    repair_system = AutomatedRepairSystem()
    results = repair_system.verify_repairs()
    
    print("\n📊 검증 결과:")
    print(f"  남은 구문 오류: {results['syntax_verification']['remaining_errors']}개")
    print(f"  남은 Import 문제: {results['import_verification']['remaining_problems']}개")
    print(f"  전체 성공률: {results['overall_success_rate']:.1f}%")
    
    if results['overall_success_rate'] >= 95:
        print("\n🎉 시스템이 정상 상태입니다!")
    elif results['overall_success_rate'] >= 80:
        print("\n👍 시스템이 양호한 상태입니다.")
    else:
        print("\n⚠️  시스템에 문제가 있습니다. 수리를 권장합니다.")
    
    if args.detailed:
        if results['syntax_verification']['errors']:
            print("\n📝 남은 구문 오류:")
            for error in results['syntax_verification']['errors'][:5]:
                print(f"  - {error['file_path']}:{error['line_number']} - {error['error_message']}")
        
        if results['import_verification']['problems']:
            print("\n📦 남은 Import 문제:")
            for problem in results['import_verification']['problems'][:5]:
                print(f"  - {problem}")


def rollback_command(args):
    """롤백 명령 실행"""
    print(f"🔄 파일 롤백을 시작합니다: {args.file}")
    
    repair_system = AutomatedRepairSystem()
    success = repair_system.rollback_changes(args.file)
    
    if success:
        print(f"✅ 파일이 성공적으로 롤백되었습니다: {args.file}")
    else:
        print(f"❌ 파일 롤백에 실패했습니다: {args.file}")
        print("   백업 파일이 존재하지 않거나 접근할 수 없습니다.")


def status_command(args):
    """상태 명령 실행"""
    print("📊 POSCO 시스템 상태 확인 중...")
    
    # 기본 파일 존재 확인
    important_files = [
        "POSCO_News_250808.py",
        "WatchHamster_v3.0_Complete_Guide.md",
        "naming_convention_manager.py",
        "file_renaming_system.py"
    ]
    
    print("\n📁 중요 파일 상태:")
    for file_name in important_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            # 유사한 파일 찾기
            similar_files = list(Path(".").glob(f"**/*{file_name.split('.')[0]}*"))
            if similar_files:
                print(f"  ⚠️  {file_name} (유사 파일: {similar_files[0].name})")
            else:
                print(f"  ❌ {file_name}")
    
    # Python 파일 구문 검사
    python_files = list(Path(".").glob("**/*.py"))
    python_files = [f for f in python_files if not any(exclude in str(f) for exclude in [".git", "__pycache__", ".backup"])]
    
    syntax_errors = 0
    for py_file in python_files[:20]:  # 최대 20개 파일만 검사
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(py_file), 'exec')
        except SyntaxError:
            syntax_errors += 1
        except:
            pass
    
    print(f"\n🐍 Python 파일 상태:")
    print(f"  전체 파일: {len(python_files)}개")
    print(f"  구문 오류 (샘플): {syntax_errors}개")
    
    if syntax_errors == 0:
        print("  ✅ 샘플 파일들이 정상입니다")
    else:
        print("  ⚠️  일부 파일에 구문 오류가 있습니다")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="POSCO 시스템 자동화된 수리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s diagnose                    # 시스템 진단
  %(prog)s diagnose --detailed         # 상세 진단
  %(prog)s repair                      # 자동 수리 실행
  %(prog)s repair --force              # 확인 없이 수리 실행
  %(prog)s verify                      # 시스템 검증
  %(prog)s rollback file.py            # 특정 파일 롤백
  %(prog)s status                      # 시스템 상태 확인
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령')
    
    # diagnose 명령
    diagnose_parser = subparsers.add_parser('diagnose', help='시스템 진단')
    diagnose_parser.add_argument('--detailed', action='store_true', help='상세 결과 표시')
    diagnose_parser.add_argument('--save-report', action='store_true', help='보고서 파일 저장')
    
    # repair 명령
    repair_parser = subparsers.add_parser('repair', help='자동 수리 실행')
    repair_parser.add_argument('--force', action='store_true', help='확인 없이 실행')
    repair_parser.add_argument('--skip-diagnosis', action='store_true', help='진단 단계 건너뛰기')
    repair_parser.add_argument('--save-report', action='store_true', help='보고서 파일 저장')
    
    # verify 명령
    verify_parser = subparsers.add_parser('verify', help='시스템 검증')
    verify_parser.add_argument('--detailed', action='store_true', help='상세 결과 표시')
    
    # rollback 명령
    rollback_parser = subparsers.add_parser('rollback', help='파일 롤백')
    rollback_parser.add_argument('file', help='롤백할 파일 경로')
    
    # status 명령
    status_parser = subparsers.add_parser('status', help='시스템 상태 확인')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    print_banner()
    
    try:
        if args.command == 'diagnose':
            diagnose_command(args)
        elif args.command == 'repair':
            repair_command(args)
        elif args.command == 'verify':
            verify_command(args)
        elif args.command == 'rollback':
            rollback_command(args)
        elif args.command == 'status':
            status_command(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()