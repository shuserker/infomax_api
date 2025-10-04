use tauri::{AppHandle, Manager};
use log::{info, warn, error};
use serde::{Deserialize, Serialize};

/// 창 정보 구조체
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowInfo {
    pub is_visible: bool,
    pub is_maximized: bool,
    pub is_minimized: bool,
    pub is_focused: bool,
    pub width: f64,
    pub height: f64,
    pub x: f64,
    pub y: f64,
}

/// 창 관리 유틸리티 구조체
pub struct WindowManager {
    app_handle: AppHandle,
}

impl WindowManager {
    /// 새로운 WindowManager 인스턴스 생성
    pub fn new(app_handle: AppHandle) -> Self {
        Self { app_handle }
    }

    /// 메인 창 표시
    pub fn show_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.show().map_err(|e| format!("창 표시 실패: {}", e))?;
            window.set_focus().map_err(|e| format!("창 포커스 설정 실패: {}", e))?;
            info!("메인 창이 표시되었습니다");
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 메인 창 숨기기
    pub fn hide_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.hide().map_err(|e| format!("창 숨기기 실패: {}", e))?;
            info!("메인 창이 숨겨졌습니다");
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창 표시/숨기기 토글
    pub fn toggle_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            let is_visible = window.is_visible().unwrap_or(false);
            if is_visible {
                self.hide_main_window()
            } else {
                self.show_main_window()
            }
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창이 표시되어 있는지 확인
    pub fn is_main_window_visible(&self) -> bool {
        if let Some(window) = self.app_handle.get_window("main") {
            window.is_visible().unwrap_or(false)
        } else {
            false
        }
    }

    /// 창을 최대화
    pub fn maximize_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.maximize().map_err(|e| format!("창 최대화 실패: {}", e))?;
            info!("메인 창이 최대화되었습니다");
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창 최대화 해제
    pub fn unmaximize_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.unmaximize().map_err(|e| format!("창 최대화 해제 실패: {}", e))?;
            info!("메인 창 최대화가 해제되었습니다");
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창을 최소화
    pub fn minimize_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.minimize().map_err(|e| format!("창 최소화 실패: {}", e))?;
            info!("메인 창이 최소화되었습니다");
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창 크기 설정
    pub fn set_window_size(&self, width: f64, height: f64) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            let size = tauri::LogicalSize::new(width, height);
            window.set_size(size).map_err(|e| format!("창 크기 설정 실패: {}", e))?;
            info!("창 크기가 {}x{}로 설정되었습니다", width, height);
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창 위치 설정
    pub fn set_window_position(&self, x: f64, y: f64) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            let position = tauri::LogicalPosition::new(x, y);
            window.set_position(position).map_err(|e| format!("창 위치 설정 실패: {}", e))?;
            info!("창 위치가 ({}, {})로 설정되었습니다", x, y);
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창을 화면 중앙으로 이동
    pub fn center_main_window(&self) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.center().map_err(|e| format!("창 중앙 정렬 실패: {}", e))?;
            info!("메인 창이 화면 중앙으로 이동되었습니다");
            Ok(())
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 프론트엔드에 이벤트 전송
    pub fn emit_to_frontend(&self, event: &str, payload: impl serde::Serialize + Clone) -> Result<(), String> {
        if let Some(window) = self.app_handle.get_window("main") {
            window.emit(event, payload).map_err(|e| format!("이벤트 전송 실패: {}", e))?;
            info!("프론트엔드에 이벤트 '{}' 전송됨", event);
            Ok(())
        } else {
            warn!("메인 창을 찾을 수 없어 이벤트를 전송할 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }

    /// 창 상태 정보 가져오기
    pub fn get_window_info(&self) -> Result<WindowInfo, String> {
        if let Some(window) = self.app_handle.get_window("main") {
            let is_visible = window.is_visible().unwrap_or(false);
            let is_maximized = window.is_maximized().unwrap_or(false);
            let is_minimized = window.is_minimized().unwrap_or(false);
            let is_focused = window.is_focused().unwrap_or(false);
            
            Ok(WindowInfo {
                is_visible,
                is_maximized,
                is_minimized,
                is_focused,
                width: 1200.0,  // 기본값
                height: 800.0,  // 기본값
                x: 0.0,         // 기본값
                y: 0.0,         // 기본값
            })
        } else {
            error!("메인 창을 찾을 수 없습니다");
            Err("메인 창을 찾을 수 없습니다".to_string())
        }
    }
}



/// 전역 창 관리자 인스턴스를 위한 헬퍼 함수들
pub fn show_window(app_handle: &AppHandle) -> Result<(), String> {
    WindowManager::new(app_handle.clone()).show_main_window()
}

pub fn hide_window(app_handle: &AppHandle) -> Result<(), String> {
    WindowManager::new(app_handle.clone()).hide_main_window()
}

pub fn toggle_window(app_handle: &AppHandle) -> Result<(), String> {
    WindowManager::new(app_handle.clone()).toggle_main_window()
}

pub fn emit_to_window(app_handle: &AppHandle, event: &str, payload: impl serde::Serialize + Clone) -> Result<(), String> {
    WindowManager::new(app_handle.clone()).emit_to_frontend(event, payload)
}

// 테스트 모듈
#[cfg(test)]
mod tests;