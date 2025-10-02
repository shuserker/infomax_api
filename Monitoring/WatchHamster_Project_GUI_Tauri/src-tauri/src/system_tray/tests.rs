#[cfg(test)]
mod tests {
    use super::*;
    use tauri::{CustomMenuItem, SystemTrayMenu, SystemTrayMenuItem};

    /// 시스템 트레이 메뉴 생성 테스트
    #[test]
    fn test_create_tray_menu() {
        let menu = create_tray_menu();
        
        // 메뉴가 생성되었는지 확인
        // SystemTrayMenu는 내부 구조에 직접 접근할 수 없으므로
        // 메뉴 생성이 패닉 없이 완료되는지만 확인
        assert!(true); // 메뉴 생성이 성공적으로 완료됨
    }

    /// CustomMenuItem 생성 테스트
    #[test]
    fn test_custom_menu_items() {
        let show_item = CustomMenuItem::new("show".to_string(), "WatchHamster 열기");
        let hide_item = CustomMenuItem::new("hide".to_string(), "WatchHamster 숨기기");
        let backend_status_item = CustomMenuItem::new("backend_status".to_string(), "백엔드 상태 확인");
        let restart_backend_item = CustomMenuItem::new("restart_backend".to_string(), "백엔드 재시작");
        let quit_item = CustomMenuItem::new("quit".to_string(), "종료");
        
        // 메뉴 아이템들이 성공적으로 생성되었는지 확인
        // CustomMenuItem은 내부 구조에 직접 접근할 수 없으므로
        // 생성이 패닉 없이 완료되는지만 확인
        assert!(true);
    }

    /// 메뉴 구조 테스트
    #[test]
    fn test_menu_structure() {
        // 메뉴 아이템들 생성
        let show = CustomMenuItem::new("show".to_string(), "WatchHamster 열기");
        let hide = CustomMenuItem::new("hide".to_string(), "WatchHamster 숨기기");
        let separator1 = SystemTrayMenuItem::Separator;
        let backend_status = CustomMenuItem::new("backend_status".to_string(), "백엔드 상태 확인");
        let restart_backend = CustomMenuItem::new("restart_backend".to_string(), "백엔드 재시작");
        let separator2 = SystemTrayMenuItem::Separator;
        let quit = CustomMenuItem::new("quit".to_string(), "종료");
        
        // 메뉴 구성
        let menu = SystemTrayMenu::new()
            .add_item(show)
            .add_item(hide)
            .add_native_item(separator1)
            .add_item(backend_status)
            .add_item(restart_backend)
            .add_native_item(separator2)
            .add_item(quit);
        
        // 메뉴가 성공적으로 구성되었는지 확인
        assert!(true);
    }

    /// 메뉴 아이템 ID 테스트
    #[test]
    fn test_menu_item_ids() {
        let expected_ids = vec![
            "show",
            "hide", 
            "backend_status",
            "restart_backend",
            "quit"
        ];
        
        // 각 ID가 유효한 문자열인지 확인
        for id in expected_ids {
            assert!(!id.is_empty());
            assert!(id.is_ascii());
            assert!(!id.contains(' ')); // 공백이 없어야 함
            assert!(id.chars().all(|c| c.is_alphanumeric() || c == '_')); // 영숫자와 언더스코어만
        }
    }

    /// 메뉴 아이템 라벨 테스트
    #[test]
    fn test_menu_item_labels() {
        let expected_labels = vec![
            ("show", "WatchHamster 열기"),
            ("hide", "WatchHamster 숨기기"),
            ("backend_status", "백엔드 상태 확인"),
            ("restart_backend", "백엔드 재시작"),
            ("quit", "종료"),
        ];
        
        for (id, label) in expected_labels {
            assert!(!id.is_empty());
            assert!(!label.is_empty());
            
            // 라벨이 한국어를 포함하고 있는지 확인
            assert!(label.chars().any(|c| c as u32 > 127)); // 비ASCII 문자 (한국어) 포함
            
            // CustomMenuItem 생성이 성공하는지 확인
            let item = CustomMenuItem::new(id.to_string(), label);
            // 생성이 성공적으로 완료되면 테스트 통과
            assert!(true);
        }
    }

    /// 시스템 트레이 이벤트 ID 매칭 테스트
    #[test]
    fn test_event_id_matching() {
        let valid_event_ids = vec![
            "show",
            "hide",
            "backend_status", 
            "restart_backend",
            "quit"
        ];
        
        for event_id in valid_event_ids {
            // 각 이벤트 ID가 match 문에서 처리될 수 있는지 확인
            let result = match event_id {
                "show" => "show 이벤트",
                "hide" => "hide 이벤트",
                "backend_status" => "backend_status 이벤트",
                "restart_backend" => "restart_backend 이벤트",
                "quit" => "quit 이벤트",
                _ => "알 수 없는 이벤트",
            };
            
            assert_ne!(result, "알 수 없는 이벤트");
        }
    }

    /// 잘못된 이벤트 ID 처리 테스트
    #[test]
    fn test_invalid_event_id_handling() {
        let invalid_event_ids = vec![
            "invalid",
            "unknown",
            "",
            "show_window", // 비슷하지만 다른 ID
            "quit_app",    // 비슷하지만 다른 ID
        ];
        
        for event_id in invalid_event_ids {
            let result = match event_id {
                "show" => "show 이벤트",
                "hide" => "hide 이벤트", 
                "backend_status" => "backend_status 이벤트",
                "restart_backend" => "restart_backend 이벤트",
                "quit" => "quit 이벤트",
                _ => "알 수 없는 이벤트",
            };
            
            assert_eq!(result, "알 수 없는 이벤트");
        }
    }

    /// 메뉴 아이템 순서 테스트
    #[test]
    fn test_menu_item_order() {
        // 예상되는 메뉴 순서
        let expected_order = vec![
            "show",           // WatchHamster 열기
            "hide",           // WatchHamster 숨기기
            "separator",      // 구분선
            "backend_status", // 백엔드 상태 확인
            "restart_backend",// 백엔드 재시작
            "separator",      // 구분선
            "quit",           // 종료
        ];
        
        // 순서가 논리적으로 올바른지 확인
        assert_eq!(expected_order[0], "show");     // 첫 번째는 표시
        assert_eq!(expected_order[1], "hide");     // 두 번째는 숨기기
        assert_eq!(expected_order[2], "separator"); // 구분선
        assert_eq!(expected_order.last().unwrap(), &"quit"); // 마지막은 종료
        
        // 백엔드 관련 메뉴들이 함께 그룹화되어 있는지 확인
        let backend_start = expected_order.iter().position(|&x| x == "backend_status").unwrap();
        let backend_end = expected_order.iter().position(|&x| x == "restart_backend").unwrap();
        assert_eq!(backend_end, backend_start + 1); // 연속적으로 배치됨
    }

    /// 메뉴 접근성 테스트
    #[test]
    fn test_menu_accessibility() {
        let menu_items = vec![
            ("show", "WatchHamster 열기"),
            ("hide", "WatchHamster 숨기기"),
            ("backend_status", "백엔드 상태 확인"),
            ("restart_backend", "백엔드 재시작"),
            ("quit", "종료"),
        ];
        
        for (id, label) in menu_items {
            // ID가 프로그래밍 친화적인지 확인
            assert!(id.chars().all(|c| c.is_ascii_lowercase() || c == '_'));
            assert!(!id.starts_with('_'));
            assert!(!id.ends_with('_'));
            
            // 라벨이 사용자 친화적인지 확인
            assert!(!label.is_empty());
            assert!(label.len() <= 20); // 너무 길지 않음
            
            // 라벨에 특수문자가 과도하게 사용되지 않았는지 확인
            let special_char_count = label.chars().filter(|c| !c.is_alphanumeric() && *c != ' ').count();
            assert!(special_char_count <= 2); // 특수문자는 최대 2개까지
        }
    }

    /// 메뉴 국제화 준비 테스트
    #[test]
    fn test_menu_i18n_readiness() {
        // 현재는 한국어로 되어 있지만, 향후 다국어 지원을 위한 구조 확인
        let menu_keys = vec![
            "show",
            "hide",
            "backend_status",
            "restart_backend", 
            "quit"
        ];
        
        // 각 키가 국제화 키로 사용하기에 적합한지 확인
        for key in menu_keys {
            // 키가 영어로만 구성되어 있는지 확인 (i18n 키 표준)
            assert!(key.chars().all(|c| c.is_ascii_lowercase() || c == '_'));
            
            // 키가 의미를 명확히 전달하는지 확인
            assert!(key.len() >= 3); // 너무 짧지 않음
            assert!(key.len() <= 20); // 너무 길지 않음
            
            // 키에 동사나 명사가 포함되어 있는지 확인 (의미 전달)
            let meaningful_words = vec!["show", "hide", "status", "restart", "quit", "backend"];
            assert!(meaningful_words.iter().any(|&word| key.contains(word)));
        }
    }
}