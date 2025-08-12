# 🐹 WatchHamster Mac 실행 가이드 v4.0

## 📋 개요
WatchHamster 시스템을 Mac 환경에서 실행하기 위한 완전한 가이드입니다. 개선된 기능들과 함께 안정적인 모니터링 시스템을 구축할 수 있습니다.

## 🚀 빠른 시작

### 1. 시스템 실행
```bash
# 메인 제어 센터 실행
bash .naming_backup/scripts/.naming_backup/scripts/watchhamster_master_control.sh

# 또는 직접 실행
./.naming_backup/scripts/.naming_backup/scripts/watchhamster_master_control.sh
```

### 2. POSCO 모니터링 실행
```bash
# POSCO 제어 센터 직접 실행
bash .naming_backup/scripts/.naming_backup/scripts/posco_control_center.sh

# 또는 메인 메뉴에서 선택
```

## 📁 파일 구조

### 핵심 파일들
```
infomax_api/
├── lib_wt_common.sh                    # 공통 라이브러리 (Mac용)
├── watchhamster_master_control.sh      # 메인 제어 센터 (Mac용)
├── posco_control_center.sh             # POSCO 제어 센터 (Mac용)
├── lib_wt_common.ps1                   # 공통 라이브러리 (PowerShell용)
├── watchhamster_master_control.ps1     # 메인 제어 센터 (PowerShell용)
├── posco_control_center.ps1            # POSCO 제어 센터 (PowerShell용)
└── Monitoring/
    └── POSCO News/
        └── posco_control_center.sh     # POSCO 모니터링 센터
```

## 🎯 주요 기능

### 메인 제어 센터 기능
- 🏭 **POSCO 뉴스 모니터링**: POSCO News 및 주가 모니터링 시스템
- 🛡️ **전체 시스템 상태**: 모든 WatchHamster 상태 확인
- 🔄 **전체 시스템 업데이트**: 모든 시스템 Git 업데이트
- 📋 **통합 로그 관리**: 모든 시스템 로그 통합 관리
- 🧪 **전체 시스템 테스트**: 모든 시스템 통합 테스트
- 📦 **전체 백업 생성**: 모든 시스템 통합 백업
- 🔧 **WatchHamster 설정**: 총괄 설정 관리
- 🎨 **UI 테마 변경**: 색상 테마 및 인터페이스 설정

### POSCO 제어 센터 기능
- 🚀 **WatchHamster 시작**: POSCO 뉴스 모니터링 시작
- 🛑 **WatchHamster 중지**: 모니터링 프로세스 중지
- 🔄 **WatchHamster 재시작**: 모니터링 시스템 재시작
- 📊 **실시간 상태 확인**: 현재 모니터링 상태 확인
- 📋 **뉴스 로그 확인**: 최신 뉴스 로그 확인
- 📈 **뉴스 통계 보기**: 뉴스 수집 통계 확인
- 🔍 **뉴스 검색**: 특정 키워드 뉴스 검색
- 🔧 **시스템 상태**: POSCO 시스템 상태 확인
- 🧪 **시스템 테스트**: 모니터링 시스템 테스트
- 📦 **데이터 백업**: 뉴스 데이터 백업

## 🔧 시스템 요구사항

### 필수 소프트웨어
- **macOS**: 10.14 (Mojave) 이상
- **Python**: 3.7 이상
- **Git**: 최신 버전 권장
- **터미널**: 기본 Terminal.app 또는 iTerm2

### 권장 사항
- **Python 패키지**: requirements.txt에 명시된 패키지들
- **네트워크**: 안정적인 인터넷 연결
- **저장공간**: 최소 1GB 여유 공간

## 📊 개선된 기능

### 1. 메모리 계산 개선
- Mac의 `vm_stat` 명령어를 활용한 정확한 메모리 사용률 계산
- `bc` 명령어를 사용한 부동소수점 연산 지원
- 대체 방법으로 `top` 명령어 사용

### 2. 로깅 시스템 강화
- 구조화된 로그 파일 관리
- 로그 레벨별 분리 (INFO, WARNING, ERROR, SUCCESS)
- 자동 로그 정리 기능 (30일 이상 된 로그 자동 삭제)

### 3. 파일명 영문화
- 이모지가 포함된 파일명을 영문으로 변경
- 터미널 호환성 향상
- 크로스 플랫폼 지원

### 4. 설정 파일 관리
- JSON 기반 설정 파일 시스템
- 사용자별 설정 저장 (`~/.watchhamster/config.json`)
- 설정 백업 및 복원 기능

## 🛠️ 설치 및 설정

### 1. 초기 설정
```bash
# 실행 권한 부여
chmod +x lib_wt_common.sh watchhamster_master_control.sh posco_control_center.sh

# Python 환경 확인
python3 --version

# 필요한 패키지 설치
pip3 install -r requirements.txt
```

### 2. 설정 파일 생성
```bash
# 설정 디렉토리 생성 (자동 생성됨)
mkdir -p ~/.watchhamster

# 기본 설정 파일 생성
cat > ~/.watchhamster/config.json << EOF
{
    "log_level": "INFO",
    "monitoring_interval": 60,
    "notification_level": "all",
    "theme": "default",
    "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. 실행 권한 오류
```bash
# 해결 방법
chmod +x *.sh
```

#### 2. Python 경로 문제
```bash
# Python 경로 확인
which python3
which python

# PATH 설정 확인
echo $PATH
```

#### 3. 로그 파일 접근 오류
```bash
# 로그 디렉토리 권한 확인
ls -la ~/.watchhamster/

# 권한 수정
chmod 755 ~/.watchhamster/
```

#### 4. 메모리 계산 오류
```bash
# bc 명령어 설치 확인
which bc

# Homebrew로 설치 (필요시)
brew install bc
```

### 디버깅 모드
```bash
# 상세 로그 활성화
export WATCHHAMSTER_DEBUG=1
bash .naming_backup/scripts/.naming_backup/scripts/watchhamster_master_control.sh
```

## 📈 성능 최적화

### 1. 시스템 리소스 모니터링
- CPU 사용률 실시간 모니터링
- 메모리 사용률 정확한 계산
- 디스크 사용률 확인

### 2. 로그 관리 최적화
- 로그 파일 크기 제한
- 자동 로그 로테이션
- 오래된 로그 자동 정리

### 3. 네트워크 최적화
- 연결 상태 실시간 확인
- 타임아웃 설정 최적화
- 재시도 로직 구현

## 🔄 업데이트 및 유지보수

### 1. 시스템 업데이트
```bash
# Git을 통한 자동 업데이트
# 메인 메뉴에서 "B. 전체 시스템 업데이트" 선택
```

### 2. 백업 생성
```bash
# 자동 백업 생성
# 메인 메뉴에서 "E. 전체 백업 생성" 선택
```

### 3. 로그 정리
```bash
# 로그 관리 메뉴에서 "3. 로그 파일 정리" 선택
```

## 🌐 크로스 플랫폼 지원

### Windows PowerShell 버전
- 동일한 기능을 PowerShell로 구현
- Windows 10/11 최적화
- Windows Terminal 지원

### 실행 방법
```powershell
# PowerShell에서 실행
.\watchhamster_master_control.ps1
```

## 📞 지원 및 문의

### 로그 확인
```bash
# 시스템 로그 확인
tail -f ~/.watchhamster/logs/system.log

# 에러 로그 확인
tail -f ~/.watchhamster/logs/error.log
```

### 문제 보고
1. 시스템 상태 확인
2. 로그 파일 분석
3. 재현 단계 기록
4. 환경 정보 수집

## 🎉 완료!

WatchHamster 시스템이 성공적으로 설정되었습니다. 이제 안정적이고 효율적인 모니터링 시스템을 사용할 수 있습니다.

### 다음 단계
1. 메인 제어 센터 실행
2. POSCO 모니터링 설정
3. 알림 설정 구성
4. 정기적인 백업 스케줄 설정

---

**버전**: v4.0  
**최종 업데이트**: $(date '+%Y-%m-%d')  
**지원 플랫폼**: macOS, Windows (PowerShell) 