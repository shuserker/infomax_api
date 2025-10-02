#[cfg(test)]
mod tests {
    use crate::python_bridge::*;
    use std::time::{Duration, SystemTime, UNIX_EPOCH};
    use tokio::time::sleep;

    /// ProcessInfo 구조체 테스트
    #[test]
    fn test_process_info_creation() {
        let pid = 12345;
        let process_info = ProcessInfo::new(pid);
        
        assert_eq!(process_info.pid, pid);
        assert_eq!(process_info.restart_count, 0);
        assert!(matches!(process_info.status, ProcessStatus::Starting));
        
        // 시간 관련 필드들이 합리적인 값인지 확인
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        assert!(process_info.start_time <= now);
        assert!(process_info.last_health_check <= now);
        
        // uptime이 0 이상인지 확인
        assert!(process_info.uptime() >= 0);
    }

    /// ProcessStatus 열거형 테스트
    #[test]
    fn test_process_status_variants() {
        let statuses = vec![
            ProcessStatus::Starting,
            ProcessStatus::Running,
            ProcessStatus::Stopping,
            ProcessStatus::Stopped,
            ProcessStatus::Error("Test error".to_string()),
        ];
        
        for status in statuses {
            // 각 상태가 올바르게 직렬화/역직렬화되는지 확인
            let serialized = serde_json::to_string(&status).unwrap();
            let deserialized: ProcessStatus = serde_json::from_str(&serialized).unwrap();
            
            match (&status, &deserialized) {
                (ProcessStatus::Starting, ProcessStatus::Starting) => {},
                (ProcessStatus::Running, ProcessStatus::Running) => {},
                (ProcessStatus::Stopping, ProcessStatus::Stopping) => {},
                (ProcessStatus::Stopped, ProcessStatus::Stopped) => {},
                (ProcessStatus::Error(e1), ProcessStatus::Error(e2)) => assert_eq!(e1, e2),
                _ => panic!("Status mismatch: {:?} != {:?}", status, deserialized),
            }
        }
    }

    /// Python 실행 파일 찾기 테스트
    #[test]
    fn test_find_python_executable() {
        let result = find_python_executable();
        
        // 시스템에 Python이 설치되어 있지 않을 수도 있으므로
        // 결과가 Ok이면 유효한 명령어인지 확인하고,
        // Err이면 적절한 오류 메시지인지 확인
        match result {
            Ok(python_cmd) => {
                assert!(!python_cmd.is_empty());
                // 일반적인 Python 명령어 중 하나여야 함
                assert!(["python", "python3", "python.exe", "python3.exe", "py.exe"]
                    .contains(&python_cmd.as_str()));
            }
            Err(e) => {
                assert!(e.to_string().contains("Python 실행 파일을 찾을 수 없습니다"));
            }
        }
    }

    /// 백엔드 경로 관련 함수 테스트
    #[test]
    fn test_backend_path_functions() {
        // get_backend_path 테스트
        let backend_path_result = get_backend_path();
        match backend_path_result {
            Ok(path) => {
                assert!(path.ends_with("main.py"));
                assert!(path.contains("python-backend"));
            }
            Err(e) => {
                // 백엔드 스크립트가 없을 수 있으므로 적절한 오류 메시지인지 확인
                assert!(e.to_string().contains("백엔드 스크립트를 찾을 수 없습니다"));
            }
        }
        
        // get_backend_dir 테스트
        let backend_dir_result = get_backend_dir();
        match backend_dir_result {
            Ok(dir) => {
                assert!(dir.ends_with("python-backend"));
            }
            Err(e) => {
                // 백엔드 디렉토리가 없을 수 있으므로 적절한 오류 메시지인지 확인
                assert!(e.to_string().contains("백엔드 디렉토리를 찾을 수 없습니다"));
            }
        }
    }

    /// 프로세스 정보 조회 테스트
    #[test]
    fn test_get_process_info() {
        // 초기 상태에서는 프로세스 정보가 없어야 함
        let initial_info = get_process_info();
        assert!(initial_info.is_none());
        
        // 프로세스 정보를 수동으로 설정하고 테스트
        {
            let mut info = PROCESS_INFO.lock().unwrap();
            *info = Some(ProcessInfo::new(12345));
        }
        
        let info = get_process_info();
        assert!(info.is_some());
        
        let process_info = info.unwrap();
        assert_eq!(process_info.pid, 12345);
        assert_eq!(process_info.restart_count, 0);
        
        // 정리
        {
            let mut info = PROCESS_INFO.lock().unwrap();
            *info = None;
        }
    }

    /// 백엔드 실행 상태 확인 테스트 (모킹 없이)
    #[tokio::test]
    async fn test_is_backend_running_no_process() {
        // 프로세스가 없는 상태에서 테스트
        {
            let mut process = PYTHON_PROCESS.lock().unwrap();
            *process = None;
        }
        {
            let mut info = PROCESS_INFO.lock().unwrap();
            *info = None;
        }
        
        let is_running = is_backend_running().await;
        assert!(!is_running);
    }

    /// 헬스 체크 함수 테스트 (실제 서버 없이)
    #[tokio::test]
    async fn test_check_backend_health_no_server() {
        // 실제 서버가 실행되지 않은 상태에서 헬스 체크
        let is_healthy = check_backend_health().await;
        // 서버가 없으므로 false여야 함
        assert!(!is_healthy);
    }

    /// ProcessInfo uptime 계산 테스트
    #[tokio::test]
    async fn test_process_info_uptime() {
        let process_info = ProcessInfo::new(12345);
        let initial_uptime = process_info.uptime();
        
        // 잠시 대기
        sleep(Duration::from_millis(100)).await;
        
        let later_uptime = process_info.uptime();
        
        // uptime이 증가했는지 확인
        assert!(later_uptime >= initial_uptime);
    }

    /// 프로세스 상태 업데이트 테스트
    #[test]
    fn test_process_status_updates() {
        let mut process_info = ProcessInfo::new(12345);
        
        // 초기 상태는 Starting
        assert!(matches!(process_info.status, ProcessStatus::Starting));
        
        // 상태 변경 테스트
        process_info.status = ProcessStatus::Running;
        assert!(matches!(process_info.status, ProcessStatus::Running));
        
        process_info.status = ProcessStatus::Error("Test error".to_string());
        if let ProcessStatus::Error(ref msg) = process_info.status {
            assert_eq!(msg, "Test error");
        } else {
            panic!("Expected Error status");
        }
        
        process_info.status = ProcessStatus::Stopped;
        assert!(matches!(process_info.status, ProcessStatus::Stopped));
    }

    /// 재시작 카운트 테스트
    #[test]
    fn test_restart_count() {
        let mut process_info = ProcessInfo::new(12345);
        
        assert_eq!(process_info.restart_count, 0);
        
        // 재시작 카운트 증가
        process_info.restart_count += 1;
        assert_eq!(process_info.restart_count, 1);
        
        process_info.restart_count += 1;
        assert_eq!(process_info.restart_count, 2);
    }

    /// 헬스 체크 시간 업데이트 테스트
    #[test]
    fn test_health_check_time_update() {
        let mut process_info = ProcessInfo::new(12345);
        let initial_time = process_info.last_health_check;
        
        // 시간을 수동으로 업데이트
        let new_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        process_info.last_health_check = new_time;
        
        assert!(process_info.last_health_check >= initial_time);
    }

    /// 프로세스 정보 직렬화/역직렬화 테스트
    #[test]
    fn test_process_info_serialization() {
        let original = ProcessInfo::new(12345);
        
        // JSON으로 직렬화
        let serialized = serde_json::to_string(&original).unwrap();
        assert!(!serialized.is_empty());
        
        // 역직렬화
        let deserialized: ProcessInfo = serde_json::from_str(&serialized).unwrap();
        
        // 필드들이 올바르게 복원되었는지 확인
        assert_eq!(deserialized.pid, original.pid);
        assert_eq!(deserialized.start_time, original.start_time);
        assert_eq!(deserialized.restart_count, original.restart_count);
        assert_eq!(deserialized.last_health_check, original.last_health_check);
        
        // 상태도 올바르게 복원되었는지 확인
        match (&original.status, &deserialized.status) {
            (ProcessStatus::Starting, ProcessStatus::Starting) => {},
            _ => panic!("Status not properly deserialized"),
        }
    }
}