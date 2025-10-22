use anyhow::{anyhow, Result};
use log::{error, info, warn};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::time::{sleep, Duration, interval};
use serde::{Deserialize, Serialize};

// Python 백엔드 프로세스와 상태를 전역으로 관리
static PYTHON_PROCESS: Mutex<Option<Child>> = Mutex::new(None);
static PROCESS_INFO: Mutex<Option<ProcessInfo>> = Mutex::new(None);

/// 프로세스 정보 구조체
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub start_time: u64,
    pub restart_count: u32,
    pub last_health_check: u64,
    pub status: ProcessStatus,
}

/// 프로세스 상태 열거형
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProcessStatus {
    Starting,
    Running,
    Stopping,
    Stopped,
    Error(String),
}

impl ProcessInfo {
    pub fn new(pid: u32) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        Self {
            pid,
            start_time: now,
            restart_count: 0,
            last_health_check: now,
            status: ProcessStatus::Starting,
        }
    }
    
    pub fn uptime(&self) -> u64 {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        now - self.start_time
    }
}

/// Python 백엔드 시작
pub async fn start_backend() -> Result<()> {
    info!("Python 백엔드 시작 시도");
    
    // 이미 실행 중인지 확인
    if is_backend_running().await {
        warn!("Python 백엔드가 이미 실행 중입니다");
        return Ok(());
    }
    
    // Python 실행 파일 경로 찾기
    let python_cmd = find_python_executable()?;
    
    // Python 백엔드 스크립트 경로
    let backend_path = get_backend_path()?;
    
    info!("Python 명령어: {}, 백엔드 경로: {}", python_cmd, backend_path);
    
    // Python 프로세스 시작
    let child = Command::new(&python_cmd)
        .arg(&backend_path)
        .current_dir(get_backend_dir()?)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| anyhow!("Python 프로세스 시작 실패: {}", e))?;
    
    // 프로세스 ID 저장
    let pid = child.id();
    info!("Python 백엔드 시작됨 (PID: {})", pid);
    
    // 프로세스 정보 생성
    let process_info = ProcessInfo::new(pid);
    
    // 전역 프로세스 및 정보 저장
    {
        let mut process = PYTHON_PROCESS.lock().unwrap();
        *process = Some(child);
    }
    {
        let mut info = PROCESS_INFO.lock().unwrap();
        *info = Some(process_info);
    }
    
    // 백엔드가 준비될 때까지 대기
    wait_for_backend_ready().await?;
    
    Ok(())
}

/// Python 백엔드 중지
pub async fn stop_backend() -> Result<()> {
    info!("Python 백엔드 중지 시도");
    
    let mut process = PYTHON_PROCESS.lock().unwrap();
    
    if let Some(mut child) = process.take() {
        let pid = child.id();
        info!("Python 백엔드 종료 중 (PID: {})", pid);
        
        // 프로세스 종료 시도
        match child.kill() {
            Ok(_) => {
                info!("Python 백엔드 프로세스 종료 신호 전송");
                // 프로세스가 완전히 종료될 때까지 대기
                match child.wait() {
                    Ok(status) => info!("Python 백엔드 종료됨: {}", status),
                    Err(e) => warn!("프로세스 대기 중 오류: {}", e),
                }
            }
            Err(e) => {
                error!("Python 백엔드 종료 실패: {}", e);
                return Err(anyhow!("프로세스 종료 실패: {}", e));
            }
        }
    } else {
        warn!("중지할 Python 백엔드 프로세스가 없습니다");
    }
    
    // 프로세스 정보 정리
    {
        let mut info = PROCESS_INFO.lock().unwrap();
        if let Some(mut process_info) = info.take() {
            process_info.status = ProcessStatus::Stopped;
            info!("프로세스 정보 정리됨");
        }
    }
    
    Ok(())
}

/// 백엔드 실행 상태 확인
pub async fn is_backend_running() -> bool {
    // 프로세스 상태 확인
    {
        let mut process = PYTHON_PROCESS.lock().unwrap();
        if let Some(child) = process.as_mut() {
            match child.try_wait() {
                Ok(Some(_)) => {
                    // 프로세스가 종료됨
                    *process = None;
                    return false;
                }
                Ok(None) => {
                    // 프로세스가 여전히 실행 중
                }
                Err(_) => {
                    // 오류 발생, 프로세스 제거
                    *process = None;
                    return false;
                }
            }
        } else {
            return false;
        }
    }
    
    // HTTP 요청으로 실제 서비스 상태 확인
    check_backend_health().await
}

/// Python 실행 파일 찾기
fn find_python_executable() -> Result<String> {
    // Windows에서는 python.exe, Unix에서는 python3 시도
    let candidates = if cfg!(windows) {
        vec!["python.exe", "python3.exe", "py.exe"]
    } else {
        vec!["python3", "python"]
    };
    
    for cmd in candidates {
        if Command::new(cmd)
            .arg("--version")
            .output()
            .is_ok()
        {
            return Ok(cmd.to_string());
        }
    }
    
    Err(anyhow!("Python 실행 파일을 찾을 수 없습니다"))
}

/// 백엔드 스크립트 경로 가져오기
fn get_backend_path() -> Result<String> {
    let current_dir = std::env::current_dir()
        .map_err(|e| anyhow!("현재 디렉토리 가져오기 실패: {}", e))?;
    
    let backend_path = current_dir
        .join("python-backend")
        .join("main.py");
    
    if !backend_path.exists() {
        return Err(anyhow!("백엔드 스크립트를 찾을 수 없습니다: {:?}", backend_path));
    }
    
    Ok(backend_path.to_string_lossy().to_string())
}

/// 백엔드 디렉토리 경로 가져오기
fn get_backend_dir() -> Result<String> {
    let current_dir = std::env::current_dir()
        .map_err(|e| anyhow!("현재 디렉토리 가져오기 실패: {}", e))?;
    
    let backend_dir = current_dir.join("python-backend");
    
    if !backend_dir.exists() {
        return Err(anyhow!("백엔드 디렉토리를 찾을 수 없습니다: {:?}", backend_dir));
    }
    
    Ok(backend_dir.to_string_lossy().to_string())
}

/// 백엔드가 준비될 때까지 대기
async fn wait_for_backend_ready() -> Result<()> {
    info!("백엔드 준비 상태 확인 중...");
    
    for i in 1..=30 {
        if check_backend_health().await {
            info!("백엔드가 준비되었습니다 ({}초 후)", i);
            return Ok(());
        }
        
        if i % 5 == 0 {
            info!("백엔드 준비 대기 중... ({}초)", i);
        }
        
        sleep(Duration::from_secs(1)).await;
    }
    
    Err(anyhow!("백엔드 준비 시간 초과 (30초)"))
}

/// 백엔드 헬스 체크
async fn check_backend_health() -> bool {
    match reqwest::get("http://localhost:8000/health").await {
        Ok(response) => {
            let is_healthy = response.status().is_success();
            
            // 헬스 체크 시간 업데이트
            {
                let mut info = PROCESS_INFO.lock().unwrap();
                if let Some(process_info) = info.as_mut() {
                    process_info.last_health_check = SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap()
                        .as_secs();
                    
                    if is_healthy {
                        process_info.status = ProcessStatus::Running;
                    }
                }
            }
            
            is_healthy
        }
        Err(e) => {
            warn!("백엔드 헬스 체크 실패: {}", e);
            
            // 오류 상태 업데이트
            {
                let mut info = PROCESS_INFO.lock().unwrap();
                if let Some(process_info) = info.as_mut() {
                    process_info.status = ProcessStatus::Error(e.to_string());
                }
            }
            
            false
        }
    }
}

/// 프로세스 정보 조회
pub fn get_process_info() -> Option<ProcessInfo> {
    let info = PROCESS_INFO.lock().unwrap();
    info.clone()
}

/// 프로세스 모니터링 시작
pub async fn start_process_monitoring() -> Result<()> {
    info!("프로세스 모니터링 시작");
    
    let mut interval = interval(Duration::from_secs(30)); // 30초마다 체크
    
    loop {
        interval.tick().await;
        
        if let Err(e) = monitor_process_health().await {
            error!("프로세스 모니터링 오류: {}", e);
        }
    }
}

/// 프로세스 헬스 모니터링
async fn monitor_process_health() -> Result<()> {
    let should_restart = {
        let mut process = PYTHON_PROCESS.lock().unwrap();
        
        if let Some(child) = process.as_mut() {
            // 프로세스가 종료되었는지 확인
            match child.try_wait() {
                Ok(Some(status)) => {
                    warn!("Python 백엔드 프로세스가 예상치 못하게 종료됨: {}", status);
                    *process = None;
                    true
                }
                Ok(None) => {
                    // 프로세스가 여전히 실행 중
                    false
                }
                Err(e) => {
                    error!("프로세스 상태 확인 오류: {}", e);
                    *process = None;
                    true
                }
            }
        } else {
            // 프로세스가 없으면 시작 필요
            true
        }
    };
    
    // 헬스 체크 수행 (프로세스가 실행 중인 경우)
    if !should_restart {
        if !check_backend_health().await {
            warn!("백엔드 헬스 체크 실패, 재시작 필요");
            {
                let mut process = PYTHON_PROCESS.lock().unwrap();
                if let Some(child) = process.as_mut() {
                    child.kill().ok();
                }
                *process = None;
            } // 뮤텍스 해제
            
            // 재시작 로직
            info!("자동 복구: Python 백엔드 재시작 시도");
            
            // 재시작 카운트 증가
            {
                let mut info = PROCESS_INFO.lock().unwrap();
                if let Some(process_info) = info.as_mut() {
                    process_info.restart_count += 1;
                    process_info.status = ProcessStatus::Starting;
                    info!("재시작 횟수: {}", process_info.restart_count);
                }
            }
            
            // 재시작 시도
            if let Err(e) = start_backend().await {
                error!("자동 복구 실패: {}", e);
                
                // 오류 상태 업데이트
                {
                    let mut info = PROCESS_INFO.lock().unwrap();
                    if let Some(process_info) = info.as_mut() {
                        process_info.status = ProcessStatus::Error(format!("자동 복구 실패: {}", e));
                    }
                }
            } else {
                info!("자동 복구 성공");
            }
        }
        return Ok(());
    }
    
    if should_restart {
        info!("자동 복구: Python 백엔드 재시작 시도");
        
        // 재시작 카운트 증가
        {
            let mut info = PROCESS_INFO.lock().unwrap();
            if let Some(process_info) = info.as_mut() {
                process_info.restart_count += 1;
                process_info.status = ProcessStatus::Starting;
                info!("재시작 횟수: {}", process_info.restart_count);
            }
        }
        
        // 재시작 시도
        if let Err(e) = start_backend().await {
            error!("자동 복구 실패: {}", e);
            
            // 오류 상태 업데이트
            {
                let mut info = PROCESS_INFO.lock().unwrap();
                if let Some(process_info) = info.as_mut() {
                    process_info.status = ProcessStatus::Error(format!("자동 복구 실패: {}", e));
                }
            }
        } else {
            info!("자동 복구 성공");
        }
    }
    
    Ok(())
}

/// 강제 프로세스 종료 (Windows/Unix 호환)
pub async fn force_kill_backend() -> Result<()> {
    info!("Python 백엔드 강제 종료 시도");
    
    let pid = {
        let info = PROCESS_INFO.lock().unwrap();
        info.as_ref().map(|p| p.pid)
    };
    
    if let Some(pid) = pid {
        #[cfg(windows)]
        {
            let output = Command::new("taskkill")
                .args(&["/F", "/PID", &pid.to_string()])
                .output();
            
            match output {
                Ok(result) => {
                    if result.status.success() {
                        info!("프로세스 {} 강제 종료됨", pid);
                    } else {
                        warn!("프로세스 강제 종료 실패: {}", String::from_utf8_lossy(&result.stderr));
                    }
                }
                Err(e) => error!("taskkill 실행 실패: {}", e),
            }
        }
        
        #[cfg(unix)]
        {
            let output = Command::new("kill")
                .args(&["-9", &pid.to_string()])
                .output();
            
            match output {
                Ok(result) => {
                    if result.status.success() {
                        info!("프로세스 {} 강제 종료됨", pid);
                    } else {
                        warn!("프로세스 강제 종료 실패: {}", String::from_utf8_lossy(&result.stderr));
                    }
                }
                Err(e) => error!("kill 실행 실패: {}", e),
            }
        }
    }
    
    // 프로세스 정보 정리
    {
        let mut process = PYTHON_PROCESS.lock().unwrap();
        *process = None;
    }
    {
        let mut info = PROCESS_INFO.lock().unwrap();
        if let Some(process_info) = info.as_mut() {
            process_info.status = ProcessStatus::Stopped;
        }
    }
    
    Ok(())
}

/// 애플리케이션 종료 시 정리 작업
pub async fn cleanup_on_exit() -> Result<()> {
    info!("애플리케이션 종료 시 정리 작업 시작");
    
    // 백엔드 중지
    if let Err(e) = stop_backend().await {
        warn!("정상 종료 실패, 강제 종료 시도: {}", e);
        force_kill_backend().await?;
    }
    
    // 잠시 대기하여 프로세스가 완전히 종료되도록 함
    sleep(Duration::from_secs(2)).await;
    
    info!("정리 작업 완료");
    Ok(())
}

// 테스트 모듈
#[cfg(test)]
mod tests;