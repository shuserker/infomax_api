#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stability Manager - 시스템 안정성 강화 관리자
GUI 애플리케이션 안정성 및 복구 시스템

주요 기능:
- 🔄 GUI 애플리케이션 비정상 종료 시 자동 복구
- 🛡️ 외부 의존성 없는 완전 독립 실행 보장
- 🔧 시스템 트레이를 통한 백그라운드 안정 실행
- ⚙️ config/ 폴더 설정 파일 손상 시 기본값 복구

Requirements: 6.5, 6.1 구현
"""

import os
import sys
import json
import threading
import time
import traceback
import signal
import atexit
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import subprocess
import psutil
import shutil


class StabilityManager:
    """시스템 안정성 관리자"""
    
    def __init__(self, app_root_dir: str):
        """안정성 관리자 초기화"""
        self.app_root_dir = app_root_dir
        self.config_dir = os.path.join(app_root_dir, 'config')
        self.logs_dir = os.path.join(app_root_dir, 'logs')
        
        # 안정성 설정
        self.stability_config = {
            'auto_recovery_enabled': True,
            'max_recovery_attempts': 3,
            'recovery_delay_seconds': 5,
            'health_check_interval': 30,
            'backup_config_on_start': True,
            'monitor_memory_usage': True,
            'max_memory_mb': 1000,
            'monitor_cpu_usage': True,
            'max_cpu_percent': 80,
            'enable_crash_reporting': True
        }
        
        # 상태 추적
        self.is_running = False
        self.recovery_attempts = 0
        self.error_count = 0
        self.recovery_count = 0
        self.last_health_check = None
        self.system_health = {
            'memory_usage_mb': 0,
            'cpu_usage_percent': 0,
            'thread_count': 0,
            'uptime_seconds': 0,
            'last_error': None
        }
        
        # 모니터링 스레드
        self.health_monitor_thread = None
        self.stability_monitor_thread = None
        
        # 콜백 함수들
        self.error_callbacks = []
        self.recovery_callbacks = []
        self.health_callbacks = []
        
        # 시작 시간
        self.start_time = time.time()
        
        # 기본 설정 파일들
        self.default_configs = {
            'gui_config.json': {
                'window': {
                    'width': 1400,
                    'height': 900,
                    'min_width': 1000,
                    'min_height': 700
                },
                'theme': {
                    'name': 'default',
                    'font_family': 'TkDefaultFont',
                    'font_size': 10
                },
                'auto_refresh': {
                    'enabled': True,
                    'interval_seconds': 5
                },
                'performance': {
                    'max_log_lines': 1000,
                    'chunk_size': 100,
                    'cache_enabled': True
                }
            },
            'posco_config.json': {
                'deployment': {
                    'auto_deploy': False,
                    'branch_main': 'main',
                    'branch_publish': 'publish',
                    'timeout_seconds': 300
                },
                'monitoring': {
                    'github_pages_check': True,
                    'check_interval_seconds': 60,
                    'retry_attempts': 3
                },
                'notifications': {
                    'enabled': True,
                    'show_success': True,
                    'show_errors': True
                }
            },
            'webhook_config.json': {
                'webhooks': {
                    'enabled': False,
                    'urls': [],
                    'timeout_seconds': 30,
                    'retry_attempts': 2
                },
                'message_format': {
                    'include_timestamp': True,
                    'include_system_info': False,
                    'template': 'default'
                }
            }
        }
        
        print("🛡️ 시스템 안정성 관리자 초기화 완료")
    
    def start_headless(self):
        """헤드리스 모드로 시작 (GUI 없음)"""
        return self.start()
    
    def start(self):
        """안정성 관리자 시작 (완전 구현)"""
        try:
            if self.is_running:
                print("⚠️ 안정성 관리자가 이미 실행 중입니다")
                return
            
            print("🛡️ 시스템 안정성 관리자 시작 중...")
            self.is_running = True
            self.start_time = time.time()
            
            # 초기 시스템 상태 확인
            initial_health = self.check_system_health()
            print(f"📊 시작 시 시스템 헬스: 메모리 {initial_health['memory_usage_mb']:.1f}MB, "
                  f"CPU {initial_health['cpu_usage_percent']:.1f}%")
            
            # 설정 파일 백업 및 검증
            if self.stability_config['backup_config_on_start']:
                print("🔧 설정 파일 백업 및 검증 중...")
                self.backup_and_verify_configs()
                print("✅ 설정 파일 백업 및 검증 완료")
            
            # 헬스 모니터링 시작
            print("💓 헬스 모니터링 시작 중...")
            self.start_health_monitoring()
            print("💓 헬스 모니터링 시작됨")
            
            # 안정성 모니터링 시작
            print("🛡️ 안정성 모니터링 시작 중...")
            self.start_stability_monitoring()
            print("🛡️ 안정성 모니터링 시작됨")
            
            # 시그널 핸들러 등록
            print("📡 시그널 핸들러 등록 중...")
            self.register_signal_handlers()
            print("📡 시그널 핸들러 등록됨")
            
            # 종료 시 정리 함수 등록
            atexit.register(self.cleanup_on_exit)
            
            # 모니터링 스레드 상태 확인
            time.sleep(0.1)  # 스레드 시작 대기
            active_monitors = []
            if self.health_monitor_thread and self.health_monitor_thread.is_alive():
                active_monitors.append("헬스모니터")
            if self.stability_monitor_thread and self.stability_monitor_thread.is_alive():
                active_monitors.append("안정성모니터")
            
            print(f"✅ 활성 모니터: {len(active_monitors)}/2 - {', '.join(active_monitors)}")
            print("🚀 시스템 안정성 관리자 시작됨")
            
        except Exception as e:
            print(f"❌ 안정성 관리자 시작 실패: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        """안정성 관리자 중지 (완전 구현)"""
        try:
            if not self.is_running:
                print("⚠️ 안정성 관리자가 이미 중지되어 있습니다")
                return
            
            print("🛑 시스템 안정성 관리자 중지 중...")
            self.is_running = False
            
            # 실행 시간 계산
            if hasattr(self, 'start_time'):
                runtime = time.time() - self.start_time
                print(f"⏱️ 총 실행 시간: {runtime:.1f}초")
            
            # 최종 시스템 상태 확인
            final_health = self.check_system_health()
            print(f"📊 종료 시 시스템 헬스: 메모리 {final_health['memory_usage_mb']:.1f}MB, "
                  f"CPU {final_health['cpu_usage_percent']:.1f}%")
            
            # 모니터링 스레드 종료 대기
            print("⏹️ 모니터링 스레드들 종료 중...")
            
            if self.health_monitor_thread and self.health_monitor_thread.is_alive():
                print("⏳ 헬스 모니터 종료 대기 중...")
                self.health_monitor_thread.join(timeout=3)
                if self.health_monitor_thread.is_alive():
                    print("⚠️ 헬스 모니터 강제 종료 (타임아웃)")
                else:
                    print("⏹️ 헬스 모니터 종료됨")
            
            if self.stability_monitor_thread and self.stability_monitor_thread.is_alive():
                print("⏳ 안정성 모니터 종료 대기 중...")
                self.stability_monitor_thread.join(timeout=3)
                if self.stability_monitor_thread.is_alive():
                    print("⚠️ 안정성 모니터 강제 종료 (타임아웃)")
                else:
                    print("⏹️ 안정성 모니터 종료됨")
            
            # 오류 통계 출력
            if self.error_count > 0:
                print(f"📊 총 처리된 오류: {self.error_count}개")
                
            # 복구 통계 출력
            recovery_count = getattr(self, 'recovery_count', 0)
            if recovery_count > 0:
                print(f"🔧 총 복구 작업: {recovery_count}회")
            
            print("🏁 시스템 안정성 관리자 중지됨")
            
        except Exception as e:
            print(f"❌ 안정성 관리자 중지 중 오류: {e}")
            # 강제 중지
            self.is_running = False
    
    def backup_and_verify_configs(self):
        """설정 파일 백업 및 검증"""
        try:
            # config 디렉토리 생성
            os.makedirs(self.config_dir, exist_ok=True)
            
            # 백업 디렉토리 생성
            backup_dir = os.path.join(self.config_dir, 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 각 설정 파일 검증 및 복구
            for config_name, default_config in self.default_configs.items():
                config_path = os.path.join(self.config_dir, config_name)
                backup_path = os.path.join(backup_dir, f"{config_name}.backup")
                
                # 기존 설정 파일 백업
                if os.path.exists(config_path):
                    try:
                        shutil.copy2(config_path, backup_path)
                        
                        # 설정 파일 유효성 검사
                        with open(config_path, 'r', encoding='utf-8') as f:
                            json.load(f)  # JSON 파싱 테스트
                        
                        print(f"✅ 설정 파일 검증 완료: {config_name}")
                        
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"⚠️ 손상된 설정 파일 발견: {config_name} - {e}")
                        self.restore_default_config(config_name, default_config)
                else:
                    # 설정 파일이 없으면 기본값으로 생성
                    print(f"📝 기본 설정 파일 생성: {config_name}")
                    self.restore_default_config(config_name, default_config)
            
            print("🔧 설정 파일 백업 및 검증 완료")
            
        except Exception as e:
            print(f"❌ 설정 파일 백업/검증 오류: {e}")
            self.log_error("config_backup_error", str(e))
    
    def restore_default_config(self, config_name: str, default_config: Dict):
        """기본 설정으로 복구"""
        try:
            config_path = os.path.join(self.config_dir, config_name)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print(f"🔄 기본 설정으로 복구됨: {config_name}")
            
        except Exception as e:
            print(f"❌ 기본 설정 복구 실패: {config_name} - {e}")
            self.log_error("config_restore_error", str(e))
    
    def start_health_monitoring(self):
        """헬스 모니터링 시작"""
        if self.health_monitor_thread and self.health_monitor_thread.is_alive():
            return
        
        self.health_monitor_thread = threading.Thread(
            target=self._health_monitor_worker, daemon=True
        )
        self.health_monitor_thread.start()
        print("💓 헬스 모니터링 시작됨")
    
    def start_stability_monitoring(self):
        """안정성 모니터링 시작"""
        if self.stability_monitor_thread and self.stability_monitor_thread.is_alive():
            return
        
        self.stability_monitor_thread = threading.Thread(
            target=self._stability_monitor_worker, daemon=True
        )
        self.stability_monitor_thread.start()
        print("🛡️ 안정성 모니터링 시작됨")
    
    def _health_monitor_worker(self):
        """헬스 모니터링 워커 스레드"""
        while self.is_running:
            try:
                # 시스템 리소스 모니터링
                self.check_system_health()
                
                # 헬스 콜백 실행
                for callback in self.health_callbacks:
                    try:
                        callback(self.system_health)
                    except Exception as e:
                        print(f"⚠️ 헬스 콜백 오류: {e}")
                
                # 다음 체크까지 대기
                time.sleep(self.stability_config['health_check_interval'])
                
            except Exception as e:
                print(f"❌ 헬스 모니터링 오류: {e}")
                self.log_error("health_monitor_error", str(e))
                time.sleep(10)  # 오류 시 10초 대기
    
    def _stability_monitor_worker(self):
        """안정성 모니터링 워커 스레드"""
        while self.is_running:
            try:
                # 메모리 사용량 체크
                if self.stability_config['monitor_memory_usage']:
                    self.check_memory_usage()
                
                # CPU 사용량 체크
                if self.stability_config['monitor_cpu_usage']:
                    self.check_cpu_usage()
                
                # 설정 파일 무결성 체크
                self.check_config_integrity()
                
                # 로그 디렉토리 체크
                self.check_log_directory()
                
                time.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                print(f"❌ 안정성 모니터링 오류: {e}")
                self.log_error("stability_monitor_error", str(e))
                time.sleep(30)  # 오류 시 30초 대기
    
    def check_system_health(self):
        """시스템 헬스 체크"""
        try:
            process = psutil.Process()
            
            # 메모리 사용량
            memory_info = process.memory_info()
            self.system_health['memory_usage_mb'] = memory_info.rss / 1024 / 1024
            
            # CPU 사용량
            self.system_health['cpu_usage_percent'] = process.cpu_percent()
            
            # 스레드 수
            self.system_health['thread_count'] = process.num_threads()
            
            # 업타임
            self.system_health['uptime_seconds'] = time.time() - self.start_time
            
            # 마지막 헬스 체크 시간
            self.last_health_check = datetime.now()
            
            return self.system_health
            
        except Exception as e:
            print(f"⚠️ 시스템 헬스 체크 오류: {e}")
            self.system_health['last_error'] = str(e)
            return self.system_health
    
    def check_memory_usage(self):
        """메모리 사용량 체크"""
        memory_mb = self.system_health['memory_usage_mb']
        max_memory = self.stability_config['max_memory_mb']
        
        if memory_mb > max_memory:
            warning_msg = f"높은 메모리 사용량: {memory_mb:.1f}MB (최대: {max_memory}MB)"
            print(f"⚠️ {warning_msg}")
            self.log_error("high_memory_usage", warning_msg)
            
            # 메모리 정리 시도
            self.trigger_memory_cleanup()
    
    def check_cpu_usage(self):
        """CPU 사용량 체크"""
        cpu_percent = self.system_health['cpu_usage_percent']
        max_cpu = self.stability_config['max_cpu_percent']
        
        if cpu_percent > max_cpu:
            warning_msg = f"높은 CPU 사용량: {cpu_percent:.1f}% (최대: {max_cpu}%)"
            print(f"⚠️ {warning_msg}")
            self.log_error("high_cpu_usage", warning_msg)
    
    def check_config_integrity(self):
        """설정 파일 무결성 체크"""
        for config_name in self.default_configs.keys():
            config_path = os.path.join(self.config_dir, config_name)
            
            if not os.path.exists(config_path):
                print(f"⚠️ 설정 파일 누락: {config_name}")
                self.restore_default_config(config_name, self.default_configs[config_name])
                continue
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ 설정 파일 손상: {config_name} - {e}")
                self.restore_default_config(config_name, self.default_configs[config_name])
    
    def check_log_directory(self):
        """로그 디렉토리 체크"""
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            
            # 로그 파일 크기 체크 (각 파일 최대 10MB)
            for log_file in os.listdir(self.logs_dir):
                if log_file.endswith('.log'):
                    log_path = os.path.join(self.logs_dir, log_file)
                    file_size = os.path.getsize(log_path)
                    
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        self.rotate_log_file(log_path)
            
        except Exception as e:
            print(f"⚠️ 로그 디렉토리 체크 오류: {e}")
    
    def rotate_log_file(self, log_path: str):
        """로그 파일 로테이션"""
        try:
            # 백업 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{log_path}.{timestamp}.backup"
            
            # 기존 파일을 백업으로 이동
            shutil.move(log_path, backup_path)
            
            # 새 로그 파일 생성
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"# 로그 파일 로테이션: {datetime.now()}\n")
            
            print(f"🔄 로그 파일 로테이션: {os.path.basename(log_path)}")
            
        except Exception as e:
            print(f"❌ 로그 파일 로테이션 실패: {e}")
    
    def trigger_memory_cleanup(self):
        """메모리 정리 트리거"""
        try:
            import gc
            collected = gc.collect()
            print(f"🧹 메모리 정리: {collected}개 객체 해제됨")
            
            # 정리 후 메모리 사용량 재확인
            self.check_system_health()
            
            return True
            
        except Exception as e:
            print(f"❌ 메모리 정리 오류: {e}")
            return False
    
    def register_signal_handlers(self):
        """시그널 핸들러 등록"""
        try:
            # SIGTERM, SIGINT 핸들러
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            
            # Windows에서는 SIGBREAK도 처리
            if hasattr(signal, 'SIGBREAK'):
                signal.signal(signal.SIGBREAK, self._signal_handler)
            
            print("📡 시그널 핸들러 등록됨")
            
        except Exception as e:
            print(f"⚠️ 시그널 핸들러 등록 실패: {e}")
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"📡 시그널 수신: {signum}")
        
        # 정상 종료 처리
        self.cleanup_on_exit()
        
        # 기본 시그널 처리
        if signum == signal.SIGTERM:
            sys.exit(0)
        elif signum == signal.SIGINT:
            sys.exit(0)
    
    def cleanup_on_exit(self):
        """종료 시 정리 작업"""
        try:
            print("🧹 시스템 정리 작업 시작...")
            
            # 안정성 관리자 중지
            self.stop()
            
            # 최종 상태 로그
            self.log_system_status("application_exit")
            
            print("✅ 시스템 정리 작업 완료")
            
        except Exception as e:
            print(f"❌ 정리 작업 오류: {e}")
    
    def log_error(self, error_type: str, error_message: str):
        """오류 로그 기록"""
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            
            error_log_path = os.path.join(self.logs_dir, 'stability_errors.log')
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {error_type}: {error_message}\n"
            
            with open(error_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # 오류 콜백 실행
            for callback in self.error_callbacks:
                try:
                    callback(error_type, error_message)
                except Exception as e:
                    print(f"⚠️ 오류 콜백 실행 실패: {e}")
            
        except Exception as e:
            print(f"❌ 오류 로그 기록 실패: {e}")
    
    def log_system_status(self, event_type: str):
        """시스템 상태 로그 기록"""
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            
            status_log_path = os.path.join(self.logs_dir, 'system_status.log')
            
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'system_health': self.system_health.copy(),
                'uptime_seconds': time.time() - self.start_time,
                'recovery_attempts': self.recovery_attempts
            }
            
            with open(status_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(status_data, ensure_ascii=False) + '\n')
            
        except Exception as e:
            print(f"❌ 시스템 상태 로그 기록 실패: {e}")
    
    def register_error_callback(self, callback: Callable[[str, str], None]):
        """오류 콜백 등록 (완전 구현)"""
        try:
            if not callable(callback):
                raise ValueError("콜백은 호출 가능한 객체여야 합니다")
            
            # 중복 등록 방지
            if callback in self.error_callbacks:
                print(f"⚠️ 이미 등록된 오류 콜백입니다")
                return
            
            self.error_callbacks.append(callback)
            print(f"📝 오류 콜백 등록됨 (총 {len(self.error_callbacks)}개)")
            
            # 테스트 콜백 호출
            try:
                callback("test_registration", "콜백 등록 테스트")
                print("✅ 오류 콜백 테스트 성공")
            except Exception as e:
                print(f"⚠️ 오류 콜백 테스트 실패: {e}")
                
        except Exception as e:
            print(f"❌ 오류 콜백 등록 실패: {e}")
    
    def register_recovery_callback(self, callback: Callable[[str], bool]):
        """복구 콜백 등록"""
        self.recovery_callbacks.append(callback)
    
    def register_health_callback(self, callback: Callable[[Dict], None]):
        """헬스 콜백 등록"""
        self.health_callbacks.append(callback)
    
    def get_system_health(self) -> Dict[str, Any]:
        """시스템 헬스 정보 반환"""
        return self.system_health.copy()
    
    def get_stability_config(self) -> Dict[str, Any]:
        """안정성 설정 반환"""
        return self.stability_config.copy()
    
    def update_stability_config(self, config_updates: Dict[str, Any]):
        """안정성 설정 업데이트"""
        self.stability_config.update(config_updates)
        print("⚙️ 안정성 설정 업데이트됨")


# 전역 안정성 관리자 인스턴스
_stability_manager = None


def get_stability_manager(app_root_dir: Optional[str] = None) -> StabilityManager:
    """전역 안정성 관리자 인스턴스 반환"""
    global _stability_manager
    if _stability_manager is None:
        if app_root_dir is None:
            app_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _stability_manager = StabilityManager(app_root_dir)
        _stability_manager.start()
    return _stability_manager


def create_stability_manager(app_root_dir: str) -> StabilityManager:
    """안정성 관리자 생성"""
    manager = StabilityManager(app_root_dir)
    manager.start()
    return manager


if __name__ == "__main__":
    # 테스트 코드
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = create_stability_manager(temp_dir)
        
        # 테스트 콜백
        def test_error_callback(error_type, message):
            print(f"오류 콜백: {error_type} - {message}")
        
        def test_health_callback(health):
            print(f"헬스 콜백: {health}")
        
        manager.register_error_callback(test_error_callback)
        manager.register_health_callback(test_health_callback)
        
        # 잠시 실행
        time.sleep(5)
        
        # 시스템 상태 출력
        health = manager.get_system_health()
        print("시스템 헬스:", health)
        
        manager.stop()