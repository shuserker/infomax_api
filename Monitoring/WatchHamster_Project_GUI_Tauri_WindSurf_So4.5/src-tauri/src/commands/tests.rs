#[cfg(test)]
mod tests {
    use crate::commands::*;
    use std::fs;
    use tempfile::TempDir;

    /// 시스템 정보 조회 테스트
    #[tokio::test]
    async fn test_get_system_info() {
        let result = get_system_info().await;
        
        assert!(result.is_ok());
        let system_info = result.unwrap();
        
        // 기본 필드들이 비어있지 않은지 확인
        assert!(!system_info.platform.is_empty());
        assert!(!system_info.arch.is_empty());
        assert!(!system_info.version.is_empty());
        assert!(!system_info.hostname.is_empty());
        
        // 플랫폼이 예상되는 값 중 하나인지 확인
        assert!(["windows", "macos", "linux", "freebsd", "openbsd", "netbsd"]
            .contains(&system_info.platform.as_str()));
    }

    /// 확장된 시스템 정보 조회 테스트
    #[tokio::test]
    async fn test_get_extended_system_info() {
        let result = get_extended_system_info().await;
        
        assert!(result.is_ok());
        let extended_info = result.unwrap();
        
        // 기본 필드들 확인
        assert!(!extended_info.platform.is_empty());
        assert!(!extended_info.arch.is_empty());
        assert!(!extended_info.hostname.is_empty());
        assert!(!extended_info.current_dir.is_empty());
        
        // 환경 변수가 존재하는지 확인
        assert!(!extended_info.env_vars.is_empty());
        
        // OS별 확장자 확인
        if cfg!(windows) {
            assert_eq!(extended_info.exe_extension, "exe");
        } else {
            assert_eq!(extended_info.exe_extension, "");
        }
    }

    /// 파일 시스템 테스트 - 디렉토리 목록 조회
    #[tokio::test]
    async fn test_list_directory() {
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path().to_string_lossy().to_string();
        
        // 테스트 파일들 생성
        let test_file = temp_dir.path().join("test.txt");
        fs::write(&test_file, "test content").unwrap();
        
        let test_subdir = temp_dir.path().join("subdir");
        fs::create_dir(&test_subdir).unwrap();
        
        // 디렉토리 목록 조회
        let result = list_directory(temp_path).await;
        
        assert!(result.is_ok());
        let listing = result.unwrap();
        
        assert_eq!(listing.total_count, 2);
        assert!(listing.files.iter().any(|f| f.name == "test.txt" && !f.is_dir));
        assert!(listing.files.iter().any(|f| f.name == "subdir" && f.is_dir));
    }

    /// 파일 시스템 테스트 - 파일 읽기/쓰기
    #[tokio::test]
    async fn test_file_read_write() {
        let temp_dir = TempDir::new().unwrap();
        let test_file_path = temp_dir.path().join("test_rw.txt").to_string_lossy().to_string();
        
        let test_content = "Hello, Tauri Test!";
        
        // 파일 쓰기 테스트
        let write_request = WriteFileRequest {
            path: test_file_path.clone(),
            content: test_content.to_string(),
            create_dirs: Some(false),
        };
        
        let write_result = write_file(write_request).await;
        assert!(write_result.is_ok());
        
        // 파일 읽기 테스트
        let read_result = read_file(test_file_path).await;
        assert!(read_result.is_ok());
        
        let file_content = read_result.unwrap();
        assert_eq!(file_content.content, test_content);
        assert_eq!(file_content.encoding, "UTF-8");
        assert_eq!(file_content.size, test_content.len() as u64);
    }

    /// 파일 시스템 테스트 - 디렉토리 생성
    #[tokio::test]
    async fn test_create_directory() {
        let temp_dir = TempDir::new().unwrap();
        let new_dir_path = temp_dir.path().join("new_directory").to_string_lossy().to_string();
        
        // 디렉토리 생성
        let result = create_directory(new_dir_path.clone(), Some(false)).await;
        assert!(result.is_ok());
        
        // 디렉토리가 실제로 생성되었는지 확인
        let exists_result = path_exists(new_dir_path).await;
        assert!(exists_result.is_ok());
        assert!(exists_result.unwrap());
    }

    /// 파일 시스템 테스트 - 파일 정보 조회
    #[tokio::test]
    async fn test_get_file_info() {
        let temp_dir = TempDir::new().unwrap();
        let test_file_path = temp_dir.path().join("info_test.txt").to_string_lossy().to_string();
        
        let test_content = "File info test content";
        fs::write(&test_file_path, test_content).unwrap();
        
        let result = get_file_info(test_file_path).await;
        assert!(result.is_ok());
        
        let file_info = result.unwrap();
        assert_eq!(file_info.name, "info_test.txt");
        assert_eq!(file_info.size, test_content.len() as u64);
        assert!(!file_info.is_dir);
        assert!(file_info.modified.is_some());
    }

    /// 파일 시스템 테스트 - 파일 복사
    #[tokio::test]
    async fn test_copy_file() {
        let temp_dir = TempDir::new().unwrap();
        let source_path = temp_dir.path().join("source.txt").to_string_lossy().to_string();
        let dest_path = temp_dir.path().join("dest.txt").to_string_lossy().to_string();
        
        let test_content = "Copy test content";
        fs::write(&source_path, test_content).unwrap();
        
        // 파일 복사
        let copy_result = copy_file(source_path, dest_path.clone()).await;
        assert!(copy_result.is_ok());
        
        // 복사된 파일 확인
        let read_result = read_file(dest_path).await;
        assert!(read_result.is_ok());
        assert_eq!(read_result.unwrap().content, test_content);
    }

    /// 파일 시스템 테스트 - 파일 이동
    #[tokio::test]
    async fn test_move_path() {
        let temp_dir = TempDir::new().unwrap();
        let source_path = temp_dir.path().join("move_source.txt").to_string_lossy().to_string();
        let dest_path = temp_dir.path().join("move_dest.txt").to_string_lossy().to_string();
        
        let test_content = "Move test content";
        fs::write(&source_path, test_content).unwrap();
        
        // 파일 이동
        let move_result = move_path(source_path.clone(), dest_path.clone()).await;
        assert!(move_result.is_ok());
        
        // 원본 파일이 없어졌는지 확인
        let source_exists = path_exists(source_path).await.unwrap();
        assert!(!source_exists);
        
        // 대상 파일이 존재하는지 확인
        let dest_exists = path_exists(dest_path.clone()).await.unwrap();
        assert!(dest_exists);
        
        // 내용이 올바른지 확인
        let read_result = read_file(dest_path).await;
        assert!(read_result.is_ok());
        assert_eq!(read_result.unwrap().content, test_content);
    }

    /// 파일 시스템 테스트 - 파일 삭제
    #[tokio::test]
    async fn test_delete_path() {
        let temp_dir = TempDir::new().unwrap();
        let test_file_path = temp_dir.path().join("delete_test.txt").to_string_lossy().to_string();
        
        fs::write(&test_file_path, "Delete test").unwrap();
        
        // 파일이 존재하는지 확인
        let exists_before = path_exists(test_file_path.clone()).await.unwrap();
        assert!(exists_before);
        
        // 파일 삭제
        let delete_result = delete_path(test_file_path.clone()).await;
        assert!(delete_result.is_ok());
        
        // 파일이 삭제되었는지 확인
        let exists_after = path_exists(test_file_path).await.unwrap();
        assert!(!exists_after);
    }

    /// 웹훅 URL 유효성 검사 테스트
    #[tokio::test]
    async fn test_validate_webhook_url() {
        // 유효한 URL 테스트
        let valid_url = "https://httpbin.org/post".to_string();
        let result = validate_webhook_url(valid_url).await;
        assert!(result.is_ok());
        // 실제 네트워크 상태에 따라 결과가 달라질 수 있으므로 결과값은 확인하지 않음
        
        // 잘못된 URL 형식 테스트
        let invalid_url = "not-a-url".to_string();
        let result = validate_webhook_url(invalid_url).await;
        assert!(result.is_ok());
        assert!(!result.unwrap()); // 잘못된 형식이므로 false여야 함
    }

    /// 경로 존재 여부 확인 테스트
    #[tokio::test]
    async fn test_path_exists() {
        let temp_dir = TempDir::new().unwrap();
        let existing_path = temp_dir.path().to_string_lossy().to_string();
        let non_existing_path = temp_dir.path().join("non_existing").to_string_lossy().to_string();
        
        // 존재하는 경로 테스트
        let exists_result = path_exists(existing_path).await;
        assert!(exists_result.is_ok());
        assert!(exists_result.unwrap());
        
        // 존재하지 않는 경로 테스트
        let not_exists_result = path_exists(non_existing_path).await;
        assert!(not_exists_result.is_ok());
        assert!(!not_exists_result.unwrap());
    }

    /// 현재 디렉토리 조회 테스트
    #[tokio::test]
    async fn test_get_current_dir() {
        let result = get_current_dir().await;
        assert!(result.is_ok());
        
        let current_dir = result.unwrap();
        assert!(!current_dir.is_empty());
        
        // 실제로 존재하는 디렉토리인지 확인
        let exists_result = path_exists(current_dir).await;
        assert!(exists_result.is_ok());
        assert!(exists_result.unwrap());
    }

    /// 홈 디렉토리 조회 테스트
    #[tokio::test]
    async fn test_get_home_dir() {
        let result = get_home_dir().await;
        assert!(result.is_ok());
        
        let home_dir = result.unwrap();
        assert!(!home_dir.is_empty());
        
        // 실제로 존재하는 디렉토리인지 확인
        let exists_result = path_exists(home_dir).await;
        assert!(exists_result.is_ok());
        assert!(exists_result.unwrap());
    }
}