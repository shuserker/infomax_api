# Tauri 명령어 인터페이스 문서

## 개요

WatchHamster Tauri 애플리케이션은 Rust 백엔드와 React 프론트엔드 간의 통신을 위해 Tauri 명령어 시스템을 사용합니다. 이 문서는 사용 가능한 모든 Tauri 명령어와 그 사용법을 설명합니다.

## 명령어 호출 방법

### JavaScript/TypeScript에서 호출

```typescript
import { invoke } from '@tauri-apps/api/tauri';

// 기본 사용법
const result = await invoke('command_name', { param1: 'value1', param2: 'value2' });

// 오류 처리
try {
    const result = await invoke('command_name', { param: 'value' });
    console.log('성공:', result);
} catch (error) {
    console.error('오류:', error);
}
```

### React Hook에서 사용

```typescript
import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

function useSystemInfo() {
    const [systemInfo, setSystemInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const fetchSystemInfo = async () => {
            try {
                const info = await invoke('get_system_info');
                setSystemInfo(info);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };
        
        fetchSystemInfo();
    }, []);
    
    return { systemInfo, loading, error };
}
```

## Python 백엔드 관리 명령어

### start_python_backend

Python 백엔드 서비스를 시작합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('start_python_backend');
console.log(result); // "Python 백엔드가 성공적으로 시작되었습니다"
```

### stop_python_backend

Python 백엔드 서비스를 중지합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('stop_python_backend');
console.log(result); // "Python 백엔드가 성공적으로 중지되었습니다"
```

### restart_python_backend

Python 백엔드 서비스를 재시작합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('restart_python_backend');
console.log(result); // "Python 백엔드가 성공적으로 재시작되었습니다"
```

### get_backend_status

Python 백엔드의 현재 상태를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<BackendStatus>`

```typescript
interface BackendStatus {
    running: boolean;
    port: number;
    uptime?: number; // 초 단위
    last_error?: string;
}
```

**예시**:
```typescript
const status = await invoke('get_backend_status');
console.log(status);
// {
//     running: true,
//     port: 8000,
//     uptime: 3600,
//     last_error: null
// }
```

### get_process_info

상세한 프로세스 정보를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<ProcessInfo | null>`

**예시**:
```typescript
const processInfo = await invoke('get_process_info');
if (processInfo) {
    console.log('프로세스 ID:', processInfo.pid);
    console.log('업타임:', processInfo.uptime);
}
```

### force_kill_backend

Python 백엔드를 강제로 종료합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('force_kill_backend');
console.log(result); // "Python 백엔드가 강제 종료되었습니다"
```

### start_process_monitoring

백그라운드 프로세스 모니터링을 시작합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('start_process_monitoring');
console.log(result); // "프로세스 모니터링이 시작되었습니다"
```

## 시스템 정보 명령어

### get_system_info

기본 시스템 정보를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<SystemInfo>`

```typescript
interface SystemInfo {
    platform: string;
    arch: string;
    version: string;
    hostname: string;
}
```

**예시**:
```typescript
const systemInfo = await invoke('get_system_info');
console.log(systemInfo);
// {
//     platform: "windows",
//     arch: "x86_64",
//     version: "1.0.0",
//     hostname: "DESKTOP-ABC123"
// }
```

### get_extended_system_info

확장된 시스템 정보를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<ExtendedSystemInfo>`

```typescript
interface ExtendedSystemInfo {
    platform: string;
    arch: string;
    version: string;
    hostname: string;
    current_exe: string;
    current_dir: string;
    env_vars: Record<string, string>;
    family: string;
    dll_extension: string;
    dll_prefix: string;
    exe_extension: string;
    exe_suffix: string;
}
```

**예시**:
```typescript
const extendedInfo = await invoke('get_extended_system_info');
console.log('실행 파일 경로:', extendedInfo.current_exe);
console.log('현재 디렉토리:', extendedInfo.current_dir);
console.log('환경 변수:', extendedInfo.env_vars);
```

## 웹훅 관리 명령어

### send_webhook

기본 웹훅을 전송합니다.

**매개변수**:
```typescript
interface WebhookPayload {
    url: string;
    message: string;
    webhook_type: string; // "discord", "slack", etc.
}
```

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const payload = {
    url: 'https://discord.com/api/webhooks/...',
    message: '테스트 메시지입니다',
    webhook_type: 'discord'
};

const result = await invoke('send_webhook', payload);
console.log(result); // "웹훅이 성공적으로 전송되었습니다"
```

### send_advanced_webhook

고급 옵션을 지원하는 웹훅을 전송합니다.

**매개변수**:
```typescript
interface AdvancedWebhookPayload {
    url: string;
    message: string;
    webhook_type: string;
    username?: string;
    headers?: Record<string, string>;
    custom_body?: string;
}
```

**반환값**: `Promise<WebhookResponse>`

```typescript
interface WebhookResponse {
    success: boolean;
    status_code: number;
    response_text: string;
    response_time: number; // 밀리초
}
```

**예시**:
```typescript
const payload = {
    url: 'https://discord.com/api/webhooks/...',
    message: '고급 웹훅 테스트',
    webhook_type: 'discord',
    username: 'WatchHamster Bot',
    headers: {
        'User-Agent': 'WatchHamster/1.0'
    }
};

const response = await invoke('send_advanced_webhook', payload);
console.log('전송 성공:', response.success);
console.log('응답 시간:', response.response_time, 'ms');
```

### validate_webhook_url

웹훅 URL의 유효성을 검사합니다.

**매개변수**:
- `url: string` - 검사할 웹훅 URL

**반환값**: `Promise<boolean>` - 유효성 여부

**예시**:
```typescript
const isValid = await invoke('validate_webhook_url', { 
    url: 'https://discord.com/api/webhooks/...' 
});

if (isValid) {
    console.log('유효한 웹훅 URL입니다');
} else {
    console.log('유효하지 않은 웹훅 URL입니다');
}
```

## 창 관리 명령어

### show_window

애플리케이션 창을 표시합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('show_window');
console.log(result); // "창이 표시되었습니다"
```

### hide_window

애플리케이션 창을 숨깁니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('hide_window');
console.log(result); // "창이 숨겨졌습니다"
```

### toggle_window

애플리케이션 창의 표시/숨김 상태를 토글합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('toggle_window');
console.log(result); // "창 상태가 토글되었습니다"
```

### get_window_info

창의 현재 상태 정보를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<WindowInfo>`

```typescript
interface WindowInfo {
    visible: boolean;
    focused: boolean;
    maximized: boolean;
    minimized: boolean;
    width: number;
    height: number;
    x: number;
    y: number;
}
```

**예시**:
```typescript
const windowInfo = await invoke('get_window_info');
console.log('창 크기:', windowInfo.width, 'x', windowInfo.height);
console.log('창 위치:', windowInfo.x, ',', windowInfo.y);
console.log('표시 상태:', windowInfo.visible);
```

### set_window_size

창의 크기를 설정합니다.

**매개변수**:
- `width: number` - 창 너비
- `height: number` - 창 높이

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('set_window_size', { width: 1200, height: 800 });
console.log(result); // "창 크기가 1200x800로 설정되었습니다"
```

### set_window_position

창의 위치를 설정합니다.

**매개변수**:
- `x: number` - X 좌표
- `y: number` - Y 좌표

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('set_window_position', { x: 100, y: 100 });
console.log(result); // "창 위치가 (100, 100)로 설정되었습니다"
```

### center_window

창을 화면 중앙으로 이동합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('center_window');
console.log(result); // "창이 화면 중앙으로 이동되었습니다"
```

### maximize_window

창을 최대화합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('maximize_window');
console.log(result); // "창이 최대화되었습니다"
```

### unmaximize_window

창의 최대화를 해제합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('unmaximize_window');
console.log(result); // "창 최대화가 해제되었습니다"
```

### minimize_window

창을 최소화합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('minimize_window');
console.log(result); // "창이 최소화되었습니다"
```

## 파일 시스템 명령어

### list_directory

디렉토리의 내용을 조회합니다.

**매개변수**:
- `path: string` - 조회할 디렉토리 경로

**반환값**: `Promise<DirectoryListing>`

```typescript
interface DirectoryListing {
    path: string;
    files: FileInfo[];
    total_count: number;
}

interface FileInfo {
    name: string;
    path: string;
    size: number;
    is_dir: boolean;
    modified?: number; // Unix 타임스탬프
    created?: number; // Unix 타임스탬프
}
```

**예시**:
```typescript
const listing = await invoke('list_directory', { path: '/home/user/documents' });
console.log('총 파일 수:', listing.total_count);
listing.files.forEach(file => {
    console.log(file.is_dir ? '[DIR]' : '[FILE]', file.name, `(${file.size} bytes)`);
});
```

### read_file

파일의 내용을 읽습니다.

**매개변수**:
- `path: string` - 읽을 파일 경로

**반환값**: `Promise<FileContent>`

```typescript
interface FileContent {
    path: string;
    content: string;
    size: number;
    encoding: string;
}
```

**예시**:
```typescript
const fileContent = await invoke('read_file', { path: '/path/to/file.txt' });
console.log('파일 내용:', fileContent.content);
console.log('파일 크기:', fileContent.size, 'bytes');
console.log('인코딩:', fileContent.encoding);
```

### write_file

파일에 내용을 씁니다.

**매개변수**:
```typescript
interface WriteFileRequest {
    path: string;
    content: string;
    create_dirs?: boolean; // 디렉토리 자동 생성 여부
}
```

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const request = {
    path: '/path/to/new/file.txt',
    content: '파일 내용입니다',
    create_dirs: true
};

const result = await invoke('write_file', request);
console.log(result); // "파일이 성공적으로 저장되었습니다 (15바이트)"
```

### delete_path

파일이나 디렉토리를 삭제합니다.

**매개변수**:
- `path: string` - 삭제할 경로

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('delete_path', { path: '/path/to/file.txt' });
console.log(result); // "파일이 삭제되었습니다: /path/to/file.txt"
```

### create_directory

디렉토리를 생성합니다.

**매개변수**:
- `path: string` - 생성할 디렉토리 경로
- `recursive?: boolean` - 상위 디렉토리도 함께 생성할지 여부

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('create_directory', { 
    path: '/path/to/new/directory',
    recursive: true 
});
console.log(result); // "디렉토리가 생성되었습니다: /path/to/new/directory"
```

### move_path

파일이나 디렉토리를 이동하거나 이름을 변경합니다.

**매개변수**:
- `from: string` - 원본 경로
- `to: string` - 대상 경로

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('move_path', { 
    from: '/path/to/old_name.txt',
    to: '/path/to/new_name.txt'
});
console.log(result); // "경로가 이동되었습니다: /path/to/old_name.txt -> /path/to/new_name.txt"
```

### copy_file

파일을 복사합니다.

**매개변수**:
- `from: string` - 원본 파일 경로
- `to: string` - 대상 파일 경로

**반환값**: `Promise<string>` - 성공 메시지

**예시**:
```typescript
const result = await invoke('copy_file', { 
    from: '/path/to/source.txt',
    to: '/path/to/destination.txt'
});
console.log(result); // "파일이 복사되었습니다: /path/to/destination.txt (1024바이트)"
```

### path_exists

경로의 존재 여부를 확인합니다.

**매개변수**:
- `path: string` - 확인할 경로

**반환값**: `Promise<boolean>` - 존재 여부

**예시**:
```typescript
const exists = await invoke('path_exists', { path: '/path/to/check' });
if (exists) {
    console.log('경로가 존재합니다');
} else {
    console.log('경로가 존재하지 않습니다');
}
```

### get_file_info

파일이나 디렉토리의 정보를 조회합니다.

**매개변수**:
- `path: string` - 조회할 경로

**반환값**: `Promise<FileInfo>`

**예시**:
```typescript
const fileInfo = await invoke('get_file_info', { path: '/path/to/file.txt' });
console.log('파일명:', fileInfo.name);
console.log('크기:', fileInfo.size, 'bytes');
console.log('디렉토리 여부:', fileInfo.is_dir);
console.log('수정 시간:', new Date(fileInfo.modified * 1000));
```

## 경로 관련 명령어

### get_app_data_dir

애플리케이션 데이터 디렉토리 경로를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 디렉토리 경로

**예시**:
```typescript
const dataDir = await invoke('get_app_data_dir');
console.log('데이터 디렉토리:', dataDir);
// Windows: C:\Users\Username\AppData\Roaming\WatchHamster
// macOS: /Users/Username/Library/Application Support/WatchHamster
// Linux: /home/username/.local/share/WatchHamster
```

### get_app_config_dir

애플리케이션 설정 디렉토리 경로를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 디렉토리 경로

**예시**:
```typescript
const configDir = await invoke('get_app_config_dir');
console.log('설정 디렉토리:', configDir);
```

### get_app_log_dir

애플리케이션 로그 디렉토리 경로를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 디렉토리 경로

**예시**:
```typescript
const logDir = await invoke('get_app_log_dir');
console.log('로그 디렉토리:', logDir);
```

### get_current_dir

현재 작업 디렉토리를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 디렉토리 경로

**예시**:
```typescript
const currentDir = await invoke('get_current_dir');
console.log('현재 디렉토리:', currentDir);
```

### get_home_dir

사용자 홈 디렉토리를 조회합니다.

**매개변수**: 없음

**반환값**: `Promise<string>` - 디렉토리 경로

**예시**:
```typescript
const homeDir = await invoke('get_home_dir');
console.log('홈 디렉토리:', homeDir);
```

## 오류 처리

모든 Tauri 명령어는 오류 발생 시 Promise를 reject합니다. 적절한 오류 처리를 위해 try-catch 블록을 사용하세요.

```typescript
try {
    const result = await invoke('command_name', { param: 'value' });
    // 성공 처리
} catch (error) {
    console.error('명령어 실행 오류:', error);
    // 오류 처리
}
```

### 일반적인 오류 유형

1. **파일 시스템 오류**: 파일이나 디렉토리가 존재하지 않음, 권한 부족
2. **네트워크 오류**: 웹훅 전송 실패, 연결 시간 초과
3. **프로세스 오류**: Python 백엔드 시작/중지 실패
4. **시스템 오류**: 시스템 정보 조회 실패, 창 관리 오류

## 사용 예시

### 완전한 서비스 관리 컴포넌트

```typescript
import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface BackendStatus {
    running: boolean;
    port: number;
    uptime?: number;
    last_error?: string;
}

function BackendManager() {
    const [status, setStatus] = useState<BackendStatus | null>(null);
    const [loading, setLoading] = useState(false);
    
    const checkStatus = async () => {
        try {
            const backendStatus = await invoke<BackendStatus>('get_backend_status');
            setStatus(backendStatus);
        } catch (error) {
            console.error('상태 확인 실패:', error);
        }
    };
    
    const startBackend = async () => {
        setLoading(true);
        try {
            const result = await invoke<string>('start_python_backend');
            console.log(result);
            await checkStatus();
        } catch (error) {
            console.error('백엔드 시작 실패:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const stopBackend = async () => {
        setLoading(true);
        try {
            const result = await invoke<string>('stop_python_backend');
            console.log(result);
            await checkStatus();
        } catch (error) {
            console.error('백엔드 중지 실패:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const restartBackend = async () => {
        setLoading(true);
        try {
            const result = await invoke<string>('restart_python_backend');
            console.log(result);
            await checkStatus();
        } catch (error) {
            console.error('백엔드 재시작 실패:', error);
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        checkStatus();
        const interval = setInterval(checkStatus, 5000); // 5초마다 상태 확인
        return () => clearInterval(interval);
    }, []);
    
    return (
        <div>
            <h2>백엔드 상태</h2>
            {status && (
                <div>
                    <p>상태: {status.running ? '실행 중' : '중지됨'}</p>
                    <p>포트: {status.port}</p>
                    {status.uptime && <p>업타임: {status.uptime}초</p>}
                    {status.last_error && <p>마지막 오류: {status.last_error}</p>}
                </div>
            )}
            
            <div>
                <button onClick={startBackend} disabled={loading || status?.running}>
                    시작
                </button>
                <button onClick={stopBackend} disabled={loading || !status?.running}>
                    중지
                </button>
                <button onClick={restartBackend} disabled={loading}>
                    재시작
                </button>
            </div>
        </div>
    );
}

export default BackendManager;
```

### 파일 브라우저 컴포넌트

```typescript
import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface FileInfo {
    name: string;
    path: string;
    size: number;
    is_dir: boolean;
    modified?: number;
}

interface DirectoryListing {
    path: string;
    files: FileInfo[];
    total_count: number;
}

function FileBrowser() {
    const [currentPath, setCurrentPath] = useState<string>('');
    const [listing, setListing] = useState<DirectoryListing | null>(null);
    const [loading, setLoading] = useState(false);
    
    const loadDirectory = async (path: string) => {
        setLoading(true);
        try {
            const result = await invoke<DirectoryListing>('list_directory', { path });
            setListing(result);
            setCurrentPath(path);
        } catch (error) {
            console.error('디렉토리 로드 실패:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const navigateToFile = (file: FileInfo) => {
        if (file.is_dir) {
            loadDirectory(file.path);
        } else {
            // 파일 선택 처리
            console.log('파일 선택됨:', file.path);
        }
    };
    
    useEffect(() => {
        // 홈 디렉토리로 시작
        const loadHome = async () => {
            try {
                const homeDir = await invoke<string>('get_home_dir');
                loadDirectory(homeDir);
            } catch (error) {
                console.error('홈 디렉토리 로드 실패:', error);
            }
        };
        
        loadHome();
    }, []);
    
    return (
        <div>
            <h2>파일 브라우저</h2>
            <p>현재 경로: {currentPath}</p>
            
            {loading && <p>로딩 중...</p>}
            
            {listing && (
                <div>
                    <p>총 {listing.total_count}개 항목</p>
                    <ul>
                        {listing.files.map((file, index) => (
                            <li key={index} onClick={() => navigateToFile(file)}>
                                {file.is_dir ? '📁' : '📄'} {file.name}
                                {!file.is_dir && ` (${file.size} bytes)`}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default FileBrowser;
```

## 성능 고려사항

1. **비동기 처리**: 모든 명령어는 비동기로 실행되므로 적절한 로딩 상태 관리가 필요합니다.
2. **오류 처리**: 네트워크나 파일 시스템 오류에 대비한 적절한 오류 처리를 구현하세요.
3. **상태 관리**: 자주 호출되는 명령어의 결과는 캐싱하여 성능을 개선하세요.
4. **메모리 관리**: 대용량 파일 처리 시 메모리 사용량에 주의하세요.

## 보안 고려사항

1. **파일 시스템 접근**: 사용자 입력을 통한 경로 접근 시 경로 검증을 수행하세요.
2. **웹훅 URL**: 웹훅 URL 유효성 검사를 통해 악성 URL 접근을 방지하세요.
3. **권한 관리**: 파일 시스템 작업 시 적절한 권한 확인을 수행하세요.

이 문서는 WatchHamster Tauri 애플리케이션의 모든 명령어에 대한 완전한 참조 가이드입니다. 추가 질문이나 기능 요청이 있으시면 개발팀에 문의하시기 바랍니다.