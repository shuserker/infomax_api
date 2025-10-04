#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core 컴포넌트 테스트 스크립트
StateManager, ProcessManager, WatchHamsterCore 동작 확인
"""

import asyncio
import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from core.state_manager import StateManager
from core.process_manager import ProcessManager, ProcessStatus, HealthStatus
from core.watchhamster_core import WatchHamsterCore, MonitoringMode


async def test_state_manager():
    """StateManager 테스트"""
    print("\n" + "="*60)
    print("🧪 StateManager 테스트")
    print("="*60)
    
    sm = StateManager()
    
    # 상태 저장 테스트
    test_state = {
        "watchhamster_running": True,
        "error_count": 0,
        "individual_monitors": {
            "test_monitor": {
                "status": "running",
                "health": "healthy"
            }
        }
    }
    
    print("✓ 상태 저장 중...")
    success = sm.save_state(test_state)
    print(f"  결과: {'성공' if success else '실패'}")
    
    # 상태 로드 테스트
    print("✓ 상태 로드 중...")
    loaded_state = sm.load_state()
    print(f"  로드된 데이터: {loaded_state.get('watchhamster_running')}")
    
    return success


async def test_process_manager():
    """ProcessManager 테스트"""
    print("\n" + "="*60)
    print("🧪 ProcessManager 테스트")
    print("="*60)
    
    pm = ProcessManager()
    
    # 헬스 모니터링 시작
    print("✓ 헬스 모니터링 시작...")
    await pm.start_health_monitoring()
    
    # 더미 모니터 함수
    async def dummy_monitor():
        print("  → 더미 모니터 실행 중...")
        await asyncio.sleep(2)
        print("  → 더미 모니터 완료")
    
    # 모니터 시작 테스트
    print("✓ 테스트 모니터 시작 중...")
    success = await pm.start_monitor("test_monitor", dummy_monitor)
    print(f"  시작 결과: {'성공' if success else '실패'}")
    
    # 프로세스 정보 확인
    await asyncio.sleep(0.5)
    info = pm.get_process_info("test_monitor")
    if info:
        print(f"  상태: {info.status.value}")
        print(f"  헬스: {info.health.value}")
    
    # 헬스 체크
    print("✓ 헬스 체크 중...")
    health = await pm.check_health("test_monitor")
    print(f"  헬스 상태: {health.value}")
    
    # 모니터 중지
    print("✓ 모니터 중지 중...")
    await pm.stop_monitor("test_monitor")
    
    # 헬스 모니터링 중지
    await pm.stop_health_monitoring()
    
    return success


async def test_watchhamster_core():
    """WatchHamsterCore 테스트"""
    print("\n" + "="*60)
    print("🧪 WatchHamsterCore 테스트")
    print("="*60)
    
    core = WatchHamsterCore()
    
    # 초기화
    print("✓ 시스템 초기화 중...")
    success = await core.initialize()
    print(f"  초기화 결과: {'성공' if success else '실패'}")
    
    # 시스템 상태 확인
    print("✓ 시스템 상태 조회...")
    status = await core.get_system_status()
    print(f"  시스템 상태: {status.status.value}")
    print(f"  초기화 여부: {status.metadata.get('initialized')}")
    
    # 모니터링 시작 (개별 모드)
    print("✓ 모니터링 시작 (개별 모드)...")
    start_success = await core.start_monitoring(
        MonitoringMode.INDIVIDUAL,
        monitors=["test1", "test2"]
    )
    print(f"  시작 결과: {'성공' if start_success else '실패'}")
    
    # 상태 재확인
    await asyncio.sleep(0.5)
    status = await core.get_system_status()
    print(f"  현재 상태: {status.status.value}")
    print(f"  모드: {status.mode.value if status.mode else 'None'}")
    
    # 모니터링 중지
    print("✓ 모니터링 중지...")
    await core.stop_monitoring()
    
    # 시스템 종료
    print("✓ 시스템 종료...")
    await core.shutdown()
    
    return success


async def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("🚀 WatchHamster Core 컴포넌트 테스트 시작")
    print("="*60)
    
    results = []
    
    # 각 컴포넌트 테스트
    try:
        results.append(("StateManager", await test_state_manager()))
        results.append(("ProcessManager", await test_process_manager()))
        results.append(("WatchHamsterCore", await test_watchhamster_core()))
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
