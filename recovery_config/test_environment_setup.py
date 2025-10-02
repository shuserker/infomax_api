#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 환경 설정 테스트
환경 설정이 올바르게 되어 있는지 검증
"""

import os
import sys
import unittest
import platform
import subprocess
from pathlib import Path
import json
import tempfile

class TestEnvironmentSetup(unittest.TestCase):
    """환경 설정 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.workspace_root = Path(".")
        self.recovery_config = self.workspace_root / "recovery_config"
        self.platform = platform.system().lower()
        
        # 필수 환경 변수들
        self.required_env_vars = ["PATH"]
        
        # 필수 디렉토리들
        self.required_directories = [
            "recovery_config",
            ".kiro",
            "docs"
        ]
        
        # 필수 파일들
        self.required_files = [
            "recovery_config/environment_settings.json",
            "recovery_config/platform_environment_handler.py"
        ]
    
    def test_python_environment(self):
        """Python 환경 테스트"""
        print("\n🐍 Python 환경을 테스트하고 있습니다...")
        
        # Python 버전 확인
        python_version = sys.version_info
        self.assertGreaterEqual(python_version.major, 3, "Python 3 이상이 필요합니다")
        self.assertGreaterEqual(python_version.minor, 6, "Python 3.6 이상이 필요합니다")
        print(f"   ✅ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Python 실행 가능 여부 확인
        python_cmd = "python3" if self.platform != "windows" else "python"
        try:
            result = subprocess.run([python_cmd, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, f"{python_cmd} 명령어를 실행할 수 없습니다")
            print(f"   ✅ {python_cmd} 명령어 실행 가능")
        except Exception as e:
            self.fail(f"{python_cmd} 실행 오류: {e}")
    
    def test_required_directories(self):
        """필수 디렉토리 존재 테스트"""
        print("\n📁 필수 디렉토리를 테스트하고 있습니다...")
        
        for directory in self.required_directories:
            dir_path = self.workspace_root / directory
            self.assertTrue(dir_path.exists(), f"필수 디렉토리가 없습니다: {directory}")
            self.assertTrue(dir_path.is_dir(), f"디렉토리가 아닙니다: {directory}")
            print(f"   ✅ 디렉토리 존재: {directory}")
    
    def test_required_files(self):
        """필수 파일 존재 테스트"""
        print("\n📄 필수 파일을 테스트하고 있습니다...")
        
        for file_path in self.required_files:
            full_path = self.workspace_root / file_path
            self.assertTrue(full_path.exists(), f"필수 파일이 없습니다: {file_path}")
            self.assertTrue(full_path.is_file(), f"파일이 아닙니다: {file_path}")
            
            # 파일이 비어있지 않은지 확인
            file_size = full_path.stat().st_size
            self.assertGreater(file_size, 0, f"파일이 비어있습니다: {file_path}")
            print(f"   ✅ 파일 존재: {file_path} ({file_size} bytes)")
    
    def test_environment_variables(self):
        """환경 변수 테스트"""
        print("\n⚙️ 환경 변수를 테스트하고 있습니다...")
        
        for env_var in self.required_env_vars:
            self.assertIn(env_var, os.environ, f"필수 환경 변수가 없습니다: {env_var}")
            env_value = os.environ[env_var]
            self.assertGreater(len(env_value), 0, f"환경 변수가 비어있습니다: {env_var}")
            print(f"   ✅ 환경 변수 존재: {env_var}")
    
    def test_file_permissions(self):
        """파일 권한 테스트"""
        print("\n🔐 파일 권한을 테스트하고 있습니다...")
        
        # Python 파일들의 읽기 권한 확인
        for py_file in self.recovery_config.glob("*.py"):
            self.assertTrue(os.access(py_file, os.R_OK), f"읽기 권한이 없습니다: {py_file}")
            print(f"   ✅ 읽기 권한: {py_file.name}")
        
        # 실행 파일들의 권한 확인 (Mac/Linux)
        if self.platform != "windows":
            for exec_file in self.workspace_root.glob("*.sh"):
                if exec_file.exists():
                    self.assertTrue(os.access(exec_file, os.X_OK), f"실행 권한이 없습니다: {exec_file}")
                    print(f"   ✅ 실행 권한: {exec_file.name}")
            
            for exec_file in self.workspace_root.glob("*.command"):
                if exec_file.exists():
                    self.assertTrue(os.access(exec_file, os.X_OK), f"실행 권한이 없습니다: {exec_file}")
                    print(f"   ✅ 실행 권한: {exec_file.name}")
    
    def test_json_configuration_files(self):
        """JSON 설정 파일 테스트"""
        print("\n📋 JSON 설정 파일을 테스트하고 있습니다...")
        
        # environment_settings.json 테스트
        env_settings_path = self.recovery_config / "environment_settings.json"
        if env_settings_path.exists():
            try:
                with open(env_settings_path, 'r', encoding='utf-8') as f:
                    env_settings = json.load(f)
                
                self.assertIsInstance(env_settings, dict, "환경 설정이 딕셔너리가 아닙니다")
                print(f"   ✅ JSON 파일 유효: environment_settings.json")
                
                # 필수 키 확인
                if "workspace_root" in env_settings:
                    print(f"   ✅ workspace_root 설정됨")
                
            except json.JSONDecodeError as e:
                self.fail(f"JSON 파일 파싱 오류: {e}")
            except Exception as e:
                self.fail(f"JSON 파일 읽기 오류: {e}")
    
    def test_python_module_imports(self):
        """Python 모듈 import 테스트"""
        print("\n🔗 Python 모듈 import를 테스트하고 있습니다...")
        
        # 표준 라이브러리 모듈들
        standard_modules = [
            "os", "sys", "json", "pathlib", "datetime", 
            "subprocess", "platform", "unittest"
        ]
        
        for module_name in standard_modules:
            try:
                __import__(module_name)
                print(f"   ✅ 모듈 import 성공: {module_name}")
            except ImportError as e:
                self.fail(f"표준 모듈 import 실패: {module_name} - {e}")
        
        # 복구 모듈들 import 테스트
        recovery_modules = []
        for py_file in self.recovery_config.glob("*.py"):
            if not py_file.name.startswith("test_") and py_file.name != "__init__.py":
                module_name = py_file.stem
                recovery_modules.append(module_name)
        
        # sys.path에 recovery_config 추가
        if str(self.recovery_config) not in sys.path:
            sys.path.insert(0, str(self.recovery_config))
        
        for module_name in recovery_modules[:5]:  # 처음 5개만 테스트
            try:
                __import__(module_name)
                print(f"   ✅ 복구 모듈 import 성공: {module_name}")
            except ImportError as e:
                print(f"   ⚠️ 복구 모듈 import 실패: {module_name} - {e}")
            except Exception as e:
                print(f"   ⚠️ 복구 모듈 오류: {module_name} - {e}")
    
    def test_file_encoding(self):
        """파일 인코딩 테스트"""
        print("\n📝 파일 인코딩을 테스트하고 있습니다...")
        
        # UTF-8 인코딩 테스트
        test_content = "테스트 한글 내용 🎉 Test English Content"
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # UTF-8로 읽기 테스트
            with open(temp_file, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            self.assertEqual(test_content, read_content, "UTF-8 인코딩/디코딩 실패")
            print(f"   ✅ UTF-8 인코딩 지원")
            
        finally:
            os.unlink(temp_file)
    
    def test_workspace_structure(self):
        """워크스페이스 구조 테스트"""
        print("\n🏗️ 워크스페이스 구조를 테스트하고 있습니다...")
        
        # 기본 구조 확인
        expected_structure = {
            "recovery_config": "directory",
            ".kiro": "directory",
            "docs": "directory"
        }
        
        for item_name, item_type in expected_structure.items():
            item_path = self.workspace_root / item_name
            
            if item_type == "directory":
                self.assertTrue(item_path.exists() and item_path.is_dir(), 
                              f"디렉토리가 없습니다: {item_name}")
                print(f"   ✅ 디렉토리 구조: {item_name}/")
            elif item_type == "file":
                self.assertTrue(item_path.exists() and item_path.is_file(),
                              f"파일이 없습니다: {item_name}")
                print(f"   ✅ 파일 구조: {item_name}")
    
    def test_platform_compatibility(self):
        """플랫폼 호환성 테스트"""
        print("\n🔄 플랫폼 호환성을 테스트하고 있습니다...")
        
        # 플랫폼 감지
        detected_platform = platform.system()
        self.assertIn(detected_platform, ["Windows", "Darwin", "Linux"], 
                     f"지원되지 않는 플랫폼: {detected_platform}")
        print(f"   ✅ 플랫폼 감지: {detected_platform}")
        
        # 플랫폼별 Python 명령어 테스트
        if detected_platform == "Windows":
            python_cmd = "python"
        else:
            python_cmd = "python3"
        
        try:
            result = subprocess.run([python_cmd, "-c", "print('Hello')"], 
                                  capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, f"{python_cmd} 실행 실패")
            self.assertEqual(result.stdout.strip(), "Hello", "Python 출력 오류")
            print(f"   ✅ {python_cmd} 명령어 호환성")
        except Exception as e:
            self.fail(f"플랫폼 호환성 테스트 실패: {e}")

class EnvironmentSetupTester:
    """환경 설정 테스트 실행기"""
    
    def __init__(self):
        self.test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnvironmentSetup)
    
    def run_tests(self):
        """테스트 실행"""
        print("🧪 POSCO 시스템 환경 설정 테스트를 시작합니다...")
        print("=" * 60)
        
        # 테스트 실행
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(self.test_suite)
        
        print("=" * 60)
        
        # 결과 요약
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 테스트 결과 요약:")
        print(f"   - 총 테스트: {total_tests}개")
        print(f"   - 성공: {total_tests - failures - errors}개")
        print(f"   - 실패: {failures}개")
        print(f"   - 오류: {errors}개")
        print(f"   - 성공률: {success_rate:.1f}%")
        
        if result.wasSuccessful():
            print("🎉 모든 환경 설정 테스트가 통과했습니다!")
            return True
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 위의 오류를 확인하세요.")
            return False

def main():
    """메인 실행 함수"""
    tester = EnvironmentSetupTester()
    success = tester.run_tests()
    
    if success:
        print("\n✅ 환경 설정이 올바르게 구성되었습니다!")
    else:
        print("\n❌ 환경 설정에 문제가 있습니다. 오류를 수정하세요.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)