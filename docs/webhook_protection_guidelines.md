# 웹훅 기능 보호 가이드라인

## 📋 개요

이 문서는 POSCO 워치햄스터 시스템의 웹훅 기능을 보호하고, 향후 동일한 문제가 발생하지 않도록 하기 위한 실행 가능한 가이드라인을 제공합니다.

## 🛡️ 핵심 보호 규칙

### 1. 웹훅 관련 파일 보호 목록

#### 절대 수정 금지 파일
```
core/monitoring/monitor_WatchHamster_v3.0.py  # 메인 모니터링 파일
webhook_message_restorer.py                   # 복원 도구
webhook_config_restorer.py                    # 설정 복원 도구
compatibility_checker.py                      # 호환성 검사 도구
```

#### 수정 시 사전 백업 필수 파일
```
config.py                                     # 웹훅 URL 설정
webhook_backup_manager.py                     # 백업 관리 도구
webhook_format_validator.py                   # 포맷 검증 도구
```

### 2. 웹훅 함수 보호 체크리스트

#### 수정 전 필수 확인사항
- [ ] 현재 상태 백업 생성 완료
- [ ] 웹훅 함수 목록 확인 (12개 함수)
- [ ] 메시지 템플릿 보존 확인
- [ ] 줄바꿈 문자 처리 방식 확인
- [ ] 제품명 표기 일관성 확인

#### 보호해야 할 웹훅 함수 목록
1. `send_status_notification` - 정기 상태 알림
2. `send_notification` - 기본 알림 전송
3. `send_status_report_v2` - v2 정기 상태 보고
4. `send_startup_notification_v2` - v2 시작 알림
5. `_send_basic_status_notification` - 기본 상태 알림
6. `send_process_error_v2` - v2 프로세스 오류 알림
7. `send_recovery_success_v2` - v2 복구 성공 알림
8. `execute_integrated_report_notification` - 통합 리포트 알림
9. `should_send_status_notification` - 상태 알림 조건 확인
10. `send_critical_alert_v2` - v2 긴급 알림
11. `send_enhanced_status_notification` - 향상된 상태 알림
12. `_send_hourly_status_notification` - 매시간 상태 알림

## 🔧 실행 가능한 보호 도구

### 1. 사전 백업 스크립트

#### 웹훅 기능 수정 전 백업
```bash
#!/bin/bash
# pre_modification_backup.sh

echo "=== 웹훅 기능 수정 전 백업 생성 ==="

# 현재 날짜와 시간으로 백업명 생성
BACKUP_NAME="pre_modification_$(date +%Y%m%d_%H%M%S)"

# 백업 생성
python3 webhook_backup_manager.py --create "$BACKUP_NAME" --description "수정 작업 전 안전 백업"

# 백업 검증
python3 webhook_backup_manager.py --verify "$BACKUP_NAME"

echo "✅ 백업 완료: $BACKUP_NAME"
echo "이제 안전하게 수정 작업을 진행할 수 있습니다."
```

#### 사용법
```bash
chmod +x pre_modification_backup.sh
./pre_modification_backup.sh
```

### 2. 웹훅 기능 검증 스크립트

#### 일일 검증 스크립트
```bash
#!/bin/bash
# daily_webhook_verification.sh

echo "=== POSCO 워치햄스터 웹훅 시스템 일일 검증 ==="

# 1. 웹훅 함수 존재 확인
echo "1. 웹훅 함수 존재 확인..."
python3 webhook_function_analysis_test.py --quiet

if [ $? -eq 0 ]; then
    echo "✅ 웹훅 함수 확인 완료"
else
    echo "❌ 웹훅 함수 문제 발견 - 즉시 확인 필요!"
    exit 1
fi

# 2. 메시지 포맷 검증
echo "2. 메시지 포맷 검증..."
python3 webhook_format_validator.py --daily-check

if [ $? -eq 0 ]; then
    echo "✅ 메시지 포맷 검증 완료"
else
    echo "❌ 메시지 포맷 문제 발견 - 즉시 수정 필요!"
    exit 1
fi

# 3. 웹훅 URL 유효성 확인
echo "3. 웹훅 URL 유효성 확인..."
python3 -c "
import requests
from config import DOORAY_WEBHOOK_URL, WATCHHAMSTER_WEBHOOK_URL

urls = [DOORAY_WEBHOOK_URL, WATCHHAMSTER_WEBHOOK_URL]
for url in urls:
    if 'dooray.com' in url and 'services' in url:
        print(f'✅ URL 형식 유효: {url[:50]}...')
    else:
        print(f'❌ URL 형식 오류: {url}')
        exit(1)
"

# 4. 백업 시스템 상태 확인
echo "4. 백업 시스템 상태 확인..."
python3 webhook_backup_manager.py --status --quiet

echo "✅ 일일 검증 완료 - 모든 시스템 정상"
```

#### 사용법
```bash
chmod +x daily_webhook_verification.sh
./daily_webhook_verification.sh

# 크론탭에 등록하여 매일 자동 실행
# crontab -e
# 0 9 * * * /path/to/daily_webhook_verification.sh >> /var/log/webhook_verification.log 2>&1
```

### 3. 비상 복구 스크립트

#### 자동 비상 복구
```bash
#!/bin/bash
# emergency_webhook_recovery.sh

echo "🚨 웹훅 시스템 비상 복구 시작 🚨"

# 1. 현재 상태 비상 백업
echo "1. 현재 상태 비상 백업 생성..."
EMERGENCY_BACKUP="emergency_backup_$(date +%Y%m%d_%H%M%S)"
python3 webhook_backup_manager.py --create "$EMERGENCY_BACKUP" --description "비상 복구 전 현재 상태 백업"

# 2. 자동 롤백 실행
echo "2. 자동 롤백 실행..."
python3 webhook_backup_manager.py --auto-rollback "Emergency recovery - $(date)"

if [ $? -eq 0 ]; then
    echo "✅ 자동 롤백 성공"
else
    echo "❌ 자동 롤백 실패 - 수동 개입 필요"
    exit 1
fi

# 3. 복구 후 검증
echo "3. 복구 후 시스템 검증..."
python3 webhook_function_analysis_test.py --quiet

if [ $? -eq 0 ]; then
    echo "✅ 복구 완료 - 시스템 정상"
    
    # 4. 테스트 메시지 전송
    echo "4. 복구 확인 테스트 메시지 전송..."
    python3 real_webhook_transmission_test.py --test-mode --single-test
    
    echo "🎉 비상 복구 완료!"
else
    echo "❌ 복구 후에도 문제 지속 - 수동 점검 필요"
    exit 1
fi
```

#### 사용법
```bash
chmod +x emergency_webhook_recovery.sh
./emergency_webhook_recovery.sh
```

## 📊 모니터링 및 알림 설정

### 1. 웹훅 시스템 상태 모니터링

#### 시스템 상태 확인 스크립트
```python
#!/usr/bin/env python3
# webhook_system_monitor.py

import json
import subprocess
import sys
from datetime import datetime

def check_webhook_system_health():
    """웹훅 시스템 전체 상태 확인"""
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "HEALTHY",
        "checks": {}
    }
    
    # 1. 웹훅 함수 존재 확인
    try:
        result = subprocess.run([
            "python3", "webhook_function_analysis_test.py", "--quiet"
        ], capture_output=True, text=True)
        
        health_report["checks"]["webhook_functions"] = {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "details": result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        health_report["checks"]["webhook_functions"] = {
            "status": "ERROR",
            "details": str(e)
        }
    
    # 2. 메시지 포맷 검증
    try:
        result = subprocess.run([
            "python3", "webhook_format_validator.py", "--daily-check"
        ], capture_output=True, text=True)
        
        health_report["checks"]["message_format"] = {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "details": result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        health_report["checks"]["message_format"] = {
            "status": "ERROR",
            "details": str(e)
        }
    
    # 3. 백업 시스템 상태
    try:
        result = subprocess.run([
            "python3", "webhook_backup_manager.py", "--status", "--quiet"
        ], capture_output=True, text=True)
        
        health_report["checks"]["backup_system"] = {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "details": result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        health_report["checks"]["backup_system"] = {
            "status": "ERROR",
            "details": str(e)
        }
    
    # 전체 상태 결정
    failed_checks = [check for check in health_report["checks"].values() 
                    if check["status"] != "PASS"]
    
    if failed_checks:
        health_report["overall_status"] = "UNHEALTHY"
        health_report["failed_checks_count"] = len(failed_checks)
    
    return health_report

if __name__ == "__main__":
    report = check_webhook_system_health()
    
    # JSON 형태로 출력
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 상태에 따른 종료 코드
    sys.exit(0 if report["overall_status"] == "HEALTHY" else 1)
```

#### 사용법
```bash
python3 webhook_system_monitor.py
```

### 2. 자동 알림 설정

#### 문제 발생 시 자동 알림
```python
#!/usr/bin/env python3
# webhook_alert_system.py

import json
import requests
import subprocess
from datetime import datetime
from config import WATCHHAMSTER_WEBHOOK_URL

def send_webhook_alert(alert_type, message, details=None):
    """웹훅 시스템 문제 발생 시 알림 전송"""
    
    emoji_map = {
        "ERROR": "🚨",
        "WARNING": "⚠️",
        "INFO": "ℹ️",
        "SUCCESS": "✅"
    }
    
    payload = {
        "botName": "POSCO 워치햄스터 시스템 알림 🛡️",
        "botIconImage": "https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/POSCO_News_250808/posco_logo_mini.jpg",
        "text": f"{emoji_map.get(alert_type, '📢')} **웹훅 시스템 알림**\n\n"
                f"**알림 유형**: {alert_type}\n"
                f"**발생 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"**메시지**: {message}\n"
                f"{'**상세 정보**: ' + str(details) if details else ''}"
    }
    
    try:
        response = requests.post(WATCHHAMSTER_WEBHOOK_URL, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"알림 전송 실패: {e}")
        return False

def check_and_alert():
    """시스템 상태 확인 후 필요시 알림 전송"""
    
    try:
        result = subprocess.run([
            "python3", "webhook_system_monitor.py"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            # 시스템 문제 발견
            try:
                report = json.loads(result.stdout)
                failed_checks = [name for name, check in report["checks"].items() 
                               if check["status"] != "PASS"]
                
                send_webhook_alert(
                    "ERROR",
                    f"웹훅 시스템에서 {len(failed_checks)}개의 문제가 발견되었습니다.",
                    f"실패한 검사: {', '.join(failed_checks)}"
                )
                
                # 자동 복구 시도
                print("자동 복구 시도 중...")
                recovery_result = subprocess.run([
                    "./emergency_webhook_recovery.sh"
                ], capture_output=True, text=True)
                
                if recovery_result.returncode == 0:
                    send_webhook_alert(
                        "SUCCESS",
                        "웹훅 시스템 자동 복구가 완료되었습니다.",
                        "시스템이 정상 상태로 복구되었습니다."
                    )
                else:
                    send_webhook_alert(
                        "ERROR",
                        "웹훅 시스템 자동 복구에 실패했습니다.",
                        "수동 개입이 필요합니다."
                    )
                    
            except json.JSONDecodeError:
                send_webhook_alert(
                    "ERROR",
                    "웹훅 시스템 상태 확인 중 오류가 발생했습니다.",
                    result.stderr
                )
        
    except Exception as e:
        send_webhook_alert(
            "ERROR",
            "웹훅 시스템 모니터링 중 예외가 발생했습니다.",
            str(e)
        )

if __name__ == "__main__":
    check_and_alert()
```

#### 사용법
```bash
python3 webhook_alert_system.py

# 크론탭에 등록하여 정기적으로 실행
# crontab -e
# */30 * * * * /path/to/webhook_alert_system.py >> /var/log/webhook_alerts.log 2>&1
```

## 📚 교육 및 지식 전수

### 1. 신규 개발자 온보딩 체크리스트

#### 웹훅 시스템 이해도 확인
- [ ] POSCO 워치햄스터 시스템 개요 이해
- [ ] 웹훅 기능의 중요성 및 역할 파악
- [ ] 12개 웹훅 함수의 용도 및 특징 숙지
- [ ] 메시지 포맷 및 템플릿 규칙 이해
- [ ] 백업/복원 시스템 사용법 숙지

#### 실습 과제
1. **백업 생성 실습**: 안전한 백업 생성 및 검증
2. **포맷 검증 실습**: 메시지 포맷 검증 도구 사용
3. **복구 시뮬레이션**: 가상 장애 상황에서 복구 실습
4. **모니터링 실습**: 시스템 상태 모니터링 및 알림 설정

### 2. 정기 교육 프로그램

#### 월간 웹훅 시스템 리뷰
- **일정**: 매월 첫째 주 금요일
- **참석자**: 모든 개발팀원
- **내용**:
  - 지난 달 웹훅 시스템 운영 현황
  - 발생한 이슈 및 해결 과정 공유
  - 새로운 보호 규칙 또는 도구 소개
  - 베스트 프랙티스 공유

#### 분기별 종합 점검
- **일정**: 분기 마지막 주
- **내용**:
  - 전체 시스템 보안 점검
  - 백업 시스템 무결성 검증
  - 복구 절차 시뮬레이션
  - 가이드라인 업데이트

## 🔄 지속적인 개선

### 1. 피드백 수집 및 반영

#### 개선 제안 프로세스
1. **문제 발견 또는 개선 아이디어 제출**
2. **기술적 검토 및 영향도 분석**
3. **테스트 환경에서 검증**
4. **팀 리뷰 및 승인**
5. **운영 환경 적용**
6. **결과 모니터링 및 피드백**

#### 개선 제안 템플릿
```markdown
## 웹훅 시스템 개선 제안

**제안자**: [이름]
**제안일**: [날짜]
**우선순위**: [높음/중간/낮음]

### 현재 문제점
[구체적인 문제 상황 설명]

### 제안 내용
[개선 방안 상세 설명]

### 예상 효과
[개선 후 기대되는 효과]

### 구현 방안
[구체적인 구현 계획]

### 위험 요소
[예상되는 위험 및 대응 방안]
```

### 2. 도구 및 프로세스 개선

#### 자동화 확대
- 더 많은 검증 과정 자동화
- 지능형 장애 예측 시스템 도입
- 자동 성능 최적화 기능 추가

#### 사용자 경험 개선
- 더 직관적인 CLI 인터페이스
- 웹 기반 모니터링 대시보드
- 모바일 알림 지원

## 📞 지원 및 문의

### 웹훅 시스템 관련 문의
- **기술 지원**: 개발팀 리더
- **긴급 상황**: 24시간 대응팀
- **교육 문의**: 시스템 관리자

### 유용한 명령어 모음
```bash
# 시스템 상태 확인
python3 webhook_system_monitor.py

# 백업 생성
python3 webhook_backup_manager.py --create "backup_name"

# 비상 복구
./emergency_webhook_recovery.sh

# 일일 검증
./daily_webhook_verification.sh

# 포맷 검증
python3 webhook_format_validator.py --validate
```

---

**이 가이드라인을 준수하여 POSCO 워치햄스터 웹훅 시스템의 안정성과 신뢰성을 유지하시기 바랍니다.**

**최종 업데이트**: 2025년 8월 12일  
**버전**: v1.0  
**작성자**: Kiro AI Assistant