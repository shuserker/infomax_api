#!/usr/bin/env python3
"""
Enhanced POSCO 시스템 수리 CLI 도구
Enhanced Command Line Interface for POSCO System Repair

향상된 자동화된 수리 기능을 위한 CLI 도구입니다.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

from enhanced_automated_repair_system import EnhancedAutomatedRepairSystem


def print_banner():
    """배너 출력"""
    print("""
🔧 Enhanced POSCO 시스템 자동화된 수리 도구 CLI v2.0
====================================================
향상된 Python 구문 오류, Import 문제, 파일 참조 오류 자동 수정
""")


def analyze_command(args):
    """분석 명령 실행"""
    print("🔍 POSCO 시스템 분석을 시작합니다...")
    
    repair_system = EnhancedAutomatedRepairSystem()
    results = repair_system.analyze_system()
    
    # 결과 출력
    print("\n📊 분석 결과:")
    print(f"  전체 Python 파일: {results['python_files']}개")
    print(f"  문제 발견 파일: {results['files_with_issues']}개")
    print(f"  발견된 수리 작업: {len(results['repair_tasks'])}개")
    print(f"  예상 수리 시간: {results['estimated_repair_time']}초")
    
    if args.detailed and results['repair_tasks']:
        print("\n📝 발견된 문제 상세:")
        
        # 문제 유형별 분류
        issues_by_type = {}
        for task in results['repair_tasks']:
            task_type = task['task_type']
            if task_type not in issues_by_type:
                issues_by_type[task_type] = []
            issues_by_type[task_type].append(task)
        
        for task_type, tasks in issues_by_type.items():
            print(f"\n  {task_type.upper()} 문제: {len(tasks)}개")
            for task in tasks[:5]:  # 최대 5개만 표시
                print(f"    - {task['description']}")
            if len(tasks) > 5:
                print(f"    ... 및 {len(tasks) - 5}개 더")
    
    if args.save_report:
        report_file = f"enhanced_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 상세 보고서가 저장되었습니다: {report_file}")
    
    print(f"\n✅ 분석 완료!")


def repair_command(args):
    """수리 명령 실행"""
    print("🔧 Enhanced POSCO 시스템 자동 수리를 시작합니다...")
    
    if not args.force:
        response = input("⚠️  이 작업은 파일을 수정합니다. 계속하시겠습니까? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("수리 작업이 취소되었습니다.")
            return
    
    repair_system = EnhancedAutomatedRepairSystem()
    
    # 분석 먼저 실행
    if not args.skip_analysis:
        print("1️⃣ 시스템 분석 중...")
        analysis_results = repair_system.analyze_system()
        
        if len(repair_system.repair_tasks) == 0:
            print("✅ 수리가 필요한 문제가 발견되지 않았습니다.")
            return
        
        print(f"   발견된 문제: {len(repair_system.repair_tasks)}개")
    
    # 수리 실행
    max_files = args.max_files if args.max_files else 20
    print(f"2️⃣ 자동 수리 실행 중 (최대 {max_files}개 파일)...")
    repair_results = repair_system.execute_repairs(max_files=max_files)
    
    # 검증 실행
    print("3️⃣ 수리 결과 검증 중...")
    verification_results = repair_system.verify_repairs()
    
    # 결과 출력
    print("\n📊 수리 결과:")
    print(f"  실행된 작업: {repair_results['executed_tasks']}개")
    print(f"  성공한 수리: {repair_results['successful_tasks']}개")
    print(f"  실패한 수리: {repair_results['failed_tasks']}개")
    print(f"  실행 시간: {repair_results['total_execution_time']:.1f}초")
    print(f"  검증 성공률: {verification_results['overall_success_rate']:.1f}%")
    
    if verification_results['overall_success_rate'] >= 90:
        print("\n🎉 수리 목표 달성! (90% 이상)")
    elif verification_results['overall_success_rate'] >= 70:
        print("\n👍 양호한 수리 결과입니다.")
    else:
        print(f"\n⚠️  추가 수리가 필요할 수 있습니다.")
    
    if args.save_report:
        report_file = f"enhanced_repair_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    repair_system = EnhancedAutomatedRepairSystem()
    
    # 간단한 분석으로 현재 상태 확인
    analysis_results = repair_system.analyze_system()
    verification_results = repair_system.verify_repairs()
    
    print("\n📊 시스템 상태:")
    print(f"  전체 Python 파일: {analysis_results['python_files']}개")
    print(f"  문제 발견 파일: {analysis_results['files_with_issues']}개")
    print(f"  구문 오류: {verification_results['syntax_errors']}개")
    print(f"  Import 문제: {verification_results['import_errors']}개")
    
    if analysis_results['files_with_issues'] == 0:
        print("\n🎉 시스템이 정상 상태입니다!")
    elif analysis_results['files_with_issues'] <= 5:
        print("\n👍 시스템이 양호한 상태입니다.")
    else:
        print("\n⚠️  시스템에 문제가 있습니다. 수리를 권장합니다.")
    
    if args.detailed and verification_results['details']:
        print("\n📝 발견된 문제 상세:")
        for detail in verification_results['details'][:10]:
            print(f"  - {detail['file']}")
            for issue in detail['issues']:
                print(f"    • {issue}")


def status_command(args):
    """상태 명령 실행"""
    print("📊 Enhanced POSCO 시스템 상태 확인 중...")
    
    # 기본 파일 존재 확인
    important_files = [
        "POSCO_News_250808.py",
        "WatchHamster_v3_v3_0_Complete_Guide.md",
        "naming_convention_manager.py",
        "file_renaming_system.py",
        "automated_repair_system.py",
        "enhanced_automated_repair_system.py"
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
    
    # 빠른 구문 검사
    python_files = list(Path(".").glob("**/*.py"))
    python_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in [
            ".git", "__pycache__", ".backup", "backup_", 
            "full_system_backup", ".enhanced_repair_backups"
        ]
    )]
    
    syntax_errors = 0
    checked_files = 0
    
    for py_file in python_files[:30]:  # 최대 30개 파일만 검사
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(py_file), 'exec')
            checked_files += 1
        except SyntaxError:
            syntax_errors += 1
            checked_files += 1
        except:
            pass
    
    print(f"\n🐍 Python 파일 상태:")
    print(f"  전체 파일: {len(python_files)}개")
    print(f"  검사한 파일: {checked_files}개")
    print(f"  구문 오류 (샘플): {syntax_errors}개")
    
    if syntax_errors == 0:
        print("  ✅ 검사한 파일들이 정상입니다")
    elif syntax_errors <= 3:
        print("  ⚠️  일부 파일에 구문 오류가 있습니다")
    else:
        print("  ❌ 많은 파일에 구문 오류가 있습니다")
    
    # 백업 상태 확인
    backup_dirs = [".repair_backups", ".enhanced_repair_backups"]
    print(f"\n💾 백업 상태:")
    for backup_dir in backup_dirs:
        backup_path = Path(backup_dir)
        if backup_path.exists():
            backup_files = list(backup_path.glob("*"))
            print(f"  ✅ {backup_dir}: {len(backup_files)}개 백업")
        else:
            print(f"  ❌ {backup_dir}: 없음")


def clean_command(args):
    """정리 명령 실행"""
    print("🧹 시스템 정리를 시작합니다...")
    
    if not args.force:
        response = input("⚠️  이 작업은 백업 파일들을 삭제합니다. 계속하시겠습니까? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("정리 작업이 취소되었습니다.")
            return
    
    # 백업 디렉토리 정리
    backup_dirs = [".repair_backups", ".enhanced_repair_backups"]
    cleaned_files = 0
    
    for backup_dir in backup_dirs:
        backup_path = Path(backup_dir)
        if backup_path.exists():
            backup_files = list(backup_path.glob("*"))
            for backup_file in backup_files:
                try:
                    if backup_file.is_file():
                        backup_file.unlink()
                        cleaned_files += 1
                    elif backup_file.is_dir():
                        import shutil
                        shutil.rmtree(backup_file)
                        cleaned_files += 1
                except Exception as e:
                    print(f"정리 실패: {backup_file} - {e}")
    
    # 임시 결과 파일 정리
    temp_files = list(Path(".").glob("*repair_results_*.json"))
    temp_files.extend(list(Path(".").glob("*analysis_report_*.json")))
    temp_files.extend(list(Path(".").glob("diagnosis_results_*.json")))
    
    for temp_file in temp_files:
        try:
            temp_file.unlink()
            cleaned_files += 1
        except Exception as e:
            print(f"정리 실패: {temp_file} - {e}")
    
    print(f"✅ 정리 완료: {cleaned_files}개 파일 삭제")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Enhanced POSCO 시스템 자동화된 수리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s analyze                     # 시스템 분석
  %(prog)s analyze --detailed          # 상세 분석
  %(prog)s repair                      # 자동 수리 실행
  %(prog)s repair --max-files 30       # 최대 30개 파일 수리
  %(prog)s verify                      # 시스템 검증
  %(prog)s status                      # 시스템 상태 확인
  %(prog)s clean                       # 백업 파일 정리
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령')
    
    # analyze 명령
    analyze_parser = subparsers.add_parser('analyze', help='시스템 분석')
    analyze_parser.add_argument('--detailed', action='store_true', help='상세 결과 표시')
    analyze_parser.add_argument('--save-report', action='store_true', help='보고서 파일 저장')
    
    # repair 명령
    repair_parser = subparsers.add_parser('repair', help='자동 수리 실행')
    repair_parser.add_argument('--force', action='store_true', help='확인 없이 실행')
    repair_parser.add_argument('--skip-analysis', action='store_true', help='분석 단계 건너뛰기')
    repair_parser.add_argument('--max-files', type=int, help='최대 수리할 파일 수')
    repair_parser.add_argument('--save-report', action='store_true', help='보고서 파일 저장')
    
    # verify 명령
    verify_parser = subparsers.add_parser('verify', help='시스템 검증')
    verify_parser.add_argument('--detailed', action='store_true', help='상세 결과 표시')
    
    # status 명령
    status_parser = subparsers.add_parser('status', help='시스템 상태 확인')
    
    # clean 명령
    clean_parser = subparsers.add_parser('clean', help='백업 파일 정리')
    clean_parser.add_argument('--force', action='store_true', help='확인 없이 실행')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    print_banner()
    
    try:
        if args.command == 'analyze':
            analyze_command(args)
        elif args.command == 'repair':
            repair_command(args)
        elif args.command == 'verify':
            verify_command(args)
        elif args.command == 'status':
            status_command(args)
        elif args.command == 'clean':
            clean_command(args)
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