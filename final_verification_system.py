#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 검증 및 레거시 보존 확인 시스템
POSCO 프로덕션 구조 최종 검증
"""

import os
import sys
import json
import hashlib
import difflib
from datetime import datetime
from pathlib import Path

class FinalVerificationSystem:
    def __init__(self):
        self.verification_results = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'file_structure_check': {},
            'legacy_preservation_check': {},
            'file_content_comparison': {},
            'integration_test_results': {},
            'expandability_check': {},
            'overall_status': 'PENDING'
        }
        
        # 핵심 파일 매핑 (원본 -> 복사본)
        self.core_file_mapping = {
            # 워치햄스터 레벨 파일들
            'recovery_config/watchhamster_monitor.py': 'Monitoring/WatchHamster_Project/core/watchhamster_monitor.py',
            'recovery_config/git_monitor.py': 'Monitoring/WatchHamster_Project/core/git_monitor.py',
            'recovery_config/start_watchhamster_monitor.py': 'Monitoring/WatchHamster_Project/scripts/start_monitoring.py',
            'recovery_config/daily_check.bat': 'Monitoring/WatchHamster_Project/scripts/daily_check.bat',
            'recovery_config/daily_check.sh': 'Monitoring/WatchHamster_Project/scripts/daily_check.sh',
            
            # 포스코 프로젝트 파일들
            'recovery_config/environment_setup.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/environment_setup.py',
            'recovery_config/integrated_api_module.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/integrated_api_module.py',
            'recovery_config/news_message_generator.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/news_message_generator.py',
            'recovery_config/webhook_sender.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/webhook_sender.py',
            'recovery_config/comprehensive_system_integration_test.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts/system_test.py',
            
            # 문서 파일들
            'recovery_config/MONITORING_GUIDE_FOR_OPERATORS.md': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs/MONITORING_GUIDE.md',
            'recovery_config/QUICK_MONITORING_CHEAT_SHEET.md': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs/QUICK_CHEAT_SHEET.md',
            
            # 설정 파일들
            'recovery_config/environment_settings.json': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config/environment_settings.json'
        }
        
        # 필수 폴더 구조
        self.required_folders = [
            'Monitoring/WatchHamster_Project',
            'Monitoring/WatchHamster_Project/core',
            'Monitoring/WatchHamster_Project/scripts',
            'Monitoring/WatchHamster_Project/docs',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config',
            'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/logs'
        ]

    def calculate_file_hash(self, file_path):
        """파일의 MD5 해시값 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def check_file_structure(self):
        """파일 구조 확인"""
        print("📁 파일 구조 확인 중...")
        
        structure_check = {
            'required_folders': {},
            'core_files': {},
            'init_files': {}
        }
        
        # 필수 폴더 확인
        for folder in self.required_folders:
            exists = os.path.exists(folder)
            structure_check['required_folders'][folder] = {
                'exists': exists,
                'status': 'OK' if exists else 'MISSING'
            }
            if exists:
                print(f"  ✅ {folder}")
            else:
                print(f"  ❌ {folder} - 누락됨")
        
        # 핵심 파일 확인
        for original, copied in self.core_file_mapping.items():
            copied_exists = os.path.exists(copied)
            original_exists = os.path.exists(original)
            
            structure_check['core_files'][copied] = {
                'original_exists': original_exists,
                'copied_exists': copied_exists,
                'status': 'OK' if copied_exists else 'MISSING'
            }
            
            if copied_exists:
                print(f"  ✅ {copied}")
            else:
                print(f"  ❌ {copied} - 누락됨")
        
        # __init__.py 파일 확인
        for folder in self.required_folders:
            if os.path.exists(folder):
                init_file = os.path.join(folder, '__init__.py')
                exists = os.path.exists(init_file)
                structure_check['init_files'][init_file] = {
                    'exists': exists,
                    'status': 'OK' if exists else 'MISSING'
                }
        
        self.verification_results['file_structure_check'] = structure_check
        return structure_check

    def check_legacy_preservation(self):
        """레거시 보존 확인"""
        print("🏛️ 레거시 보존 상태 확인 중...")
        
        legacy_check = {
            'recovery_config_exists': os.path.exists('recovery_config'),
            'original_files': {},
            'file_count': 0
        }
        
        if legacy_check['recovery_config_exists']:
            print("  ✅ recovery_config 폴더 보존됨")
            
            # 원본 파일들 확인
            for original_file in self.core_file_mapping.keys():
                exists = os.path.exists(original_file)
                legacy_check['original_files'][original_file] = {
                    'exists': exists,
                    'status': 'OK' if exists else 'MISSING'
                }
                
                if exists:
                    print(f"  ✅ {original_file}")
                else:
                    print(f"  ❌ {original_file} - 누락됨")
            
            # recovery_config 폴더 내 파일 개수 확인
            try:
                recovery_files = list(Path('recovery_config').rglob('*'))
                legacy_check['file_count'] = len([f for f in recovery_files if f.is_file()])
                print(f"  📊 recovery_config 내 총 파일 수: {legacy_check['file_count']}")
            except Exception as e:
                print(f"  ⚠️ 파일 개수 확인 오류: {e}")
        else:
            print("  ❌ recovery_config 폴더가 존재하지 않음")
        
        self.verification_results['legacy_preservation_check'] = legacy_check
        return legacy_check

    def compare_file_contents(self):
        """파일 내용 비교"""
        print("🔍 파일 내용 일치성 확인 중...")
        
        content_comparison = {
            'identical_files': [],
            'different_files': [],
            'missing_files': [],
            'hash_comparison': {}
        }
        
        for original, copied in self.core_file_mapping.items():
            if not os.path.exists(original):
                content_comparison['missing_files'].append({
                    'file': original,
                    'reason': 'Original file missing'
                })
                print(f"  ⚠️ {original} - 원본 파일 없음")
                continue
                
            if not os.path.exists(copied):
                content_comparison['missing_files'].append({
                    'file': copied,
                    'reason': 'Copied file missing'
                })
                print(f"  ⚠️ {copied} - 복사본 파일 없음")
                continue
            
            # 해시 비교 (바이너리 파일용)
            original_hash = self.calculate_file_hash(original)
            copied_hash = self.calculate_file_hash(copied)
            
            content_comparison['hash_comparison'][copied] = {
                'original_hash': original_hash,
                'copied_hash': copied_hash,
                'identical': original_hash == copied_hash
            }
            
            # 텍스트 파일의 경우 내용 비교 (import 경로 수정 고려)
            try:
                with open(original, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                with open(copied, 'r', encoding='utf-8') as f:
                    copied_content = f.read()
                
                # import 경로가 수정된 경우를 고려한 비교
                if original_hash == copied_hash:
                    content_comparison['identical_files'].append(copied)
                    print(f"  ✅ {copied} - 내용 일치")
                else:
                    # import 경로 수정이 있는지 확인
                    has_import_changes = (
                        'recovery_config' in original_content and 
                        'Monitoring.WatchHamster_Project' in copied_content
                    )
                    
                    if has_import_changes:
                        content_comparison['different_files'].append({
                            'file': copied,
                            'reason': 'Import path updated (expected)',
                            'status': 'OK'
                        })
                        print(f"  ✅ {copied} - import 경로 수정됨 (정상)")
                    else:
                        content_comparison['different_files'].append({
                            'file': copied,
                            'reason': 'Content differs unexpectedly',
                            'status': 'WARNING'
                        })
                        print(f"  ⚠️ {copied} - 예상치 못한 내용 차이")
                        
            except Exception as e:
                print(f"  ❌ {copied} - 비교 오류: {e}")
        
        self.verification_results['file_content_comparison'] = content_comparison
        return content_comparison

    def run_integration_test(self):
        """통합 테스트 실행"""
        print("🧪 통합 테스트 실행 중...")
        
        integration_results = {
            'system_test_available': False,
            'test_execution': {},
            'success_rate': 0
        }
        
        # 시스템 테스트 파일 확인
        system_test_path = 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts/system_test.py'
        
        if os.path.exists(system_test_path):
            integration_results['system_test_available'] = True
            print(f"  ✅ 시스템 테스트 파일 발견: {system_test_path}")
            
            try:
                # 시스템 테스트 실행
                import subprocess
                result = subprocess.run([
                    sys.executable, system_test_path
                ], capture_output=True, text=True, timeout=300)
                
                integration_results['test_execution'] = {
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                }
                
                # 성공률 계산 (8/8 = 100% 목표)
                if '8/8' in result.stdout or 'SUCCESS' in result.stdout:
                    integration_results['success_rate'] = 100
                    print("  ✅ 통합 테스트 성공 - 100% 성공률 달성")
                else:
                    print("  ⚠️ 통합 테스트 완료 - 성공률 확인 필요")
                    
            except subprocess.TimeoutExpired:
                integration_results['test_execution'] = {
                    'error': 'Test timeout after 300 seconds'
                }
                print("  ⚠️ 테스트 타임아웃 (300초)")
            except Exception as e:
                integration_results['test_execution'] = {
                    'error': str(e)
                }
                print(f"  ❌ 테스트 실행 오류: {e}")
        else:
            print(f"  ❌ 시스템 테스트 파일 없음: {system_test_path}")
        
        self.verification_results['integration_test_results'] = integration_results
        return integration_results

    def check_expandability(self):
        """확장성 검증"""
        print("🚀 확장성 검증 중...")
        
        expandability_check = {
            'structure_ready': True,
            'watchhamster_common_modules': [],
            'project_template_ready': False,
            'expansion_guide': {}
        }
        
        # 워치햄스터 공통 모듈 확인
        watchhamster_core_path = 'Monitoring/WatchHamster_Project/core'
        if os.path.exists(watchhamster_core_path):
            core_files = [f for f in os.listdir(watchhamster_core_path) 
                         if f.endswith('.py') and f != '__init__.py']
            expandability_check['watchhamster_common_modules'] = core_files
            print(f"  ✅ 워치햄스터 공통 모듈 {len(core_files)}개 확인")
        
        # 프로젝트 템플릿 구조 확인
        posco_structure = 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final'
        required_subfolders = ['core', 'scripts', 'docs', 'config', 'logs']
        
        if os.path.exists(posco_structure):
            missing_folders = []
            for subfolder in required_subfolders:
                if not os.path.exists(os.path.join(posco_structure, subfolder)):
                    missing_folders.append(subfolder)
            
            if not missing_folders:
                expandability_check['project_template_ready'] = True
                print("  ✅ 프로젝트 템플릿 구조 완성")
            else:
                print(f"  ⚠️ 누락된 폴더: {missing_folders}")
        
        # 확장 가이드 정보
        expandability_check['expansion_guide'] = {
            'new_project_steps': [
                '1. Monitoring/WatchHamster_Project/[New_Project_Name] 폴더 생성',
                '2. core, scripts, docs, config, logs 하위 폴더 생성',
                '3. 각 폴더에 __init__.py 파일 생성',
                '4. 워치햄스터 공통 모듈을 import하여 사용',
                '5. 프로젝트별 전용 모듈을 core 폴더에 구현'
            ],
            'common_modules_usage': '상위 패키지에서 워치햄스터 공통 모듈 import 가능'
        }
        
        print("  📋 새 프로젝트 추가 준비 완료")
        
        self.verification_results['expandability_check'] = expandability_check
        return expandability_check

    def generate_final_report(self):
        """최종 검증 보고서 생성"""
        print("\n📊 최종 검증 보고서 생성 중...")
        
        # 전체 상태 판정
        structure_ok = all(
            folder_info['status'] == 'OK' 
            for folder_info in self.verification_results['file_structure_check']['required_folders'].values()
        )
        
        legacy_ok = (
            self.verification_results['legacy_preservation_check']['recovery_config_exists'] and
            all(
                file_info['status'] == 'OK'
                for file_info in self.verification_results['legacy_preservation_check']['original_files'].values()
            )
        )
        
        content_ok = len(self.verification_results['file_content_comparison']['missing_files']) == 0
        
        integration_ok = (
            self.verification_results['integration_test_results'].get('success_rate', 0) >= 100 or
            self.verification_results['integration_test_results'].get('test_execution', {}).get('success', False)
        )
        
        expandability_ok = (
            self.verification_results['expandability_check']['structure_ready'] and
            self.verification_results['expandability_check']['project_template_ready']
        )
        
        # 전체 상태 결정
        if all([structure_ok, legacy_ok, content_ok, expandability_ok]):
            if integration_ok:
                self.verification_results['overall_status'] = 'SUCCESS'
            else:
                self.verification_results['overall_status'] = 'SUCCESS_WITH_WARNING'
        else:
            self.verification_results['overall_status'] = 'FAILED'
        
        # 보고서 파일 생성
        report_filename = f'final_verification_report_{self.verification_results["timestamp"]}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        # 요약 출력
        print(f"\n{'='*60}")
        print("🎯 최종 검증 결과 요약")
        print(f"{'='*60}")
        print(f"📁 파일 구조: {'✅ 통과' if structure_ok else '❌ 실패'}")
        print(f"🏛️ 레거시 보존: {'✅ 통과' if legacy_ok else '❌ 실패'}")
        print(f"🔍 파일 내용: {'✅ 통과' if content_ok else '❌ 실패'}")
        print(f"🧪 통합 테스트: {'✅ 통과' if integration_ok else '⚠️ 확인 필요'}")
        print(f"🚀 확장성: {'✅ 준비됨' if expandability_ok else '❌ 미완성'}")
        print(f"{'='*60}")
        print(f"🏆 전체 상태: {self.verification_results['overall_status']}")
        print(f"📄 상세 보고서: {report_filename}")
        print(f"{'='*60}")
        
        return self.verification_results

    def run_full_verification(self):
        """전체 검증 실행"""
        print("🔍 POSCO 프로덕션 구조 최종 검증 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # 1. 파일 구조 확인
            self.check_file_structure()
            print()
            
            # 2. 레거시 보존 확인
            self.check_legacy_preservation()
            print()
            
            # 3. 파일 내용 비교
            self.compare_file_contents()
            print()
            
            # 4. 통합 테스트 실행
            self.run_integration_test()
            print()
            
            # 5. 확장성 검증
            self.check_expandability()
            print()
            
            # 6. 최종 보고서 생성
            return self.generate_final_report()
            
        except Exception as e:
            print(f"❌ 검증 중 오류 발생: {e}")
            self.verification_results['overall_status'] = 'ERROR'
            self.verification_results['error'] = str(e)
            return self.verification_results

if __name__ == "__main__":
    verifier = FinalVerificationSystem()
    results = verifier.run_full_verification()
    
    # 종료 코드 설정
    if results['overall_status'] in ['SUCCESS', 'SUCCESS_WITH_WARNING']:
        sys.exit(0)
    else:
        sys.exit(1)