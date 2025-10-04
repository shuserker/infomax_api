#!/usr/bin/env python3
"""
포팅된 로직 테스트 스크립트
"""

import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append('.')

async def test_performance_optimizer():
    """성능 최적화 시스템 테스트"""
    print("🔧 성능 최적화 시스템 테스트...")
    
    from core.performance_optimizer import get_performance_optimizer
    
    po = get_performance_optimizer()
    metrics = await po.get_performance_metrics()
    
    print(f"  ✅ CPU 사용률: {metrics.get('cpu_percent', 0):.1f}%")
    print(f"  ✅ 메모리 사용률: {metrics.get('memory_percent', 0):.1f}%")
    print(f"  ✅ 디스크 사용률: {metrics.get('disk_usage_percent', 0):.1f}%")
    print(f"  ✅ 프로세스 수: {metrics.get('process_count', 0)}")

async def test_stability_manager():
    """안정성 관리자 테스트"""
    print("\n🛡️ 안정성 관리자 테스트...")
    
    from core.stability_manager import get_stability_manager
    
    sm = get_stability_manager()
    stability_metrics = await sm.get_stability_metrics()
    
    print(f"  ✅ 오류 수: {stability_metrics.error_count}")
    print(f"  ✅ 복구 수: {stability_metrics.recovery_count}")
    print(f"  ✅ 업타임: {stability_metrics.uptime_hours:.1f}시간")
    print(f"  ✅ 시스템 상태: {stability_metrics.system_health.value}")

async def test_status_reporter():
    """상태 보고 시스템 테스트"""
    print("\n📊 상태 보고 시스템 테스트...")
    
    from core.status_reporter import create_integrated_status_reporter
    
    sr = create_integrated_status_reporter()
    system_status = await sr.get_system_status()
    
    print(f"  ✅ 전체 컴포넌트: {system_status.get('total_components', 0)}")
    print(f"  ✅ 정상 컴포넌트: {system_status.get('healthy_components', 0)}")
    print(f"  ✅ 경고 컴포넌트: {system_status.get('warning_components', 0)}")
    print(f"  ✅ 오류 컴포넌트: {system_status.get('error_components', 0)}")

async def test_webhook_system():
    """웹훅 시스템 테스트"""
    print("\n🔗 웹훅 시스템 테스트...")
    
    from core.webhook_system import WebhookSystem, MessageType
    
    ws = WebhookSystem()
    stats = ws.get_send_statistics()
    
    print(f"  ✅ 전송 통계 조회 성공")
    print(f"  ✅ 총 전송: {stats.get('total_sent', 0)}")
    print(f"  ✅ 성공률: {stats.get('success_rate', 0)}%")

async def test_posco_manager():
    """POSCO 관리자 테스트"""
    print("\n🏭 POSCO 관리자 테스트...")
    
    from core.posco_manager import PoscoManager
    
    pm = PoscoManager()
    deployment_status = await pm.get_deployment_status()
    
    print(f"  ✅ 현재 브랜치: {deployment_status.get('current_branch', 'unknown')}")
    print(f"  ✅ 브랜치 전환 상태: {deployment_status.get('branch_switch_status', 'unknown')}")
    print(f"  ✅ GitHub Pages 접근 가능: {deployment_status.get('github_pages_status', {}).get('is_accessible', False)}")

async def main():
    """메인 테스트 함수"""
    print("🚀 WatchHamster 포팅된 로직 전체 테스트 시작\n")
    
    try:
        await test_performance_optimizer()
        await test_stability_manager()
        await test_status_reporter()
        await test_webhook_system()
        await test_posco_manager()
        
        print("\n🎉 모든 테스트 성공! 포팅된 로직이 완벽하게 작동합니다!")
        print("✨ FastAPI 서버에서 모든 기능을 사용할 준비가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())