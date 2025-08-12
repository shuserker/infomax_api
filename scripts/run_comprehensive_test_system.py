#!/usr/bin/env python3
"""
POSCO 시스템 종합 테스트 실행기
Comprehensive Test System Runner for POSCO System

이 스크립트는 종합 테스트 시스템을 실행하고 결과를 분석합니다.
"""

import sys
import json
import argparse
from pathlib import Path
from comprehensive_test_system import (
    ComprehensiveTestSystem,
    SyntaxVerificationSystem,
    ModuleImportTestSystem,
    FileReferenceIntegritySystem,
    PerformanceMonitoringSystem
)

def load_config(config_file: str = "comprehensive_test_config.json") -> dict:
    """설정 파일을 로드"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  설정 파일을 찾을 수 없습니다: {config_file}")
        print("기본 설정을 사용합니다.")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ 설정 파일 파싱 오류: {e}")
        sys.exit(1)

def run_syntax_test_only():
    """구문 검증 테스트만 실행"""
    print("📝 구문 검증 테스트 실행...")
    
    syntax_system = SyntaxVerificationSystem()
    syntax_system.discover_python_files()
    
    print(f"발견된 Python 파일: {len(syntax_system.python_files)}개")
    
    results = syntax_system.verify_all_files()
    report = syntax_system.generate_syntax_report()
    
    print(f"\n📊 구문 검증 결과:")
    print(f"  총 파일: {report['summary']['total_files']}")
    print(f"  성공: {report['summary']['successful_files']}")
    print(f"  실패: {report['summary']['failed_files']}")
    print(f"  성공률: {report['summary']['success_rate']:.1f}%")
    
    if report['summary']['failed_files'] > 0:
        print(f"\n❌ 실패한 파일들:")
        for failed_file in report['failed_files'][:10]:  # 최대 10개만 표시
            print(f"  - {failed_file['file']}: {failed_file['error']}")
        
        if len(report['failed_files']) > 10:
            print(f"  ... 및 {len(report['failed_files']) - 10}개 더")
    
    return report

def run_import_test_only():
    """모듈 Import 테스트만 실행"""
    print("📦 모듈 Import 테스트 실행...")
    
    import_system = ModuleImportTestSystem()
    results = import_system.test_all_core_modules()
    report = import_system.generate_import_report()
    
    print(f"\n📊 Import 테스트 결과:")
    print(f"  총 모듈: {report['summary']['total_modules']}")
    print(f"  성공: {report['summary']['successful_imports']}")
    print(f"  실패: {report['summary']['failed_imports']}")
    print(f"  성공률: {report['summary']['success_rate']:.1f}%")
    
    if report['summary']['failed_imports'] > 0:
        print(f"\n❌ 실패한 모듈들:")
        for failed_module in report['failed_modules']:
            print(f"  - {failed_module['module']}: {failed_module['error']}")
    
    return report

def run_reference_test_only():
    """파일 참조 무결성 테스트만 실행"""
    print("🔗 파일 참조 무결성 테스트 실행...")
    
    reference_system = FileReferenceIntegritySystem()
    references = reference_system.scan_file_references()
    
    print(f"발견된 파일 참조: {len(references)}개")
    
    results = reference_system.verify_all_references()
    report = reference_system.generate_integrity_report()
    
    print(f"\n📊 참조 무결성 결과:")
    print(f"  총 참조: {report['summary']['total_references']}")
    print(f"  유효: {report['summary']['valid_references']}")
    print(f"  깨짐: {report['summary']['broken_references']}")
    print(f"  무결성률: {report['summary']['integrity_rate']:.1f}%")
    
    if report['summary']['broken_references'] > 0:
        print(f"\n❌ 깨진 참조들:")
        for broken_ref in report['broken_references'][:10]:  # 최대 10개만 표시
            print(f"  - {broken_ref['source']} → {broken_ref['reference']}: {broken_ref['error']}")
        
        if len(report['broken_references']) > 10:
            print(f"  ... 및 {len(report['broken_references']) - 10}개 더")
    
    return report

def run_performance_test_only():
    """성능 모니터링 테스트만 실행"""
    print("⚡ 성능 모니터링 테스트 실행...")
    
    performance_system = PerformanceMonitoringSystem()
    
    # 샘플 테스트 함수들
    def cpu_intensive_test():
        """CPU 집약적 테스트"""
        result = 0
        for i in range(1000000):
            result += i * i
        return result
    
    def memory_intensive_test():
        """메모리 집약적 테스트"""
        data = []
        for i in range(100000):
            data.append(f"test_data_{i}" * 10)
        return len(data)
    
    def io_intensive_test():
        """I/O 집약적 테스트"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for i in range(10000):
                f.write(f"line {i}\n")
            temp_file = f.name
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        os.unlink(temp_file)
        return len(lines)
    
    # 각 테스트 실행
    tests = [
        (cpu_intensive_test, "CPU 집약적 테스트"),
        (memory_intensive_test, "메모리 집약적 테스트"),
        (io_intensive_test, "I/O 집약적 테스트")
    ]
    
    for test_func, test_name in tests:
        print(f"  실행 중: {test_name}...")
        result = performance_system.run_performance_test(test_func, test_name)
        print(f"    CPU: {result.cpu_usage:.1f}%, 메모리: {result.memory_usage:.1f}%, "
              f"시간: {result.execution_time:.2f}초")
    
    report = performance_system.generate_performance_report()
    
    print(f"\n📊 성능 테스트 결과:")
    print(f"  총 테스트: {report['summary']['total_tests']}")
    print(f"  성공: {report['summary']['successful_tests']}")
    print(f"  평균 CPU: {report['summary']['average_cpu_usage']:.1f}%")
    print(f"  평균 메모리: {report['summary']['average_memory_usage']:.1f}%")
    print(f"  총 실행 시간: {report['summary']['total_execution_time']:.2f}초")
    
    return report

def analyze_test_results(report: dict):
    """테스트 결과를 분석하고 권장사항 제공"""
    print("\n🔍 테스트 결과 분석:")
    print("=" * 50)
    
    issues = []
    recommendations = []
    
    # 구문 검증 분석
    if 'syntax_verification' in report['detailed_results']:
        syntax_data = report['detailed_results']['syntax_verification']
        if 'summary' in syntax_data:
            success_rate = syntax_data['summary']['success_rate']
            if success_rate < 100:
                issues.append(f"구문 오류: {syntax_data['summary']['failed_files']}개 파일에 문제")
                recommendations.append("aggressive_syntax_repair.py 또는 final_syntax_repair.py 실행 권장")
    
    # 모듈 Import 분석
    if 'module_import' in report['detailed_results']:
        import_data = report['detailed_results']['module_import']
        if 'summary' in import_data:
            success_rate = import_data['summary']['success_rate']
            if success_rate < 100:
                issues.append(f"Import 오류: {import_data['summary']['failed_imports']}개 모듈 실패")
                recommendations.append("모듈 의존성 문제 해결 필요")
    
    # 파일 참조 분석
    if 'file_reference_integrity' in report['detailed_results']:
        integrity_data = report['detailed_results']['file_reference_integrity']
        if 'summary' in integrity_data:
            integrity_rate = integrity_data['summary']['integrity_rate']
            if integrity_rate < 95:
                issues.append(f"파일 참조 문제: {integrity_data['summary']['broken_references']}개 깨진 참조")
                recommendations.append("comprehensive_file_reference_repairer.py 실행 권장")
    
    # 성능 분석
    if 'performance_monitoring' in report['detailed_results']:
        perf_data = report['detailed_results']['performance_monitoring']
        if 'summary' in perf_data:
            avg_cpu = perf_data['summary']['average_cpu_usage']
            avg_memory = perf_data['summary']['average_memory_usage']
            
            if avg_cpu > 80:
                issues.append(f"높은 CPU 사용률: {avg_cpu:.1f}%")
                recommendations.append("CPU 집약적 작업 최적화 필요")
            
            if avg_memory > 80:
                issues.append(f"높은 메모리 사용률: {avg_memory:.1f}%")
                recommendations.append("메모리 사용량 최적화 필요")
    
    # 결과 출력
    if issues:
        print("⚠️  발견된 문제점들:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("✅ 모든 테스트가 정상적으로 통과했습니다!")
    
    if recommendations:
        print("\n💡 권장사항:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # 전체 시스템 상태 평가
    overall_health = "양호"
    if len(issues) > 3:
        overall_health = "심각"
    elif len(issues) > 1:
        overall_health = "주의"
    
    print(f"\n🎯 전체 시스템 상태: {overall_health}")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="POSCO 시스템 종합 테스트 실행기")
    parser.add_argument("--test", choices=['all', 'syntax', 'import', 'reference', 'performance'],
                       default='all', help="실행할 테스트 유형")
    parser.add_argument("--config", default="comprehensive_test_config.json",
                       help="설정 파일 경로")
    parser.add_argument("--output", help="결과 저장 파일명")
    parser.add_argument("--no-performance", action="store_true",
                       help="성능 테스트 제외")
    parser.add_argument("--analyze", action="store_true",
                       help="결과 분석 및 권장사항 제공")
    
    args = parser.parse_args()
    
    print("🔧 POSCO 시스템 종합 테스트 실행기")
    print("=" * 50)
    
    # 설정 로드
    config = load_config(args.config)
    
    report = None
    
    if args.test == 'syntax':
        report = {"detailed_results": {"syntax_verification": run_syntax_test_only()}}
    elif args.test == 'import':
        report = {"detailed_results": {"module_import": run_import_test_only()}}
    elif args.test == 'reference':
        report = {"detailed_results": {"file_reference_integrity": run_reference_test_only()}}
    elif args.test == 'performance':
        report = {"detailed_results": {"performance_monitoring": run_performance_test_only()}}
    else:  # all
        test_system = ComprehensiveTestSystem()
        include_perf = not args.no_performance
        report = test_system.run_all_tests(include_performance=include_perf)
        
        if args.output:
            saved_file = test_system.save_report(report, args.output)
            print(f"\n💾 보고서 저장됨: {saved_file}")
    
    # 결과 분석
    if args.analyze and report:
        analyze_test_results(report)
    
    print("\n✨ 테스트 실행 완료!")

if __name__ == "__main__":
    main()