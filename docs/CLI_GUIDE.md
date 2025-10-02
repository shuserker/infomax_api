# 🖥️ POSCO 뉴스 AI 분석 시스템 CLI 가이드

## 📋 개요

POSCO 뉴스 AI 분석 시스템의 모든 기능을 명령줄에서 사용할 수 있는 통합 CLI 도구입니다.

## 🚀 설치 및 실행

### 실행 방법
```bash
# 직접 실행
# BROKEN_REF: python3 posco_cli.py [명령어]

# 실행 권한 부여 후 실행
chmod +x posco_cli.py
./posco_cli.py [명령어]
```

### 도움말 확인
```bash
# BROKEN_REF: python3 posco_cli.py --help
```

## 📚 명령어 목록

### 🔍 상태 확인
```bash
# 현재 시스템 상태 확인
# BROKEN_REF: python3 posco_cli.py status

# 시스템 상태 점검
# BROKEN_REF: python3 posco_cli.py health
```

### 🚀 모니터링
```bash
# 기본 모니터링 시작 (60분 간격)
# BROKEN_REF: python3 posco_cli.py monitor

# 사용자 지정 간격으로 모니터링
# BROKEN_REF: python3 posco_cli.py monitor --interval 30

# 스마트 모니터링 시작
# BROKEN_REF: python3 posco_cli.py monitor --smart
```

### 🧠 분석
```bash
# 기본 분석 실행
# BROKEN_REF: python3 posco_cli.py analyze

# 간단 분석 실행
# BROKEN_REF: python3 posco_cli.py analyze --simple

# 고급 분석 실행
# BROKEN_REF: python3 posco_cli.py analyze --advanced

# 특정 일수로 분석
# BROKEN_REF: python3 posco_cli.py analyze --days 7
```

### 🚀 배포
```bash
# 자동 배포 실행
# BROKEN_REF: python3 posco_cli.py deploy

# 커스텀 메시지로 배포
# BROKEN_REF: python3 posco_cli.py deploy --message "🚀 새로운 기능 배포"
```

### 🧪 테스트
```bash
# 전체 시스템 테스트
# BROKEN_REF: python3 posco_cli.py test
```

### ⚙️ 설정 관리
```bash
# 현재 설정 확인
# BROKEN_REF: python3 posco_cli.py config --show

# 설정 유효성 검사
# BROKEN_REF: python3 posco_cli.py config --validate
```

### 📋 로그 관리
```bash
# 전체 로그 확인
# BROKEN_REF: python3 posco_cli.py logs

# 최근 50줄 로그 확인
# BROKEN_REF: python3 posco_cli.py logs --lines 50
```

### 📊 대시보드
```bash
# 대시보드 정보 확인
# BROKEN_REF: python3 posco_cli.py dashboard
```

### 📄 리포트 관리
```bash
# 리포트 목록 확인
# BROKEN_REF: python3 posco_cli.py report --list

# 오래된 리포트 정리 (7일 이상)
# BROKEN_REF: python3 posco_cli.py report --clean
```

### 💾 백업 관리
```bash
# 백업 생성
# BROKEN_REF: python3 posco_cli.py backup --create

# 백업 목록 확인
# BROKEN_REF: python3 posco_cli.py backup --list
```

## 🎯 사용 시나리오

### 1. 일일 모니터링 시작
```bash
# 스마트 모니터링으로 시작
# BROKEN_REF: python3 posco_cli.py monitor --smart
```

### 2. 주간 분석 실행
```bash
# 고급 분석으로 주간 리포트 생성
# BROKEN_REF: python3 posco_cli.py analyze --advanced --days 7
```

### 3. 시스템 점검
```bash
# 시스템 상태 점검
# BROKEN_REF: python3 posco_cli.py health

# 설정 확인
# BROKEN_REF: python3 posco_cli.py config --show
```

### 4. 배포 및 관리
```bash
# 분석 후 자동 배포
# BROKEN_REF: python3 posco_cli.py deploy

# 리포트 정리
# BROKEN_REF: python3 posco_cli.py report --clean

# 백업 생성
# BROKEN_REF: python3 posco_cli.py backup --create
```

### 5. 문제 해결
```bash
# 시스템 테스트
# BROKEN_REF: python3 posco_cli.py test

# 로그 확인
# BROKEN_REF: python3 posco_cli.py logs --lines 100

# 상태 확인
# BROKEN_REF: python3 posco_cli.py status
```

## 🔧 고급 사용법

### 배치 스크립트 예시
```bash
#!/bin/bash
# daily_analysis.sh

echo "🚀 일일 분석 시작..."

# 시스템 상태 점검
# BROKEN_REF: python3 posco_cli.py health

# 고급 분석 실행
# BROKEN_REF: python3 posco_cli.py analyze --advanced --days 30

# 자동 배포
# BROKEN_REF: python3 posco_cli.py deploy

# 오래된 리포트 정리
# BROKEN_REF: python3 posco_cli.py report --clean

echo "✅ 일일 분석 완료!"
```

### 크론 작업 설정
```bash
# crontab -e
# 매일 오전 9시에 분석 실행
# BROKEN_REF: 0 9 * * * cd /path/to/posco_news_mini && python3 posco_cli.py analyze --advanced

# 매주 일요일 오전 8시에 백업 생성
# BROKEN_REF: 0 8 * * 0 cd /path/to/posco_news_mini && python3 posco_cli.py backup --create
```

## 📊 출력 예시

### 상태 확인
```
📊 POSCO 뉴스 모니터링 상태 확인 중...
🔗 API 연결 테스트 중...
✅ API 연결 성공

==================================================
📈 POSCO 뉴스 모니터링 상태
==================================================

📰 KOSPI CLOSE
   상태: 정상
   최신 뉴스: [뉴욕마켓워치] 트럼프와 폰데어라이엔의 무역 담판…주식·채권·달러↑
   발행 시간: 2025-07-28 09:00:00
   예상 발행: 2025-07-29 09:00:00

🕐 확인 시간: 2025-07-28 15:30:45
```

### 시스템 점검
```
🏥 시스템 상태 점검 중...

============================================================
📊 시스템 상태 점검 결과
============================================================
✅ Python 버전: 3.9.7
✅ requests 패키지: 설치됨
✅ textblob 패키지: 설치됨
✅ numpy 패키지: 설치됨
✅ pandas 패키지: 설치됨
✅ config.py 파일: 존재함
✅ core/__init__.py 파일: 존재함
✅ docs 디렉토리: 존재함
✅ reports 디렉토리: 존재함
✅ docs/reports 디렉토리: 존재함

============================================================
🎉 모든 점검이 통과되었습니다!
```

## 🆘 문제 해결

### 일반적인 문제들

#### 1. 모듈을 찾을 수 없음
```bash
# Python 경로 확인
# BROKEN_REF: python3 -c "import sys; print(sys.path)"

# 프로젝트 루트에서 실행
cd /path/to/posco_news_mini
# BROKEN_REF: python3 posco_cli.py [명령어]
```

#### 2. 권한 오류
```bash
# 실행 권한 부여
chmod +x posco_cli.py

# 또는 python3로 직접 실행
# BROKEN_REF: python3 posco_cli.py [명령어]
```

#### 3. 설정 오류
```bash
# 설정 확인
# BROKEN_REF: python3 posco_cli.py config --show

# 설정 유효성 검사
# BROKEN_REF: python3 posco_cli.py config --validate
```

#### 4. API 연결 실패
```bash
# 연결 테스트
# BROKEN_REF: python3 posco_cli.py test

# 상태 확인
# BROKEN_REF: python3 posco_cli.py status
```

## 🔗 관련 문서

- **배포 가이드**: DEPLOYMENT.md
- **GitHub Pages 설정**: GITHUB_PAGES_SETUP.md
- **메인 README**: README.md

---

## 🎯 CLI 특징

✅ **통합 관리**: 모든 기능을 하나의 CLI로 관리  
✅ **자동화 지원**: 배치 스크립트 및 크론 작업 지원  
✅ **상태 모니터링**: 실시간 시스템 상태 확인  
✅ **백업 관리**: 자동 백업 및 복구 기능  
✅ **로그 관리**: 체계적인 로그 확인 및 관리  
✅ **문제 해결**: 자동 진단 및 문제 해결 도구  

**🚀 이제 명령줄에서 POSCO 뉴스 AI 분석 시스템의 모든 기능을 쉽게 사용할 수 있습니다!** 