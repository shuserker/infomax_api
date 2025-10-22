# WatchHamster Tauri FAQ (자주 묻는 질문)

## 📋 목차

1. [일반적인 질문](#일반적인-질문)
2. [설치 및 설정](#설치-및-설정)
3. [기능 관련](#기능-관련)
4. [성능 및 최적화](#성능-및-최적화)
5. [문제 해결](#문제-해결)
6. [보안 및 개인정보](#보안-및-개인정보)
7. [개발 및 커스터마이징](#개발-및-커스터마이징)

## 🤔 일반적인 질문

### Q1: WatchHamster Tauri 버전과 기존 Tkinter 버전의 차이점은 무엇인가요?

**A:** 주요 차이점은 다음과 같습니다:

| 구분 | 기존 Tkinter 버전 | 새로운 Tauri 버전 |
|------|------------------|------------------|
| **UI 기술** | Python Tkinter | React + Chakra UI |
| **성능** | 느린 시작 시간 (~8초) | 빠른 시작 시간 (~3초) |
| **메모리 사용** | ~150MB | ~80MB |
| **실시간 업데이트** | 폴링 기반 | WebSocket 기반 |
| **사용자 경험** | 기본적인 GUI | 현대적인 웹 UI |
| **크로스 플랫폼** | 제한적 지원 | 완전한 크로스 플랫폼 |
| **확장성** | 모놀리식 구조 | 마이크로서비스 아키텍처 |

### Q2: 기존 설정과 데이터가 자동으로 마이그레이션되나요?

**A:** 네, 자동 마이그레이션을 지원합니다:
- ✅ 서비스 설정 자동 변환
- ✅ 웹훅 URL 및 메시지 템플릿 보존
- ✅ 사용자 설정 (테마, 알림 등) 유지
- ✅ 로그 파일 위치 자동 감지
- ⚠️ 일부 고급 설정은 수동 조정 필요할 수 있음

### Q3: 두 버전을 동시에 사용할 수 있나요?

**A:** 기술적으로는 가능하지만 권장하지 않습니다:
- 🔴 **포트 충돌**: 두 버전 모두 8000번 포트 사용
- 🔴 **리소스 중복**: 동일한 서비스를 두 번 모니터링
- 🔴 **설정 충돌**: 동일한 설정 파일 접근 시 문제 발생
- ✅ **테스트 목적**: 다른 포트로 설정하여 테스트 가능

### Q4: Tauri 버전의 시스템 요구사항은 무엇인가요?

**A:** 최소 시스템 요구사항:

**Windows:**
- Windows 10 1903 이상 (64비트)
- RAM: 4GB 이상 (8GB 권장)
- 디스크 공간: 500MB 이상
- .NET Framework 4.8 이상

**macOS:**
- macOS 10.15 (Catalina) 이상
- RAM: 4GB 이상 (8GB 권장)
- 디스크 공간: 500MB 이상

**Linux:**
- Ubuntu 18.04 LTS 이상 또는 동등한 배포판
- RAM: 4GB 이상 (8GB 권장)
- 디스크 공간: 500MB 이상
- GTK 3.24 이상

## 🔧 설치 및 설정

### Q5: 설치 과정에서 "바이러스가 감지되었습니다" 경고가 나타나는데 안전한가요?

**A:** 이는 일반적인 오탐지입니다:
- 🛡️ **코드 서명**: 모든 릴리스는 디지털 서명됨
- 🔍 **오픈 소스**: 전체 소스 코드가 공개되어 검증 가능
- 📋 **해결 방법**:
  1. Windows Defender SmartScreen에서 "추가 정보" → "실행" 클릭
  2. 바이러스 백신 프로그램의 예외 목록에 추가
  3. 공식 GitHub 릴리스에서만 다운로드

### Q6: 설치 후 첫 실행 시 해야 할 설정이 있나요?

**A:** 기본 설정 체크리스트:

1. **웹훅 설정** (선택사항)
   - Discord/Slack 웹훅 URL 추가
   - 테스트 메시지 전송으로 연결 확인

2. **알림 설정**
   - 시스템 알림 활성화/비활성화
   - 알림 우선순위 설정

3. **테마 선택**
   - 라이트/다크 모드 선택
   - POSCO 기업 테마 적용 (선택사항)

4. **자동 시작 설정**
   - 시스템 부팅 시 자동 실행 여부

### Q7: 포터블 버전이 있나요?

**A:** 현재는 설치 버전만 제공하지만, 포터블 모드를 지원합니다:
- 📁 **포터블 모드**: `--portable` 플래그로 실행
- 💾 **설정 저장**: 실행 파일과 같은 폴더에 설정 저장
- 🔄 **USB 실행**: USB 드라이브에서 직접 실행 가능
- ⚠️ **제한사항**: 시스템 서비스 등록 불가

## ⚙️ 기능 관련

### Q8: 새로운 서비스를 추가할 수 있나요?

**A:** 네, 여러 방법으로 가능합니다:

1. **플러그인 시스템** (권장)
   - JavaScript/TypeScript로 플러그인 개발
   - 설정 → 플러그인에서 설치

2. **커스텀 스크립트**
   - Python/PowerShell 스크립트 등록
   - 이벤트 기반 또는 스케줄 기반 실행

3. **API 통합**
   - REST API를 통한 외부 시스템 연동
   - WebSocket으로 실시간 데이터 수신

### Q9: 로그를 외부 시스템으로 전송할 수 있나요?

**A:** 다양한 방법을 지원합니다:

- 📤 **웹훅**: Discord, Slack, 커스텀 웹훅으로 실시간 전송
- 📊 **Syslog**: 표준 Syslog 프로토콜 지원
- 📁 **파일 공유**: 네트워크 드라이브에 로그 파일 저장
- 🔌 **API**: REST API를 통한 로그 데이터 조회
- 📧 **이메일**: 중요한 이벤트 발생 시 이메일 알림

### Q10: 여러 대의 컴퓨터에서 동일한 설정을 사용할 수 있나요?

**A:** 설정 동기화 기능을 제공합니다:

1. **설정 내보내기/가져오기**
   - 설정 → 고급 → "설정 내보내기"
   - JSON 파일로 설정 백업 및 복원

2. **클라우드 동기화** (향후 지원 예정)
   - Google Drive, OneDrive 연동
   - 자동 설정 동기화

3. **네트워크 설정 공유**
   - 공유 폴더에 설정 파일 저장
   - 여러 컴퓨터에서 동일한 설정 파일 참조

### Q11: 모바일에서도 사용할 수 있나요?

**A:** 현재는 데스크톱 전용이지만, 웹 인터페이스를 통한 접근이 가능합니다:

- 🌐 **웹 대시보드**: 브라우저에서 `http://localhost:8000` 접속
- 📱 **모바일 브라우저**: 스마트폰/태블릿 브라우저에서 접근 가능
- 🔒 **보안 주의**: 외부 접근 시 VPN 또는 보안 설정 필요
- 📋 **제한사항**: 일부 고급 기능은 데스크톱 앱에서만 사용 가능

## 🚀 성능 및 최적화

### Q12: 메모리 사용량을 줄이는 방법이 있나요?

**A:** 여러 최적화 방법을 제공합니다:

1. **메모리 최적화 모드**
   - 설정 → 일반 → 성능 → "메모리 최적화" 활성화

2. **로그 버퍼 크기 조정**
   - 설정 → 로그 → "최대 메모리 내 로그 수" 감소

3. **차트 데이터 보관 기간 단축**
   - 설정 → 대시보드 → "차트 데이터 보관 기간" 조정

4. **불필요한 서비스 비활성화**
   - 사용하지 않는 모니터링 서비스 중지

5. **새로고침 간격 증가**
   - 설정 → 일반 → "새로고침 간격" 5초 이상으로 설정

### Q13: CPU 사용률이 높은 경우 어떻게 해야 하나요?

**A:** CPU 사용률 최적화 방법:

1. **새로고침 간격 조정**
   - 1초 → 5초 이상으로 변경하여 부하 감소

2. **로그 레벨 조정**
   - DEBUG 레벨 비활성화
   - ERROR/WARNING만 활성화

3. **실시간 기능 제한**
   - 실시간 차트 업데이트 비활성화
   - WebSocket 연결 수 제한

4. **백그라운드 작업 최적화**
   - 자동 백업 주기 증가
   - 로그 정리 작업 시간 조정

### Q14: 대용량 로그 파일 처리 시 성능이 느려지는데 해결 방법이 있나요?

**A:** 대용량 로그 최적화 기능:

1. **가상화된 로그 뷰어**
   - 수백만 줄의 로그도 부드럽게 스크롤
   - 메모리 사용량 최소화

2. **로그 인덱싱**
   - 자동 인덱스 생성으로 빠른 검색
   - 시간 범위 기반 빠른 필터링

3. **로그 압축**
   - 오래된 로그 자동 압축
   - 압축된 로그도 검색 가능

4. **로그 분할**
   - 일정 크기 초과 시 자동 분할
   - 로테이션 정책 설정

## 🔧 문제 해결

### Q15: "백엔드에 연결할 수 없습니다" 오류가 계속 발생해요.

**A:** 단계별 해결 방법:

1. **포트 충돌 확인**
   ```bash
   # Windows
   netstat -an | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

2. **방화벽 설정 확인**
   - Windows: Windows Defender 방화벽에서 포트 8000 허용
   - macOS: 시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽
   - Linux: `sudo ufw allow 8000`

3. **Python 환경 확인**
   ```bash
   python --version  # 3.9 이상 필요
   pip list | grep fastapi
   ```

4. **수동 백엔드 시작**
   ```bash
   cd python-backend
   python main.py --debug
   ```

### Q16: 웹훅이 전송되지 않아요.

**A:** 웹훅 문제 해결 체크리스트:

1. **URL 유효성 확인**
   - 브라우저에서 웹훅 URL 직접 접속 테스트
   - Discord/Slack에서 웹훅이 활성화되어 있는지 확인

2. **네트워크 연결 테스트**
   ```bash
   # Discord 연결 테스트
   ping discord.com
   
   # Slack 연결 테스트
   ping hooks.slack.com
   ```

3. **프록시 설정 확인**
   - 회사 네트워크의 경우 프록시 설정 필요
   - 설정 → 고급 → 네트워크 → 프록시 설정

4. **웹훅 테스트 기능 사용**
   - 설정 → 웹훅 → "테스트 전송" 버튼 클릭
   - 오류 메시지 확인

### Q17: 로그가 실시간으로 업데이트되지 않아요.

**A:** 실시간 로그 문제 해결:

1. **실시간 모드 확인**
   - 로그 뷰어에서 "실시간" 토글 버튼이 활성화되어 있는지 확인

2. **WebSocket 연결 상태 확인**
   - 우상단 연결 상태 표시기 확인
   - 🔴 빨간색인 경우 백엔드 재시작

3. **로그 파일 권한 확인**
   - 로그 파일에 읽기 권한이 있는지 확인
   - Windows: 파일 속성 → 보안 탭 확인

4. **로그 서비스 재시작**
   - 서비스 관리에서 로그 관련 서비스 재시작

### Q18: 설정이 저장되지 않아요.

**A:** 설정 저장 문제 해결:

1. **관리자 권한으로 실행**
   - 실행 파일 우클릭 → "관리자 권한으로 실행"

2. **디스크 공간 확인**
   - 충분한 디스크 공간이 있는지 확인

3. **바이러스 백신 예외 처리**
   - WatchHamster 폴더를 바이러스 백신 예외 목록에 추가

4. **설정 파일 권한 확인**
   - 설정 폴더에 쓰기 권한이 있는지 확인

## 🔒 보안 및 개인정보

### Q19: WatchHamster는 어떤 데이터를 수집하나요?

**A:** 개인정보 보호 정책:

**수집하지 않는 데이터:**
- ❌ 개인 식별 정보
- ❌ 브라우징 기록
- ❌ 파일 내용
- ❌ 네트워크 트래픽 내용

**로컬에서만 처리되는 데이터:**
- ✅ 시스템 성능 메트릭 (CPU, 메모리 등)
- ✅ 서비스 상태 정보
- ✅ 로그 파일 (로컬 저장만)
- ✅ 사용자 설정

**외부 전송 데이터 (사용자 설정 시에만):**
- 🔔 웹훅 메시지 (Discord/Slack)
- 📧 이메일 알림 (설정한 경우)

### Q20: 웹훅 URL이 안전하게 저장되나요?

**A:** 보안 저장 방식:

1. **암호화 저장**
   - 모든 민감한 정보는 AES-256으로 암호화
   - 시스템별 고유 키 사용

2. **접근 제한**
   - 설정 파일은 현재 사용자만 접근 가능
   - 관리자 권한 없이는 읽기 불가

3. **메모리 보호**
   - 메모리에서 민감한 정보 자동 삭제
   - 프로세스 덤프에서 정보 보호

4. **로그 마스킹**
   - 로그 파일에 웹훅 URL 기록 시 자동 마스킹
   - 디버그 정보에서도 민감한 정보 제외

### Q21: 원격에서 WatchHamster에 접근할 수 있나요?

**A:** 원격 접근 옵션과 보안 고려사항:

**가능한 방법:**
1. **VPN 연결**
   - 가장 안전한 방법
   - 회사 VPN을 통한 접근

2. **SSH 터널링**
   ```bash
   ssh -L 8000:localhost:8000 user@remote-server
   ```

3. **리버스 프록시** (고급 사용자)
   - Nginx, Apache 등을 통한 HTTPS 접근
   - 인증 및 SSL 인증서 필수

**보안 주의사항:**
- 🔒 **HTTPS 필수**: 평문 HTTP 사용 금지
- 🔑 **인증 설정**: 기본 인증 또는 토큰 기반 인증
- 🛡️ **방화벽 설정**: 필요한 IP만 접근 허용
- 📊 **접근 로그**: 모든 원격 접근 기록

## 💻 개발 및 커스터마이징

### Q22: 플러그인을 개발하고 싶은데 어떻게 시작하나요?

**A:** 플러그인 개발 가이드:

1. **개발 환경 설정**
   ```bash
   # Node.js 18+ 설치
   node --version
   
   # 플러그인 템플릿 다운로드
   git clone https://github.com/watchhamster/plugin-template
   ```

2. **플러그인 구조**
   ```
   my-plugin/
   ├── package.json
   ├── src/
   │   ├── index.ts
   │   ├── components/
   │   └── services/
   └── README.md
   ```

3. **API 사용 예시**
   ```typescript
   import { WatchHamsterAPI } from '@watchhamster/api';
   
   export class MyPlugin {
     async onLoad(api: WatchHamsterAPI) {
       // 플러그인 초기화
       api.registerService('my-service', this.handleService);
     }
   }
   ```

4. **플러그인 설치**
   - 개발 모드: 설정 → 플러그인 → "로컬 플러그인 로드"
   - 배포: 플러그인 스토어에 업로드

### Q23: 커스텀 테마를 만들 수 있나요?

**A:** 테마 커스터마이징 방법:

1. **CSS 변수 사용**
   ```css
   :root {
     --primary-color: #your-color;
     --secondary-color: #your-color;
     --background-color: #your-color;
   }
   ```

2. **테마 파일 생성**
   ```json
   {
     "name": "My Custom Theme",
     "colors": {
       "primary": "#1a365d",
       "secondary": "#2d3748",
       "background": "#f7fafc"
     }
   }
   ```

3. **테마 적용**
   - 설정 → 테마 → "커스텀 테마 가져오기"
   - JSON 파일 선택하여 적용

### Q24: API를 통해 외부 시스템과 연동하고 싶어요.

**A:** API 연동 가이드:

1. **REST API 사용**
   ```javascript
   // 서비스 상태 조회
   const response = await fetch('http://localhost:8000/api/services/');
   const services = await response.json();
   
   // 서비스 제어
   await fetch('http://localhost:8000/api/services/posco_news/start', {
     method: 'POST'
   });
   ```

2. **WebSocket 연결**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     console.log('실시간 업데이트:', data);
   };
   ```

3. **Python 클라이언트 예시**
   ```python
   import requests
   import websocket
   
   # REST API 호출
   response = requests.get('http://localhost:8000/api/metrics/')
   metrics = response.json()
   
   # WebSocket 연결
   def on_message(ws, message):
       print(f"수신: {message}")
   
   ws = websocket.WebSocketApp("ws://localhost:8000/ws",
                               on_message=on_message)
   ws.run_forever()
   ```

### Q25: 소스 코드를 수정하고 싶은데 어떻게 빌드하나요?

**A:** 개발 환경 설정 및 빌드:

1. **소스 코드 클론**
   ```bash
   git clone https://github.com/watchhamster/tauri-gui
   cd watchhamster-tauri-gui
   ```

2. **의존성 설치**
   ```bash
   # Node.js 의존성
   npm install
   
   # Rust 의존성
   cd src-tauri
   cargo build
   cd ..
   
   # Python 의존성
   cd python-backend
   pip install -r requirements.txt
   cd ..
   ```

3. **개발 서버 실행**
   ```bash
   npm run dev
   ```

4. **프로덕션 빌드**
   ```bash
   npm run build:tauri
   ```

5. **테스트 실행**
   ```bash
   # 프론트엔드 테스트
   npm test
   
   # 백엔드 테스트
   cd python-backend
   pytest
   
   # Rust 테스트
   cd src-tauri
   cargo test
   ```

## 📞 추가 지원

### 더 많은 도움이 필요하신가요?

**공식 리소스:**
- 📖 [사용자 가이드](USER_GUIDE.md)
- 🔧 [개발자 문서](DEVELOPMENT.md)
- 🚀 [마이그레이션 가이드](MIGRATION_GUIDE.md)
- 🌐 [API 참조](API_REFERENCE.md)

**커뮤니티 지원:**
- 💬 [GitHub Discussions](https://github.com/watchhamster/discussions)
- 🐛 [버그 리포트](https://github.com/watchhamster/issues)
- 💡 [기능 요청](https://github.com/watchhamster/feature-requests)

**직접 연락:**
- 📧 이메일: support@watchhamster.com
- 💼 기업 지원: enterprise@watchhamster.com

---

이 FAQ는 지속적으로 업데이트됩니다. 새로운 질문이나 개선 사항이 있으시면 언제든지 제안해 주세요!