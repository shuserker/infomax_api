#[cfg(test)]
mod tests {
    use crate::window_manager::*;

    /// WindowInfo 구조체 테스트
    #[test]
    fn test_window_info_creation() {
        let window_info = WindowInfo {
            is_visible: true,
            is_maximized: false,
            is_minimized: false,
            is_focused: true,
            width: 1200.0,
            height: 800.0,
            x: 100.0,
            y: 100.0,
        };

        assert_eq!(window_info.is_visible, true);
        assert_eq!(window_info.is_maximized, false);
        assert_eq!(window_info.is_minimized, false);
        assert_eq!(window_info.is_focused, true);
        assert_eq!(window_info.width, 1200.0);
        assert_eq!(window_info.height, 800.0);
    }

    /// WindowInfo 직렬화 테스트
    #[test]
    fn test_window_info_serialization() {
        let original = WindowInfo {
            is_visible: true,
            is_maximized: false,
            is_minimized: false,
            is_focused: true,
            width: 1200.0,
            height: 800.0,
            x: 100.0,
            y: 100.0,
        };

        let serialized = serde_json::to_string(&original).unwrap();
        assert!(serialized.contains("\"is_visible\":true"));
        assert!(serialized.contains("\"is_maximized\":false"));

        let deserialized: WindowInfo = serde_json::from_str(&serialized).unwrap();
        assert_eq!(original.is_visible, deserialized.is_visible);
        assert_eq!(original.is_maximized, deserialized.is_maximized);
        assert_eq!(original.width, deserialized.width);
        assert_eq!(original.height, deserialized.height);
    }

    /// WindowInfo 기본값 테스트
    #[test]
    fn test_window_info_defaults() {
        let window_info = WindowInfo {
            is_visible: false,
            is_maximized: false,
            is_minimized: true,
            is_focused: false,
            width: 800.0,
            height: 600.0,
            x: 0.0,
            y: 0.0,
        };

        assert_eq!(window_info.is_visible, false);
        assert_eq!(window_info.is_minimized, true);
        assert_eq!(window_info.width, 800.0);
        assert_eq!(window_info.height, 600.0);
    }
}