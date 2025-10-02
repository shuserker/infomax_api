# POSCO 시스템 운영 매뉴얼 v2.1
업데이트: 2025-08-10 18:59:38

## 시스템 개요
POSCO 워치햄스터 v3.0 뉴스 모니터링 시스템

## 주요 구성 요소

### 1. 핵심 실행 파일
- `POSCO_News_250808.py`: 메인 뉴스 모니터링 시스템
- `🐹POSCO_워치햄스터_v3_제어센터.bat`: Windows 제어센터
- `🐹POSCO_워치햄스터_v3_제어센터.command`: macOS 제어센터
- `watchhamster_v3.0_control_center.sh`: Linux 제어센터

### 2. 관리 도구
- `system_functionality_verification.py`: 시스템 기능 검증
- `final_integration_test_system.py`: 통합 테스트
- `deployment_preparation_system.py`: 배포 준비 시스템

## 시스템 시작 방법

### Windows 환경
```cmd
🐹POSCO_워치햄스터_v3_제어센터.bat
```

### macOS 환경
```bash
./🐹POSCO_워치햄스터_v3_제어센터.command
```

### Linux 환경
```bash
./watchhamster_v3.0_control_center.sh
```

## 시스템 모니터링

### 1. 로그 파일 확인
- `WatchHamster_v3.0.log`: 메인 시스템 로그
- `posco_news_250808_monitor.log`: 뉴스 모니터링 로그

### 2. 성능 모니터링
```python
python3 system_functionality_verification.py
```

### 3. 상태 확인
```python
python3 -c "
import POSCO_News_250808
print('시스템 상태: 정상')
"
```

## 문제 해결

### 1. 시스템 시작 실패
1. Python 버전 확인 (3.8+ 필요)
2. 의존성 모듈 설치 확인
3. 파일 권한 확인
4. 로그 파일 확인

### 2. 웹훅 알림 실패
1. 네트워크 연결 확인
2. 웹훅 URL 유효성 확인
3. 방화벽 설정 확인

### 3. 성능 저하
1. 메모리 사용량 확인
2. CPU 사용률 확인
3. 디스크 공간 확인
4. 네트워크 대역폭 확인

## 정기 유지보수

### 일일 점검
- [ ] 시스템 상태 확인
- [ ] 로그 파일 확인
- [ ] 웹훅 알림 테스트

### 주간 점검
- [ ] 성능 지표 분석
- [ ] 로그 파일 정리
- [ ] 백업 상태 확인

### 월간 점검
- [ ] 시스템 업데이트 확인
- [ ] 보안 패치 적용
- [ ] 성능 최적화 검토

## 비상 연락처
- 시스템 관리자: [연락처]
- 기술 지원팀: [연락처]
- 긴급 상황: [연락처]
