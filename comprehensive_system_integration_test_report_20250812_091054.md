# 전체 시스템 통합 테스트 보고서

**테스트 일시**: 2025-08-12 09:10:54
**전체 결과**: ❌ 실패

## 📊 테스트 요약

- **총 테스트 수**: 5
- **성공한 테스트**: 2
- **실패한 테스트**: 3
- **성공률**: 40.0%
- **소요 시간**: 2.12초

## 📋 상세 테스트 결과

### 모니터 초기화 테스트 - ❌ 실패

**세부 정보**:
```json
{
  "error": "No module named 'monitor_WatchHamster_v3_0'",
  "traceback": "Traceback (most recent call last):\n  File \"/Users/jy_lee/Desktop/GIT_DEV/infomax_api/comprehensive_system_integration_test.py\", line 123, in test_monitor_initialization\n    import monitor_WatchHamster_v3_0 as monitor_module\nModuleNotFoundError: No module named 'monitor_WatchHamster_v3_0'\n"
}
```

### 핵심 모듈 Import 테스트 - ✅ 성공

**세부 정보**:
```json
{
  "success_count": 4,
  "total_count": 4,
  "results": [
    {
      "module": "json",
      "success": true,
      "error": null
    },
    {
      "module": "requests",
      "success": true,
      "error": null
    },
    {
      "module": "psutil",
      "success": true,
      "error": null
    },
    {
      "module": "datetime",
      "success": true,
      "error": null
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
    "rss": 24.3125,
    "vms": 425073.515625,
    "percent": 0.1483917236328125
  },
  "memory_increase_mb": 10.40625,
  "memory_increase_percent": 74.8314606741573,
  "cpu_percent": 24.2,
  "disk_usage_percent": 69.52168190152904,
  "test_duration": 1.1160321235656738
}
```

### 시스템 성능 테스트 - ❌ 실패

**세부 정보**:
```json
{
  "memory": {
    "rss": 24.3125,
    "vms": 425073.515625,
    "percent": 0.1483917236328125
  },
  "memory_increase_mb": 10.40625,
  "memory_increase_percent": 74.8314606741573,
  "cpu_percent": 21.9,
  "disk_usage_percent": 69.52170195736984,
  "test_duration": 2.118990898132324
}
```

## ⚡ 성능 데이터

- **메모리 사용량**: 24.3MB
- **메모리 증가**: 10.4MB (74.8%)
- **CPU 사용률**: 21.9%
- **디스크 사용률**: 69.5%

## 🔍 권장사항

- ⚠️ 일부 테스트가 실패했습니다. 상세 결과를 확인하여 문제를 해결하세요.
- ⚠️ 실패한 기능들이 전체 시스템 운영에 미치는 영향을 평가하세요.
