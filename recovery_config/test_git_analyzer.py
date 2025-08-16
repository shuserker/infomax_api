#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 커밋 분석 도구 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from git_commit_analyzer import GitCommitAnalyzer

def test_git_analyzer():
    """Git 분석기 기본 기능 테스트"""
    print("🧪 Git 커밋 분석 도구 테스트 시작")
    
    analyzer = GitCommitAnalyzer()
    
    # 1. 현재 커밋 정보 테스트
    print("\n1️⃣ 현재 커밋 정보 테스트")
    current_commit = analyzer.get_current_commit()
    if current_commit:
        print(f"✅ 현재 커밋: {current_commit[:8]}...")
        
        commit_info = analyzer.get_commit_info(current_commit)
        if commit_info:
            print(f"✅ 커밋 정보: {commit_info['message']}")
        else:
            print("❌ 커밋 정보 가져오기 실패")
    else:
        print("❌ 현재 커밋 가져오기 실패")
    
    # 2. 정상 커밋 정보 테스트
    print("\n2️⃣ 정상 커밋 정보 테스트")
    target_commit = "a763ef84be08b5b1dab0c0ba20594b141baec7ab"
    target_info = analyzer.get_commit_info(target_commit)
    if target_info:
        print(f"✅ 정상 커밋: {target_info['message']}")
        print(f"✅ 작성자: {target_info['author']}")
        print(f"✅ 날짜: {target_info['date']}")
    else:
        print("❌ 정상 커밋 정보 가져오기 실패")
    
    # 3. 핵심 로직 파일 식별 테스트
    print("\n3️⃣ 핵심 로직 파일 식별 테스트")
    test_files = [
        "posco_main_notifier.py",
        "monitor_WatchHamster_v3.0.py",
        "webhook_sender.py",
        "test_file.py",
        "backup_file.backup",
        "script.sh",
        "config.bat"
    ]
    
    core_files = analyzer.identify_core_logic_files(test_files)
    print(f"✅ 테스트 파일 {len(test_files)}개 중 핵심 로직 파일 {len(core_files)}개 식별:")
    for file in core_files:
        print(f"   - {file}")
    
    # 4. Git 명령어 안전 실행 테스트
    print("\n4️⃣ Git 명령어 안전 실행 테스트")
    success, stdout, stderr = analyzer.execute_git_command(['git', 'status', '--porcelain'])
    if success:
        print("✅ Git 명령어 실행 성공")
        if stdout.strip():
            lines = stdout.strip().split('\n')
            print(f"   변경된 파일 수: {len(lines)}")
        else:
            print("   변경된 파일 없음")
    else:
        print(f"❌ Git 명령어 실행 실패: {stderr}")
    
    print("\n🎉 Git 커밋 분석 도구 테스트 완료!")

if __name__ == "__main__":
    test_git_analyzer()