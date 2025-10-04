# WatchHamster Tauri 기여 가이드

## 📋 목차

1. [기여 방법](#기여-방법)
2. [개발 환경 설정](#개발-환경-설정)
3. [코딩 컨벤션](#코딩-컨벤션)
4. [커밋 가이드라인](#커밋-가이드라인)
5. [Pull Request 프로세스](#pull-request-프로세스)
6. [이슈 리포팅](#이슈-리포팅)
7. [코드 리뷰 가이드](#코드-리뷰-가이드)
8. [릴리스 프로세스](#릴리스-프로세스)

## 🤝 기여 방법

WatchHamster Tauri 프로젝트에 기여해 주셔서 감사합니다! 다음과 같은 방법으로 기여할 수 있습니다:

### 기여 유형

- 🐛 **버그 수정**: 발견된 버그를 수정
- ✨ **새 기능**: 새로운 기능 추가
- 📚 **문서화**: 문서 개선 및 추가
- 🎨 **UI/UX 개선**: 사용자 인터페이스 개선
- ⚡ **성능 최적화**: 성능 향상
- 🧪 **테스트**: 테스트 커버리지 향상
- 🔧 **리팩토링**: 코드 구조 개선

### 기여 전 확인사항

1. **이슈 확인**: 기존 이슈가 있는지 확인
2. **중복 작업 방지**: 다른 기여자와 중복되지 않는지 확인
3. **논의**: 큰 변경사항은 먼저 이슈에서 논의
4. **라이선스 동의**: 기여한 코드는 프로젝트 라이선스를 따름

## 🛠️ 개발 환경 설정

### 1. 저장소 포크 및 클론

```bash
# 1. GitHub에서 저장소 포크
# 2. 포크한 저장소 클론
git clone https://github.com/YOUR_USERNAME/watchhamster-tauri.git
cd watchhamster-tauri

# 3. 원본 저장소를 upstream으로 추가
git remote add upstream https://github.com/original/watchhamster-tauri.git
```

### 2. 개발 환경 구성

```bash
# Node.js 의존성 설치
npm install

# Python 가상환경 생성 및 활성화
cd python-backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Python 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

cd ..
```

### 3. 개발 도구 설정

#### VS Code 설정 (권장)

```json
// .vscode/settings.json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "python.defaultInterpreterPath": "./python-backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "rust-analyzer.checkOnSave.command": "clippy"
}
```

#### 권장 VS Code 확장

```json
// .vscode/extensions.json
{
  "recommendations": [
    "rust-lang.rust-analyzer",
    "tauri-apps.tauri-vscode",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-python.python",
    "ms-python.pylint"
  ]
}
```

### 4. 개발 서버 실행

```bash
# 전체 개발 환경 실행
npm run dev

# 개별 실행
npm run dev:frontend  # React 개발 서버
npm run dev:backend   # Python FastAPI 서버
npm run dev:tauri     # Tauri 개발 모드
```

## 📝 코딩 컨벤션

### TypeScript/React 컨벤션

#### 파일 및 폴더 명명

```
# 컴포넌트 파일
PascalCase: ServiceCard.tsx, MetricsGrid.tsx

# 훅 파일
camelCase with 'use' prefix: useSystemMetrics.ts, useWebSocket.ts

# 유틸리티 파일
camelCase: formatters.ts, validators.ts

# 상수 파일
camelCase: constants.ts, apiEndpoints.ts

# 폴더명
kebab-case: components/service-management/
```

#### 컴포넌트 작성 규칙

```typescript
// ✅ 좋은 예시
import React, { useState, useCallback, useMemo } from 'react';
import { Box, Button, Text } from '@chakra-ui/react';
import { Service } from '@/types/services';

interface ServiceCardProps {
  service: Service;
  onStart: (serviceId: string) => void;
  onStop: (serviceId: string) => void;
  className?: string;
}

/**
 * 서비스 정보를 표시하고 제어할 수 있는 카드 컴포넌트
 */
const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  onStart,
  onStop,
  className
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleStart = useCallback(async () => {
    setIsLoading(true);
    try {
      await onStart(service.id);
    } finally {
      setIsLoading(false);
    }
  }, [service.id, onStart]);

  const statusColor = useMemo(() => {
    switch (service.status) {
      case 'running': return 'green.500';
      case 'stopped': return 'red.500';
      case 'error': return 'orange.500';
      default: return 'gray.500';
    }
  }, [service.status]);

  return (
    <Box
      className={className}
      p={4}
      borderWidth="1px"
      borderRadius="md"
      shadow="sm"
    >
      <Text fontSize="lg" fontWeight="bold">
        {service.name}
      </Text>
      <Text fontSize="sm" color={statusColor}>
        {service.status}
      </Text>
      <Button
        size="sm"
        colorScheme="blue"
        isLoading={isLoading}
        onClick={handleStart}
        disabled={service.status === 'running'}
      >
        시작
      </Button>
    </Box>
  );
};

export default ServiceCard;
```

#### 타입 정의 규칙

```typescript
// types/services.ts

// 기본 타입
export type ServiceStatus = 'running' | 'stopped' | 'starting' | 'stopping' | 'error';

// 인터페이스
export interface Service {
  id: string;
  name: string;
  description: string;
  status: ServiceStatus;
  uptime?: number;
  lastError?: string;
  config: ServiceConfig;
}

// 제네릭 타입
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  timestamp: string;
}

// 유니온 타입
export type WebhookType = 'discord' | 'slack' | 'custom';

// 함수 타입
export type ServiceActionHandler = (serviceId: string) => Promise<void>;
```

### Python 컨벤션

#### 파일 및 클래스 명명

```python
# 파일명: snake_case
service_manager.py
webhook_system.py

# 클래스명: PascalCase
class ServiceManager:
    pass

class WebhookSystem:
    pass

# 함수명: snake_case
def get_system_metrics():
    pass

def send_webhook_message():
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
```

#### 클래스 작성 규칙

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ServiceConfig(BaseModel):
    """서비스 설정 모델"""
    name: str = Field(..., description="서비스 이름")
    enabled: bool = Field(default=True, description="서비스 활성화 여부")
    check_interval: int = Field(default=60, ge=1, le=3600, description="체크 간격(초)")
    retry_count: int = Field(default=3, ge=0, le=10, description="재시도 횟수")

class Service(ABC):
    """서비스 추상 기본 클래스"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self._status = "stopped"
        self._last_check = None
        self._error_count = 0
    
    @property
    def status(self) -> str:
        """현재 서비스 상태 반환"""
        return self._status
    
    @abstractmethod
    async def start(self) -> bool:
        """서비스 시작"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """서비스 중지"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """서비스 상태 확인"""
        pass
    
    async def restart(self) -> bool:
        """서비스 재시작"""
        await self.stop()
        return await self.start()
    
    def _update_status(self, status: str, error: Optional[str] = None) -> None:
        """내부 상태 업데이트"""
        self._status = status
        self._last_check = datetime.now()
        if error:
            self._error_count += 1
        else:
            self._error_count = 0

class PoscoNewsService(Service):
    """POSCO 뉴스 모니터링 서비스"""
    
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self._news_url = "https://posco.com/news"
        self._last_news_id = None
    
    async def start(self) -> bool:
        """뉴스 모니터링 시작"""
        try:
            # 초기 뉴스 데이터 로드
            await self._load_initial_news()
            self._update_status("running")
            return True
        except Exception as e:
            self._update_status("error", str(e))
            return False
    
    async def stop(self) -> bool:
        """뉴스 모니터링 중지"""
        self._update_status("stopped")
        return True
    
    async def health_check(self) -> bool:
        """뉴스 서비스 상태 확인"""
        try:
            # 뉴스 사이트 접근 가능성 확인
            response = await self._check_news_site()
            return response.status_code == 200
        except Exception:
            return False
    
    async def _load_initial_news(self) -> None:
        """초기 뉴스 데이터 로드"""
        # 구현 로직
        pass
    
    async def _check_news_site(self):
        """뉴스 사이트 접근 확인"""
        # 구현 로직
        pass
```

#### API 엔드포인트 작성 규칙

```python
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List
import logging

router = APIRouter(prefix="/api/services", tags=["services"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ServiceResponse])
async def get_services(
    service_manager: ServiceManager = Depends(get_service_manager)
) -> List[ServiceResponse]:
    """
    모든 서비스 목록 조회
    
    Returns:
        List[ServiceResponse]: 서비스 목록
    
    Raises:
        HTTPException: 서비스 조회 실패 시
    """
    try:
        services = await service_manager.get_all_services()
        return [ServiceResponse.from_service(service) for service in services]
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서비스 목록을 조회할 수 없습니다"
        )

@router.post("/{service_id}/start")
async def start_service(
    service_id: str,
    service_manager: ServiceManager = Depends(get_service_manager)
) -> JSONResponse:
    """
    특정 서비스 시작
    
    Args:
        service_id: 시작할 서비스 ID
        
    Returns:
        JSONResponse: 시작 결과
        
    Raises:
        HTTPException: 서비스를 찾을 수 없거나 시작 실패 시
    """
    service = await service_manager.get_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"서비스를 찾을 수 없습니다: {service_id}"
        )
    
    try:
        success = await service.start()
        if success:
            return JSONResponse(
                content={"message": f"서비스 '{service_id}'가 시작되었습니다"},
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"서비스 '{service_id}' 시작에 실패했습니다"
            )
    except Exception as e:
        logger.error(f"서비스 시작 오류 [{service_id}]: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서비스 시작 중 오류가 발생했습니다: {str(e)}"
        )
```

### Rust 컨벤션

#### 파일 및 구조체 명명

```rust
// 파일명: snake_case
python_bridge.rs
window_manager.rs

// 구조체: PascalCase
struct ServiceManager {
    services: HashMap<String, Service>,
}

// 함수명: snake_case
fn start_python_backend() -> Result<(), String> {
    // 구현
}

// 상수: SCREAMING_SNAKE_CASE
const MAX_RETRY_COUNT: u32 = 3;
const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);
```

#### Tauri 명령어 작성 규칙

```rust
use serde::{Deserialize, Serialize};
use tauri::command;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceInfo {
    pub id: String,
    pub name: String,
    pub status: String,
    pub uptime: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceActionRequest {
    pub service_id: String,
    pub action: String,
    pub options: Option<HashMap<String, String>>,
}

/// 서비스 목록 조회
#[command]
pub async fn get_services() -> Result<Vec<ServiceInfo>, String> {
    match get_all_services().await {
        Ok(services) => {
            let service_infos: Vec<ServiceInfo> = services
                .into_iter()
                .map(|service| ServiceInfo {
                    id: service.id,
                    name: service.name,
                    status: service.status,
                    uptime: service.uptime,
                })
                .collect();
            Ok(service_infos)
        }
        Err(e) => {
            log::error!("서비스 목록 조회 실패: {}", e);
            Err(format!("서비스 목록을 조회할 수 없습니다: {}", e))
        }
    }
}

/// 서비스 제어 (시작/중지/재시작)
#[command]
pub async fn control_service(request: ServiceActionRequest) -> Result<String, String> {
    let ServiceActionRequest { service_id, action, options } = request;
    
    // 입력 검증
    if service_id.is_empty() {
        return Err("서비스 ID가 필요합니다".to_string());
    }
    
    match action.as_str() {
        "start" => {
            match start_service(&service_id, options).await {
                Ok(_) => Ok(format!("서비스 '{}'가 시작되었습니다", service_id)),
                Err(e) => {
                    log::error!("서비스 시작 실패 [{}]: {}", service_id, e);
                    Err(format!("서비스 시작 실패: {}", e))
                }
            }
        }
        "stop" => {
            match stop_service(&service_id, options).await {
                Ok(_) => Ok(format!("서비스 '{}'가 중지되었습니다", service_id)),
                Err(e) => {
                    log::error!("서비스 중지 실패 [{}]: {}", service_id, e);
                    Err(format!("서비스 중지 실패: {}", e))
                }
            }
        }
        "restart" => {
            match restart_service(&service_id, options).await {
                Ok(_) => Ok(format!("서비스 '{}'가 재시작되었습니다", service_id)),
                Err(e) => {
                    log::error!("서비스 재시작 실패 [{}]: {}", service_id, e);
                    Err(format!("서비스 재시작 실패: {}", e))
                }
            }
        }
        _ => Err(format!("지원하지 않는 액션입니다: {}", action)),
    }
}

// 비동기 헬퍼 함수들
async fn get_all_services() -> Result<Vec<Service>, Box<dyn std::error::Error>> {
    // 구현
    todo!()
}

async fn start_service(
    service_id: &str, 
    _options: Option<HashMap<String, String>>
) -> Result<(), Box<dyn std::error::Error>> {
    // 구현
    todo!()
}

async fn stop_service(
    service_id: &str, 
    _options: Option<HashMap<String, String>>
) -> Result<(), Box<dyn std::error::Error>> {
    // 구현
    todo!()
}

async fn restart_service(
    service_id: &str, 
    options: Option<HashMap<String, String>>
) -> Result<(), Box<dyn std::error::Error>> {
    stop_service(service_id, options.clone()).await?;
    
    // 잠시 대기
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    
    start_service(service_id, options).await
}
```

## 📝 커밋 가이드라인

### 커밋 메시지 형식

```
<타입>(<범위>): <제목>

<본문>

<푸터>
```

#### 타입 (Type)

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅, 세미콜론 누락 등 (기능 변경 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가 또는 수정
- `chore`: 빌드 프로세스 또는 보조 도구 변경

#### 범위 (Scope)

- `frontend`: React 프론트엔드
- `backend`: Python FastAPI 백엔드
- `tauri`: Rust Tauri 백엔드
- `docs`: 문서
- `config`: 설정 파일
- `deps`: 의존성

#### 예시

```bash
# 좋은 커밋 메시지
feat(frontend): 실시간 로그 스트리밍 기능 추가

WebSocket을 통한 실시간 로그 스트리밍 기능을 구현했습니다.
- LogViewer 컴포넌트에 실시간 모드 추가
- useWebSocket 훅으로 WebSocket 연결 관리
- 자동 스크롤 및 필터링 기능 포함

Closes #123

fix(backend): 웹훅 전송 시 타임아웃 오류 수정

웹훅 전송 시 30초 타임아웃으로 인한 실패 문제를 해결했습니다.
타임아웃을 60초로 증가하고 재시도 로직을 추가했습니다.

Fixes #456

docs(api): WebSocket API 문서 업데이트

WebSocket 메시지 포맷과 이벤트 타입에 대한 상세한 설명을 추가했습니다.
```

### 브랜치 전략

```bash
# 메인 브랜치
main                    # 프로덕션 준비 코드
develop                 # 개발 통합 브랜치

# 기능 브랜치
feature/실시간-로그-뷰어    # 새 기능 개발
feature/webhook-system  # 영어도 가능

# 버그 수정 브랜치
fix/memory-leak        # 버그 수정
hotfix/critical-bug    # 긴급 수정

# 릴리스 브랜치
release/v1.2.0         # 릴리스 준비
```

## 🔄 Pull Request 프로세스

### 1. PR 생성 전 체크리스트

- [ ] 최신 `develop` 브랜치와 동기화
- [ ] 모든 테스트 통과
- [ ] 린팅 및 포맷팅 적용
- [ ] 관련 문서 업데이트
- [ ] 커밋 메시지 가이드라인 준수

### 2. PR 템플릿

```markdown
## 변경사항 요약
<!-- 이 PR에서 변경된 내용을 간략히 설명해주세요 -->

## 변경 타입
- [ ] 🐛 버그 수정
- [ ] ✨ 새 기능
- [ ] 📚 문서 업데이트
- [ ] 🎨 UI/UX 개선
- [ ] ⚡ 성능 개선
- [ ] 🧪 테스트 추가
- [ ] 🔧 리팩토링

## 관련 이슈
<!-- 관련된 이슈 번호를 적어주세요 -->
Closes #이슈번호

## 테스트 방법
<!-- 이 변경사항을 테스트하는 방법을 설명해주세요 -->
1. 
2. 
3. 

## 스크린샷 (UI 변경 시)
<!-- UI 변경이 있는 경우 스크린샷을 첨부해주세요 -->

## 체크리스트
- [ ] 코드가 프로젝트의 코딩 스타일을 따릅니다
- [ ] 자체 코드 리뷰를 수행했습니다
- [ ] 변경사항에 대한 테스트를 작성했습니다
- [ ] 모든 테스트가 통과합니다
- [ ] 관련 문서를 업데이트했습니다
```

### 3. PR 리뷰 프로세스

1. **자동 검사**: CI/CD 파이프라인 통과 확인
2. **코드 리뷰**: 최소 1명의 승인 필요
3. **테스트**: 기능 테스트 및 회귀 테스트
4. **문서 확인**: 관련 문서 업데이트 여부
5. **병합**: Squash and merge 사용

## 🐛 이슈 리포팅

### 버그 리포트 템플릿

```markdown
## 버그 설명
<!-- 발생한 버그에 대해 명확하고 간결하게 설명해주세요 -->

## 재현 단계
1. 
2. 
3. 

## 예상 동작
<!-- 어떤 동작을 예상했는지 설명해주세요 -->

## 실제 동작
<!-- 실제로 어떤 일이 일어났는지 설명해주세요 -->

## 환경 정보
- OS: [예: Windows 11, macOS 13.0, Ubuntu 22.04]
- WatchHamster 버전: [예: v1.2.0]
- Node.js 버전: [예: 18.17.0]
- Python 버전: [예: 3.11.0]

## 추가 정보
<!-- 스크린샷, 로그, 기타 관련 정보를 첨부해주세요 -->
```

### 기능 요청 템플릿

```markdown
## 기능 요청 요약
<!-- 요청하는 기능에 대해 간략히 설명해주세요 -->

## 문제 상황
<!-- 현재 어떤 문제나 불편함이 있는지 설명해주세요 -->

## 제안하는 해결책
<!-- 어떤 기능이나 변경사항을 원하는지 설명해주세요 -->

## 대안
<!-- 고려해본 다른 해결책이 있다면 설명해주세요 -->

## 추가 컨텍스트
<!-- 기타 관련 정보나 스크린샷을 첨부해주세요 -->
```

## 👀 코드 리뷰 가이드

### 리뷰어 가이드라인

#### 확인 사항

1. **기능성**: 코드가 의도한 대로 작동하는가?
2. **가독성**: 코드를 이해하기 쉬운가?
3. **성능**: 성능에 부정적인 영향은 없는가?
4. **보안**: 보안 취약점은 없는가?
5. **테스트**: 적절한 테스트가 포함되어 있는가?
6. **문서**: 필요한 문서가 업데이트되었는가?

#### 리뷰 코멘트 예시

```markdown
# 👍 좋은 리뷰 코멘트
- "이 함수의 복잡도가 높아 보입니다. 더 작은 함수로 분리하는 것은 어떨까요?"
- "메모리 누수 가능성이 있어 보입니다. useEffect의 cleanup 함수를 추가해주세요."
- "이 로직이 명확하지 않습니다. 주석을 추가하거나 변수명을 더 명확하게 해주세요."

# ❌ 피해야 할 리뷰 코멘트
- "이 코드는 잘못되었습니다." (구체적인 이유 없음)
- "다시 작성하세요." (건설적인 제안 없음)
- "이건 별로네요." (감정적인 표현)
```

### 작성자 가이드라인

#### PR 작성 시

1. **자체 리뷰**: PR 생성 전 자신의 코드를 먼저 리뷰
2. **명확한 설명**: 변경사항과 이유를 명확히 설명
3. **작은 단위**: 가능한 한 작은 단위로 PR 분리
4. **테스트 포함**: 변경사항에 대한 테스트 포함

#### 피드백 대응

1. **열린 마음**: 건설적인 피드백을 환영
2. **빠른 응답**: 리뷰 코멘트에 빠르게 응답
3. **설명**: 변경사항에 대한 이유 설명
4. **감사 표현**: 리뷰어에게 감사 표현

## 🚀 릴리스 프로세스

### 버전 관리

WatchHamster는 [Semantic Versioning](https://semver.org/)을 따릅니다:

- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환되는 기능 추가
- **PATCH**: 하위 호환되는 버그 수정

### 릴리스 단계

1. **릴리스 브랜치 생성**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.3.0
   ```

2. **버전 업데이트**
   ```bash
   # package.json 버전 업데이트
   npm version 1.3.0
   
   # Cargo.toml 버전 업데이트
   # pyproject.toml 버전 업데이트
   ```

3. **CHANGELOG 업데이트**
   ```markdown
   # Changelog
   
   ## [1.3.0] - 2024-01-15
   
   ### Added
   - 실시간 로그 스트리밍 기능
   - 새로운 테마 옵션
   
   ### Changed
   - 성능 최적화
   - UI 개선
   
   ### Fixed
   - 메모리 누수 문제 해결
   - 웹훅 전송 오류 수정
   ```

4. **테스트 및 검증**
   ```bash
   npm run test
   npm run build:tauri
   npm run e2e
   ```

5. **릴리스 PR 생성**
   - `release/v1.3.0` → `main` PR 생성
   - 모든 테스트 통과 확인
   - 리뷰 및 승인

6. **태그 생성 및 배포**
   ```bash
   git tag v1.3.0
   git push origin v1.3.0
   ```

7. **develop 브랜치 동기화**
   ```bash
   git checkout develop
   git merge main
   git push origin develop
   ```

### 핫픽스 프로세스

긴급한 버그 수정이 필요한 경우:

1. **핫픽스 브랜치 생성**
   ```bash
   git checkout main
   git checkout -b hotfix/v1.2.1
   ```

2. **버그 수정 및 테스트**

3. **버전 업데이트** (PATCH 버전)

4. **main과 develop에 병합**

## 📞 도움 요청

### 질문하기 전에

1. **문서 확인**: 관련 문서를 먼저 확인
2. **이슈 검색**: 기존 이슈에서 유사한 문제 검색
3. **FAQ 확인**: 자주 묻는 질문 섹션 확인

### 질문 방법

- **GitHub Discussions**: 일반적인 질문
- **GitHub Issues**: 버그 리포트 또는 기능 요청
- **이메일**: 보안 관련 문제

### 커뮤니티 가이드라인

1. **존중**: 모든 기여자를 존중
2. **건설적**: 건설적인 피드백 제공
3. **도움**: 다른 기여자 도움
4. **학습**: 지속적인 학습과 개선

---

WatchHamster Tauri 프로젝트에 기여해 주셔서 감사합니다! 함께 더 나은 소프트웨어를 만들어 갑시다. 🚀