#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 안정성 검증 시스템
POSCO 프로덕션 구조 안정성 확인
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

class FinalStabilityVerification:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'stability_tests': {},
            'performance_metrics': {},
            'error_handling': {},
            'final_score': 0,
            'status': 'PENDING'
        }

    def test_module_imports(self):
        """모듈 import 안정성 테스트"""
        print("📦 모듈 import 안정성 테스트 중...")
        
        import_tests = {
            'watchhamster_core': [],
            'posco_core': [],
            'cross_imports': []
        }
        
        # 워치햄스터 핵심 모듈 import 테스트
        watchhamster_modules = [
            'Monitoring.WatchHamster_Project.core.watchhamster_monitor',
            'Monitoring.WatchHamster_Project.core.git_monitor',
            'Monitoring.WatchHamster_Project.core.system_monitor'
        ]
        
        for module in watchhamster_modules:
            try:
                __import__(module)
                import_tests['watchhamster_core'].append({
                    'module': module,
                    'status': 'SUCCESS'
                })
                print(f"  ✅ {module}")
            except Exception as e:
                import_tests['watchhamster_core'].append({
                    'module': module,
                    'status': 'FAILED',
                    'error': str(e)
                })
                print(f"  ❌ {module} - {e}")
        
        # 포스코 핵심 모듈 import 테스트
        posco_modules = [
            'Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.environment_setup',
            'Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.integrated_api_module',
            'Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.news_message_generator',
            'Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.webhook_sender'
        ]
        
        for module in posco_modules:
            try:
                __import__(module)
                import_tests['posco_core'].append({
                    'module': module,
                    'status': 'SUCCESS'
                })
                print(f"  ✅ {module}")
            except Exception as e:
                import_tests['posco_core'].append({
                    'module': module,
                    'status': 'FAILED',
                    'error': str(e)
                })
                print(f"  ❌ {module} - {e}")
        
        self.results['stability_tests']['module_imports'] = import_tests
        return import_tests

    def test_file_system_stability(self):
        """파일 시스템 안정성 테스트"""
        print("🗂️ 파일 시스템 안정성 테스트 중...")
        
        fs_tests = {
            'read_permissions': [],
            'write_permissions': [],
            'path_resolution': []
        }
        
        # 읽기 권한 테스트
        critical_files = [
            'Monitoring/WatchHamster_Project/core/watchhamster_monitor.py',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/environment_setup.py',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config/environment_settings.json'
        ]
        
        for file_path in critical_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fs_tests['read_permissions'].append({
                    'file': file_path,
                    'status': 'SUCCESS',
                    'size': len(content)
                })
                print(f"  ✅ 읽기 권한: {file_path}")
            except Exception as e:
                fs_tests['read_permissions'].append({
                    'file': file_path,
                    'status': 'FAILED',
                    'error': str(e)
                })
                print(f"  ❌ 읽기 권한: {file_path} - {e}")
        
        # 쓰기 권한 테스트 (로그 폴더)
        log_dirs = [
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/logs'
        ]
        
        for log_dir in log_dirs:
            try:
                test_file = os.path.join(log_dir, 'stability_test.tmp')
                with open(test_file, 'w') as f:
                    f.write('stability test')
                os.remove(test_file)
                fs_tests['write_permissions'].append({
                    'directory': log_dir,
                    'status': 'SUCCESS'
                })
                print(f"  ✅ 쓰기 권한: {log_dir}")
            except Exception as e:
                fs_tests['write_permissions'].append({
                    'directory': log_dir,
                    'status': 'FAILED',
                    'error': str(e)
                })
                print(f"  ❌ 쓰기 권한: {log_dir} - {e}")
        
        self.results['stability_tests']['file_system'] = fs_tests
        return fs_tests

    def test_script_execution(self):
        """스크립트 실행 안정성 테스트"""
        print("🚀 스크립트 실행 안정성 테스트 중...")
        
        script_tests = {
            'python_scripts': [],
            'shell_scripts': []
        }
        
        # Python 스크립트 구문 검사
        python_scripts = [
            'Monitoring/WatchHamster_Project/scripts/start_monitoring.py',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts/system_test.py'
        ]
        
        for script in python_scripts:
            try:
                # 구문 검사만 수행 (실제 실행 X)
                with open(script, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, script, 'exec')
                script_tests['python_scripts'].append({
                    'script': script,
                    'status': 'SYNTAX_OK'
                })
                print(f"  ✅ 구문 검사: {script}")
            except Exception as e:
                script_tests['python_scripts'].append({
                    'script': script,
                    'status': 'SYNTAX_ERROR',
                    'error': str(e)
                })
                print(f"  ❌ 구문 오류: {script} - {e}")
        
        # Shell 스크립트 존재 확인
        shell_scripts = [
            'Monitoring/WatchHamster_Project/scripts/daily_check.sh',
            'Monitoring/WatchHamster_Project/scripts/daily_check.bat'
        ]
        
        for script in shell_scripts:
            if os.path.exists(script):
                script_tests['shell_scripts'].append({
                    'script': script,
                    'status': 'EXISTS'
                })
                print(f"  ✅ 스크립트 존재: {script}")
            else:
                script_tests['shell_scripts'].append({
                    'script': script,
                    'status': 'MISSING'
                })
                print(f"  ❌ 스크립트 누락: {script}")
        
        self.results['stability_tests']['script_execution'] = script_tests
        return script_tests

    def test_configuration_integrity(self):
        """설정 파일 무결성 테스트"""
        print("⚙️ 설정 파일 무결성 테스트 중...")
        
        config_tests = {
            'json_files': [],
            'required_keys': []
        }
        
        # JSON 설정 파일 검증
        json_configs = [
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config/environment_settings.json'
        ]
        
        for config_file in json_configs:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                config_tests['json_files'].append({
                    'file': config_file,
                    'status': 'VALID_JSON',
                    'keys_count': len(config_data) if isinstance(config_data, dict) else 0
                })
                print(f"  ✅ JSON 유효성: {config_file}")
            except Exception as e:
                config_tests['json_files'].append({
                    'file': config_file,
                    'status': 'INVALID_JSON',
                    'error': str(e)
                })
                print(f"  ❌ JSON 오류: {config_file} - {e}")
        
        self.results['stability_tests']['configuration'] = config_tests
        return config_tests

    def measure_performance_metrics(self):
        """성능 지표 측정"""
        print("📊 성능 지표 측정 중...")
        
        performance = {
            'import_time': {},
            'file_access_time': {},
            'memory_usage': {}
        }
        
        # 모듈 import 시간 측정
        test_modules = [
            'Monitoring.WatchHamster_Project.core.watchhamster_monitor',
            'Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.environment_setup'
        ]
        
        for module in test_modules:
            try:
                start_time = time.time()
                __import__(module)
                import_time = time.time() - start_time
                performance['import_time'][module] = {
                    'time_seconds': round(import_time, 4),
                    'status': 'SUCCESS'
                }
                print(f"  ⏱️ {module}: {import_time:.4f}초")
            except Exception as e:
                performance['import_time'][module] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                print(f"  ❌ {module}: 실패")
        
        # 파일 접근 시간 측정
        test_files = [
            'Monitoring/WatchHamster_Project/core/watchhamster_monitor.py',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config/environment_settings.json'
        ]
        
        for file_path in test_files:
            try:
                start_time = time.time()
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                access_time = time.time() - start_time
                performance['file_access_time'][file_path] = {
                    'time_seconds': round(access_time, 4),
                    'file_size': len(content),
                    'status': 'SUCCESS'
                }
                print(f"  ⏱️ {file_path}: {access_time:.4f}초")
            except Exception as e:
                performance['file_access_time'][file_path] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                print(f"  ❌ {file_path}: 실패")
        
        self.results['performance_metrics'] = performance
        return performance

    def calculate_final_score(self):
        """최종 점수 계산"""
        print("🎯 최종 점수 계산 중...")
        
        scores = {
            'module_imports': 0,
            'file_system': 0,
            'script_execution': 0,
            'configuration': 0,
            'performance': 0
        }
        
        # 모듈 import 점수 (30점)
        if 'module_imports' in self.results['stability_tests']:
            total_modules = 0
            success_modules = 0
            for category in self.results['stability_tests']['module_imports'].values():
                for test in category:
                    total_modules += 1
                    if test['status'] == 'SUCCESS':
                        success_modules += 1
            if total_modules > 0:
                scores['module_imports'] = (success_modules / total_modules) * 30
        
        # 파일 시스템 점수 (25점)
        if 'file_system' in self.results['stability_tests']:
            total_tests = 0
            success_tests = 0
            for category in self.results['stability_tests']['file_system'].values():
                for test in category:
                    total_tests += 1
                    if test['status'] == 'SUCCESS':
                        success_tests += 1
            if total_tests > 0:
                scores['file_system'] = (success_tests / total_tests) * 25
        
        # 스크립트 실행 점수 (20점)
        if 'script_execution' in self.results['stability_tests']:
            total_scripts = 0
            success_scripts = 0
            for category in self.results['stability_tests']['script_execution'].values():
                for test in category:
                    total_scripts += 1
                    if test['status'] in ['SYNTAX_OK', 'EXISTS']:
                        success_scripts += 1
            if total_scripts > 0:
                scores['script_execution'] = (success_scripts / total_scripts) * 20
        
        # 설정 파일 점수 (15점)
        if 'configuration' in self.results['stability_tests']:
            total_configs = 0
            success_configs = 0
            for category in self.results['stability_tests']['configuration'].values():
                for test in category:
                    total_configs += 1
                    if test['status'] == 'VALID_JSON':
                        success_configs += 1
            if total_configs > 0:
                scores['configuration'] = (success_configs / total_configs) * 15
        
        # 성능 점수 (10점)
        if 'import_time' in self.results['performance_metrics']:
            total_perf = 0
            success_perf = 0
            for test in self.results['performance_metrics']['import_time'].values():
                total_perf += 1
                if test['status'] == 'SUCCESS':
                    success_perf += 1
            if total_perf > 0:
                scores['performance'] = (success_perf / total_perf) * 10
        
        final_score = sum(scores.values())
        self.results['final_score'] = round(final_score, 2)
        self.results['score_breakdown'] = scores
        
        # 상태 결정
        if final_score >= 90:
            self.results['status'] = 'EXCELLENT'
        elif final_score >= 80:
            self.results['status'] = 'GOOD'
        elif final_score >= 70:
            self.results['status'] = 'ACCEPTABLE'
        else:
            self.results['status'] = 'NEEDS_IMPROVEMENT'
        
        print(f"  📊 모듈 import: {scores['module_imports']:.1f}/30")
        print(f"  📊 파일 시스템: {scores['file_system']:.1f}/25")
        print(f"  📊 스크립트 실행: {scores['script_execution']:.1f}/20")
        print(f"  📊 설정 파일: {scores['configuration']:.1f}/15")
        print(f"  📊 성능: {scores['performance']:.1f}/10")
        print(f"  🏆 최종 점수: {final_score:.1f}/100")
        
        return final_score

    def generate_stability_report(self):
        """안정성 보고서 생성"""
        print("\n📋 안정성 보고서 생성 중...")
        
        report_filename = f'final_stability_report_{self.results["timestamp"]}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 요약 출력
        print(f"\n{'='*60}")
        print("🎯 최종 안정성 검증 결과")
        print(f"{'='*60}")
        print(f"🏆 최종 점수: {self.results['final_score']}/100")
        print(f"📊 상태: {self.results['status']}")
        print(f"⏰ 검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📄 상세 보고서: {report_filename}")
        print(f"{'='*60}")
        
        return self.results

    def run_full_stability_test(self):
        """전체 안정성 테스트 실행"""
        print("🔍 POSCO 프로덕션 구조 최종 안정성 검증 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # 1. 모듈 import 테스트
            self.test_module_imports()
            print()
            
            # 2. 파일 시스템 안정성 테스트
            self.test_file_system_stability()
            print()
            
            # 3. 스크립트 실행 안정성 테스트
            self.test_script_execution()
            print()
            
            # 4. 설정 파일 무결성 테스트
            self.test_configuration_integrity()
            print()
            
            # 5. 성능 지표 측정
            self.measure_performance_metrics()
            print()
            
            # 6. 최종 점수 계산
            self.calculate_final_score()
            print()
            
            # 7. 보고서 생성
            return self.generate_stability_report()
            
        except Exception as e:
            print(f"❌ 안정성 검증 중 오류 발생: {e}")
            self.results['status'] = 'ERROR'
            self.results['error'] = str(e)
            return self.results

if __name__ == "__main__":
    verifier = FinalStabilityVerification()
    results = verifier.run_full_stability_test()
    
    # 종료 코드 설정
    if results['final_score'] >= 80:
        sys.exit(0)
    else:
        sys.exit(1)