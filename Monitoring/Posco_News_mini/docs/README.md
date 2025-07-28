# POSCO 뉴스 AI 분석 대시보드

## 📊 GitHub Pages 설정 가이드

이 디렉토리는 GitHub Pages를 통해 공개 웹사이트로 제공되는 POSCO 뉴스 AI 분석 대시보드입니다.

### 🚀 설정 방법

1. **GitHub 저장소 설정**
   - GitHub 저장소의 Settings → Pages로 이동
   - Source를 "Deploy from a branch"로 설정
   - Branch를 "main"으로, 폴더를 "/docs"로 설정
   - Save 클릭

2. **자동 배포**
   - `docs/` 폴더의 내용이 자동으로 GitHub Pages에 배포됩니다
   - URL: `https://shuserker.github.io/infomax_api/`

### 📁 파일 구조

```
docs/
├── index.html              # 메인 대시보드 페이지
├── 404.html               # 404 에러 페이지
├── robots.txt             # 검색 엔진 크롤링 설정
├── sitemap.xml            # 사이트맵
├── .nojekyll              # Jekyll 비활성화
├── CNAME                  # 커스텀 도메인 설정
├── sw.js                  # Service Worker
├── assets/                # 정적 자원
│   ├── favicon.svg        # 파비콘
│   ├── manifest.json      # PWA 매니페스트
│   └── ...
├── dashboard_data.json    # 리포트 목록 데이터
├── reports/               # HTML 리포트 파일들
│   ├── posco_analysis_*.html
│   └── ...
└── README.md              # 이 파일
```

### 🔄 자동 업데이트

- 새로운 분석이 실행될 때마다 자동으로 `docs/` 폴더가 업데이트됩니다
- `dashboard_data.json`이 실시간으로 업데이트되어 최신 리포트 목록을 제공합니다
- HTML 리포트 파일들이 `docs/reports/` 폴더에 자동 생성됩니다

### 📱 접근 방법

1. **웹 브라우저**: `https://shuserker.github.io/infomax_api/`로 직접 접근
2. **모바일**: 반응형 디자인으로 모바일에서도 최적화
3. **공유**: URL을 통해 누구나 접근 가능
4. **PWA 설치**: Chrome/Edge에서 앱처럼 설치 가능

### 🛠️ 기술 스택

- **HTML5**: 반응형 웹 디자인
- **CSS3**: 모던한 스타일링
- **JavaScript**: 동적 데이터 로딩
- **Chart.js**: 인터랙티브 차트
- **PWA**: Service Worker, Web App Manifest
- **GitHub Pages**: 무료 호스팅

### 📊 주요 기능

- **실시간 대시보드**: 최신 분석 결과 표시
- **인터랙티브 차트**: 시각적 데이터 분석
- **반응형 디자인**: 모든 디바이스 지원
- **자동 업데이트**: 새로운 분석 자동 반영
- **PWA 지원**: 오프라인 사용 가능
- **SEO 최적화**: 검색 엔진 최적화

### 🔗 링크

- **대시보드**: `https://shuserker.github.io/infomax_api/`
- **개별 리포트**: `https://shuserker.github.io/infomax_api/reports/[파일명].html`
- **GitHub 저장소**: `https://github.com/shuserker/infomax_api`

### 📈 분석 리포트

#### 제공되는 분석
- **KOSPI CLOSE**: 코스피 종가 분석
- **EXCHANGE RATE**: 환율 분석  
- **NEWYORK MARKET WATCH**: 뉴욕 시장 분석

#### 리포트 내용
- 섹터별 성과 분석
- 투자 전략 가이드
- 글로벌 영향도 분석
- 월간/주간 트렌드 분석
- AI 예측 분석

### 🔧 설정 완료 상태

✅ **GitHub Pages 설정**: `shuserker.github.io/infomax_api/`  
✅ **PWA 지원**: Service Worker, Manifest  
✅ **SEO 최적화**: Open Graph, Twitter Cards, Sitemap  
✅ **오프라인 지원**: 캐싱 및 오프라인 기능  
✅ **반응형 디자인**: 모바일/태블릿/데스크톱 지원  

---

© 2025 POSCO 뉴스 AI 분석 시스템 | 실시간 시장 모니터링 