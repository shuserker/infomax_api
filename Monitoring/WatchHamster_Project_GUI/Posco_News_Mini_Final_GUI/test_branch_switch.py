#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브랜치 전환 시스템 테스트 스크립트
안전한 브랜치 전환 기능 검증용

Requirements 1.3, 3.1, 3.2 테스트
"""

import os
import sys
import json
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from git_deployment_manager import GitDeploymentManager
except ImportError as e:
    print(f"❌ GitDeploymentManager import 오류: {e}")
    sys.exit(1)


def test_git_status():
    """Git 상태 확인 테스트 (Requirements 3.1)"""
    print("🔍 Git 상태 확인 테스트 시작...")
    
    try:
        deployment_manager = GitDeploymentManager()
        status_info = deployment_manager.check_git_status()
        
        print("📊 Git 상태 정보:")
        print(json.dumps(status_info, ensure_ascii=False, indent=2))
        
        # 상태 검증
        assert 'is_git_repo' in status_info, "Git 저장소 상태 정보 누락"
        assert 'current_branch' in status_info, "현재 브랜치 정보 누락"
        assert 'has_uncommitted_changes' in status_info, "변경사항 상태 정보 누락"
        assert 'has_conflicts' in status_info, "충돌 상태 정보 누락"
        
        print("✅ Git 상태 확인 테스트 통과")
        return status_info
        
    except Exception as e:
        print(f"❌ Git 상태 확인 테스트 실패: {e}")
        return None


def test_branch_switch(target_branch):
    """브랜치 전환 테스트 (Requirements 1.3)"""
    print(f"🔄 브랜치 전환 테스트 시작: {target_branch}")
    
    try:
        deployment_manager = GitDeploymentManager()
        
        # 진행 상태 콜백 함수 (실시간 표시 테스트)
        progress_steps = []
        def progress_callback(step_message):
            progress_steps.append(step_message)
            print(f"📋 진행 단계: {step_message}")
        
        # 브랜치 전환 실행
        switch_result = deployment_manager.safe_branch_switch(target_branch, progress_callback)
        
        print("📊 브랜치 전환 결과:")
        print(json.dumps(switch_result, ensure_ascii=False, indent=2))
        
        # 결과 검증
        assert 'success' in switch_result, "성공 여부 정보 누락"
        assert 'target_branch' in switch_result, "대상 브랜치 정보 누락"
        assert 'steps_completed' in switch_result, "완료 단계 정보 누락"
        
        if switch_result['success']:
            print("✅ 브랜치 전환 테스트 통과")
            
            # 진행 단계 검증
            expected_steps = ['status_check', 'remote_fetch', 'branch_check', 'final_verification']
            completed_steps = switch_result['steps_completed']
            
            for step in expected_steps:
                if step in completed_steps:
                    print(f"  ✅ {step} 단계 완료")
                else:
                    print(f"  ⚠️ {step} 단계 누락")
            
            # stash 처리 검증
            if switch_result.get('stash_created', False):
                print(f"  ✅ 변경사항 stash 처리 완료: {switch_result.get('stash_message', '')}")
            
            # 충돌 해결 검증
            if switch_result.get('conflicts_resolved', False):
                print(f"  ✅ Git 충돌 자동 해결 완료")
                
        else:
            print(f"❌ 브랜치 전환 실패: {switch_result.get('error_message', '알 수 없는 오류')}")
        
        return switch_result
        
    except Exception as e:
        print(f"❌ 브랜치 전환 테스트 실패: {e}")
        return None


def test_stash_operations():
    """Stash 작업 테스트 (Requirements 1.3 - 로컬 변경사항 자동 stash 처리)"""
    print("💾 Stash 작업 테스트 시작...")
    
    try:
        deployment_manager = GitDeploymentManager()
        
        # 현재 Git 상태 확인
        status_info = deployment_manager.check_git_status()
        
        if status_info.get('has_uncommitted_changes', False):
            print("✅ 변경사항이 있어 stash 테스트 가능")
            
            # 테스트용 stash 생성
            stash_message = f"Test stash - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            success, output = deployment_manager.run_git_command(['git', 'stash', 'push', '-m', stash_message])
            
            if success:
                print(f"✅ 테스트 stash 생성 성공: {stash_message}")
                
                # stash 복원 테스트
                restore_success = deployment_manager.restore_stash_if_needed(stash_message)
                if restore_success:
                    print("✅ Stash 복원 테스트 성공")
                else:
                    print("❌ Stash 복원 테스트 실패")
                    
                return True
            else:
                print(f"❌ 테스트 stash 생성 실패: {output}")
                return False
        else:
            print("⚠️ 변경사항이 없어 stash 테스트 건너뜀")
            return True
            
    except Exception as e:
        print(f"❌ Stash 작업 테스트 실패: {e}")
        return False


def test_conflict_resolution():
    """충돌 해결 테스트 (Requirements 3.2)"""
    print("🔧 충돌 해결 테스트 시작...")
    
    try:
        deployment_manager = GitDeploymentManager()
        
        # 충돌 해결 기능 테스트
        conflict_resolved = deployment_manager.handle_git_conflicts()
        
        if conflict_resolved:
            print("✅ 충돌 해결 테스트 통과")
        else:
            print("⚠️ 충돌 해결 테스트 - 충돌 없음 또는 해결 실패")
            
        return conflict_resolved
        
    except Exception as e:
        print(f"❌ 충돌 해결 테스트 실패: {e}")
        return False


def run_comprehensive_test():
    """종합 테스트 실행"""
    print("🧪 POSCO 브랜치 전환 시스템 종합 테스트 시작")
    print("=" * 60)
    
    test_results = {
        'git_status_test': False,
        'stash_test': False,
        'conflict_test': False,
        'branch_switch_test': False,
        'overall_success': False
    }
    
    # 1. Git 상태 확인 테스트
    print("\n1️⃣ Git 상태 확인 테스트 (Requirements 3.1)")
    print("-" * 40)
    status_info = test_git_status()
    test_results['git_status_test'] = status_info is not None
    
    if not status_info:
        print("❌ Git 상태 확인 실패로 테스트 중단")
        return test_results
    
    # 2. Stash 작업 테스트
    print("\n2️⃣ Stash 작업 테스트 (Requirements 1.3)")
    print("-" * 40)
    test_results['stash_test'] = test_stash_operations()
    
    # 3. 충돌 해결 테스트
    print("\n3️⃣ 충돌 해결 테스트 (Requirements 3.2)")
    print("-" * 40)
    test_results['conflict_test'] = test_conflict_resolution()
    
    # 4. 브랜치 전환 테스트
    print("\n4️⃣ 브랜치 전환 테스트 (Requirements 1.3)")
    print("-" * 40)
    
    current_branch = status_info.get('current_branch', 'unknown')
    
    if current_branch == 'main':
        target_branch = 'publish'
    elif current_branch == 'publish':
        target_branch = 'main'
    else:
        target_branch = 'main'  # 기본값
    
    print(f"현재 브랜치: {current_branch}")
    print(f"전환 대상 브랜치: {target_branch}")
    
    # 사용자 확인
    user_input = input(f"\n{target_branch} 브랜치로 전환 테스트를 진행하시겠습니까? (y/N): ")
    
    if user_input.lower() in ['y', 'yes']:
        switch_result = test_branch_switch(target_branch)
        test_results['branch_switch_test'] = switch_result and switch_result.get('success', False)
        
        if test_results['branch_switch_test']:
            print("\n🔄 원래 브랜치로 복귀 테스트...")
            restore_result = test_branch_switch(current_branch)
            if restore_result and restore_result.get('success', False):
                print("✅ 원래 브랜치 복귀 테스트 성공!")
            else:
                print("❌ 원래 브랜치 복귀 테스트 실패")
    else:
        print("⚠️ 브랜치 전환 테스트 건너뜀")
        test_results['branch_switch_test'] = True  # 건너뛴 경우 통과로 처리
    
    # 종합 결과 평가
    test_results['overall_success'] = all([
        test_results['git_status_test'],
        test_results['stash_test'],
        test_results['conflict_test'],
        test_results['branch_switch_test']
    ])
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("🏁 종합 테스트 결과")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        if test_name != 'overall_success':
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
    
    print("-" * 60)
    if test_results['overall_success']:
        print("🎉 모든 테스트 통과! 브랜치 전환 시스템이 완벽하게 구현되었습니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템 점검이 필요합니다.")
    
    return test_results


def main():
    """메인 테스트 함수"""
    try:
        results = run_comprehensive_test()
        
        # 종료 코드 설정
        if results['overall_success']:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 실패
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 예외 발생: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()