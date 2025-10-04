// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_bridge;
mod window_manager;

use tauri::{Manager, WindowEvent, SystemTray, SystemTrayMenu, CustomMenuItem, SystemTrayMenuItem};
use log::{info, error, warn};

fn main() {
    // 로깅 초기화
    env_logger::init();
    info!("WatchHamster Tauri 애플리케이션 시작");

    // 시스템 트레이 메뉴 생성
    let tray_menu = tauri::SystemTrayMenu::new()
        .add_item(tauri::CustomMenuItem::new("show".to_string(), "창 표시"))
        .add_item(tauri::CustomMenuItem::new("hide".to_string(), "창 숨기기"))
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(tauri::CustomMenuItem::new("quit".to_string(), "종료"));

    let system_tray = tauri::SystemTray::new()
        .with_menu(tray_menu)
        .with_tooltip("WatchHamster - POSCO 시스템 모니터링");

    tauri::Builder::default()
        .system_tray(system_tray)
        .invoke_handler(tauri::generate_handler![
            commands::start_python_backend,
            commands::stop_python_backend,
            commands::get_system_info,
            commands::send_webhook,
            commands::get_backend_status,
            commands::restart_python_backend,
            commands::get_process_info,
            commands::force_kill_backend,
            commands::start_process_monitoring,
            commands::show_window,
            commands::hide_window,
            commands::toggle_window,
            commands::get_window_info,
            commands::set_window_size,
            commands::set_window_position,
            commands::center_window,
            commands::maximize_window,
            commands::unmaximize_window,
            commands::minimize_window,
            commands::list_directory,
            commands::read_file,
            commands::write_file,
            commands::delete_path,
            commands::create_directory,
            commands::move_path,
            commands::copy_file,
            commands::path_exists,
            commands::get_file_info,
            commands::get_app_data_dir,
            commands::get_app_config_dir,
            commands::get_app_log_dir,
            commands::get_current_dir,
            commands::get_home_dir,
            commands::get_extended_system_info,
            commands::send_advanced_webhook,
            commands::validate_webhook_url
        ])
        .setup(|app| {
            info!("애플리케이션 설정 초기화 시작");
            
            // 메인 창 설정
            if let Some(window) = app.get_window("main") {
                // 창 제목 설정
                let _ = window.set_title("WatchHamster - POSCO 시스템 모니터링");
                
                // 최소 크기 설정
                let _ = window.set_min_size(Some(tauri::LogicalSize::new(800.0, 600.0)));
                
                info!("메인 창 설정 완료");
            }
            
            // 애플리케이션 시작 시 Python 백엔드 자동 시작
            let app_handle = app.handle();
            tauri::async_runtime::spawn(async move {
                info!("Python 백엔드 시작 시도");
                match python_bridge::start_backend().await {
                    Ok(_) => {
                        info!("Python 백엔드 성공적으로 시작됨");
                        // 프론트엔드에 백엔드 시작 알림
                        if let Err(e) = window_manager::emit_to_window(&app_handle, "backend-started", "Python 백엔드가 시작되었습니다") {
                            warn!("백엔드 시작 알림 전송 실패: {}", e);
                        }
                    }
                    Err(e) => {
                        error!("Python 백엔드 시작 실패: {}", e);
                        // 프론트엔드에 오류 알림
                        let error_msg = format!("백엔드 시작 실패: {}", e);
                        if let Err(e) = window_manager::emit_to_window(&app_handle, "backend-error", error_msg) {
                            error!("백엔드 오류 알림 전송 실패: {}", e);
                        }
                    }
                }
            });
            
            // 프로세스 모니터링 시작
            let monitoring_handle = app.handle();
            tauri::async_runtime::spawn(async move {
                info!("프로세스 모니터링 시작");
                if let Err(e) = python_bridge::start_process_monitoring().await {
                    error!("프로세스 모니터링 오류: {}", e);
                }
            });
            
            Ok(())
        })
        .on_system_tray_event(|app, event| {
            use tauri::SystemTrayEvent;
            match event {
                SystemTrayEvent::LeftClick { .. } => {
                    info!("시스템 트레이 좌클릭 - 창 토글");
                    if let Some(window) = app.get_window("main") {
                        if window.is_visible().unwrap_or(false) {
                            let _ = window.hide();
                        } else {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                }
                SystemTrayEvent::RightClick { .. } => {
                    info!("시스템 트레이 우클릭");
                }
                SystemTrayEvent::DoubleClick { .. } => {
                    info!("시스템 트레이 더블클릭 - 창 표시");
                    if let Some(window) = app.get_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
                SystemTrayEvent::MenuItemClick { id, .. } => {
                    info!("시스템 트레이 메뉴 클릭: {}", id);
                    match id.as_str() {
                        "show" => {
                            if let Some(window) = app.get_window("main") {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                        "hide" => {
                            if let Some(window) = app.get_window("main") {
                                let _ = window.hide();
                            }
                        }
                        "quit" => {
                            info!("애플리케이션 종료 요청");
                            app.exit(0);
                        }
                        _ => {}
                    }
                }
                _ => {
                    // 기타 시스템 트레이 이벤트 처리
                }
            }
        })
        .on_window_event(|event| {
            match event.event() {
                WindowEvent::CloseRequested { api, .. } => {
                    info!("창 닫기 요청 - 시스템 트레이로 최소화");
                    // 창 닫기 시 시스템 트레이로 최소화
                    if let Err(e) = event.window().hide() {
                        warn!("창 숨기기 실패: {}", e);
                    }
                    api.prevent_close();
                }
                WindowEvent::Focused(focused) => {
                    if *focused {
                        info!("창이 포커스를 받음");
                    }
                }
                WindowEvent::Resized(size) => {
                    info!("창 크기 변경: {}x{}", size.width, size.height);
                }
                WindowEvent::Moved(position) => {
                    info!("창 위치 변경: ({}, {})", position.x, position.y);
                }
                _ => {}
            }
        })
        .run(tauri::generate_context!())
        .expect("Tauri 애플리케이션 실행 중 오류 발생");
}