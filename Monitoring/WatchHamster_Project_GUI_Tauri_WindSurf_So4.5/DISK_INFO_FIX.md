# 💾 디스크 정보 표시 수정 완료

## 🐛 문제

### Before
```
디스크 사용량: 30.3%
(용량 정보 없음)
```

### 요구사항
```
30.3% 사용 중
210.6 GB / 245.1 GB (실제 용량 표시)
```

---

## ✅ 수정 내역

### 1. 백엔드 API (metrics.py)
```python
# SystemMetrics 모델에 필드 추가
disk_used_gb: float = 0.0   # 사용 중
disk_total_gb: float = 0.0  # 전체 용량
disk_free_gb: float = 0.0   # 남은 용량

# psutil로 실제 디스크 정보 수집
disk = psutil.disk_usage('/')
disk_usage = disk.percent
disk_used_gb = disk.used / (1024**3)   # bytes → GB
disk_total_gb = disk.total / (1024**3)
disk_free_gb = disk.free / (1024**3)
```

### 2. 프론트엔드 Hook (useSystemMetrics.ts)
```typescript
const disk: MetricData = {
  value: rawData.disk_usage || 0,
  unit: '%',
  // 추가 정보
  used_gb: rawData.disk_used_gb || 0,
  total_gb: rawData.disk_total_gb || 0,
  free_gb: rawData.disk_free_gb || 0,
}
```

### 3. UI 컴포넌트 (SystemMetricCard.tsx)
```typescript
// MetricData 인터페이스 확장
interface MetricData {
  // 기존 필드...
  used_gb?: number
  total_gb?: number
  free_gb?: number
}

// 디스크 정보 표시
{type === 'disk' && data.used_gb && data.total_gb && (
  <Text fontSize="sm" color={textColor}>
    {data.used_gb.toFixed(1)} GB / {data.total_gb.toFixed(1)} GB
  </Text>
)}
```

---

## ✅ 수정 결과

### API 응답 (실제 데이터)
```json
{
  "disk_usage": 30.3,
  "disk_used_gb": 11.9,
  "disk_total_gb": 228.2,
  "disk_free_gb": 27.3
}
```

### UI 표시
```
디스크 사용량

30.3%
11.9 GB / 228.2 GB  ← 추가됨!

[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]
0%        경고: 80%        위험: 90%        100%
```

---

## 🎯 테스트

### 백엔드
```bash
curl http://localhost:8000/api/metrics/

✅ disk_usage: 30.3%
✅ disk_used_gb: 11.9 GB
✅ disk_total_gb: 228.2 GB
✅ disk_free_gb: 27.3 GB
```

### 프론트엔드
```
1. 브라우저 새로고침 (F5)
2. 대시보드 확인
3. 디스크 카드에 용량 정보 표시 확인
```

---

## 🎉 완료!

**디스크 정보가 이제 제대로 표시됩니다!**

```
30.3% 사용 중
11.9 GB / 228.2 GB
```

**브라우저를 새로고침하세요!** 🔄
