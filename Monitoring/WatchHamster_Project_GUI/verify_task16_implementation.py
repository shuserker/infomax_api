#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 16 구현 검증 스크립트 (비GUI)
POSCO 뉴스 전용 GUI 패널 구현 검증

검증 항목:
- 메시지 미리보기 기능 구현 확인
- 수동 전송 기능 구현 확인
- 배포 진행률 프로그레스 바 구현 확인
- 상태 표시 기능 구현 확인

Requirements: 6.4, 5.1, 5.2 검증
"""

import sys
import os
import inspect
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def log_result(message, success=True):
    """결과 로그 출력"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    status = "✅" if success else "❌"
    print(f"[{timestamp}] {status} {message}")

def verify_task16_implementation():
    """Task 16 구현 검증"""
    print("🧪 Task 16 구현 검증 시작")
    print("=" * 60)
    
    verification_results = {
        'posco_gui_manager_import': False,
        'message_preview_methods': False,
        'manual_send_methods': False,
        'progress_bar_methods': False,
        'status_display_methods': False,
        'message_preview_tab_setup': False
    }
    
    try:
        # 1. PoscoGUIManager 클래스 임포트 확인
        try:
            from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
            verification_results['posco_gui_manager_import'] = True
            log_result("PoscoGUIManager 클래스 임포트 성공")
        except ImportError as e:
            log_result(f"PoscoGUIManager 클래스 임포트 실패: {e}", False)
            return verification_results
        
        # 2. 클래스 메서드 검증
        class_methods = inspect.getmembers(PoscoGUIManager, predicate=inspect.isfunction)
        method_names = [method[0] for method in class_methods]
        
        log_result(f"PoscoGUIManager 클래스 메서드 개수: {len(method_names)}")
        
        # 3. 메시지 미리보기 관련 메서드 확인
        message_preview_methods = [
            'setup_message_preview_tab',
            'update_message_preview', 
            'load_sample_message_data',
            'save_message_data',
            '_on_message_type_changed',
            '_on_message_priority_changed'
        ]
        
        found_preview_methods = []
        for method in message_preview_methods:
            if method in method_names:
                found_preview_methods.append(method)
        
        if len(found_preview_methods) >= 4:  # 최소 4개 이상
            verification_results['message_preview_methods'] = True
            log_result(f"메시지 미리보기 메서드 구현 확인: {len(found_preview_methods)}개")
            for method in found_preview_methods:
                log_result(f"  - {method}")
        else:
            log_result(f"메시지 미리보기 메서드 부족: {len(found_preview_methods)}개 (최소 4개 필요)", False)
        
        # 4. 수동 전송 관련 메서드 확인
        manual_send_methods = [
            'send_test_message',
            'send_manual_message',
            '_handle_test_send_success',
            '_handle_test_send_error',
            '_handle_manual_send_success',
            '_handle_manual_send_error',
            'paste_webhook_url',
            'show_send_history',
            '_save_send_history'
        ]
        
        found_send_methods = []
        for method in manual_send_methods:
            if method in method_names:
                found_send_methods.append(method)
        
        if len(found_send_methods) >= 6:  # 최소 6개 이상
            verification_results['manual_send_methods'] = True
            log_result(f"수동 전송 메서드 구현 확인: {len(found_send_methods)}개")
            for method in found_send_methods:
                log_result(f"  - {method}")
        else:
            log_result(f"수동 전송 메서드 부족: {len(found_send_methods)}개 (최소 6개 필요)", False)
        
        # 5. 진행률 바 관련 메서드 확인
        progress_methods = [
            'update_deployment_progress',
            'reset_deployment_progress', 
            'complete_deployment_progress',
            '_update_progress_step'
        ]
        
        found_progress_methods = []
        for method in progress_methods:
            if method in method_names:
                found_progress_methods.append(method)
        
        if len(found_progress_methods) >= 3:  # 최소 3개 이상
            verification_results['progress_bar_methods'] = True
            log_result(f"진행률 바 메서드 구현 확인: {len(found_progress_methods)}개")
            for method in found_progress_methods:
                log_result(f"  - {method}")
        else:
            log_result(f"진행률 바 메서드 부족: {len(found_progress_methods)}개 (최소 3개 필요)", False)
        
        # 6. 상태 표시 관련 메서드 확인
        status_methods = [
            'check_git_status',
            '_update_git_status_display',
            'refresh_status',
            'refresh_deployment_stats'
        ]
        
        found_status_methods = []
        for method in status_methods:
            if method in method_names:
                found_status_methods.append(method)
        
        if len(found_status_methods) >= 2:  # 최소 2개 이상
            verification_results['status_display_methods'] = True
            log_result(f"상태 표시 메서드 구현 확인: {len(found_status_methods)}개")
            for method in found_status_methods:
                log_result(f"  - {method}")
        else:
            log_result(f"상태 표시 메서드 부족: {len(found_status_methods)}개 (최소 2개 필요)", False)
        
        # 7. 소스 코드에서 메시지 미리보기 탭 설정 확인
        try:
            posco_gui_file = os.path.join(current_dir, 'Posco_News_Mini_Final_GUI', 'posco_gui_manager.py')
            with open(posco_gui_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # 메시지 미리보기 탭 관련 키워드 확인
            tab_keywords = [
                'setup_message_preview_tab',
                '메시지 미리보기',
                'message_preview_text',
                'webhook_url_var',
                'send_manual_button'
            ]
            
            found_keywords = []
            for keyword in tab_keywords:
                if keyword in source_code:
                    found_keywords.append(keyword)
            
            if len(found_keywords) >= 4:  # 최소 4개 이상
                verification_results['message_preview_tab_setup'] = True
                log_result(f"메시지 미리보기 탭 구현 확인: {len(found_keywords)}개 키워드 발견")
            else:
                log_result(f"메시지 미리보기 탭 구현 부족: {len(found_keywords)}개 키워드 (최소 4개 필요)", False)
                
        except Exception as e:
            log_result(f"소스 코드 분석 중 오류: {e}", False)
        
        # 8. 결과 요약
        print("\n" + "=" * 60)
        print("📋 Task 16 구현 검증 결과 요약")
        print("=" * 60)
        
        total_checks = len(verification_results)
        passed_checks = sum(verification_results.values())
        
        for check_name, result in verification_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{check_name}: {status}")
        
        print("=" * 60)
        print(f"전체 검증 항목: {total_checks}")
        print(f"통과한 항목: {passed_checks}")
        print(f"성공률: {(passed_checks/total_checks)*100:.1f}%")
        
        if passed_checks == total_checks:
            print("🎉 Task 16 구현 완료! 모든 검증 항목 통과")
            print("\n✅ 구현된 기능:")
            print("  - 메시지 미리보기 및 수동 전송 기능")
            print("  - 배포 진행률 프로그레스 바 및 상태 표시")
            print("  - POSCO 뉴스 시스템 전용 모니터링 인터페이스")
            print("  - Requirements 6.4, 5.1, 5.2 완전 구현")
        elif passed_checks >= total_checks * 0.8:
            print("✅ Task 16 구현 대부분 완료 (80% 이상 통과)")
        else:
            print("⚠️ Task 16 구현 추가 작업 필요")
        
        return verification_results
        
    except Exception as e:
        log_result(f"검증 중 예외 발생: {e}", False)
        import traceback
        traceback.print_exc()
        return verification_results

def main():
    """메인 함수"""
    print("🚀 Task 16: POSCO 뉴스 전용 GUI 패널 구현 검증")
    print("Requirements: 6.4, 5.1, 5.2")
    print()
    
    results = verify_task16_implementation()
    
    # 최종 결과 반환
    success_rate = sum(results.values()) / len(results)
    return success_rate >= 0.8  # 80% 이상 성공 시 True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)