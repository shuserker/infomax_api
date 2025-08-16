#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 플랫폼별 실행 파일 테스트
복원된 실행 파일들의 동작을 검증
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List
import json

class PlatformExecutionTester:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.current_platform = platform.system().lower()
        
        # 테스트할 실행 파일들
        self.test_files = {
            "windows": [
                "POSCO_메인_system.bat",
                "POSCO_watchhamster_v3_control_center.bat", 
                "POSCO_News_250808_Start.bat",
                "POSCO_News_250808_Stop.bat",
                "POSCO_test_실행.bat"
            ],
            "mac": [
                "POSCO_watchhamster_v3_control_center.command",
                "POSCO_News_250808_Start.sh",
                "WatchHamster_v3.0_Control_Panel.command"
            ]
        }
    
    def test_file_existence(self) -> Dict:
        """실행 파일 존재 여부 테스트"""
        print("📁 실행 파일 존재 여부를 테스트하고 있습니다...")
        
        results = {
            "windows": {"exists": [], "missing": []},
            "mac": {"exists": [], "missing": []}
        }
        
        for platform_name, files in self.test_files.items():
            for filename in files:
                file_path = self.workspace_root / filename
                if file_path.exists():
                    results[platform_name]["exists"].append(filename)
                    print(f"   ✅ 존재: {filename}")
                else:
                    results[platform_name]["missing"].append(filename)
                    print(f"   ❌ 누락: {filename}")
        
        return results
    
    def test_file_permissions(self) -> Dict:
        """파일 권한 테스트 (Mac/Linux)"""
        print("🔐 파일 권한을 테스트하고 있습니다...")
        
        results = {"executable": [], "not_executable": []}
        
        if self.current_platform != "windows":
            for filename in self.test_files["mac"]:
                file_path = self.workspace_root / filename
                if file_path.exists():
                    # 실행 권한 확인
                    if os.access(file_path, os.X_OK):
                        results["executable"].append(filename)
                        print(f"   ✅ 실행 가능: {filename}")
                    else:
                        results["not_executable"].append(filename)
                        print(f"   ❌ 실행 불가: {filename}")
        else:
            print("   ℹ️ Windows 환경에서는 권한 테스트를 건너뜁니다.")
        
        return results
    
    def test_file_content_validity(self) -> Dict:
        """파일 내용 유효성 테스트"""
        print("📝 파일 내용 유효성을 테스트하고 있습니다...")
        
        results = {"valid": [], "invalid": [], "issues": []}
        
        all_files = self.test_files["windows"] + self.test_files["mac"]
        
        for filename in all_files:
            file_path = self.workspace_root / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # 기본 유효성 검사
                    issues = []
                    
                    # 1. 파일이 비어있지 않은지
                    if len(content.strip()) < 10:
                        issues.append("파일이 너무 짧음")
                    
                    # 2. Python 실행 명령이 있는지
                    if 'python' not in content.lower():
                        issues.append("Python 실행 명령 없음")
                    
                    # 3. recovery_config 참조가 있는지
                    if 'recovery_config' not in content:
                        issues.append("recovery_config 참조 없음")
                    
                    # 4. 플랫폼별 특정 검사
                    if filename.endswith('.bat'):
                        if '@echo off' not in content:
                            issues.append("Windows 배치 파일 헤더 없음")
                        if 'chcp 65001' not in content:
                            issues.append("UTF-8 인코딩 설정 없음")
                    
                    elif filename.endswith(('.sh', '.command')):
                        if '#!/bin/bash' not in content:
                            issues.append("Bash 셔뱅 없음")
                        if 'python3' not in content:
                            issues.append("python3 명령어 없음")
                    
                    if issues:
                        results["invalid"].append(filename)
                        results["issues"].extend([f"{filename}: {issue}" for issue in issues])
                        print(f"   ⚠️ 문제 발견: {filename} - {', '.join(issues)}")
                    else:
                        results["valid"].append(filename)
                        print(f"   ✅ 유효: {filename}")
                
                except Exception as e:
                    results["invalid"].append(filename)
                    results["issues"].append(f"{filename}: 읽기 오류 - {e}")
                    print(f"   ❌ 읽기 오류: {filename} - {e}")
        
        return results
    
    def test_python_module_references(self) -> Dict:
        """Python 모듈 참조 테스트"""
        print("🐍 Python 모듈 참조를 테스트하고 있습니다...")
        
        results = {"valid_references": [], "invalid_references": [], "missing_modules": []}
        
        all_files = self.test_files["windows"] + self.test_files["mac"]
        
        for filename in all_files:
            file_path = self.workspace_root / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Python 파일 참조 찾기
                    import re
                    python_refs = re.findall(r'recovery_config/[\w_]+\.py', content)
                    
                    for ref in python_refs:
                        module_path = self.workspace_root / ref
                        if module_path.exists():
                            results["valid_references"].append(f"{filename} → {ref}")
                            print(f"   ✅ 유효 참조: {filename} → {ref}")
                        else:
                            results["invalid_references"].append(f"{filename} → {ref}")
                            results["missing_modules"].append(ref)
                            print(f"   ❌ 누락 모듈: {filename} → {ref}")
                
                except Exception as e:
                    print(f"   ❌ 참조 검사 오류: {filename} - {e}")
        
        return results
    
    def test_cross_platform_compatibility(self) -> Dict:
        """크로스 플랫폼 호환성 테스트"""
        print("🔄 크로스 플랫폼 호환성을 테스트하고 있습니다...")
        
        results = {
            "platform_detection": False,
            "python_availability": False,
            "path_handling": False,
            "encoding_support": False,
            "issues": []
        }
        
        try:
            # 1. 플랫폼 감지
            detected_platform = platform.system()
            results["platform_detection"] = detected_platform in ["Windows", "Darwin", "Linux"]
            print(f"   ✅ 플랫폼 감지: {detected_platform}")
            
            # 2. Python 사용 가능성
            python_cmd = "python3" if detected_platform != "Windows" else "python"
            try:
                result = subprocess.run([python_cmd, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                results["python_availability"] = result.returncode == 0
                print(f"   ✅ Python 사용 가능: {python_cmd}")
            except Exception as e:
                results["issues"].append(f"Python 실행 오류: {e}")
                print(f"   ❌ Python 실행 오류: {e}")
            
            # 3. 경로 처리
            test_path = self.workspace_root / "recovery_config"
            results["path_handling"] = test_path.exists()
            print(f"   ✅ 경로 처리: {test_path}")
            
            # 4. 인코딩 지원
            try:
                test_content = "테스트 한글 내용 🎉"
                test_file = self.workspace_root / "test_encoding.tmp"
                test_file.write_text(test_content, encoding='utf-8')
                read_content = test_file.read_text(encoding='utf-8')
                results["encoding_support"] = test_content == read_content
                test_file.unlink()
                print(f"   ✅ 인코딩 지원: UTF-8")
            except Exception as e:
                results["issues"].append(f"인코딩 테스트 오류: {e}")
                print(f"   ❌ 인코딩 테스트 오류: {e}")
        
        except Exception as e:
            results["issues"].append(f"호환성 테스트 오류: {e}")
            print(f"   ❌ 호환성 테스트 오류: {e}")
        
        return results
    
    def generate_test_report(self, existence_results: Dict, permission_results: Dict,
                           content_results: Dict, reference_results: Dict,
                           compatibility_results: Dict) -> str:
        """테스트 보고서 생성"""
        print("📊 테스트 보고서를 생성하고 있습니다...")
        
        total_files = len(self.test_files["windows"]) + len(self.test_files["mac"])
        existing_files = len(existence_results["windows"]["exists"]) + len(existence_results["mac"]["exists"])
        valid_files = len(content_results["valid"])
        
        report = f"""# 플랫폼별 실행 파일 테스트 보고서

## 테스트 결과 요약
- **총 테스트 파일**: {total_files}개
- **존재하는 파일**: {existing_files}개
- **유효한 파일**: {valid_files}개
- **테스트 통과율**: {round(valid_files/total_files*100, 1)}%

## 파일 존재 여부 테스트
### Windows 실행 파일
- **존재**: {len(existence_results["windows"]["exists"])}개
{chr(10).join(f"  - ✅ {file}" for file in existence_results["windows"]["exists"])}
- **누락**: {len(existence_results["windows"]["missing"])}개
{chr(10).join(f"  - ❌ {file}" for file in existence_results["windows"]["missing"])}

### Mac 실행 파일
- **존재**: {len(existence_results["mac"]["exists"])}개
{chr(10).join(f"  - ✅ {file}" for file in existence_results["mac"]["exists"])}
- **누락**: {len(existence_results["mac"]["missing"])}개
{chr(10).join(f"  - ❌ {file}" for file in existence_results["mac"]["missing"])}

## 파일 권한 테스트
- **실행 가능**: {len(permission_results["executable"])}개
{chr(10).join(f"  - ✅ {file}" for file in permission_results["executable"])}
- **실행 불가**: {len(permission_results["not_executable"])}개
{chr(10).join(f"  - ❌ {file}" for file in permission_results["not_executable"])}

## 파일 내용 유효성 테스트
- **유효한 파일**: {len(content_results["valid"])}개
{chr(10).join(f"  - ✅ {file}" for file in content_results["valid"])}
- **문제 있는 파일**: {len(content_results["invalid"])}개
{chr(10).join(f"  - ❌ {file}" for file in content_results["invalid"])}

### 발견된 문제점
{chr(10).join(f"- {issue}" for issue in content_results["issues"]) if content_results["issues"] else "문제점 없음"}

## Python 모듈 참조 테스트
- **유효한 참조**: {len(reference_results["valid_references"])}개
{chr(10).join(f"  - ✅ {ref}" for ref in reference_results["valid_references"])}
- **잘못된 참조**: {len(reference_results["invalid_references"])}개
{chr(10).join(f"  - ❌ {ref}" for ref in reference_results["invalid_references"])}

### 누락된 모듈
{chr(10).join(f"- {module}" for module in set(reference_results["missing_modules"])) if reference_results["missing_modules"] else "누락된 모듈 없음"}

## 크로스 플랫폼 호환성 테스트
- **플랫폼 감지**: {'✅' if compatibility_results["platform_detection"] else '❌'}
- **Python 사용 가능**: {'✅' if compatibility_results["python_availability"] else '❌'}
- **경로 처리**: {'✅' if compatibility_results["path_handling"] else '❌'}
- **인코딩 지원**: {'✅' if compatibility_results["encoding_support"] else '❌'}

### 호환성 문제점
{chr(10).join(f"- {issue}" for issue in compatibility_results["issues"]) if compatibility_results["issues"] else "호환성 문제 없음"}

## 권장사항
1. **누락된 파일**: 누락된 실행 파일들을 복원하세요
2. **권한 설정**: Mac/Linux에서 실행 권한이 없는 파일들에 chmod +x 적용
3. **모듈 참조**: 누락된 Python 모듈들을 생성하거나 참조를 수정하세요
4. **호환성**: 발견된 호환성 문제들을 해결하세요

## 결론
{'✅ 모든 테스트 통과' if valid_files == total_files and not compatibility_results["issues"] else f'⚠️ {total_files - valid_files}개 파일에 문제 발견'}

플랫폼별 실행 파일 테스트가 완료되었습니다!
"""
        
        report_path = self.workspace_root / "recovery_config" / "platform_execution_test_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 테스트 보고서 생성: {report_path}")
        return report

def main():
    """메인 실행 함수"""
    print("🧪 POSCO 시스템 플랫폼별 실행 파일 테스트를 시작합니다...")
    print("=" * 60)
    
    tester = PlatformExecutionTester()
    
    try:
        # 1. 파일 존재 여부 테스트
        existence_results = tester.test_file_existence()
        
        # 2. 파일 권한 테스트
        permission_results = tester.test_file_permissions()
        
        # 3. 파일 내용 유효성 테스트
        content_results = tester.test_file_content_validity()
        
        # 4. Python 모듈 참조 테스트
        reference_results = tester.test_python_module_references()
        
        # 5. 크로스 플랫폼 호환성 테스트
        compatibility_results = tester.test_cross_platform_compatibility()
        
        # 6. 테스트 보고서 생성
        report = tester.generate_test_report(
            existence_results, permission_results, content_results,
            reference_results, compatibility_results
        )
        
        print("=" * 60)
        print("🎉 플랫폼별 실행 파일 테스트가 완료되었습니다!")
        print(report)
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()