use crate::{python_bridge, window_manager};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use tauri::{command, AppHandle, api::path};

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub platform: String,
    pub arch: String,
    pub version: String,
    pub hostname: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ExtendedSystemInfo {
    pub platform: String,
    pub arch: String,
    pub version: String,
    pub hostname: String,
    pub current_exe: String,
    pub current_dir: String,
    pub env_vars: HashMap<String, String>,
    pub family: String,
    pub dll_extension: String,
    pub dll_prefix: String,
    pub exe_extension: String,
    pub exe_suffix: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WebhookPayload {
    pub url: String,
    pub message: String,
    pub webhook_type: String, // discord, slack, etc.
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AdvancedWebhookPayload {
    pub url: String,
    pub message: String,
    pub webhook_type: String,
    pub username: Option<String>,
    pub headers: Option<HashMap<String, String>>,
    pub custom_body: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WebhookResponse {
    pub success: bool,
    pub status_code: u16,
    pub response_text: String,
    pub response_time: u64, // milliseconds
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BackendStatus {
    pub running: bool,
    pub port: u16,
    pub uptime: Option<u64>,
    pub last_error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileInfo {
    pub name: String,
    pub path: String,
    pub size: u64,
    pub is_dir: bool,
    pub modified: Option<u64>,
    pub created: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DirectoryListing {
    pub path: String,
    pub files: Vec<FileInfo>,
    pub total_count: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileContent {
    pub path: String,
    pub content: String,
    pub size: u64,
    pub encoding: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WriteFileRequest {
    pub path: String,
    pub content: String,
    pub create_dirs: Option<bool>,
}

/// Python 백엔드 시작
#[command]
pub async fn start_python_backend() -> Result<String, String> {
    match python_bridge::start_backend().await {
        Ok(_) => Ok("Python 백엔드가 성공적으로 시작되었습니다".to_string()),
        Err(e) => Err(format!("Python 백엔드 시작 실패: {}", e)),
    }
}

/// Python 백엔드 중지
#[command]
pub async fn stop_python_backend() -> Result<String, String> {
    match python_bridge::stop_backend().await {
        Ok(_) => Ok("Python 백엔드가 성공적으로 중지되었습니다".to_string()),
        Err(e) => Err(format!("Python 백엔드 중지 실패: {}", e)),
    }
}

/// Python 백엔드 재시작
#[command]
pub async fn restart_python_backend() -> Result<String, String> {
    // 먼저 중지
    if let Err(e) = python_bridge::stop_backend().await {
        log::warn!("백엔드 중지 중 오류 (무시됨): {}", e);
    }
    
    // 잠시 대기
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    
    // 다시 시작
    match python_bridge::start_backend().await {
        Ok(_) => Ok("Python 백엔드가 성공적으로 재시작되었습니다".to_string()),
        Err(e) => Err(format!("Python 백엔드 재시작 실패: {}", e)),
    }
}

/// 시스템 정보 조회
#[command]
pub async fn get_system_info() -> Result<SystemInfo, String> {
    Ok(SystemInfo {
        platform: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        hostname: gethostname::gethostname()
            .to_string_lossy()
            .to_string(),
    })
}

/// 확장된 시스템 정보 조회
#[command]
pub async fn get_extended_system_info() -> Result<ExtendedSystemInfo, String> {
    let current_exe = std::env::current_exe()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|_| "알 수 없음".to_string());
    
    let current_dir = std::env::current_dir()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|_| "알 수 없음".to_string());
    
    let env_vars: HashMap<String, String> = std::env::vars().collect();
    
    Ok(ExtendedSystemInfo {
        platform: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        hostname: gethostname::gethostname()
            .to_string_lossy()
            .to_string(),
        current_exe,
        current_dir,
        env_vars,
        family: std::env::consts::FAMILY.to_string(),
        dll_extension: std::env::consts::DLL_EXTENSION.to_string(),
        dll_prefix: std::env::consts::DLL_PREFIX.to_string(),
        exe_extension: std::env::consts::EXE_EXTENSION.to_string(),
        exe_suffix: std::env::consts::EXE_SUFFIX.to_string(),
    })
}

/// 웹훅 전송
#[command]
pub async fn send_webhook(payload: WebhookPayload) -> Result<String, String> {
    let client = reqwest::Client::new();
    
    let mut webhook_data = HashMap::new();
    
    match payload.webhook_type.as_str() {
        "discord" => {
            webhook_data.insert("content", payload.message);
        }
        "slack" => {
            webhook_data.insert("text", payload.message);
        }
        _ => {
            webhook_data.insert("message", payload.message);
        }
    }
    
    match client
        .post(&payload.url)
        .json(&webhook_data)
        .send()
        .await
    {
        Ok(response) => {
            if response.status().is_success() {
                Ok("웹훅이 성공적으로 전송되었습니다".to_string())
            } else {
                Err(format!("웹훅 전송 실패: HTTP {}", response.status()))
            }
        }
        Err(e) => Err(format!("웹훅 전송 오류: {}", e)),
    }
}

/// 고급 웹훅 전송 (헤더 및 추가 옵션 지원)
#[command]
pub async fn send_advanced_webhook(payload: AdvancedWebhookPayload) -> Result<WebhookResponse, String> {
    let client = reqwest::Client::new();
    
    let mut request = client.post(&payload.url);
    
    // 헤더 추가
    if let Some(headers) = payload.headers {
        for (key, value) in headers {
            request = request.header(&key, &value);
        }
    }
    
    // 바디 설정
    let body = if let Some(custom_body) = payload.custom_body {
        custom_body
    } else {
        match payload.webhook_type.as_str() {
            "discord" => {
                let mut data = HashMap::new();
                data.insert("content".to_string(), payload.message);
                if let Some(username) = payload.username {
                    data.insert("username".to_string(), username);
                }
                serde_json::to_string(&data).map_err(|e| format!("JSON 직렬화 실패: {}", e))?
            }
            "slack" => {
                let mut data = HashMap::new();
                data.insert("text".to_string(), payload.message);
                if let Some(username) = payload.username {
                    data.insert("username".to_string(), username);
                }
                serde_json::to_string(&data).map_err(|e| format!("JSON 직렬화 실패: {}", e))?
            }
            _ => {
                let mut data = HashMap::new();
                data.insert("message".to_string(), payload.message);
                serde_json::to_string(&data).map_err(|e| format!("JSON 직렬화 실패: {}", e))?
            }
        }
    };
    
    // 요청 전송
    let start_time = std::time::Instant::now();
    
    match request
        .header("Content-Type", "application/json")
        .body(body)
        .send()
        .await
    {
        Ok(response) => {
            let status_code = response.status().as_u16();
            let response_time = start_time.elapsed().as_millis() as u64;
            let response_text = response.text().await.unwrap_or_else(|_| "응답 읽기 실패".to_string());
            
            Ok(WebhookResponse {
                success: status_code >= 200 && status_code < 300,
                status_code,
                response_text,
                response_time,
            })
        }
        Err(e) => Err(format!("웹훅 전송 오류: {}", e)),
    }
}

/// 웹훅 URL 유효성 검사
#[command]
pub async fn validate_webhook_url(url: String) -> Result<bool, String> {
    // URL 형식 검사
    if !url.starts_with("http://") && !url.starts_with("https://") {
        return Ok(false);
    }
    
    // 간단한 HEAD 요청으로 URL 접근 가능성 확인
    let client = reqwest::Client::new();
    
    match client.head(&url).send().await {
        Ok(response) => Ok(response.status().is_success() || response.status().as_u16() == 405), // 405는 HEAD 메서드를 지원하지 않는 경우
        Err(_) => Ok(false),
    }
}

/// 백엔드 상태 확인
#[command]
pub async fn get_backend_status() -> Result<BackendStatus, String> {
    let running = python_bridge::is_backend_running().await;
    let process_info = python_bridge::get_process_info();
    
    Ok(BackendStatus {
        running,
        port: 8000,
        uptime: process_info.as_ref().map(|info| info.uptime()),
        last_error: process_info.and_then(|info| {
            match info.status {
                python_bridge::ProcessStatus::Error(ref e) => Some(e.clone()),
                _ => None,
            }
        }),
    })
}

/// 상세한 프로세스 정보 조회
#[command]
pub async fn get_process_info() -> Result<Option<python_bridge::ProcessInfo>, String> {
    Ok(python_bridge::get_process_info())
}

/// 백엔드 강제 종료
#[command]
pub async fn force_kill_backend() -> Result<String, String> {
    match python_bridge::force_kill_backend().await {
        Ok(_) => Ok("Python 백엔드가 강제 종료되었습니다".to_string()),
        Err(e) => Err(format!("강제 종료 실패: {}", e)),
    }
}

/// 프로세스 모니터링 시작
#[command]
pub async fn start_process_monitoring() -> Result<String, String> {
    // 백그라운드에서 모니터링 시작
    tauri::async_runtime::spawn(async {
        if let Err(e) = python_bridge::start_process_monitoring().await {
            log::error!("프로세스 모니터링 오류: {}", e);
        }
    });
    
    Ok("프로세스 모니터링이 시작되었습니다".to_string())
}

/// 창 표시
#[command]
pub async fn show_window(app_handle: AppHandle) -> Result<String, String> {
    window_manager::show_window(&app_handle)?;
    Ok("창이 표시되었습니다".to_string())
}

/// 창 숨기기
#[command]
pub async fn hide_window(app_handle: AppHandle) -> Result<String, String> {
    window_manager::hide_window(&app_handle)?;
    Ok("창이 숨겨졌습니다".to_string())
}

/// 창 토글
#[command]
pub async fn toggle_window(app_handle: AppHandle) -> Result<String, String> {
    window_manager::toggle_window(&app_handle)?;
    Ok("창 상태가 토글되었습니다".to_string())
}

/// 창 상태 정보 조회
#[command]
pub async fn get_window_info(app_handle: AppHandle) -> Result<window_manager::WindowInfo, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.get_window_info()
}

/// 창 크기 설정
#[command]
pub async fn set_window_size(app_handle: AppHandle, width: f64, height: f64) -> Result<String, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.set_window_size(width, height)?;
    Ok(format!("창 크기가 {}x{}로 설정되었습니다", width, height))
}

/// 창 위치 설정
#[command]
pub async fn set_window_position(app_handle: AppHandle, x: f64, y: f64) -> Result<String, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.set_window_position(x, y)?;
    Ok(format!("창 위치가 ({}, {})로 설정되었습니다", x, y))
}

/// 창 중앙 정렬
#[command]
pub async fn center_window(app_handle: AppHandle) -> Result<String, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.center_main_window()?;
    Ok("창이 화면 중앙으로 이동되었습니다".to_string())
}

/// 창 최대화
#[command]
pub async fn maximize_window(app_handle: AppHandle) -> Result<String, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.maximize_main_window()?;
    Ok("창이 최대화되었습니다".to_string())
}

/// 창 최대화 해제
#[command]
pub async fn unmaximize_window(app_handle: AppHandle) -> Result<String, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.unmaximize_main_window()?;
    Ok("창 최대화가 해제되었습니다".to_string())
}

/// 창 최소화
#[command]
pub async fn minimize_window(app_handle: AppHandle) -> Result<String, String> {
    let window_manager_instance = window_manager::WindowManager::new(app_handle);
    window_manager_instance.minimize_main_window()?;
    Ok("창이 최소화되었습니다".to_string())
}

/// 디렉토리 목록 조회
#[command]
pub async fn list_directory(path: String) -> Result<DirectoryListing, String> {
    let dir_path = Path::new(&path);
    
    if !dir_path.exists() {
        return Err(format!("디렉토리가 존재하지 않습니다: {}", path));
    }
    
    if !dir_path.is_dir() {
        return Err(format!("지정된 경로가 디렉토리가 아닙니다: {}", path));
    }
    
    let mut files = Vec::new();
    
    match fs::read_dir(dir_path) {
        Ok(entries) => {
            for entry in entries {
                match entry {
                    Ok(entry) => {
                        let file_path = entry.path();
                        let metadata = entry.metadata().ok();
                        
                        let file_info = FileInfo {
                            name: entry.file_name().to_string_lossy().to_string(),
                            path: file_path.to_string_lossy().to_string(),
                            size: metadata.as_ref().map(|m| m.len()).unwrap_or(0),
                            is_dir: file_path.is_dir(),
                            modified: metadata.as_ref()
                                .and_then(|m| m.modified().ok())
                                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                                .map(|d| d.as_secs()),
                            created: metadata.as_ref()
                                .and_then(|m| m.created().ok())
                                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                                .map(|d| d.as_secs()),
                        };
                        
                        files.push(file_info);
                    }
                    Err(e) => {
                        log::warn!("디렉토리 항목 읽기 실패: {}", e);
                    }
                }
            }
        }
        Err(e) => {
            return Err(format!("디렉토리 읽기 실패: {}", e));
        }
    }
    
    // 파일명으로 정렬 (디렉토리 우선)
    files.sort_by(|a, b| {
        match (a.is_dir, b.is_dir) {
            (true, false) => std::cmp::Ordering::Less,
            (false, true) => std::cmp::Ordering::Greater,
            _ => a.name.to_lowercase().cmp(&b.name.to_lowercase()),
        }
    });
    
    let total_count = files.len();
    
    Ok(DirectoryListing {
        path: path.clone(),
        files,
        total_count,
    })
}

/// 파일 내용 읽기
#[command]
pub async fn read_file(path: String) -> Result<FileContent, String> {
    let file_path = Path::new(&path);
    
    if !file_path.exists() {
        return Err(format!("파일이 존재하지 않습니다: {}", path));
    }
    
    if !file_path.is_file() {
        return Err(format!("지정된 경로가 파일이 아닙니다: {}", path));
    }
    
    match fs::read_to_string(file_path) {
        Ok(content) => {
            let metadata = fs::metadata(file_path).ok();
            let size = metadata.map(|m| m.len()).unwrap_or(0);
            
            Ok(FileContent {
                path: path.clone(),
                content,
                size,
                encoding: "UTF-8".to_string(),
            })
        }
        Err(e) => {
            // UTF-8이 아닌 경우 바이너리로 읽기 시도
            match fs::read(file_path) {
                Ok(bytes) => {
                    let content = format!("바이너리 파일 ({}바이트)", bytes.len());
                    Ok(FileContent {
                        path: path.clone(),
                        content,
                        size: bytes.len() as u64,
                        encoding: "binary".to_string(),
                    })
                }
                Err(read_err) => {
                    Err(format!("파일 읽기 실패: {} (원본 오류: {})", read_err, e))
                }
            }
        }
    }
}

/// 파일 쓰기
#[command]
pub async fn write_file(request: WriteFileRequest) -> Result<String, String> {
    let file_path = Path::new(&request.path);
    
    // 디렉토리 생성 옵션 확인
    if request.create_dirs.unwrap_or(false) {
        if let Some(parent) = file_path.parent() {
            if !parent.exists() {
                fs::create_dir_all(parent)
                    .map_err(|e| format!("디렉토리 생성 실패: {}", e))?;
            }
        }
    }
    
    match fs::write(file_path, &request.content) {
        Ok(_) => {
            let size = request.content.len();
            Ok(format!("파일이 성공적으로 저장되었습니다 ({}바이트)", size))
        }
        Err(e) => Err(format!("파일 쓰기 실패: {}", e)),
    }
}

/// 파일/디렉토리 삭제
#[command]
pub async fn delete_path(path: String) -> Result<String, String> {
    let target_path = Path::new(&path);
    
    if !target_path.exists() {
        return Err(format!("경로가 존재하지 않습니다: {}", path));
    }
    
    if target_path.is_dir() {
        match fs::remove_dir_all(target_path) {
            Ok(_) => Ok(format!("디렉토리가 삭제되었습니다: {}", path)),
            Err(e) => Err(format!("디렉토리 삭제 실패: {}", e)),
        }
    } else {
        match fs::remove_file(target_path) {
            Ok(_) => Ok(format!("파일이 삭제되었습니다: {}", path)),
            Err(e) => Err(format!("파일 삭제 실패: {}", e)),
        }
    }
}

/// 디렉토리 생성
#[command]
pub async fn create_directory(path: String, recursive: Option<bool>) -> Result<String, String> {
    let dir_path = Path::new(&path);
    
    if dir_path.exists() {
        return Err(format!("디렉토리가 이미 존재합니다: {}", path));
    }
    
    let result = if recursive.unwrap_or(false) {
        fs::create_dir_all(dir_path)
    } else {
        fs::create_dir(dir_path)
    };
    
    match result {
        Ok(_) => Ok(format!("디렉토리가 생성되었습니다: {}", path)),
        Err(e) => Err(format!("디렉토리 생성 실패: {}", e)),
    }
}

/// 파일/디렉토리 이동/이름 변경
#[command]
pub async fn move_path(from: String, to: String) -> Result<String, String> {
    let from_path = Path::new(&from);
    let to_path = Path::new(&to);
    
    if !from_path.exists() {
        return Err(format!("원본 경로가 존재하지 않습니다: {}", from));
    }
    
    if to_path.exists() {
        return Err(format!("대상 경로가 이미 존재합니다: {}", to));
    }
    
    match fs::rename(from_path, to_path) {
        Ok(_) => Ok(format!("경로가 이동되었습니다: {} -> {}", from, to)),
        Err(e) => Err(format!("경로 이동 실패: {}", e)),
    }
}

/// 파일 복사
#[command]
pub async fn copy_file(from: String, to: String) -> Result<String, String> {
    let from_path = Path::new(&from);
    let to_path = Path::new(&to);
    
    if !from_path.exists() {
        return Err(format!("원본 파일이 존재하지 않습니다: {}", from));
    }
    
    if !from_path.is_file() {
        return Err(format!("원본이 파일이 아닙니다: {}", from));
    }
    
    if to_path.exists() {
        return Err(format!("대상 파일이 이미 존재합니다: {}", to));
    }
    
    match fs::copy(from_path, to_path) {
        Ok(bytes_copied) => Ok(format!("파일이 복사되었습니다: {} ({}바이트)", to, bytes_copied)),
        Err(e) => Err(format!("파일 복사 실패: {}", e)),
    }
}

/// 경로 존재 여부 확인
#[command]
pub async fn path_exists(path: String) -> Result<bool, String> {
    Ok(Path::new(&path).exists())
}

/// 파일 정보 조회
#[command]
pub async fn get_file_info(path: String) -> Result<FileInfo, String> {
    let file_path = Path::new(&path);
    
    if !file_path.exists() {
        return Err(format!("경로가 존재하지 않습니다: {}", path));
    }
    
    let metadata = fs::metadata(file_path)
        .map_err(|e| format!("메타데이터 읽기 실패: {}", e))?;
    
    let file_name = file_path.file_name()
        .unwrap_or_else(|| std::ffi::OsStr::new(""))
        .to_string_lossy()
        .to_string();
    
    Ok(FileInfo {
        name: file_name,
        path: path.clone(),
        size: metadata.len(),
        is_dir: metadata.is_dir(),
        modified: metadata.modified().ok()
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map(|d| d.as_secs()),
        created: metadata.created().ok()
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map(|d| d.as_secs()),
    })
}

/// 애플리케이션 데이터 디렉토리 경로 조회
#[command]
pub async fn get_app_data_dir(app_handle: AppHandle) -> Result<String, String> {
    match path::app_data_dir(&app_handle.config()) {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("애플리케이션 데이터 디렉토리를 찾을 수 없습니다".to_string()),
    }
}

/// 애플리케이션 설정 디렉토리 경로 조회
#[command]
pub async fn get_app_config_dir(app_handle: AppHandle) -> Result<String, String> {
    match path::app_config_dir(&app_handle.config()) {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("애플리케이션 설정 디렉토리를 찾을 수 없습니다".to_string()),
    }
}

/// 애플리케이션 로그 디렉토리 경로 조회
#[command]
pub async fn get_app_log_dir(app_handle: AppHandle) -> Result<String, String> {
    match path::app_log_dir(&app_handle.config()) {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("애플리케이션 로그 디렉토리를 찾을 수 없습니다".to_string()),
    }
}

/// 현재 작업 디렉토리 조회
#[command]
pub async fn get_current_dir() -> Result<String, String> {
    match std::env::current_dir() {
        Ok(path) => Ok(path.to_string_lossy().to_string()),
        Err(e) => Err(format!("현재 디렉토리 조회 실패: {}", e)),
    }
}

/// 홈 디렉토리 조회
#[command]
pub async fn get_home_dir() -> Result<String, String> {
    match dirs::home_dir() {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("홈 디렉토리를 찾을 수 없습니다".to_string()),
    }
}

// gethostname 크레이트를 위한 extern crate 선언
extern crate gethostname;

// 테스트 모듈
#[cfg(test)]
mod tests;