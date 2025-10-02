# 전체 시스템 통합 테스트 보고서

**테스트 일시**: 2025-08-12 09:09:51
**전체 결과**: ❌ 실패

## 📊 테스트 요약

- **총 테스트 수**: 5
- **성공한 테스트**: 1
- **실패한 테스트**: 4
- **성공률**: 20.0%
- **소요 시간**: 2.15초

## 📋 상세 테스트 결과

### 모니터 초기화 테스트 - ❌ 실패

**세부 정보**:
```json
{
  "error": "No module named 'core.monitoring.monitor_WatchHamster_v3_0'",
  "traceback": "Traceback (most recent call last):\n  File \"/Users/jy_lee/Desktop/GIT_DEV/infomax_api/comprehensive_system_integration_test.py\", line 123, in test_monitor_initialization\n    from core.monitoring.monitor_WatchHamster_v3_0 import WatchHamsterMonitor\nModuleNotFoundError: No module named 'core.monitoring.monitor_WatchHamster_v3_0'\n"
}
```

### 핵심 모듈 Import 테스트 - ❌ 실패

**세부 정보**:
```json
{
  "success_count": 0,
  "total_count": 5,
  "results": [
    {
      "module": "core.monitoring.monitor_WatchHamster_v3.0",
      "success": false,
      "error": "No module named 'core.monitoring.monitor_WatchHamster_v3'"
    },
    {
      "module": "core.process_manager",
      "success": false,
      "error": "No module named 'core.process_manager'"
    },
    {
      "module": "core.state_manager",
      "success": false,
      "error": "No module named 'core.state_manager'"
    },
    {
      "module": "core.notification_manager",
      "success": false,
      "error": "No module named 'core.notification_manager'"
    },
    {
      "module": "core.performance_monitor",
      "success": false,
      "error": "No module named 'core.performance_monitor'"
    }
  ]
}
```

### 회귀 테스트 - ✅ 성공

**세부 정보**:
```json
{
  "success_count": 3,
  "total_count": 3,
  "tests": [
    {
      "test": "파일 시스템 접근",
      "success": true,
      "error": null
    },
    {
      "test": "JSON 처리",
      "success": true,
      "error": null
    },
    {
      "test": "네트워크 모듈",
      "success": true,
      "error": null
    }
  ]
}
```

### 시스템 성능 테스트 - ❌ 실패

**세부 정보**:
```json
{
  "memory": {
    "rss": 24.21875,
    "vms": 425073.21875,
    "percent": 0.14781951904296875
  },
  "memory_increase_mb": 10.265625,
  "memory_increase_percent": 73.57222844344905,
  "cpu_percent": 31.3,
  "disk_usage_percent": 69.52318107562951,
  "test_duration": 1.1449048519134521
}
```

### 시스템 성능 테스트 - ❌ 실패

**세부 정보**:
```json
{
  "memory": {
    "rss": 24.21875,
    "vms": 425073.21875,
    "percent": 0.14781951904296875
  },
  "memory_increase_mb": 10.265625,
  "memory_increase_percent": 73.57222844344905,
  "cpu_percent": 29.7,
  "disk_usage_percent": 69.52378776481399,
  "test_duration": 2.151007652282715
}
```

## ⚡ 성능 데이터

- **메모리 사용량**: 24.2MB
- **메모리 증가**: 10.3MB (73.6%)
- **CPU 사용률**: 29.7%
- **디스크 사용률**: 69.5%

## 🔍 권장사항

- ⚠️ 일부 테스트가 실패했습니다. 상세 결과를 확인하여 문제를 해결하세요.
- ⚠️ 실패한 기능들이 전체 시스템 운영에 미치는 영향을 평가하세요.
