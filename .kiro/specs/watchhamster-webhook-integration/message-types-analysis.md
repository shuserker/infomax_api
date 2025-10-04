# 메시지 타입 전체 분석

## 🔍 발견된 메시지 타입

### 1. 뉴스 모니터링 웹훅 (8개) - ✅ 통합 완료
**위치**: `WatchHamster_Project/Posco_News_Mini_Final/core/`

1. ✅ `test` - 테스트 메시지
2. ✅ `business_day_comparison` - 영업일 비교 분석
3. ✅ `delay_notification` - 지연 발행 알림
4. ✅ `daily_report` - 일일 통합 리포트
5. ✅ `status_notification` - 정시 발행 알림
6. ✅ `no_data_notification` - 데이터 갱신 없음
7. ✅ `watchhamster_error` - 워치햄스터 오류
8. ✅ `watchhamster_status` - 워치햄스터 상태

**파일**:
- `webhook_sender.py` (875 lines)
- `news_message_generator.py` (1,409 lines)

---

### 2. 배포 관련 템플릿 (7개) - ⚠️ GUI 프로젝트
**위치**: `WatchHamster_Project_GUI/Posco_News_Mini_Final_GUI/`

1. ⚠️ `deployment_success` - 배포 성공
2. ⚠️ `deployment_failure` - 배포 실패
3. ⚠️ `deployment_start` - 배포 시작
4. ⚠️ `system_status` - 시스템 상태
5. ⚠️ `data_update` - 데이터 업데이트
6. ⚠️ `error_alert` - 오류 알림
7. ⚠️ `maintenance` - 시스템 점검

**파일**:
- `message_template_engine.py` (890 lines)
- `dynamic_data_manager.py`

**특징**:
- GUI 프로젝트 전용
- 배포 모니터링용
- 동적 데이터 연동

---

### 3. API 엔드포인트 (19개)
**위치**: `python-backend/api_test_results.json`

이것은 **API 엔드포인트 개수**이지 메시지 타입이 아닙니다:
1. /api/companies
2. /api/companies/posco
3. /api/companies/posco/stats
4. /api/companies/posco/webhooks
5. /api/companies/posco/api-configs
6. /api/webhook-manager/stats
7. /api/webhook-manager/logs
8. /api/webhook-manager/message-types
9. /api/webhook-manager/queue-status
10. /health
11. /api/system/status
12. /api/system/health
13. /api/logs/
14. /api/monitor-logs/recent
15. /api/config/monitors
16. /api/settings/all
17. /api/diagnostics/health-check
18. /api/diagnostics/config-info
19. /api/metrics/summary

---

## 🎯 질문: 어떤 메시지 타입을 말씀하시는 건가요?

### 옵션 1: 뉴스 모니터링 웹훅 (8개) ✅
현재 **완전히 통합 완료**된 상태입니다.
- 원본 로직 100% 보존
- 모든 템플릿 100% 보존
- 실제 작동 테스트 완료

### 옵션 2: 배포 관련 템플릿 (7개) ⚠️
GUI 프로젝트의 **배포 모니터링용** 템플릿입니다.
- 뉴스 모니터링과는 별개 시스템
- 배포 프로세스 알림용
- 통합 필요 여부 확인 필요

### 옵션 3: 합계 15개?
뉴스 모니터링 (8개) + 배포 관련 (7개) = 15개

---

## 📋 현재 통합 상태

### ✅ 통합 완료 (8개)
- `WatchHamster_Project/Posco_News_Mini_Final/core/` → 완전 복사
- 모든 로직, 템플릿, 텍스트 100% 보존
- API 엔드포인트 연결 완료
- 실제 작동 테스트 완료

### ⚠️ 미통합 (7개)
- `WatchHamster_Project_GUI/Posco_News_Mini_Final_GUI/message_template_engine.py`
- 배포 관련 템플릿
- GUI 프로젝트 전용

---

## 🤔 확인 필요

**질문**: 배포 관련 템플릿 7개도 함께 통합해야 하나요?

만약 그렇다면:
1. `message_template_engine.py` 복사
2. `dynamic_data_manager.py` 복사
3. API 엔드포인트 추가
4. 총 15개 메시지 타입 지원

---

**작성일**: 2025-10-04 16:53 KST
