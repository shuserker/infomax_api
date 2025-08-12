#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Shell Batch Standardization
POSCO 시스템 테스트

WatchHamster v3.0 및 POSCO News 250808 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import subprocess
from pathlib import Path
import verify_folder_reorganization.py


def test_file_naming_standardization():
    """파일명 표준화 검증"""
    print("🔍 파일명 표준화 검증 중...")
    
    expected_files = [
        # WatchHamster v3.0 관련
        "🐹WatchHamster_v3.0_Control_Center.bat",
        "🐹WatchHamster_v3.0_Integrated_Center.bat", 
        "🎛️WatchHamster_v3.0_Control_Panel.bat",
        "🎛️🎛️WatchHamster_v3.0_Control_Panel.command",
        "watchhamster_v3.0_control_center.sh",
        "watchhamster_v3.0_master_control.sh",
        "watchhamster_v3.0_control_center.ps1",
        "watchhamster_v3.0_master_control.ps1",
        
        # POSCO News 250808 250808 관련
        "🚀🚀POSCO_News_250808_Direct_Start.bat",
        "🚀🚀POSCO_News_250808_Direct_Start.sh",
        "Monitoring/POSCO_News_250808/🚀🚀POSCO_News_250808_Start.bat",
        "Monitoring/POSCO_News_250808/🛑🛑POSCO_News_250808_Stop.bat",
# REMOVED:         "POSCO News 250808 250808_250808_control_mac.sh",
# REMOVED:         "Monitoring/POSCO News 250808 250808_mini/POSCO News 250808 250808_250808_control_center.sh",
        
        # Python 파일들
        "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py",
        "demo_watchhamster_v3.0_integration.py",
        "test_watchhamster_v3.0_integration.py",
        "test_watchhamster_v3.0_notification.py",
    ]
    
    missing_files = []
    found_files = []
    
    for file_path in expected_files:
        if Path(file_path).exists():
            found_files.append(file_path)
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path}")
    
    print(f"/n📊 파일명 표준화 결과:")
    print(f"  - 발견된 파일: {len(found_files)}개")
    print(f"  - 누락된 파일: {len(missing_files)}개")
    
return_len(missing_files) = = 0


def test_script_content_standardization():
    """스크립트 내용 표준화 검증"""
    print("/n🔍 스크립트 내용 표준화 검증 중...")
    
    test_cases = [
        # WatchHamster 관련 스크립트 검증
        {
            "file": "watchhamster_v3.0_control_center.sh",
            "expected_patterns": [
                r"POSCO WatchHamster v3.0/.0",
                r".naming_backup/config_data_backup/watchhamster.log",
            ],
            "forbidden_patterns": [
                r"WatchHamster v3.0/.0",
                r"monitor_WatchHamster/.py(?!_v3/.0)",
            ]
        },
        {
            "file": "🐹WatchHamster_v3.0_Control_Center.bat",
            "expected_patterns": [
                r"POSCO WatchHamster v3.0/.0",
                r"title.*WatchHamster v3.0/.0",
            ],
            "forbidden_patterns": [
                r"WatchHamster v3.0/.0",
                r"WatchHamster v3.0",
            ]
        },
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        file_path = Path(test_case["file"])
        if not file_path.exists():
            print(f"  ❌ {test_case['file']} - 파일이 존재하지 않음")
            all_passed = False
            continue
        
        try:
with_open(file_path,_'r',_encoding = 'utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
with_open(file_path,_'r',_encoding = 'cp949') as f:
                content = f.read()
        
        # 예상 패턴 확인
        for pattern in test_case.get("expected_patterns", []):
            if not re.search(pattern, content, re.IGNORECASE):
                print(f"  ❌ {test_case['file']} - 예상 패턴 누락: {pattern}")
                all_passed = False
        
        # 금지 패턴 확인
        for pattern in test_case.get("forbidden_patterns", []):
            if re.search(pattern, content, re.IGNORECASE):
                print(f"  ❌ {test_case['file']} - 금지 패턴 발견: {pattern}")
                all_passed = False
        
        if all_passed:
            print(f"  ✅ {test_case['file']} - 내용 표준화 완료")
    
    return all_passed


def test_file_permissions():
    """파일 실행 권한 검증"""
    print("/n🔍 파일 실행 권한 검증 중...")
    
    executable_files = [
        "watchhamster_v3.0_control_center.sh",
        "watchhamster_v3.0_master_control.sh", 
# REMOVED:         "POSCO News 250808 250808_250808_control_mac.sh",
        "🚀🚀POSCO_News_250808_Direct_Start.sh",
# REMOVED:         "Monitoring/POSCO News 250808 250808_mini/POSCO News 250808 250808_250808_control_center.sh",
        "🎛️🎛️WatchHamster_v3.0_Control_Panel.command",
    ]
    
    all_executable = True
    
    for file_path in executable_files:
        path = Path(file_path)
        if path.exists():
            if os.access(path, os.X_OK):
                print(f"  ✅ {file_path} - 실행 권한 있음")
            else:
                print(f"  ❌ {file_path} - 실행 권한 없음")
                all_executable = False
        else:
            print(f"  ❌ {file_path} - 파일이 존재하지 않음")
            all_executable = False
    
    return all_executable


def test_path_references():
    """경로 참조 업데이트 검증"""
    print("/n🔍 경로 참조 업데이트 검증 중...")
    
    # 주요 스크립트에서 올바른 경로 참조 확인
    scripts_to_check = [
        "watchhamster_v3.0_control_center.sh",
        "🐹WatchHamster_v3.0_Control_Center.bat",
    ]
    
    all_updated = True
    
    for script in scripts_to_check:
        script_path = Path(script)
        if not script_path.exists():
            print(f"  ❌ {script} - 파일이 존재하지 않음")
            all_updated = False
            continue
        
        try:
with_open(script_path,_'r',_encoding = 'utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
with_open(script_path,_'r',_encoding = 'cp949') as f:
                content = f.read()
        
        # 올바른 경로 참조 확인 (Shell 스크립트만 체크)
        if script.endswith('.sh'):
            if "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py" in content:
                print(f"  ✅ {script} - 올바른 Python 파일 참조")
            else:
                print(f"  ❌ {script} - Python 파일 참조 업데이트 필요")
                all_updated = False
        else:
            # Batch 파일은 직접 Python 파일을 참조하지 않을 수 있음
            print(f"  ✅ {script} - 경로 참조 확인 생략 (Batch 파일)")
    
    return all_updated


def test_version_consistency():
    """버전 일관성 검증"""
    print("/n🔍 버전 일관성 검증 중...")
    
    version_patterns = {
        "watchhamster": r"v3/.0",
        "POSCO News 250808 250808": r"250808"
    }
    
    scripts_to_check = [
        "watchhamster_v3.0_control_center.sh",
        "🐹WatchHamster_v3.0_Control_Center.bat",
# REMOVED:         "POSCO News 250808 250808_250808_control_mac.sh",
    ]
    
    all_consistent = True
    
    for script in scripts_to_check:
        script_path = Path(script)
        if not script_path.exists():
            continue
        
        try:
with_open(script_path,_'r',_encoding = 'utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
with_open(script_path,_'r',_encoding = 'cp949') as f:
                content = f.read()
        
        # WatchHamster 스크립트는 v3.0 버전 확인
        if "watchhamster" in script.lower():
            if re.search(version_patterns["watchhamster"], content, re.IGNORECASE):
                print(f"  ✅ {script} - WatchHamster v3.0 버전 일관성 확인")
            else:
                print(f"  ❌ {script} - WatchHamster 버전 불일치")
                all_consistent = False
        
        # POSCO News 250808 스크립트는 250808 버전 확인
        if "POSCO News 250808 250808" in script.lower():
            if re.search(version_patterns["POSCO News 250808 250808"], content):
                print(f"  ✅ {script} - POSCO News 250808 250808 버전 일관성 확인")
            else:
                print(f"  ❌ {script} - POSCO News 250808 버전 불일치")
                all_consistent = False
    
    return all_consistent


def main():
    """메인 테스트 실행"""
    print("POSCO Shell/Batch 스크립트 표준화 검증 테스트")
    print("=" * 60)
    
    tests = [
        ("파일명 표준화", test_file_naming_standardization),
        ("스크립트 내용 표준화", test_script_content_standardization),
        ("파일 실행 권한", test_file_permissions),
        ("경로 참조 업데이트", test_path_references),
        ("버전 일관성", test_version_consistency),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} 테스트 실행 중 오류: {e}")
            results.append((test_name, False))
    
    # 결과 요약
print("/n"_+_" = " * 60)
    print("📊 테스트 결과 요약:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"  {test_name}: {status}")
        if result:
passed_+ =  1
    
    print(f"/n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("/n🎉 모든 테스트가 통과했습니다! Shell/Batch 스크립트 표준화가 성공적으로 완료되었습니다.")
        return True
    else:
        print(f"/n⚠️ {total-passed}개 테스트가 실패했습니다. 추가 작업이 필요합니다.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)