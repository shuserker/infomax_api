# POSCO 리포트 대시보드 개선 설계 문서

## 개요

현재 단순한 리포트 목록 형태의 대시보드를 현대적이고 기능이 풍부한 대시보드로 개선합니다. 사용자 경험을 중심으로 한 직관적인 인터페이스와 실시간 모니터링 기능을 제공합니다.

## 아키텍처

### 전체 구조
```
대시보드 시스템
├── 프론트엔드 (정적 HTML/CSS/JS)
│   ├── 메인 대시보드 (index.html)
│   ├── 리포트 뷰어 (report-viewer.html)
│   └── 관리자 패널 (admin.html)
├── 데이터 레이어
│   ├── 리포트 메타데이터 (reports.json)
│   ├── 시스템 상태 (status.json)
│   └── 사용자 설정 (localStorage)
└── 백엔드 연동
    ├── GitHub Pages 정적 호스팅
    ├── API 엔드포인트 (상태 조회)
    └── 실시간 업데이트 (polling)
```

### 컴포넌트 구조
```
Dashboard
├── Header (제목, 네비게이션, 테마 토글)
├── StatusBar (실시간 뉴스 상태)
├── FilterPanel (검색, 필터, 정렬)
├── StatsSection (통계 차트)
├── ReportGrid (리포트 카드들)
├── QuickAccess (즐겨찾기, 최근 본 항목)
└── Footer (정보, 링크)
```

## 컴포넌트 및 인터페이스

### 1. 메인 대시보드 (index.html)

#### Header 컴포넌트
- **로고 및 제목**: POSCO 뉴스 AI 분석 대시보드
- **네비게이션**: 홈, 통계, 설정
- **테마 토글**: 라이트/다크 모드 전환
- **실시간 시계**: 현재 시간 표시

#### StatusBar 컴포넌트
```javascript
{
  newsStatus: {
    exchangeRate: { published: true, time: "16:30", status: "latest" },
    kospiClose: { published: true, time: "15:40", status: "latest" },
    newyorkWatch: { published: true, time: "06:24", status: "latest" }
  },
  systemStatus: {
    monitoring: "active",
    lastUpdate: "2025-08-02 23:30:00",
    uptime: "99.8%"
  }
}
```

#### FilterPanel 컴포넌트
- **검색바**: 리포트 제목/내용 검색
- **타입 필터**: 통합리포트, 서환마감, 증시마감, 뉴욕마켓워치
- **날짜 필터**: 오늘, 어제, 최근 7일, 최근 30일, 사용자 정의
- **정렬 옵션**: 최신순, 오래된순, 이름순

#### StatsSection 컴포넌트
- **일일 통계**: 오늘 생성된 리포트 수
- **주간 트렌드**: 최근 7일 리포트 생성 추이
- **타입별 분포**: 각 뉴스 타입별 리포트 비율
- **성공률**: 리포트 생성 성공률

#### ReportGrid 컴포넌트
```javascript
ReportCard {
  id: "report_id",
  title: "POSCO 뉴스 통합 분석 리포트",
  type: "integrated", // integrated, exchange-rate, kospi-close, newyork-market-watch
  date: "2025-08-02",
  time: "18:00",
  thumbnail: "preview_image_url",
  summary: "3개 뉴스 완료, 시장 분위기 긍정",
  url: "report_url",
  isFavorite: false,
  tags: ["통합분석", "일일리포트"]
}
```

### 2. 리포트 뷰어 (report-viewer.html)

#### 기능
- **임베드 뷰어**: iframe으로 리포트 표시
- **네비게이션**: 이전/다음 리포트 이동
- **공유 기능**: URL 복사, 다운로드
- **즐겨찾기**: 리포트 즐겨찾기 추가/제거

### 3. 관리자 패널 (admin.html)

#### 기능
- **시스템 상태 모니터링**: 실시간 시스템 상태
- **리포트 관리**: 리포트 삭제, 메타데이터 수정
- **설정 관리**: 대시보드 설정 변경
- **로그 뷰어**: 시스템 로그 확인

## 데이터 모델

### 리포트 메타데이터 (reports.json)
```json
{
  "lastUpdate": "2025-08-02T23:30:00Z",
  "totalReports": 156,
  "reports": [
    {
      "id": "20250802_180000_integrated",
      "filename": "posco_integrated_analysis_20250802_180000.html",
      "title": "POSCO 뉴스 통합 분석 리포트",
      "type": "integrated",
      "date": "2025-08-02",
      "time": "18:00:00",
      "size": 245760,
      "summary": {
        "newsCount": 3,
        "completionRate": "3/3",
        "marketSentiment": "긍정",
        "keyInsights": ["환율 안정", "증시 상승", "뉴욕 호조"]
      },
      "tags": ["통합분석", "일일리포트", "완전분석"],
      "url": "https://shuserker.github.io/infomax_api/reports/posco_integrated_analysis_20250802_180000.html",
      "createdAt": "2025-08-02T18:00:00Z"
    }
  ]
}
```

### 시스템 상태 (status.json)
```json
{
  "lastUpdate": "2025-08-02T23:30:00Z",
  "newsStatus": {
    "exchange-rate": {
      "published": true,
      "publishTime": "16:30:00",
      "status": "latest",
      "title": "달러-원 환율 1,350원대 마감"
    },
    "kospi-close": {
      "published": true,
      "publishTime": "15:40:00", 
      "status": "latest",
      "title": "KOSPI 2,500선 회복"
    },
    "newyork-market-watch": {
      "published": true,
      "publishTime": "06:24:00",
      "status": "latest",
      "title": "뉴욕 증시 상승 마감"
    }
  },
  "systemStatus": {
    "monitoring": "active",
    "uptime": "99.8%",
    "lastReportGenerated": "2025-08-02T18:00:00Z",
    "totalReportsToday": 12,
    "errors": []
  }
}
```

## 오류 처리

### 클라이언트 사이드 오류
- **네트워크 오류**: 오프라인 모드 지원, 재시도 메커니즘
- **데이터 로딩 실패**: 스켈레톤 UI, 오류 메시지 표시
- **브라우저 호환성**: 폴리필 제공, 우아한 성능 저하

### 서버 사이드 오류
- **GitHub Pages 장애**: 캐시된 데이터 사용
- **API 응답 지연**: 타임아웃 설정, 로딩 인디케이터
- **데이터 파싱 오류**: 기본값 사용, 오류 로깅

## 테스트 전략

### 단위 테스트
- **JavaScript 함수**: Jest를 사용한 유틸리티 함수 테스트
- **컴포넌트 로직**: 필터링, 정렬, 검색 기능 테스트
- **데이터 처리**: JSON 파싱, 날짜 처리 함수 테스트

### 통합 테스트
- **API 연동**: 실제 데이터 소스와의 연동 테스트
- **브라우저 테스트**: Chrome, Firefox, Safari 호환성 테스트
- **반응형 테스트**: 다양한 화면 크기에서의 레이아웃 테스트

### 성능 테스트
- **로딩 시간**: 초기 로딩 3초 이내 목표
- **메모리 사용량**: 대량 데이터 처리 시 메모리 누수 방지
- **네트워크 최적화**: 이미지 압축, 리소스 번들링

## 보안 고려사항

### 클라이언트 보안
- **XSS 방지**: 사용자 입력 데이터 이스케이프 처리
- **CSRF 방지**: 토큰 기반 요청 검증
- **데이터 검증**: 클라이언트 사이드 입력 검증

### 데이터 보안
- **민감 정보 보호**: API 키, 토큰 등 클라이언트 노출 방지
- **HTTPS 강제**: 모든 통신 암호화
- **접근 제어**: 관리자 기능 접근 제한

## 성능 최적화

### 프론트엔드 최적화
- **코드 분할**: 필요한 기능만 로딩
- **이미지 최적화**: WebP 포맷, 지연 로딩
- **캐싱 전략**: 브라우저 캐시, 서비스 워커 활용

### 데이터 최적화
- **페이지네이션**: 대량 데이터 분할 로딩
- **압축**: Gzip 압축 적용
- **CDN 활용**: 정적 리소스 CDN 배포

## 배포 전략

### GitHub Pages 배포
- **자동 배포**: GitHub Actions를 통한 자동 빌드/배포
- **브랜치 전략**: main 브랜치에서 publish 브랜치로 자동 배포
- **롤백 계획**: 이전 버전으로 빠른 롤백 지원

### 모니터링
- **사용자 분석**: Google Analytics 연동
- **오류 추적**: 클라이언트 오류 로깅
- **성능 모니터링**: Core Web Vitals 추적