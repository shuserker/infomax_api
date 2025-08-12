#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 함수 복원 검증 테스트
복원된 웹훅 관련 함수들이 올바르게 작동하는지 검증합니다.
"""

import sys
import os
import re
from datetime import datetime

def test_webhook_functions():
    """복원된 웹훅 함수들 검증"""
    
    print("🔍 웹훅 함수 복원 검증 시작...")
    
    # 대상 파일 경로
    target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
    
    if not os.path.exists(target_file):
        print(f"❌ 대상 파일을 찾을 수 없습니다: {target_file}")
        return False
    
    # 파일 읽기
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 검증할 웹훅 함수 목록
    webhook_functions = [
        "send_status_notification",
        "send_notification", 
        "send_status_report_v2",
        "send_startup_notification_v2",
        "_send_basic_status_notification",
        "send_process_error_v2",
        "send_recovery_success_v2",
        "execute_integrated_report_notification",
        "should_send_status_notification",
        "send_critical_alert_v2",
        "send_enhanced_status_notification",
        "_send_hourly_status_notification"
    ]
    
    test_results = {}
    
    print("\n📋 웹훅 함수 존재 여부 검증:")
    print("-" * 50)
    
    for func_name in webhook_functions:
        # 함수 정의 패턴 검색
        pattern = rf'def {func_name}\s*\('
        match = re.search(pattern, content)
        
        if match:
            test_results[func_name] = "✅ 존재"
            print(f"✅ {func_name}: 발견됨")
        else:
            test_results[func_name] = "❌ 누락"
            print(f"❌ {func_name}: 누락됨")
    
    print("\n🔍 메시지 포맷 검증:")
    print("-" * 50)
    
    # 1. 줄바꿈 문자 검증
    wrong_linebreaks = content.count('/n')
    if wrong_linebreaks == 0:
        print("✅ 줄바꿈 문자: 올바름 (\\n 사용)")
    else:
        print(f"❌ 줄바꿈 문자: {wrong_linebreaks}개의 잘못된 '/n' 발견")
    
    # 2. POSCO 워치햄스터 제품명 검증
    product_names = ['POSCO 워치햄스터', 'POSCO WatchHamster', '워치햄스터']
    found_names = []
    for name in product_names:
        if name in content:
            found_names.append(name)
    
    if found_names:
        print(f"✅ 제품명: 확인됨 ({', '.join(found_names)})")
    else:
        print("❌ 제품명: 누락됨")
    
    # 3. 웹훅 URL 형식 검증
    webhook_url_pattern = r'https://[^/]+\.dooray\.com/services/\d+/\d+/[A-Za-z0-9_-]+'
    if re.search(webhook_url_pattern, content):
        print("✅ 웹훅 URL: 올바른 형식 확인됨")
    else:
        print("❌ 웹훅 URL: 올바른 형식을 찾을 수 없음")
    
    # 4. 메시지 구조 검증 (기본적인 패턴)
    message_patterns = [
        r'botName.*워치햄스터',  # 봇 이름에 워치햄스터 포함
        r'attachments.*color',   # attachments 구조
        r'requests\.post.*json'  # requests.post 호출
    ]
    
    print("\n📨 메시지 구조 검증:")
    print("-" * 50)
    
    for i, pattern in enumerate(message_patterns, 1):
        if re.search(pattern, content, re.IGNORECASE):
            print(f"✅ 패턴 {i}: 확인됨")
        else:
            print(f"❌ 패턴 {i}: 누락됨")
    
    # 전체 결과 요약
    print("\n📊 검증 결과 요약:")
    print("=" * 50)
    
    total_functions = len(webhook_functions)
    found_functions = sum(1 for result in test_results.values() if result == "✅ 존재")
    
    print(f"웹훅 함수: {found_functions}/{total_functions}개 복원됨")
    print(f"줄바꿈 문자: {'✅ 정상' if wrong_linebreaks == 0 else '❌ 문제'}")
    print(f"제품명: {'✅ 정상' if found_names else '❌ 문제'}")
    
    success_rate = (found_functions / total_functions) * 100
    print(f"전체 성공률: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 웹훅 함수 복원이 성공적으로 완료되었습니다!")
        return True
    else:
        print("\n⚠️ 일부 웹훅 함수 복원에 문제가 있습니다.")
        return False

if __name__ == "__main__":
    success = test_webhook_functions()
    sys.exit(0 if success else 1)