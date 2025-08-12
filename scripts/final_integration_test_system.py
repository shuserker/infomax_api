#!/usr/bin/env python3
"""
POSCO 네이밍 컨벤션 표준화 최종 통합 테스트 시스템
Final Integration Test System for POSCO Naming Convention Standardization

이 시스템은 다음을 검증합니다:
- 변경된 시스템의 전체 기능 테스트
- 모든 스크립트 및 프로그램 정상 동작 확인
- 네이밍 일관성 최종 검증
- 사용자 가이드 및 문서 최종 검토

Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1
"""

# SYNTAX_FIX: import posco_news_250808_monitor.log
# SYNTAX_FIX: import system_functionality_verification.py
# SYNTAX_FIX: import test_config.json
import subprocess
# SYNTAX_FIX: import verify_folder_reorganization.py
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import sys
import json
import datetime
import pathlib
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_integration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    details: Optional[Dict] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class FinalIntegrationTestSystem:
    """최종 통합 테스트 시스템"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
self.test_results:_List[TestResult] =  []
        self.watchhamster_version = "v3.0"
        self.posco_news_version = "var_25080_8"
        
        # 예상되는 파일 매핑 (기존 → 새로운)
        self.expected_file_mappings = {
            # 워치햄스터 제어센터 파일들
            ".naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat": "🐹WatchHamster_v3.var_0__Control_Center.bat",
            ".naming_backup/scripts/🐹워치햄스터_통합_관리_센터.bat": "🐹WatchHamster_v3.var_0__Integrated_Center.bat",
            ".naming_backup/scripts/🎛️POSCO_제어센터_실행_v2.bat": "🎛️WatchHamster_v3.var_0__Control_Panel.bat",
            ".naming_backup/scripts/🎛️POSCO_제어센터_Mac실행.command": "WatchHamster_v3.0.log",
            ".naming_backup/scripts/watchhamster_control_center.sh": "watchhamster_v3.var_0__control_center.sh",
            ".naming_backup/scripts/watchhamster_master_control.sh": "watchhamster_v3.var_0__master_control.sh",
            
            # Python 스크립트들
            ".naming_backup/config_data_backup/watchhamster.log": "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py",
"verify_folder_reorganization.py": "demo_watchhamster_v3_v3_0_integration.py",
"final_integration_test_system.py": "test_watchhamster_v3_v3_0_integration.py",
"system_functionality_verification.py": "test_watchhamster_v3_v3_0_notification.py",
            
            # 포스코 뉴스 메인 스크립트들
            "POSCO_News_250808.py": "POSCO_News_250808.py",
            "Monitoring/POSCO_News_250808/posco_main_notifier.py": "POSCO_News_250808.py",
            "posco_continuous_monitor.py": "posco_news_250808_monitor.log",
            
            # 데이터 파일들
            ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_news_data.json": "posco_news_250808_data.json",
            ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_news_cache.json": "posco_news_250808_cache.json",
            ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_news_historical_cache.json": "posco_news_250808_historical.json",
            
            # 문서 파일들
            "📋POSCO_워치햄스터_v2_사용자_가이드.md": "WatchHamster_v3.0.log",
            "🔄POSCO_워치햄스터_마이그레이션_가이드.md": "WatchHamster_v3.0.log",
            "🛠️POSCO_워치햄스터_개발자_가이드.md": "WatchHamster_v3.0.log"
        }
        
        # 예상되는 폴더 매핑
        self.expected_folder_mappings = {
            "Monitoring/Posco_News_mini_v2/": "Monitoring/WatchHamster_v3.0/",
            ".kiro/specs/posco-watchhamster-v2-integration/": ".kiro/specs/watchhamster-v3.0-integration/",
            "Monitoring/Posco_News_mini/": "Monitoring/POSCO_News_250808/"
        }

    def run_all_tests(self) -> Dict:
        """모든 테스트 실행"""
        logger.info("🚀 POSCO 네이밍 컨벤션 표준화 최종 통합 테스트 시작")
        
        # 1. 파일명 표준화 검증 (요구사항 1.1)
        self._test_file_naming_standardization()
        
        # 2. 폴더명 표준화 검증 (요구사항 2.1)
        self._test_folder_naming_standardization()
        
        # 3. 내부 주석 표준화 검증 (요구사항 3.1)
        self._test_comment_standardization()
        
        # 4. 변수명 및 클래스명 표준화 검증 (요구사항 4.1)
        self._test_code_naming_standardization()
        
        # 5. 문서 표준화 검증 (요구사항 5.1)
        self._test_documentation_standardization()
        
        # 6. 로그 및 출력 메시지 표준화 검증 (요구사항 6.1)
        self._test_output_message_standardization()
        
        # 7. 설정 파일 표준화 검증 (요구사항 7.1)
        self._test_config_file_standardization()
        
        # 8. 스크립트 실행 가능성 테스트
        self._test_script_functionality()
        
        # 9. 시스템 통합 테스트
        self._test_system_integration()
        
        # var_1_0. 사용자 가이드 검토
        self._test_user_guide_review()
        
        return self._generate_final_report()

    def _test_file_naming_standardization(self):
        """파일명 표준화 검증 (요구사항 1.1)"""
        logger.info("📁 파일명 표준화 검증 중...")
        
        try:
            # 워치햄스터 관련 파일 검증
            watchhamster_files = []
            posco_news_files = []
            
            for root, dirs, files in os.walk(self.workspace_root):
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.workspace_root)
                    
                    # 워치햄스터 관련 파일 검증
                    if any(keyword in file.lower() for keyword in ['watchhamster', 'watch_hamster']):
                        if 'v3.0' in file or 'v3_0' in file:
                            watchhamster_files.append(str(relative_path))
                        elif any(old_version in file for old_version in ['v2', 'v3', 'mini_v2']):
                            self.test_results.append(TestResult(
                                "File Naming - WatchHamster",
                                "FAIL",
                                f"파일 {relative_path}에 구버전 표기가 남아있음"
                            ))
                    
                    # 포스코 뉴스 관련 파일 검증
                    if any(keyword in file.lower() for keyword in ['posco_news', 'posco-news']):
                        if 'var_25080_8' in file:
                            posco_news_files.append(str(relative_path))
                        elif any(old_version in file for old_version in ['mini', 'v2']):
                            self.test_results.append(TestResult(
                                "File Naming - POSCO News",
                                "FAIL",
                                f"파일 {relative_path}에 구버전 표기가 남아있음"
                            ))
            
            self.test_results.append(TestResult(
                "File Naming Standardization",
                "PASS",
                f"워치햄스터 v3.0 파일 {len(watchhamster_files)}개, 포스코 뉴스 250808 파일 {len(posco_news_files)}개 확인",
                {"watchhamster_files": watchhamster_files, "posco_news_files": posco_news_files}
            ))
            
        except Exception as e:
            self.test_results.append(TestResult(
                "File Naming Standardization",
                "FAIL",
                f"파일명 검증 중 오류: {str(e)}"
            ))

    def _test_folder_naming_standardization(self):
        """폴더명 표준화 검증 (요구사항 2.1)"""
        logger.info("📂 폴더명 표준화 검증 중...")
        
        try:
            standardized_folders = []
            non_standard_folders = []
            
            for root, dirs, files in os.walk(self.workspace_root):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    relative_path = dir_path.relative_to(self.workspace_root)
                    
                    # 워치햄스터 관련 폴더 검증
                    if 'watchhamster' in dir_name.lower():
                        if 'v3.0' in dir_name or 'v3_0' in dir_name:
                            standardized_folders.append(str(relative_path))
                        else:
                            non_standard_folders.append(str(relative_path))
                    
                    # 포스코 뉴스 관련 폴더 검증
                    if 'posco_news' in dir_name.lower() or 'posco-news' in dir_name.lower():
                        if 'var_25080_8' in dir_name:
                            standardized_folders.append(str(relative_path))
                        else:
                            non_standard_folders.append(str(relative_path))
            
            if non_standard_folders:
                self.test_results.append(TestResult(
                    "Folder Naming Standardization",
                    "FAIL",
                    f"표준화되지 않은 폴더 발견: {non_standard_folders}"
                ))
            else:
                self.test_results.append(TestResult(
                    "Folder Naming Standardization",
                    "PASS",
                    f"표준화된 폴더 {len(standardized_folders)}개 확인",
                    {"standardized_folders": standardized_folders}
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Folder Naming Standardization",
                "FAIL",
                f"폴더명 검증 중 오류: {str(e)}"
            ))

    def _test_comment_standardization(self):
        """내부 주석 표준화 검증 (요구사항 3.1)"""
        logger.info("💬 주석 표준화 검증 중...")
        
        try:
            standardized_files = []
            non_standard_files = []
            
            # Python 파일들 검사
            for py_file in self.workspace_root.rglob("*.py"):
                try:
with_open(py_file,_'r',_encoding = 'utf-8') as f:
                        content = f.read()
                        
                    # 워치햄스터 관련 주석 검증
                    if 'watchhamster' in content.lower():
                        if 'v3.0' in content or 'v3_0' in content:
                            standardized_files.append(str(py_file.relative_to(self.workspace_root)))
                        elif any(old_version in content.lower() for old_version in ['v2.0', 'v2', 'mini_v2']):
                            non_standard_files.append(str(py_file.relative_to(self.workspace_root)))
                    
                    # 포스코 뉴스 관련 주석 검증
                    if 'posco_news' in content.lower() or 'posco news' in content.lower():
                        if 'var_25080_8' in content:
                            if str(py_file.relative_to(self.workspace_root)) not in standardized_files:
                                standardized_files.append(str(py_file.relative_to(self.workspace_root)))
                        elif 'mini' in content.lower():
                            if str(py_file.relative_to(self.workspace_root)) not in non_standard_files:
                                non_standard_files.append(str(py_file.relative_to(self.workspace_root)))
                                
                except Exception as e:
                    logger.warning(f"파일 {py_file} 읽기 실패: {e}")
            
            if non_standard_files:
                self.test_results.append(TestResult(
                    "Comment Standardization",
                    "FAIL",
                    f"표준화되지 않은 주석이 있는 파일: {non_standard_files[:5]}..."  # 처음 var_5_개만 표시
                ))
            else:
                self.test_results.append(TestResult(
                    "Comment Standardization",
                    "PASS",
                    f"표준화된 주석을 가진 파일 {len(standardized_files)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Comment Standardization",
                "FAIL",
                f"주석 검증 중 오류: {str(e)}"
            ))

    def _test_code_naming_standardization(self):
        """변수명 및 클래스명 표준화 검증 (요구사항 4.1)"""
        logger.info("🔤 코드 네이밍 표준화 검증 중...")
        
        try:
            standardized_classes = []
            standardized_variables = []
            non_standard_items = []
            
            for py_file in self.workspace_root.rglob("*.py"):
                try:
with_open(py_file,_'r',_encoding = 'utf-8') as f:
                        content = f.read()
                    
                    # 클래스명 검증
                    class_pattern = r'class/s+(/w+)'
                    classes = re.findall(class_pattern, content)
                    
                    for class_name in classes:
                        if 'watchhamster' in class_name.lower():
                            if 'v30' in class_name.lower() or 'v3_0' in class_name.lower():
                                standardized_classes.append(f"{py_file.name}:{class_name}")
                            else:
                                non_standard_items.append(f"{py_file.name}:{class_name}")
                        
                        if 'posconews' in class_name.lower():
                            if 'var_25080_8' in class_name:
                                standardized_classes.append(f"{py_file.name}:{class_name}")
                            else:
                                non_standard_items.append(f"{py_file.name}:{class_name}")
                    
                    # 변수명 검증 (VERSION 상수들)
# SYNTAX_FIX:                     version_pattern = r'(/w*VERSION/w*)/s*=/s*["/']([^"/']+)["/']'
                    versions = re.findall(version_pattern, content)
                    
                    for var_name, version_value in versions:
                        if 'watchhamster' in var_name.lower():
                            if 'v3.0' in version_value:
                                standardized_variables.append(f"{py_file.name}:{var_name}={version_value}")
                            else:
                                non_standard_items.append(f"{py_file.name}:{var_name}={version_value}")
                        
                        if 'posco' in var_name.lower() and 'news' in var_name.lower():
                            if 'var_25080_8' in version_value:
                                standardized_variables.append(f"{py_file.name}:{var_name}={version_value}")
                            else:
                                non_standard_items.append(f"{py_file.name}:{var_name}={version_value}")
                                
                except Exception as e:
                    logger.warning(f"파일 {py_file} 분석 실패: {e}")
            
            if non_standard_items:
                self.test_results.append(TestResult(
                    "Code Naming Standardization",
                    "FAIL",
                    f"표준화되지 않은 코드 네이밍: {non_standard_items[:3]}..."
                ))
            else:
                self.test_results.append(TestResult(
                    "Code Naming Standardization",
                    "PASS",
                    f"표준화된 클래스 {len(standardized_classes)}개, 변수 {len(standardized_variables)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Code Naming Standardization",
                "FAIL",
                f"코드 네이밍 검증 중 오류: {str(e)}"
            ))

    def _test_documentation_standardization(self):
        """문서 표준화 검증 (요구사항 5.1)"""
        logger.info("📚 문서 표준화 검증 중...")
        
        try:
            standardized_docs = []
            non_standard_docs = []
            
            # 마크다운 파일들 검사
            for md_file in self.workspace_root.rglob("*.md"):
                try:
with_open(md_file,_'r',_encoding = 'utf-8') as f:
                        content = f.read()
                    
                    # 제목에서 버전 정보 검증
                    title_lines = [line for line in content.split('/n') if line.startswith('#')]
                    
                    for title in title_lines:
                        if 'watchhamster' in title.lower() or '워치햄스터' in title:
                            if 'v3.0' in title:
                                standardized_docs.append(str(md_file.relative_to(self.workspace_root)))
                                break
                            elif any(old_version in title.lower() for old_version in ['v2.0', 'v2', 'mini']):
                                non_standard_docs.append(str(md_file.relative_to(self.workspace_root)))
                                break
                        
                        if 'posco news' in title.lower() or 'posco_news' in title.lower():
                            if 'var_25080_8' in title:
                                if str(md_file.relative_to(self.workspace_root)) not in standardized_docs:
                                    standardized_docs.append(str(md_file.relative_to(self.workspace_root)))
                                break
                            elif 'mini' in title.lower():
                                if str(md_file.relative_to(self.workspace_root)) not in non_standard_docs:
                                    non_standard_docs.append(str(md_file.relative_to(self.workspace_root)))
                                break
                                
                except Exception as e:
                    logger.warning(f"문서 {md_file} 읽기 실패: {e}")
            
            if non_standard_docs:
                self.test_results.append(TestResult(
                    "Documentation Standardization",
                    "FAIL",
                    f"표준화되지 않은 문서: {non_standard_docs[:3]}..."
                ))
            else:
                self.test_results.append(TestResult(
                    "Documentation Standardization",
                    "PASS",
                    f"표준화된 문서 {len(standardized_docs)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Documentation Standardization",
                "FAIL",
                f"문서 검증 중 오류: {str(e)}"
            ))

    def _test_output_message_standardization(self):
        """로그 및 출력 메시지 표준화 검증 (요구사항 6.1)"""
        logger.info("📢 출력 메시지 표준화 검증 중...")
        
        try:
            standardized_messages = []
            non_standard_messages = []
            
            # Python 파일에서 print, logger 메시지 검사
            for py_file in self.workspace_root.rglob("*.py"):
                try:
with_open(py_file,_'r',_encoding = 'utf-8') as f:
                        content = f.read()
                    
                    # print 문과 logger 메시지 찾기
                    print_pattern = r'print/s*/(["/']([^"/']*(?:watchhamster|posco.*news)[^"/']*)["/']')
                    logger_pattern = r'logger/./w+/(["/']([^"/']*(?:watchhamster|posco.*news)[^"/']*)["/']')
                    
                    messages = re.findall(print_pattern, content, re.IGNORECASE)
                    messages.extend(re.findall(logger_pattern, content, re.IGNORECASE))
                    
                    for message in messages:
                        if 'watchhamster' in message.lower():
                            if 'v3.0' in message:
                                standardized_messages.append(f"{py_file.name}: {message[:50]}...")
                            elif any(old_version in message.lower() for old_version in ['v2', 'mini']):
                                non_standard_messages.append(f"{py_file.name}: {message[:50]}...")
                        
                        if 'posco' in message.lower() and 'news' in message.lower():
                            if 'var_25080_8' in message:
                                standardized_messages.append(f"{py_file.name}: {message[:50]}...")
                            elif 'mini' in message.lower():
                                non_standard_messages.append(f"{py_file.name}: {message[:50]}...")
                                
                except Exception as e:
                    logger.warning(f"파일 {py_file} 메시지 검사 실패: {e}")
            
            if non_standard_messages:
                self.test_results.append(TestResult(
                    "Output Message Standardization",
                    "FAIL",
                    f"표준화되지 않은 메시지: {non_standard_messages[:2]}..."
                ))
            else:
                self.test_results.append(TestResult(
                    "Output Message Standardization",
                    "PASS",
                    f"표준화된 출력 메시지 {len(standardized_messages)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Output Message Standardization",
                "FAIL",
                f"출력 메시지 검증 중 오류: {str(e)}"
            ))

    def _test_config_file_standardization(self):
        """설정 파일 표준화 검증 (요구사항 7.1)"""
        logger.info("⚙️ 설정 파일 표준화 검증 중...")
        
        try:
            standardized_configs = []
            non_standard_configs = []
            
            # JSON 설정 파일들 검사
            for json_file in self.workspace_root.rglob("*.json"):
                try:
with_open(json_file,_'r',_encoding = 'utf-8') as f:
                        content = f.read()
                        data = json.loads(content)
                    
                    # 버전 정보 필드 검사
                    version_found = False
                    
                    def check_version_in_dict(d, path=""):
                        nonlocal version_found
                        if isinstance(d, dict):
                            for key, value in d.items():
                                current_path = f"{path}.{key}" if path else key
                                
                                if 'version' in key.lower():
                                    if isinstance(value, str):
                                        if 'watchhamster' in current_path.lower() and 'v3.0' in value:
                                            version_found = True
                                        elif 'posco' in current_path.lower() and '250808' in value:
                                            version_found = True
                                        elif any(old_version in value for old_version in ['v2', 'mini']):
                                            non_standard_configs.append(f"{json_file.name}:{current_path}={value}")
                                
                                if isinstance(value, (dict, list)):
                                    check_version_in_dict(value, current_path)
                        elif isinstance(d, list):
                            for i, item in enumerate(d):
                                check_version_in_dict(item, f"{path}[{i}]")
                    
                    check_version_in_dict(data)
                    
                    if version_found:
                        standardized_configs.append(str(json_file.relative_to(self.workspace_root)))
                        
                except Exception as e:
                    logger.warning(f"JSON 파일 {json_file} 검사 실패: {e}")
            
            if non_standard_configs:
                self.test_results.append(TestResult(
                    "Config File Standardization",
                    "FAIL",
                    f"표준화되지 않은 설정: {non_standard_configs[:3]}..."
                ))
            else:
                self.test_results.append(TestResult(
                    "Config File Standardization",
                    "PASS",
                    f"표준화된 설정 파일 {len(standardized_configs)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Config File Standardization",
                "FAIL",
                f"설정 파일 검증 중 오류: {str(e)}"
            ))

    def _test_script_functionality(self):
        """스크립트 실행 가능성 테스트"""
        logger.info("🔧 스크립트 기능 테스트 중...")
        
        try:
            executable_scripts = []
            failed_scripts = []
            
            # Python 스크립트 구문 검사
            for py_file in self.workspace_root.rglob("*.py"):
                if any(keyword in py_file.name.lower() for keyword in ['watchhamster', 'posco_news']):
                    try:
                        # 구문 검사
with_open(py_file,_'r',_encoding = 'utf-8') as f:
                            content = f.read()
                        
                        compile(content, str(py_file), 'exec')
                        executable_scripts.append(str(py_file.relative_to(self.workspace_root)))
                        
                    except SyntaxError as e:
                        failed_scripts.append(f"{py_file.name}: {str(e)}")
                    except Exception as e:
                        logger.warning(f"스크립트 {py_file} 검사 실패: {e}")
            
            # Shell 스크립트 기본 검사
            for sh_file in self.workspace_root.rglob("*.sh"):
                if any(keyword in sh_file.name.lower() for keyword in ['watchhamster', 'posco']):
                    try:
                        # 실행 권한 확인
                        if os.access(sh_file, os.X_OK):
                            executable_scripts.append(str(sh_file.relative_to(self.workspace_root)))
                        else:
                            failed_scripts.append(f"{sh_file.name}: 실행 권한 없음")
                    except Exception as e:
                        logger.warning(f"Shell 스크립트 {sh_file} 검사 실패: {e}")
            
            if failed_scripts:
                self.test_results.append(TestResult(
                    "Script Functionality",
                    "FAIL",
                    f"실행 불가능한 스크립트: {failed_scripts[:3]}..."
                ))
            else:
                self.test_results.append(TestResult(
                    "Script Functionality",
                    "PASS",
                    f"실행 가능한 스크립트 {len(executable_scripts)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Script Functionality",
                "FAIL",
                f"스크립트 기능 테스트 중 오류: {str(e)}"
            ))

    def _test_system_integration(self):
        """시스템 통합 테스트"""
        logger.info("🔗 시스템 통합 테스트 중...")
        
        try:
            integration_checks = []
            
            # 1. 모듈 import .naming_backup/scripts/🧪POSCO_테스트_실행.bat
            try:
                # 네이밍 컨벤션 매니저 import .naming_backup/scripts/🧪POSCO_테스트_실행.bat
                if (self.workspace_root / "naming_convention_manager.py").exists():
                    sys.path.insert(0, str(self.workspace_root))
# SYNTAX_FIX:                     import naming_convention_manager.py
            except Exception as e:
            
            # 2. 파일 시스템 일관성 검사
            try:
                # 참조 무결성 검사 (파일 간 참조가 올바른지)
                broken_references = []
                
                for py_file in self.workspace_root.rglob("*.py"):
                    try:
with_open(py_file,_'r',_encoding = 'utf-8') as f:
                            content = f.read()
                        
                        # import 문에서 파일 참조 검사
# SYNTAX_FIX:                         import_pattern = r'from/s+(/w+)/s+import|import/s+(/w+)'
                        imports = re.findall(import_pattern, content)
                        
                        for imp in imports:
                            module_name = imp[0] or imp[1]
                            if module_name and not module_name.startswith('_'):
                                module_file = self.workspace_root / f"{module_name}.py"
                                if not module_file.exists() and module_name not in ['os', 'sys', 'json', 'datetime']:
                                    broken_references.append(f"{py_file.name} -> {module_name}")
                                    
                    except Exception as e:
                        logger.warning(f"참조 검사 실패 {py_file}: {e}")
                
                if broken_references:
                    integration_checks.append(f"깨진 참조 발견: {broken_references[:2]}...")
                else:
                    integration_checks.append("파일 참조 무결성 확인")
                    
            except Exception as e:
                integration_checks.append(f"참조 무결성 검사 실패: {e}")
            
            # 3. 버전 일관성 검사
            try:
                version_consistency = True
                watchhamster_versions = set()
                posco_news_versions = set()
                
                for py_file in self.workspace_root.rglob("*.py"):
                    try:
with_open(py_file,_'r',_encoding = 'utf-8') as f:
                            content = f.read()
                        
                        # 버전 상수 찾기
# SYNTAX_FIX:                         version_pattern = r'(/w*VERSION/w*)/s*=/s*["/']([^"/']+)["/']'
                        versions = re.findall(version_pattern, content)
                        
                        for var_name, version_value in versions:
                            if 'watchhamster' in var_name.lower():
                                watchhamster_versions.add(version_value)
                            elif 'posco' in var_name.lower() and 'news' in var_name.lower():
                                posco_news_versions.add(version_value)
                                
                    except Exception as e:
                        logger.warning(f"버전 검사 실패 {py_file}: {e}")
                
                if len(watchhamster_versions) > 1:
                    integration_checks.append(f"워치햄스터 버전 불일치: {watchhamster_versions}")
                    version_consistency = False
                
                if len(posco_news_versions) > 1:
                    integration_checks.append(f"포스코 뉴스 버전 불일치: {posco_news_versions}")
                    version_consistency = False
                
                if version_consistency:
                    integration_checks.append("버전 일관성 확인")
                    
            except Exception as e:
                integration_checks.append(f"버전 일관성 검사 실패: {e}")
            
            self.test_results.append(TestResult(
                "System Integration",
                "PASS" if all("실패" not in check and "불일치" not in check for check in integration_checks) else "FAIL",
                f"통합 검사 결과: {'; '.join(integration_checks)}"
            ))
            
        except Exception as e:
            self.test_results.append(TestResult(
                "System Integration",
                "FAIL",
                f"시스템 통합 테스트 중 오류: {str(e)}"
            ))

    def _test_user_guide_review(self):
        """사용자 가이드 검토"""
        logger.info("📖 사용자 가이드 검토 중...")
        
        try:
            guide_files = []
            guide_issues = []
            
            # 가이드 관련 파일들 찾기
            guide_patterns = ['*guide*.md', '*가이드*.md', '*manual*.md', '*메뉴얼*.md', 'README.md']
            
            for pattern in guide_patterns:
                for guide_file in self.workspace_root.rglob(pattern):
                    try:
with_open(guide_file,_'r',_encoding = 'utf-8') as f:
                            content = f.read()
                        
                        # 가이드 품질 검사
                        issues = []
                        
                        # 1. 제목 구조 검사
                        headers = [line for line in content.split('/n') if line.startswith('#')]
                        if len(headers) < 3:
                            issues.append("제목 구조 부족")
                        
                        # 2. 버전 정보 일관성 검사
                        if 'watchhamster' in content.lower() or '워치햄스터' in content:
                            if 'v3.0' not in content:
                                issues.append("워치햄스터 v3.0 버전 정보 누락")
                        
                        if 'posco news' in content.lower() or 'posco_news' in content.lower():
                            if 'var_25080_8' not in content:
                                issues.append("포스코 뉴스 250808 버전 정보 누락")
                        
                        # 3. 기본 섹션 검사
                        required_sections = ['설치', '사용법', '설정']
                        missing_sections = []
                        for section in required_sections:
                            if section not in content and section.upper() not in content:
                                missing_sections.append(section)
                        
                        if missing_sections:
                            issues.append(f"필수 섹션 누락: {missing_sections}")
                        
                        if issues:
                            guide_issues.extend([f"{guide_file.name}: {issue}" for issue in issues])
                        else:
                            guide_files.append(str(guide_file.relative_to(self.workspace_root)))
                            
                    except Exception as e:
                        logger.warning(f"가이드 파일 {guide_file} 검토 실패: {e}")
            
            if guide_issues:
                self.test_results.append(TestResult(
                    "User Guide Review",
                    "FAIL",
                    f"가이드 문제점: {guide_issues[:3]}..."
                ))
            else:
                self.test_results.append(TestResult(
                    "User Guide Review",
                    "PASS",
                    f"검토 완료된 가이드 {len(guide_files)}개 확인"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "User Guide Review",
                "FAIL",
                f"사용자 가이드 검토 중 오류: {str(e)}"
            ))

    def _generate_final_report(self) -> Dict:
        """최종 보고서 생성"""
        logger.info("📊 최종 보고서 생성 중...")
        
        # 테스트 결과 통계
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r.status == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 보고서 데이터
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": round(success_rate, 2)
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "status": result.status,
                    "message": result.message,
                    "timestamp": result.timestamp,
                    "details": result.details
                }
                for result in self.test_results
            ],
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            "recommendations": self._generate_recommendations(),
            "generated_at": datetime.now().isoformat()
        }
        
        # JSON 보고서 저장
        report_file = self.workspace_root / "final_integration_test_report.json"
with_open(report_file,_'w',_encoding = 'utf-8') as f:
json.dump(report,_f,_ensure_ascii = False, indent=2)
        
        # HTML 보고서 생성
        self._generate_html_report(report)
        
        logger.info(f"✅ 최종 통합 테스트 완료 - 성공률: {success_rate:.1f}%")
        logger.info(f"📄 보고서 저장: {report_file}")
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r.status == "FAIL"]
        
        for test in failed_tests:
            if "File Naming" in test.test_name:
                recommendations.append("파일명 표준화 작업을 완료하여 모든 파일이 v3.0/250808 규칙을 따르도록 하세요.")
            elif "Folder Naming" in test.test_name:
                recommendations.append("폴더명 표준화 작업을 완료하여 일관된 폴더 구조를 구축하세요.")
            elif "Comment" in test.test_name:
                recommendations.append("코드 주석의 버전 정보를 표준 형식으로 업데이트하세요.")
            elif "Code Naming" in test.test_name:
                recommendations.append("클래스명과 변수명을 표준 네이밍 규칙에 맞게 수정하세요.")
            elif "Documentation" in test.test_name:
                recommendations.append("문서의 제목과 내용에서 버전 정보를 표준화하세요.")
            elif "Output Message" in test.test_name:
                recommendations.append("시스템 출력 메시지의 버전 표기를 통일하세요.")
            elif "Config File" in test.test_name:
                recommendations.append("설정 파일의 버전 정보 필드를 표준 형식으로 업데이트하세요.")
            elif "Script Functionality" in test.test_name:
                recommendations.append("스크립트 구문 오류를 수정하고 실행 권한을 확인하세요.")
            elif "System Integration" in test.test_name:
                recommendations.append("시스템 통합 문제를 해결하여 모든 컴포넌트가 올바르게 연동되도록 하세요.")
            elif "User Guide" in test.test_name:
                recommendations.append("사용자 가이드의 내용을 보완하고 버전 정보를 업데이트하세요.")
        
        if not recommendations:
            recommendations.append("모든 테스트가 통과했습니다. 네이밍 컨벤션 표준화가 성공적으로 완료되었습니다.")
        
        return list(set(recommendations))  # 중복 제거

    def _generate_html_report(self, report: Dict):
        """HTML 보고서 생성"""
        html_content = f""
<!DOCTYPE html>
<html_lang = "ko">
<head>
<meta_charset = "UTF-8">
<meta_name = "viewport" content="width=device-width, initial-scale=1.0">
    <title>POSCO 네이밍 컨벤션 표준화 최종 통합 테스트 보고서</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: var_20_px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #var_2_c3e50; text-align: center; margin-bottom: var_30_px; }}
        h2 {{ color: #var_34495_e; border-bottom: var_2_px solid #var_3498_db; padding-bottom: var_10_px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 var_10_px 0; font-size: var_2_em; }}
        .summary-card p {{ margin: 0; opacity: 0.9; }}
        .status-pass {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .status-fail {{ background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }}
        .test-results {{ margin-bottom: var_30_px; }}
        .test-item {{ background-color: #f8f9fa; margin-bottom: var_15_px; padding: var_20_px; border-radius: var_8_px; border-left: var_5_px solid #var_3498_db; }}
        .test-item.pass {{ border-left-color: #var_27_ae60; }}
        .test-item.fail {{ border-left-color: #e74c3c; }}
        .test-item.skip {{ border-left-color: #f39c12; }}
        .test-name {{ font-weight: bold; font-size: 1.var_1_em; margin-bottom: var_10_px; }}
        .test-message {{ color: #var_66_6; margin-bottom: var_10_px; }}
        .test-timestamp {{ font-size: 0.var_9_em; color: #var_99_9; }}
        .recommendations {{ background-color: #fff3cd; border: var_1_px solid #ffeaa7; border-radius: var_8_px; padding: var_20_px; }}
        .recommendations ul {{ margin: var_10_px 0; padding-left: var_20_px; }}
        .recommendations li {{ margin-bottom: var_10_px; }}
        .footer {{ text-align: center; margin-top: var_30_px; color: #var_66_6; font-size: 0.var_9_em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 POSCO 네이밍 컨벤션 표준화 최종 통합 테스트 보고서</h1>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{report['test_summary']['total_tests']}</h3>
                <p>총 테스트</p>
            </div>
            <div class="summary-card status-pass">
                <h3>{report['test_summary']['passed']}</h3>
                <p>통과</p>
            </div>
            <div class="summary-card status-fail">
                <h3>{report['test_summary']['failed']}</h3>
                <p>실패</p>
            </div>
            <div class="summary-card">
                <h3>{report['test_summary']['success_rate']}%</h3>
                <p>성공률</p>
            </div>
        </div>
        
        <h2>📋 테스트 결과</h2>
        <div class="test-results">
"""
        
        for result in report['test_results']:
            status_class = result['status'].lower()
html_content_+ =  f""
            <div class="test-item {status_class}">
                <div class="test-name">{result['test_name']} - {result['status']}</div>
                <div class="test-message">{result['message']}</div>
                <div class="test-timestamp">실행 시간: {result['timestamp']}</div>
            </div>
"""
        
html_content_+ =  f""
        </div>
        
        <h2>💡 권장사항</h2>
        <div class="recommendations">
            <ul>
"""
        
        for recommendation in report['recommendations']:
html_content_+ =  f"<li>{recommendation}</li>"
        
html_content_+ =  f""
            </ul>
        </div>
        
        <div class="footer">
            <p>보고서 생성 시간: {report['generated_at']}</p>
            <p>POSCO WatchHamster v3.0 & POSCO News var_25080_8 네이밍 컨벤션 표준화 프로젝트</p>
        </div>
    </div>
</body>
</html>
"""
        
        html_file = self.workspace_root / "final_integration_test_report.html"
with_open(html_file,_'w',_encoding = 'utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📄 HTML 보고서 저장: {html_file}")


def main():
    """메인 실행 함수"""
    print("🚀 POSCO 네이밍 컨벤션 표준화 최종 통합 테스트 시작")
    print("=" * 60)
    
    test_system = FinalIntegrationTestSystem()
    report = test_system.run_all_tests()
    
print("/n"_+_" = " * 60)
    print("📊 최종 테스트 결과 요약")
    print("=" * 60)
    print(f"총 테스트: {report['test_summary']['total_tests']}")
    print(f"통과: {report['test_summary']['passed']}")
    print(f"실패: {report['test_summary']['failed']}")
    print(f"건너뜀: {report['test_summary']['skipped']}")
    print(f"성공률: {report['test_summary']['success_rate']}%")
    print(f"전체 상태: {report['overall_status']}")
    
    if report['overall_status'] == "FAIL":
        print("/n❌ 일부 테스트가 실패했습니다. 상세 내용은 보고서를 확인하세요.")
        return 1
    else:
        print("/n✅ 모든 테스트가 성공적으로 완료되었습니다!")
        return 0


if __name__ == "__main__":
    sys.exit(main())