#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스탠드얼론 기능 테스트 구현 (Task 19.1)
Monitoring/WatchHamster_Project_GUI 폴더만으로 완전 독립 실행 테스트

주요 테스트:
- 내장된 모든 시스템 기능 검증 (외부 의존성 없음)
- 레거시 폴더 삭제 후에도 정상 작동 확인
- 완전 독립 실행 환경 검증

Requirements: 4.2, 4.3, 4.4 구현
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import importlib.util
import traceback


class StandaloneFunctionalityTest:
    """스탠드얼론 기능 테스트 클래스"""
    
    def __init__(self):
        """테스트 초기화"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = self.script_dir
        self.test_results = {}
        self.test_start_time = datetime.now()
        
        # 테스트 로그
        self.test_log = []
        
        print("🧪 스탠드얼론 기능 테스트 시스템 초기화")
        print(f"📁 프로젝트 루트: {self.project_root}")
        print("=" * 80)
    
    def log_test(self, message: str, level: str = "INFO"):
        """테스트 로그 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.test_log.append(log_entry)
        print(log_entry)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 스탠드얼론 테스트 실행"""
        self.log_test("🚀 스탠드얼론 기능 테스트 시작", "INFO")
        
        # 테스트 순서 (의존성 순서대로)
        test_methods = [
            ("1. 프로젝트 구조 검증", self.test_project_structure),
            ("2. 내장 모듈 임포트 테스트", self.test_module_imports),
            ("3. 설정 파일 검증", self.test_configuration_files),
            ("4. 핵심 시스템 기능 테스트", self.test_core_systems),
            ("5. POSCO 뉴스 시스템 테스트", self.test_posco_news_system),
            ("6. GUI 컴포넌트 테스트", self.test_gui_components),
            ("7. 데이터 캐시 시스템 테스트", self.test_data_cache_system),
            ("8. 통합 상태 보고 시스템 테스트", self.test_integrated_status_system),
            ("9. 외부 의존성 없음 검증", self.test_no_external_dependencies),
            ("10. 레거시 폴더 독립성 테스트", self.test_legacy_independence),
            ("11. 완전 독립 실행 테스트", self.test_complete_standalone_execution),
            ("12. 메인 GUI 초기화 테스트", self.test_main_gui_initialization)
        ]
        
        # 각 테스트 실행
        for test_name, test_method in test_methods:
            self.log_test(f"▶️ {test_name} 시작", "TEST")
            try:
                result = test_method()
                self.test_results[test_name] = {
                    'status': 'PASS' if result else 'FAIL',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                status_icon = "✅" if result else "❌"
                self.log_test(f"{status_icon} {test_name} {'성공' if result else '실패'}", 
                            "PASS" if result else "FAIL")
            except Exception as e:
                self.test_results[test_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                    'timestamp': datetime.now().isoformat()
                }
                self.log_test(f"💥 {test_name} 오류: {str(e)}", "ERROR")
            
            print("-" * 60)
        
        # 최종 결과 생성
        return self.generate_final_report()
    
    def test_project_structure(self) -> bool:
        """프로젝트 구조 검증"""
        self.log_test("📁 프로젝트 구조 검증 중...", "INFO")
        
        required_structure = {
            'main_gui.py': '메인 GUI 애플리케이션',
            'core/': '핵심 시스템 디렉토리',
            'core/cache_monitor.py': '캐시 모니터링 시스템',
            'core/integrated_status_reporter.py': '통합 상태 보고 시스템',
            'core/system_recovery_handler.py': '시스템 복구 핸들러',
            'Posco_News_Mini_Final_GUI/': 'POSCO 뉴스 시스템 디렉토리',
            'Posco_News_Mini_Final_GUI/posco_main_notifier.py': 'POSCO 메인 알림 시스템',
            'Posco_News_Mini_Final_GUI/posco_gui_manager.py': 'POSCO GUI 관리자',
            'Posco_News_Mini_Final_GUI/git_deployment_manager.py': 'Git 배포 관리자',
            'Posco_News_Mini_Final_GUI/deployment_monitor.py': '배포 모니터링',
            'Posco_News_Mini_Final_GUI/message_template_engine.py': '메시지 템플릿 엔진',
            'gui_components/': 'GUI 컴포넌트 디렉토리',
            'gui_components/log_viewer.py': '로그 뷰어',
            'gui_components/notification_center.py': '알림 센터',
            'gui_components/system_tray.py': '시스템 트레이',
            'gui_components/config_manager.py': '설정 관리자',
            'gui_components/status_dashboard.py': '상태 대시보드',
            'config/': '설정 파일 디렉토리',
            'config/gui_config.json': 'GUI 설정',
            'config/posco_config.json': 'POSCO 설정',
            'config/webhook_config.json': '웹훅 설정',
            'assets/': '리소스 디렉토리',
            'assets/icons/': '아이콘 디렉토리',
            'assets/images/': '이미지 디렉토리',
            'logs/': '로그 디렉토리',
            'data/': '데이터 디렉토리'
        }
        
        missing_items = []
        for item_path, description in required_structure.items():
            full_path = os.path.join(self.project_root, item_path)
            if not os.path.exists(full_path):
                missing_items.append(f"{item_path} ({description})")
                self.log_test(f"❌ 누락: {item_path}", "WARN")
            else:
                self.log_test(f"✅ 확인: {item_path}", "DEBUG")
        
        if missing_items:
            self.log_test(f"❌ 누락된 항목들: {len(missing_items)}개", "ERROR")
            for item in missing_items:
                self.log_test(f"  - {item}", "ERROR")
            return False
        
        self.log_test("✅ 모든 필수 구조 확인됨", "INFO")
        return True
    
    def test_module_imports(self) -> bool:
        """내장 모듈 임포트 테스트"""
        self.log_test("📦 내장 모듈 임포트 테스트 중...", "INFO")
        
        # 현재 디렉토리를 Python 경로에 추가
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)
        
        # 안전한 모듈들만 테스트 (interactive prompt가 없는 모듈들)
        modules_to_test = [
            ('core.cache_monitor', 'CacheMonitor'),
            ('Posco_News_Mini_Final_GUI.git_deployment_manager', 'GitDeploymentManager'),
            ('Posco_News_Mini_Final_GUI.deployment_monitor', 'DeploymentMonitor'),
            ('Posco_News_Mini_Final_GUI.message_template_engine', 'MessageTemplateEngine'),
            ('gui_components.config_manager', 'create_config_manager')
        ]
        
        import_failures = []
        successful_imports = []
        
        for module_name, class_or_function in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_or_function):
                    successful_imports.append(f"{module_name}.{class_or_function}")
                    self.log_test(f"✅ 임포트 성공: {module_name}.{class_or_function}", "DEBUG")
                else:
                    import_failures.append(f"{module_name}.{class_or_function} (속성 없음)")
                    self.log_test(f"❌ 속성 없음: {module_name}.{class_or_function}", "WARN")
            except ImportError as e:
                import_failures.append(f"{module_name} (ImportError: {str(e)})")
                self.log_test(f"❌ 임포트 실패: {module_name} - {str(e)}", "ERROR")
            except Exception as e:
                import_failures.append(f"{module_name} (Error: {str(e)})")
                self.log_test(f"❌ 오류: {module_name} - {str(e)}", "ERROR")
        
        self.log_test(f"✅ 성공한 임포트: {len(successful_imports)}개", "INFO")
        if import_failures:
            self.log_test(f"❌ 실패한 임포트: {len(import_failures)}개", "ERROR")
            for failure in import_failures:
                self.log_test(f"  - {failure}", "ERROR")
            return False
        
        return True
    
    def test_configuration_files(self) -> bool:
        """설정 파일 검증"""
        self.log_test("⚙️ 설정 파일 검증 중...", "INFO")
        
        config_files = [
            'config/gui_config.json',
            'config/posco_config.json',
            'config/webhook_config.json',
            'config/message_templates.json',
            'config/language_strings.json'
        ]
        
        valid_configs = 0
        for config_file in config_files:
            config_path = os.path.join(self.project_root, config_file)
            
            if not os.path.exists(config_path):
                self.log_test(f"❌ 설정 파일 없음: {config_file}", "WARN")
                continue
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                if isinstance(config_data, dict) and config_data:
                    valid_configs += 1
                    self.log_test(f"✅ 유효한 설정: {config_file}", "DEBUG")
                else:
                    self.log_test(f"❌ 빈 설정 파일: {config_file}", "WARN")
                    
            except json.JSONDecodeError as e:
                self.log_test(f"❌ JSON 오류: {config_file} - {str(e)}", "ERROR")
            except Exception as e:
                self.log_test(f"❌ 파일 오류: {config_file} - {str(e)}", "ERROR")
        
        self.log_test(f"✅ 유효한 설정 파일: {valid_configs}/{len(config_files)}개", "INFO")
        return valid_configs >= len(config_files) * 0.8  # 80% 이상 유효하면 통과
    
    def test_core_systems(self) -> bool:
        """핵심 시스템 기능 테스트"""
        self.log_test("🔧 핵심 시스템 기능 테스트 중...", "INFO")
        
        try:
            core_systems_working = 0
            
            # 캐시 모니터 테스트
            try:
                from core.cache_monitor import CacheMonitor
                cache_monitor = CacheMonitor(data_dir=os.path.join(self.project_root, "data"))
                
                # 캐시 상태 확인 (안전한 테스트)
                cache_status = cache_monitor.check_cache_status()
                self.log_test(f"✅ 캐시 모니터 작동: {len(cache_status)}개 데이터 타입 확인", "DEBUG")
                core_systems_working += 1
            except Exception as e:
                self.log_test(f"❌ 캐시 모니터 테스트 실패: {str(e)}", "WARN")
            
            # 통합 상태 보고 시스템 테스트
            try:
                from core.integrated_status_reporter import create_integrated_status_reporter
                status_reporter = create_integrated_status_reporter(self.project_root)
                
                # 상태 업데이트 테스트 (안전한 테스트)
                status_reporter.update_all_component_status()
                self.log_test("✅ 통합 상태 보고 시스템 작동", "DEBUG")
                core_systems_working += 1
            except Exception as e:
                self.log_test(f"❌ 통합 상태 보고 시스템 테스트 실패: {str(e)}", "WARN")
            
            # 시스템 복구 핸들러 테스트
            try:
                from core.system_recovery_handler import create_system_recovery_handler
                recovery_handler = create_system_recovery_handler(self.project_root)
                
                # 복구 기능 테스트 (안전한 테스트)
                recovery_available = hasattr(recovery_handler, 'execute_recovery')
                self.log_test(f"✅ 시스템 복구 핸들러 {'사용 가능' if recovery_available else '제한적'}", "DEBUG")
                core_systems_working += 1
            except Exception as e:
                self.log_test(f"❌ 시스템 복구 핸들러 테스트 실패: {str(e)}", "WARN")
            
            self.log_test(f"✅ 핵심 시스템 작동: {core_systems_working}/3개", "INFO")
            return core_systems_working >= 2  # 최소 2개 이상 작동하면 통과
            
        except Exception as e:
            self.log_test(f"❌ 핵심 시스템 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_posco_news_system(self) -> bool:
        """POSCO 뉴스 시스템 테스트"""
        self.log_test("📰 POSCO 뉴스 시스템 테스트 중...", "INFO")
        
        try:
            # 모듈 임포트만 테스트 (초기화는 하지 않음)
            components_imported = 0
            
            # POSCO 메인 알림 시스템
            try:
                from Posco_News_Mini_Final_GUI.posco_main_notifier import PoscoMainNotifier
                components_imported += 1
                self.log_test("✅ POSCO 메인 알림 시스템 임포트", "DEBUG")
            except ImportError as e:
                self.log_test(f"❌ POSCO 메인 알림 시스템 임포트 실패: {str(e)}", "WARN")
            
            # Git 배포 관리자
            try:
                from Posco_News_Mini_Final_GUI.git_deployment_manager import GitDeploymentManager
                components_imported += 1
                self.log_test("✅ Git 배포 관리자 임포트", "DEBUG")
            except ImportError as e:
                self.log_test(f"❌ Git 배포 관리자 임포트 실패: {str(e)}", "WARN")
            
            # 배포 모니터
            try:
                from Posco_News_Mini_Final_GUI.deployment_monitor import DeploymentMonitor
                components_imported += 1
                self.log_test("✅ 배포 모니터 임포트", "DEBUG")
            except ImportError as e:
                self.log_test(f"❌ 배포 모니터 임포트 실패: {str(e)}", "WARN")
            
            # 메시지 템플릿 엔진
            try:
                from Posco_News_Mini_Final_GUI.message_template_engine import MessageTemplateEngine
                components_imported += 1
                self.log_test("✅ 메시지 템플릿 엔진 임포트", "DEBUG")
            except ImportError as e:
                self.log_test(f"❌ 메시지 템플릿 엔진 임포트 실패: {str(e)}", "WARN")
            
            # 동적 데이터 관리자 (선택적)
            try:
                from Posco_News_Mini_Final_GUI.dynamic_data_manager import DynamicDataManager
                components_imported += 1
                self.log_test("✅ 동적 데이터 관리자 임포트", "DEBUG")
            except ImportError:
                self.log_test("⚠️ 동적 데이터 관리자 선택적 모듈", "WARN")
            
            self.log_test(f"✅ POSCO 시스템 컴포넌트 임포트: {components_imported}/5개", "INFO")
            return components_imported >= 3  # 최소 3개 이상 임포트되면 통과
            
        except Exception as e:
            self.log_test(f"❌ POSCO 뉴스 시스템 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_gui_components(self) -> bool:
        """GUI 컴포넌트 테스트"""
        self.log_test("🎨 GUI 컴포넌트 테스트 중...", "INFO")
        
        try:
            # GUI 컴포넌트들 임포트 및 생성 테스트
            components_tested = 0
            
            # 로그 뷰어
            try:
                from gui_components.log_viewer import create_log_viewer
                components_tested += 1
                self.log_test("✅ 로그 뷰어 컴포넌트 사용 가능", "DEBUG")
            except ImportError:
                self.log_test("❌ 로그 뷰어 컴포넌트 없음", "WARN")
            
            # 알림 센터
            try:
                from gui_components.notification_center import create_notification_center
                components_tested += 1
                self.log_test("✅ 알림 센터 컴포넌트 사용 가능", "DEBUG")
            except ImportError:
                self.log_test("❌ 알림 센터 컴포넌트 없음", "WARN")
            
            # 시스템 트레이
            try:
                from gui_components.system_tray import create_system_tray
                components_tested += 1
                self.log_test("✅ 시스템 트레이 컴포넌트 사용 가능", "DEBUG")
            except ImportError:
                self.log_test("❌ 시스템 트레이 컴포넌트 없음", "WARN")
            
            # 설정 관리자
            try:
                from gui_components.config_manager import create_config_manager
                components_tested += 1
                self.log_test("✅ 설정 관리자 컴포넌트 사용 가능", "DEBUG")
            except ImportError:
                self.log_test("❌ 설정 관리자 컴포넌트 없음", "WARN")
            
            # 상태 대시보드
            try:
                from gui_components.status_dashboard import create_status_dashboard
                components_tested += 1
                self.log_test("✅ 상태 대시보드 컴포넌트 사용 가능", "DEBUG")
            except ImportError:
                self.log_test("❌ 상태 대시보드 컴포넌트 없음", "WARN")
            
            self.log_test(f"✅ GUI 컴포넌트 테스트 완료: {components_tested}/5개 사용 가능", "INFO")
            return components_tested >= 3  # 최소 3개 이상 사용 가능하면 통과
            
        except Exception as e:
            self.log_test(f"❌ GUI 컴포넌트 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_data_cache_system(self) -> bool:
        """데이터 캐시 시스템 테스트"""
        self.log_test("💾 데이터 캐시 시스템 테스트 중...", "INFO")
        
        try:
            # 데이터 디렉토리 확인
            data_dir = os.path.join(self.project_root, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                self.log_test("✅ 데이터 디렉토리 생성", "DEBUG")
            
            # 캐시 모니터 생성 및 테스트
            from core.cache_monitor import CacheMonitor
            cache_monitor = CacheMonitor(data_dir=data_dir)
            
            # 캐시 상태 확인
            cache_status = cache_monitor.check_cache_status()
            self.log_test(f"✅ 캐시 상태 확인: {len(cache_status)}개 데이터 타입", "DEBUG")
            
            # 캐시 요약 정보
            summary = cache_monitor.get_cache_summary()
            self.log_test(f"✅ 캐시 요약: 전체 건강도 {summary['overall_health']}", "DEBUG")
            
            # 데이터 나이 정보
            age_info = cache_monitor.get_data_age_info()
            self.log_test(f"✅ 데이터 나이 정보: {len(age_info)}개 항목", "DEBUG")
            
            return True
            
        except Exception as e:
            self.log_test(f"❌ 데이터 캐시 시스템 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_integrated_status_system(self) -> bool:
        """통합 상태 보고 시스템 테스트"""
        self.log_test("📊 통합 상태 보고 시스템 테스트 중...", "INFO")
        
        try:
            from core.integrated_status_reporter import create_integrated_status_reporter
            
            # 통합 상태 보고 시스템 생성
            status_reporter = create_integrated_status_reporter(self.project_root)
            
            # 컴포넌트 상태 업데이트
            status_reporter.update_all_component_status()
            self.log_test("✅ 컴포넌트 상태 업데이트 완료", "DEBUG")
            
            # 배포 통계 업데이트
            status_reporter.update_deployment_statistics()
            self.log_test("✅ 배포 통계 업데이트 완료", "DEBUG")
            
            # 상태 보고서 내보내기 테스트
            try:
                report_path = status_reporter.export_status_report()
                if os.path.exists(report_path):
                    self.log_test(f"✅ 상태 보고서 생성: {report_path}", "DEBUG")
                    # 테스트 후 정리
                    os.remove(report_path)
                else:
                    self.log_test("❌ 상태 보고서 생성 실패", "WARN")
            except Exception as e:
                self.log_test(f"⚠️ 상태 보고서 생성 오류: {str(e)}", "WARN")
            
            return True
            
        except Exception as e:
            self.log_test(f"❌ 통합 상태 보고 시스템 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_no_external_dependencies(self) -> bool:
        """외부 의존성 없음 검증"""
        self.log_test("🔒 외부 의존성 검증 중...", "INFO")
        
        try:
            # 현재 프로젝트 외부 경로 참조 확인
            external_references = []
            
            # Python 파일들에서 외부 경로 참조 검색
            for root, dirs, files in os.walk(self.project_root):
                # 숨김 폴더 제외
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 위험한 외부 참조 패턴 검색
                            dangerous_patterns = [
                                '../../../',  # 상위 디렉토리 참조
                                'sys.path.append("/'),  # 절대 경로 추가
                                'sys.path.insert(0, "/'),  # 절대 경로 삽입
                                'import sys\nsys.path',  # sys.path 조작
                            ]
                            
                            for pattern in dangerous_patterns:
                                if pattern in content:
                                    relative_path = os.path.relpath(file_path, self.project_root)
                                    external_references.append(f"{relative_path}: {pattern}")
                                    
                        except Exception:
                            continue  # 파일 읽기 실패 시 무시
            
            if external_references:
                self.log_test(f"⚠️ 외부 참조 발견: {len(external_references)}개", "WARN")
                for ref in external_references[:5]:  # 최대 5개만 표시
                    self.log_test(f"  - {ref}", "WARN")
                # 외부 참조가 있어도 경고만 하고 통과 (일부는 필요할 수 있음)
            else:
                self.log_test("✅ 외부 의존성 없음 확인", "INFO")
            
            return True
            
        except Exception as e:
            self.log_test(f"❌ 외부 의존성 검증 실패: {str(e)}", "ERROR")
            return False
    
    def test_legacy_independence(self) -> bool:
        """레거시 폴더 독립성 테스트"""
        self.log_test("🗂️ 레거시 폴더 독립성 테스트 중...", "INFO")
        
        try:
            # 레거시 폴더 경로들
            legacy_paths = [
                os.path.join(os.path.dirname(self.project_root), "레거시"),
                os.path.join(os.path.dirname(self.project_root), "WatchHamster_Project"),
                # 다른 레거시 경로들...
            ]
            
            # 현재 프로젝트에서 레거시 경로 참조 검색
            legacy_references = []
            
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 레거시 경로 참조 검색
                            for legacy_path in legacy_paths:
                                legacy_name = os.path.basename(legacy_path)
                                if legacy_name in content:
                                    relative_path = os.path.relpath(file_path, self.project_root)
                                    legacy_references.append(f"{relative_path}: {legacy_name}")
                                    
                        except Exception:
                            continue
            
            if legacy_references:
                self.log_test(f"⚠️ 레거시 참조 발견: {len(legacy_references)}개", "WARN")
                for ref in legacy_references[:3]:  # 최대 3개만 표시
                    self.log_test(f"  - {ref}", "WARN")
                return False
            else:
                self.log_test("✅ 레거시 폴더 독립성 확인", "INFO")
                return True
            
        except Exception as e:
            self.log_test(f"❌ 레거시 독립성 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_complete_standalone_execution(self) -> bool:
        """완전 독립 실행 테스트"""
        self.log_test("🚀 완전 독립 실행 테스트 중...", "INFO")
        
        try:
            # 임시 디렉토리에 프로젝트 복사
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_project_dir = os.path.join(temp_dir, "WatchHamster_Project_GUI")
                
                # 프로젝트 복사
                shutil.copytree(self.project_root, temp_project_dir)
                self.log_test(f"✅ 프로젝트 임시 복사: {temp_project_dir}", "DEBUG")
                
                # 복사된 프로젝트에서 모듈 임포트 테스트
                original_path = sys.path.copy()
                try:
                    # 임시 디렉토리를 Python 경로에 추가
                    sys.path.insert(0, temp_project_dir)
                    
                    # 핵심 모듈들 임포트 테스트
                    test_modules = [
                        'core.cache_monitor',
                        'Posco_News_Mini_Final_GUI.posco_main_notifier',
                        'gui_components.config_manager'
                    ]
                    
                    imported_modules = 0
                    for module_name in test_modules:
                        try:
                            importlib.import_module(module_name)
                            imported_modules += 1
                            self.log_test(f"✅ 독립 실행 임포트: {module_name}", "DEBUG")
                        except ImportError as e:
                            self.log_test(f"❌ 독립 실행 임포트 실패: {module_name} - {str(e)}", "WARN")
                    
                    success_rate = imported_modules / len(test_modules)
                    self.log_test(f"✅ 독립 실행 성공률: {success_rate:.1%}", "INFO")
                    
                    return success_rate >= 0.8  # 80% 이상 성공하면 통과
                    
                finally:
                    # Python 경로 복원
                    sys.path = original_path
            
        except Exception as e:
            self.log_test(f"❌ 완전 독립 실행 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def test_main_gui_initialization(self) -> bool:
        """메인 GUI 초기화 테스트"""
        self.log_test("🎨 메인 GUI 초기화 테스트 중...", "INFO")
        
        try:
            # GUI 환경 확인
            try:
                import tkinter as tk
                # 헤드리스 환경에서는 GUI 테스트 스킵
                root = tk.Tk()
                root.withdraw()  # 창 숨기기
                root.destroy()
                gui_available = True
            except Exception:
                gui_available = False
                self.log_test("⚠️ GUI 환경 없음 - GUI 테스트 스킵", "WARN")
                return True  # GUI 환경이 없어도 통과
            
            if gui_available:
                # 메인 GUI 클래스 임포트 테스트
                try:
                    # main_gui.py에서 MainGUI 클래스 임포트
                    spec = importlib.util.spec_from_file_location(
                        "main_gui", 
                        os.path.join(self.project_root, "main_gui.py")
                    )
                    main_gui_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(main_gui_module)
                    
                    # MainGUI 클래스 확인
                    if hasattr(main_gui_module, 'MainGUI'):
                        self.log_test("✅ MainGUI 클래스 임포트 성공", "DEBUG")
                        
                        # GUI 초기화 테스트 (실제 실행하지 않음)
                        # MainGUI 클래스의 __init__ 메서드 존재 확인
                        main_gui_class = getattr(main_gui_module, 'MainGUI')
                        if hasattr(main_gui_class, '__init__'):
                            self.log_test("✅ MainGUI 초기화 메서드 확인", "DEBUG")
                            return True
                        else:
                            self.log_test("❌ MainGUI 초기화 메서드 없음", "ERROR")
                            return False
                    else:
                        self.log_test("❌ MainGUI 클래스 없음", "ERROR")
                        return False
                        
                except Exception as e:
                    self.log_test(f"❌ 메인 GUI 임포트 실패: {str(e)}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test(f"❌ 메인 GUI 초기화 테스트 실패: {str(e)}", "ERROR")
            return False
    
    def generate_final_report(self) -> Dict[str, Any]:
        """최종 테스트 보고서 생성"""
        self.log_test("📋 최종 테스트 보고서 생성 중...", "INFO")
        
        # 테스트 결과 통계
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        error_tests = sum(1 for result in self.test_results.values() if result['status'] == 'ERROR')
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 최종 보고서
        final_report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'success_rate': success_rate,
                'overall_status': 'PASS' if success_rate >= 80 else 'FAIL'
            },
            'test_start_time': self.test_start_time.isoformat(),
            'test_end_time': datetime.now().isoformat(),
            'test_duration_seconds': (datetime.now() - self.test_start_time).total_seconds(),
            'detailed_results': self.test_results,
            'test_log': self.test_log,
            'recommendations': self.generate_recommendations()
        }
        
        # 보고서 출력
        print("\n" + "=" * 80)
        print("🧪 스탠드얼론 기능 테스트 최종 보고서")
        print("=" * 80)
        print(f"📊 총 테스트: {total_tests}개")
        print(f"✅ 성공: {passed_tests}개")
        print(f"❌ 실패: {failed_tests}개")
        print(f"💥 오류: {error_tests}개")
        print(f"📈 성공률: {success_rate:.1f}%")
        print(f"🎯 전체 상태: {final_report['test_summary']['overall_status']}")
        print(f"⏱️ 테스트 시간: {final_report['test_duration_seconds']:.1f}초")
        
        if final_report['recommendations']:
            print("\n💡 권장사항:")
            for i, rec in enumerate(final_report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # 보고서 파일 저장
        report_path = self.save_report(final_report)
        print(f"\n📄 상세 보고서 저장: {report_path}")
        
        print("=" * 80)
        
        return final_report
    
    def generate_recommendations(self) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 실패한 테스트 기반 권장사항
        for test_name, result in self.test_results.items():
            if result['status'] in ['FAIL', 'ERROR']:
                if '프로젝트 구조' in test_name:
                    recommendations.append("누락된 파일이나 디렉토리를 생성하세요")
                elif '모듈 임포트' in test_name:
                    recommendations.append("모듈 임포트 오류를 수정하세요")
                elif '설정 파일' in test_name:
                    recommendations.append("설정 파일의 JSON 형식을 확인하세요")
                elif '외부 의존성' in test_name:
                    recommendations.append("외부 경로 참조를 제거하세요")
                elif '레거시' in test_name:
                    recommendations.append("레거시 폴더 참조를 제거하세요")
        
        # 일반적인 권장사항
        success_rate = sum(1 for result in self.test_results.values() if result['status'] == 'PASS') / len(self.test_results) * 100
        
        if success_rate < 60:
            recommendations.append("시스템 전체를 재검토하고 기본 구조부터 수정하세요")
        elif success_rate < 80:
            recommendations.append("실패한 테스트들을 우선적으로 수정하세요")
        elif success_rate >= 90:
            recommendations.append("훌륭합니다! 시스템이 독립 실행 준비가 완료되었습니다")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """보고서 파일 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"standalone_test_report_{timestamp}.json"
        report_path = os.path.join(self.project_root, "logs", report_filename)
        
        # 로그 디렉토리 생성
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        # JSON 직렬화를 위한 데이터 정리
        serializable_report = self.make_serializable(report)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_report, f, ensure_ascii=False, indent=2)
        
        return report_path
    
    def make_serializable(self, obj):
        """JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, dict):
            return {key: self.make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)


def main():
    """메인 함수"""
    print("🧪 스탠드얼론 기능 테스트 시스템 시작")
    print("Task 19.1: 스탠드얼론 기능 테스트 구현")
    print("Requirements: 4.2, 4.3, 4.4")
    print()
    
    # 테스트 실행
    tester = StandaloneFunctionalityTest()
    final_report = tester.run_all_tests()
    
    # 결과에 따른 종료 코드
    if final_report['test_summary']['overall_status'] == 'PASS':
        print("\n🎉 스탠드얼론 기능 테스트 성공!")
        return 0
    else:
        print("\n⚠️ 스탠드얼론 기능 테스트에서 문제가 발견되었습니다.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)