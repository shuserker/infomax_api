# 🚀 POSCO 뉴스 AI 분석 시스템 배포 가이드

## 📋 배포 개요

이 문서는 POSCO 뉴스 AI 분석 시스템을 GitHub Pages에 배포하는 방법을 설명합니다.

## 🌐 배포 URL

**https://shuserker.github.io/infomax_api/**

## 🛠️ 배포 방법

### 1. 자동 배포 (권장)

```bash
# 배포 스크립트 실행
./deploy.sh
```

### 2. 수동 배포

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 분석 리포트 생성
python run_monitor.py 8

# 3. Git 커밋 및 푸시
git add .
git commit -m "🚀 배포 업데이트"
git push origin main
```

## 📁 배포 구조

```
docs/
├── index.html              # 메인 대시보드
├── 404.html               # 에러 페이지
├── robots.txt             # SEO 설정
├── sitemap.xml            # 사이트맵
├── sw.js                  # Service Worker
├── assets/                # 정적 자원
│   ├── favicon.svg        # 파비콘
│   ├── manifest.json      # PWA 매니페스트
│   ├── og-image.svg       # Open Graph 이미지
│   └── twitter-image.svg  # Twitter Card 이미지
├── reports/               # 분석 리포트
└── dashboard_data.json    # 대시보드 데이터
```

## 🔧 GitHub Pages 설정

### 1. 저장소 설정
- GitHub 저장소 → Settings → Pages
- Source: "Deploy from a branch"
- Branch: "main"
- Folder: "/docs"

### 2. 자동 배포 활성화
- GitHub Actions 워크플로우 자동 실행
- main 브랜치에 푸시 시 자동 배포

## 📱 PWA 기능

### 설치 방법
1. Chrome/Edge에서 대시보드 접속
2. 주소창 옆 설치 아이콘 클릭
3. "설치" 버튼 클릭

### 오프라인 지원
- Service Worker가 주요 페이지 캐싱
- 인터넷 연결 없이도 기본 기능 사용 가능

## 🔄 자동 업데이트

### 웹훅 연동
- 새로운 분석 실행 시 자동으로 대시보드 업데이트
- Dooray 웹훅에 상세 리포트 링크 자동 포함

### 실시간 새로고침
- 대시보드에서 "🔄 새로고침" 버튼으로 수동 업데이트
- 30초마다 자동 시간 업데이트

## 🎨 테마 지원

### 다크/라이트 모드
- 🌙/☀️ 버튼으로 테마 전환
- 사용자 설정 자동 저장

## 📊 분석 리포트

### 제공되는 분석
- **KOSPI CLOSE**: 코스피 종가 분석
- **EXCHANGE RATE**: 환율 분석
- **NEWYORK MARKET WATCH**: 뉴욕 시장 분석

### 리포트 내용
- 섹터별 성과 분석
- 투자 전략 가이드
- 글로벌 영향도 분석
- AI 예측 분석

## 🔍 SEO 최적화

### 메타데이터
- Open Graph 태그
- Twitter Cards
- 검색 엔진 최적화

### 사이트맵
- 자동 생성되는 sitemap.xml
- 검색 엔진 크롤링 최적화

## 🛡️ 보안

### HTTPS 강제
- GitHub Pages 자동 HTTPS 제공
- 보안 연결 보장

### CSP 설정
- Content Security Policy 적용
- XSS 공격 방지

## 📈 성능 최적화

### 캐싱
- Service Worker를 통한 정적 자원 캐싱
- 빠른 로딩 속도

### 압축
- 이미지 및 파일 최적화
- 대역폭 절약

## 🔗 관련 링크

- **대시보드**: https://shuserker.github.io/infomax_api/
- **GitHub 저장소**: https://github.com/shuserker/infomax_api
- **문서**: https://shuserker.github.io/infomax_api/docs/README.md

## 🆘 문제 해결

### 배포 실패 시
1. GitHub Actions 로그 확인
2. 의존성 설치 상태 확인
3. 파일 권한 확인

### 접속 불가 시
1. GitHub Pages 설정 확인
2. DNS 설정 확인
3. 캐시 삭제 후 재시도

---

© 2025 POSCO 뉴스 AI 분석 시스템 | 실시간 시장 모니터링 