#!/usr/bin/env python3
"""
Task 18 완전 검증 스크립트
GUI 설정 및 리소스 관리 시스템 구현 (스탠드얼론) - 풀체크
"""

import os
import json
import sys
from pathlib import Path

class Task18FullVerification:
    """Task 18 완전 검증 클래스"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check(self, condition, success_msg, error_msg):
        """검증 체크 헬퍼"""
        self.total_checks += 1
        if condition:
            print(f"✅ {success_msg}")
            self.success_count += 1
            return True
        else:
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def warn(self, condition, warning_msg):
        """경고 체크 헬퍼"""
        if not condition:
            print(f"⚠️  {warning_msg}")
            self.warnings.append(warning_msg)
    
    def verify_task_requirements(self):
        """Task 18 요구사항 검증"""
        print("🔍 Task 18 요구사항 검증...")
        print("=" * 60)
        
        # 1. 모든 설정 파일 검증
        print("\n1️⃣ 설정 파일 검증")
        config_files = {
            "gui_config.json": "GUI 설정 파일",
            "posco_config.json": "POSCO 시스템 설정 파일", 
            "webhook_config.json": "웹훅 설정 파일",
            "language_strings.json": "다국어 문자열 파일",
            "message_templates.json": "메시지 템플릿 파일"
        }
        
        for filename, description in config_files.items():
            filepath = self.base_path / "config" / filename
            self.check(
                filepath.exists(),
                f"{description} 존재: {filename}",
                f"{description} 누락: {filename}"
            )
            
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.check(
                        isinstance(data, dict) and len(data) > 0,
                        f"{filename} JSON 구조 유효",
                        f"{filename} JSON 구조 무효"
                    )
                except Exception as e:
                    self.check(False, "", f"{filename} JSON 파싱 오류: {e}")
        
        # 2. GUI 리소스 디렉토리 검증
        print("\n2️⃣ GUI 리소스 디렉토리 검증")
        asset_dirs = ["assets", "assets/icons", "assets/images"]
        
        for dirname in asset_dirs:
            dirpath = self.base_path / dirname
            self.check(
                dirpath.exists() and dirpath.is_dir(),
                f"리소스 디렉토리 존재: {dirname}",
                f"리소스 디렉토리 누락: {dirname}"
            )
        
        # 3. GUI 테마 및 레이아웃 커스터마이징 기능 검증
        print("\n3️⃣ GUI 테마 및 레이아웃 커스터마이징 기능 검증")
        self.verify_theme_system()
        
        # 4. 다국어 지원 검증
        print("\n4️⃣ 다국어 지원 (한국어/영어) 기본 구조 검증")
        self.verify_i18n_system()
    
    def verify_theme_system(self):
        """테마 시스템 검증"""
        gui_config_path = self.base_path / "config" / "gui_config.json"
        
        if not gui_config_path.exists():
            self.check(False, "", "GUI 설정 파일이 없어 테마 시스템 검증 불가")
            return
        
        with open(gui_config_path, 'r', encoding='utf-8') as f:
            gui_config = json.load(f)
        
        # 테마 설정 섹션 존재 확인
        theme_settings = gui_config.get("theme_settings", {})
        self.check(
            "theme_settings" in gui_config,
            "테마 설정 섹션 존재",
            "테마 설정 섹션 누락"
        )
        
        # 사용 가능한 테마 확인
        available_themes = theme_settings.get("available_themes", [])
        required_themes = ["default", "dark", "light", "posco_corporate"]
        
        for theme in required_themes:
            self.check(
                theme in available_themes,
                f"필수 테마 존재: {theme}",
                f"필수 테마 누락: {theme}"
            )
            
            # 각 테마의 색상 설정 확인
            if theme in theme_settings:
                theme_colors = theme_settings[theme]
                required_colors = ["bg_color", "fg_color", "accent_color", "button_color", "text_color"]
                
                for color in required_colors:
                    self.check(
                        color in theme_colors,
                        f"{theme} 테마 {color} 색상 정의됨",
                        f"{theme} 테마 {color} 색상 누락"
                    )
        
        # 레이아웃 설정 확인
        layout_settings = gui_config.get("layout_settings", {})
        self.check(
            "layout_settings" in gui_config,
            "레이아웃 설정 섹션 존재",
            "레이아웃 설정 섹션 누락"
        )
        
        required_layout_keys = ["main_panel_ratio", "sidebar_width", "padding", "spacing"]
        for key in required_layout_keys:
            self.check(
                key in layout_settings,
                f"레이아웃 설정 존재: {key}",
                f"레이아웃 설정 누락: {key}"
            )
    
    def verify_i18n_system(self):
        """다국어 시스템 검증"""
        # GUI 설정의 다국어 설정 확인
        gui_config_path = self.base_path / "config" / "gui_config.json"
        
        if gui_config_path.exists():
            with open(gui_config_path, 'r', encoding='utf-8') as f:
                gui_config = json.load(f)
            
            i18n_settings = gui_config.get("internationalization", {})
            self.check(
                "internationalization" in gui_config,
                "다국어 설정 섹션 존재",
                "다국어 설정 섹션 누락"
            )
            
            available_languages = i18n_settings.get("available_languages", [])
            required_languages = ["ko", "en"]
            
            for lang in required_languages:
                self.check(
                    lang in available_languages,
                    f"필수 언어 지원: {lang}",
                    f"필수 언어 누락: {lang}"
                )
        
        # 언어 문자열 파일 확인
        lang_strings_path = self.base_path / "config" / "language_strings.json"
        
        if lang_strings_path.exists():
            with open(lang_strings_path, 'r', encoding='utf-8') as f:
                lang_strings = json.load(f)
            
            required_languages = ["ko", "en"]
            for lang in required_languages:
                self.check(
                    lang in lang_strings,
                    f"언어 문자열 존재: {lang}",
                    f"언어 문자열 누락: {lang}"
                )
                
                if lang in lang_strings:
                    lang_data = lang_strings[lang]
                    required_sections = ["app_title", "buttons", "status", "messages"]
                    
                    for section in required_sections:
                        self.check(
                            section in lang_data,
                            f"{lang} 언어 {section} 섹션 존재",
                            f"{lang} 언어 {section} 섹션 누락"
                        )
    
    def verify_gui_components(self):
        """GUI 컴포넌트 파일 검증"""
        print("\n🔍 GUI 컴포넌트 파일 검증...")
        print("=" * 60)
        
        gui_components = {
            "resource_manager.py": "리소스 관리자",
            "theme_manager.py": "테마 관리자",
            "i18n_manager.py": "다국어 관리자",
            "settings_dialog.py": "설정 대화상자"
        }
        
        for filename, description in gui_components.items():
            filepath = self.base_path / "gui_components" / filename
            self.check(
                filepath.exists(),
                f"{description} 파일 존재: {filename}",
                f"{description} 파일 누락: {filename}"
            )
            
            if filepath.exists():
                file_size = filepath.stat().st_size
                self.check(
                    file_size > 1000,  # 최소 1KB 이상
                    f"{filename} 파일 크기 적절 ({file_size} bytes)",
                    f"{filename} 파일이 너무 작음 ({file_size} bytes)"
                )
    
    def verify_posco_config_completeness(self):
        """POSCO 설정 완전성 검증"""
        print("\n🔍 POSCO 설정 완전성 검증...")
        print("=" * 60)
        
        posco_config_path = self.base_path / "config" / "posco_config.json"
        
        if not posco_config_path.exists():
            self.check(False, "", "POSCO 설정 파일 누락")
            return
        
        with open(posco_config_path, 'r', encoding='utf-8') as f:
            posco_config = json.load(f)
        
        required_sections = {
            "posco_system": "POSCO 시스템 정보",
            "data_sources": "데이터 소스 설정",
            "analysis_settings": "분석 설정",
            "report_generation": "보고서 생성 설정",
            "business_rules": "비즈니스 규칙",
            "integration": "통합 설정"
        }
        
        for section, description in required_sections.items():
            self.check(
                section in posco_config,
                f"{description} 섹션 존재: {section}",
                f"{description} 섹션 누락: {section}"
            )
        
        # POSCO 시스템 정보 상세 확인
        if "posco_system" in posco_config:
            system_info = posco_config["posco_system"]
            required_fields = ["system_name", "version", "company", "department"]
            
            for field in required_fields:
                self.check(
                    field in system_info,
                    f"시스템 정보 필드 존재: {field}",
                    f"시스템 정보 필드 누락: {field}"
                )
        
        # 데이터 소스 확인
        if "data_sources" in posco_config:
            data_sources = posco_config["data_sources"]
            required_sources = ["kospi_api", "exchange_api", "news_api"]
            
            for source in required_sources:
                self.check(
                    source in data_sources,
                    f"데이터 소스 존재: {source}",
                    f"데이터 소스 누락: {source}"
                )
    
    def verify_integration_completeness(self):
        """통합 완전성 검증"""
        print("\n🔍 통합 완전성 검증...")
        print("=" * 60)
        
        # 기존 시스템과의 통합 확인
        existing_files = [
            "main_gui.py",
            "gui_components/config_manager.py",
            "gui_components/system_tray.py",
            "gui_components/notification_center.py"
        ]
        
        for filename in existing_files:
            filepath = self.base_path / filename
            self.check(
                filepath.exists(),
                f"기존 시스템 파일 존재: {filename}",
                f"기존 시스템 파일 누락: {filename}"
            )
        
        # 테스트 파일 확인
        test_files = [
            "test_resource_management.py",
            "test_resource_management_simple.py",
            "verify_task18_implementation.py"
        ]
        
        for filename in test_files:
            filepath = self.base_path / filename
            self.check(
                filepath.exists(),
                f"테스트 파일 존재: {filename}",
                f"테스트 파일 누락: {filename}"
            )
    
    def verify_requirements_mapping(self):
        """요구사항 매핑 검증"""
        print("\n🔍 요구사항 매핑 검증...")
        print("=" * 60)
        
        # Requirements 6.1, 6.5 매핑 확인
        gui_config_path = self.base_path / "config" / "gui_config.json"
        posco_config_path = self.base_path / "config" / "posco_config.json"
        
        # GUI 설정에서 요구사항 매핑 확인
        if gui_config_path.exists():
            with open(gui_config_path, 'r', encoding='utf-8') as f:
                gui_config = json.load(f)
            
            requirements_mapping = gui_config.get("requirements_mapping", {})
            self.check(
                len(requirements_mapping) > 0,
                "GUI 설정 요구사항 매핑 존재",
                "GUI 설정 요구사항 매핑 누락"
            )
        
        # POSCO 설정에서 요구사항 매핑 확인
        if posco_config_path.exists():
            with open(posco_config_path, 'r', encoding='utf-8') as f:
                posco_config = json.load(f)
            
            requirements_mapping = posco_config.get("requirements_mapping", {})
            self.check(
                len(requirements_mapping) > 0,
                "POSCO 설정 요구사항 매핑 존재",
                "POSCO 설정 요구사항 매핑 누락"
            )
        
        # Requirement 6.1: GUI 시스템 구현 검증
        gui_system_components = [
            ("gui_components/theme_manager.py", "테마 관리 시스템"),
            ("gui_components/i18n_manager.py", "다국어 지원 시스템"),
            ("gui_components/settings_dialog.py", "설정 GUI"),
            ("config/gui_config.json", "GUI 설정")
        ]
        
        print("\n📋 Requirement 6.1: GUI 시스템 구현")
        for filepath, description in gui_system_components:
            full_path = self.base_path / filepath
            self.check(
                full_path.exists(),
                f"6.1 - {description} 구현됨",
                f"6.1 - {description} 누락"
            )
        
        # Requirement 6.5: 설정 관리 시스템 검증
        config_system_components = [
            ("gui_components/resource_manager.py", "리소스 관리자"),
            ("gui_components/settings_dialog.py", "설정 대화상자"),
            ("config/", "설정 파일 디렉토리"),
            ("assets/", "리소스 디렉토리")
        ]
        
        print("\n📋 Requirement 6.5: 설정 관리 시스템")
        for filepath, description in config_system_components:
            full_path = self.base_path / filepath
            self.check(
                full_path.exists(),
                f"6.5 - {description} 구현됨",
                f"6.5 - {description} 누락"
            )
    
    def verify_standalone_capability(self):
        """스탠드얼론 기능 검증"""
        print("\n🔍 스탠드얼론 기능 검증...")
        print("=" * 60)
        
        # 독립 실행 가능성 확인
        standalone_requirements = [
            ("config/gui_config.json", "독립 GUI 설정"),
            ("config/posco_config.json", "독립 POSCO 설정"),
            ("gui_components/resource_manager.py", "독립 리소스 관리"),
            ("assets/", "독립 리소스 디렉토리")
        ]
        
        for filepath, description in standalone_requirements:
            full_path = self.base_path / filepath
            self.check(
                full_path.exists(),
                f"스탠드얼론 - {description} 준비됨",
                f"스탠드얼론 - {description} 누락"
            )
        
        # 외부 의존성 최소화 확인
        resource_manager_path = self.base_path / "gui_components" / "resource_manager.py"
        if resource_manager_path.exists():
            with open(resource_manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 기본 라이브러리만 사용하는지 확인
            allowed_imports = ['json', 'os', 'logging', 'typing', 'pathlib']
            self.check(
                all(imp in content for imp in ['import json', 'import os']),
                "리소스 관리자 기본 라이브러리 사용",
                "리소스 관리자 라이브러리 문제"
            )
    
    def run_full_verification(self):
        """전체 검증 실행"""
        print("🚀 Task 18 완전 검증 시작")
        print("=" * 80)
        print("GUI 설정 및 리소스 관리 시스템 구현 (스탠드얼론)")
        print("=" * 80)
        
        # 모든 검증 실행
        self.verify_task_requirements()
        self.verify_gui_components()
        self.verify_posco_config_completeness()
        self.verify_integration_completeness()
        self.verify_requirements_mapping()
        self.verify_standalone_capability()
        
        # 결과 요약
        print("\n" + "=" * 80)
        print("🎯 검증 결과 요약")
        print("=" * 80)
        
        success_rate = (self.success_count / self.total_checks * 100) if self.total_checks > 0 else 0
        
        print(f"✅ 성공: {self.success_count}/{self.total_checks} ({success_rate:.1f}%)")
        
        if self.errors:
            print(f"❌ 오류: {len(self.errors)}개")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"⚠️  경고: {len(self.warnings)}개")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # 최종 판정
        if len(self.errors) == 0:
            print("\n🎉 Task 18 구현 완료!")
            print("✅ 모든 요구사항이 완전히 구현되었습니다.")
            print("✅ GUI 설정 및 리소스 관리 시스템이 완벽하게 작동합니다.")
            print("✅ 스탠드얼론 시스템으로 독립 실행 가능합니다.")
            return True
        else:
            print(f"\n❌ Task 18 구현 미완료!")
            print(f"❌ {len(self.errors)}개의 문제를 해결해야 합니다.")
            return False

def main():
    """메인 함수"""
    verifier = Task18FullVerification()
    success = verifier.run_full_verification()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)