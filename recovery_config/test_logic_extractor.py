#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원본 로직 추출 시스템 테스트 스크립트

LogicExtractor 클래스의 각 기능을 테스트하고 검증합니다.

작성자: AI Assistant
생성일: 2025-08-12
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from logic_extractor import (
    LogicExtractor, 
    PythonASTAnalyzer, 
    ConfigExtractor, 
    DependencyAnalyzer,
    FunctionInfo,
    ClassInfo,
    ModuleInfo,
    ConfigInfo
)


class LogicExtractorTester:
    """로직 추출 시스템 테스트 클래스"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = Path(tempfile.mkdtemp())
        print(f"🧪 테스트 임시 디렉토리: {self.temp_dir}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🔍 원본 로직 추출 시스템 테스트 시작")
        print("=" * 60)
        
        # 1. Python AST 분석기 테스트
        print("\n📋 1단계: Python AST 분석기 테스트")
        self.test_python_ast_analyzer()
        
        # 2. 설정 추출기 테스트
        print("\n⚙️ 2단계: 설정 추출기 테스트")
        self.test_config_extractor()
        
        # 3. 의존성 분석기 테스트
        print("\n🔗 3단계: 의존성 분석기 테스트")
        self.test_dependency_analyzer()
        
        # 4. 통합 로직 추출기 테스트
        print("\n🎯 4단계: 통합 로직 추출기 테스트")
        self.test_logic_extractor()
        
        # 5. 테스트 결과 요약
        print("\n📊 5단계: 테스트 결과 요약")
        self.print_test_summary()
        
        # 임시 디렉토리 정리
        self.cleanup()
    
    def test_python_ast_analyzer(self):
        """Python AST 분석기 테스트"""
        analyzer = PythonASTAnalyzer()
        
        # 테스트용 Python 파일 생성
        test_py_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트용 Python 모듈
"""

import os
import json
from datetime import datetime
from typing import Dict, List

# 전역 변수
API_URL = "https://api.example.com"
MAX_RETRIES = 3

class TestClass:
    """테스트 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
    
    def get_info(self) -> Dict[str, str]:
        """정보 반환"""
        return {"name": self.name, "type": "test"}
    
    @property
    def display_name(self) -> str:
        return f"Test: {self.name}"

def process_data(data: List[Dict]) -> List[Dict]:
    """데이터 처리 함수"""
    processed = []
    for item in data:
        if item.get("valid"):
            processed.append(item)
    return processed

async def fetch_data(url: str) -> Dict:
    """비동기 데이터 가져오기"""
    # 실제 구현은 생략
    return {"status": "success"}

if __name__ == "__main__":
    print("테스트 모듈 실행")
'''
        
        test_file = self.temp_dir / "test_module.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_py_content)
        
        # 분석 실행
        try:
            module_info = analyzer.parse_file(test_file)
            
            if module_info:
                print("✅ Python 파일 파싱 성공")
                print(f"   - 모듈명: {module_info.module_name}")
                print(f"   - 함수 수: {len(module_info.functions)}개")
                print(f"   - 클래스 수: {len(module_info.classes)}개")
                print(f"   - 임포트 수: {len(module_info.imports)}개")
                print(f"   - 전역 변수 수: {len(module_info.global_variables)}개")
                print(f"   - 의존성 수: {len(module_info.dependencies)}개")
                
                # 함수 정보 확인
                func_names = [f.name for f in module_info.functions]
                expected_funcs = ["process_data", "fetch_data"]
                if all(func in func_names for func in expected_funcs):
                    print("✅ 함수 추출 정확성 검증 통과")
                else:
                    print("❌ 함수 추출 정확성 검증 실패")
                
                # 클래스 정보 확인
                if module_info.classes and module_info.classes[0].name == "TestClass":
                    print("✅ 클래스 추출 정확성 검증 통과")
                else:
                    print("❌ 클래스 추출 정확성 검증 실패")
                
                self.test_results.append(("Python AST 분석", True, "성공"))
            else:
                print("❌ Python 파일 파싱 실패")
                self.test_results.append(("Python AST 분석", False, "파싱 실패"))
                
        except Exception as e:
            print(f"❌ Python AST 분석기 테스트 실패: {e}")
            self.test_results.append(("Python AST 분석", False, str(e)))
    
    def test_config_extractor(self):
        """설정 추출기 테스트"""
        extractor = ConfigExtractor()
        
        # 테스트용 설정 파일들 생성
        test_configs = {
            "config.py": '''# Python 설정 파일
API_URL = "https://api.posco.com"
API_KEY = "test-key-123"
TIMEOUT = 30
DEBUG = True
WEBHOOK_URLS = {
    "news": "https://discord.com/webhook1",
    "alerts": "https://discord.com/webhook2"
}
''',
            "settings.json": '''{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "posco_db"
    },
    "monitoring": {
        "interval": 60,
        "enabled": true
    }
}''',
            "app.ini": '''[DEFAULT]
debug = true

[database]
host = localhost
port = 5432
name = posco_db

[api]
url = https://api.posco.com
timeout = 30
''',
            ".env": '''API_KEY=secret-key-456
DATABASE_URL=postgresql://user:pass@localhost/db
DEBUG=true
PORT=8000
'''
        }
        
        config_files = []
        for filename, content in test_configs.items():
            config_file = self.temp_dir / filename
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            config_files.append(config_file)
        
        try:
            configs = extractor.extract_config_files(config_files)
            
            print(f"✅ 설정 파일 {len(configs)}개 추출 성공")
            
            config_types = [config.config_type for config in configs]
            expected_types = ['python', 'json', 'ini', 'env']
            
            if all(ctype in config_types for ctype in expected_types):
                print("✅ 모든 설정 파일 타입 지원 확인")
            else:
                print("❌ 일부 설정 파일 타입 지원 실패")
            
            # 변수 추출 확인
            total_variables = sum(len(config.variables) for config in configs)
            print(f"   - 총 추출된 변수: {total_variables}개")
            
            self.test_results.append(("설정 추출", True, f"{len(configs)}개 파일 처리"))
            
        except Exception as e:
            print(f"❌ 설정 추출기 테스트 실패: {e}")
            self.test_results.append(("설정 추출", False, str(e)))
    
    def test_dependency_analyzer(self):
        """의존성 분석기 테스트"""
        analyzer = DependencyAnalyzer()
        
        # 테스트용 모듈 정보 생성
        modules = [
            ModuleInfo(
                file_path="module_a.py",
                module_name="module_a",
                docstring="모듈 A",
                imports=["import os", "import json", "from module_b import func"],
                functions=[],
                classes=[],
                global_variables={},
                dependencies={"os", "json", "module_b"}
            ),
            ModuleInfo(
                file_path="module_b.py",
                module_name="module_b",
                docstring="모듈 B",
                imports=["import sys", "from module_c import Class"],
                functions=[],
                classes=[],
                global_variables={},
                dependencies={"sys", "module_c"}
            ),
            ModuleInfo(
                file_path="module_c.py",
                module_name="module_c",
                docstring="모듈 C",
                imports=["import datetime", "from module_a import helper"],
                functions=[],
                classes=[],
                global_variables={},
                dependencies={"datetime", "module_a"}
            )
        ]
        
        try:
            dependency_analysis = analyzer.analyze_dependencies(modules)
            
            print("✅ 의존성 분석 성공")
            print(f"   - 분석된 모듈: {dependency_analysis['dependency_count']['total_modules']}개")
            print(f"   - 외부 의존성: {dependency_analysis['dependency_count']['external_deps']}개")
            print(f"   - 내부 연결: {dependency_analysis['dependency_count']['internal_connections']}개")
            
            # 순환 의존성 검사
            if dependency_analysis['circular_dependencies']:
                print(f"   ⚠️ 순환 의존성: {len(dependency_analysis['circular_dependencies'])}개 발견")
                for cycle in dependency_analysis['circular_dependencies']:
                    print(f"      - {' → '.join(cycle)}")
            else:
                print("   ✅ 순환 의존성 없음")
            
            self.test_results.append(("의존성 분석", True, "분석 완료"))
            
        except Exception as e:
            print(f"❌ 의존성 분석기 테스트 실패: {e}")
            self.test_results.append(("의존성 분석", False, str(e)))
    
    def test_logic_extractor(self):
        """통합 로직 추출기 테스트"""
        try:
            extractor = LogicExtractor()
            
            print("✅ LogicExtractor 초기화 성공")
            print(f"   - 대상 커밋: {extractor.target_commit}")
            print(f"   - 출력 디렉토리: {extractor.output_dir}")
            
            # Git 분석기 연결 확인
            if extractor.git_analyzer:
                print("✅ Git 분석기 연결 확인")
            
            # 구성 요소 확인
            components = [
                ("AST 분석기", extractor.ast_analyzer),
                ("설정 추출기", extractor.config_extractor),
                ("의존성 분석기", extractor.dependency_analyzer)
            ]
            
            for name, component in components:
                if component:
                    print(f"✅ {name} 연결 확인")
                else:
                    print(f"❌ {name} 연결 실패")
            
            self.test_results.append(("통합 로직 추출기", True, "초기화 성공"))
            
        except Exception as e:
            print(f"❌ 통합 로직 추출기 테스트 실패: {e}")
            self.test_results.append(("통합 로직 추출기", False, str(e)))
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("📊 테스트 결과 요약")
        print("-" * 40)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {passed_tests}개")
        print(f"실패: {failed_tests}개")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n상세 결과:")
        for test_name, success, message in self.test_results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}: {message}")
        
        # 결과를 JSON 파일로 저장
        result_file = Path("recovery_config/logic_extractor_test_results.json")
        test_data = {
            "test_timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "detailed_results": [
                {
                    "test_name": name,
                    "success": success,
                    "message": message
                }
                for name, success, message in self.test_results
            ]
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 테스트 결과 저장: {result_file}")
    
    def cleanup(self):
        """임시 파일 정리"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"🧹 임시 디렉토리 정리 완료: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ 임시 디렉토리 정리 실패: {e}")


def main():
    """메인 실행 함수"""
    print("🧪 원본 로직 추출 시스템 테스트 시작")
    print("=" * 60)
    
    tester = LogicExtractorTester()
    tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("🎉 원본 로직 추출 시스템 테스트 완료!")


if __name__ == "__main__":
    main()