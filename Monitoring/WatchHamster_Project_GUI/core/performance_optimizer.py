#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer - GUI 성능 최적화 시스템
멀티스레딩 및 비동기 처리를 통한 GUI 응답성 개선

주요 기능:
- 🚀 GUI 응답성 개선 (멀티스레딩 적용)
- 📊 대용량 로그 표시 성능 최적화
- ⚡ 실시간 모니터링 데이터 업데이트 최적화
- 🔄 백그라운드 작업 스케줄링

Requirements: 6.4, 5.1, 5.2 구현
"""

import threading
import queue
import time
import sys
import os
import gc
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref
import gc


class PerformanceOptimizer:
    """GUI 성능 최적화 관리자"""
    
    def __init__(self, max_workers: int = 4):
        """성능 최적화 시스템 초기화"""
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # 작업 큐들
        self.ui_update_queue = queue.Queue()
        self.background_task_queue = queue.Queue()
        self.log_processing_queue = queue.Queue()
        
        # 스레드 관리
        self.worker_threads = {}
        self.running = False
        
        # 성능 메트릭
        self.performance_metrics = {
            'ui_updates_per_second': 0,
            'background_tasks_completed': 0,
            'log_processing_time': 0,
            'memory_usage_mb': 0,
            'thread_count': 0
        }
        
        # 캐시 관리
        self.data_cache = {}
        self.cache_timestamps = {}
        self.cache_max_age = 30  # 30초
        self.cache_max_size = 1000
        
        # 로그 처리 최적화
        self.log_chunk_size = 1000  # 한 번에 처리할 로그 라인 수
        self.log_cache = {}
        self.log_file_positions = {}
        
        print("⚡ 성능 최적화 시스템 초기화 완료")
    
    def start_backend_only(self):
        """백엔드만 시작 (헤드리스 모드)"""
        return self.start()
    
    def start(self):
        """성능 최적화 시스템 시작 (완전 구현)"""
        try:
            if self.running:
                print("⚠️ 성능 최적화 시스템이 이미 실행 중입니다")
                return
            
            print("🚀 성능 최적화 시스템 시작 중...")
            self.running = True
            self.start_time = time.time()
            
            # 시스템 리소스 초기 상태 확인
            initial_memory = psutil.virtual_memory().percent
            initial_cpu = psutil.cpu_percent()
            print(f"📊 시작 시 시스템 상태 - 메모리: {initial_memory:.1f}%, CPU: {initial_cpu:.1f}%")
            
            # UI 업데이트 워커 시작
            print("🖥️ UI 업데이트 워커 시작 중...")
            self.worker_threads['ui_updater'] = threading.Thread(
                target=self._ui_update_worker, daemon=True, name="UIUpdater"
            )
            self.worker_threads['ui_updater'].start()
            
            # 백그라운드 작업 워커 시작
            print("🔄 백그라운드 작업 워커 시작 중...")
            self.worker_threads['background_worker'] = threading.Thread(
                target=self._background_task_worker, daemon=True, name="BackgroundWorker"
            )
            self.worker_threads['background_worker'].start()
            
            # 로그 처리 워커 시작
            print("📝 로그 처리 워커 시작 중...")
            self.worker_threads['log_processing_worker'] = threading.Thread(
                target=self._log_processing_worker, daemon=True, name="LogProcessor"
            )
            self.worker_threads['log_processing_worker'].start()
            
            # 성능 모니터링 워커 시작
            print("📈 성능 모니터링 워커 시작 중...")
            self.worker_threads['performance_monitor'] = threading.Thread(
                target=self._performance_monitor_worker, daemon=True, name="PerformanceMonitor"
            )
            self.worker_threads['performance_monitor'].start()
            
            # 메모리 정리 워커 시작
            print("🧹 메모리 정리 워커 시작 중...")
            self.worker_threads['memory_cleaner'] = threading.Thread(
                target=self._memory_cleanup_worker, daemon=True, name="MemoryCleaner"
            )
            self.worker_threads['memory_cleaner'].start()
            
            # 워커 스레드 시작 확인
            time.sleep(0.1)  # 스레드 시작 대기
            active_workers = [name for name, thread in self.worker_threads.items() if thread.is_alive()]
            print(f"✅ 활성 워커: {len(active_workers)}/5 - {', '.join(active_workers)}")
            
            print("🚀 성능 최적화 워커들 시작됨")
            
        except Exception as e:
            print(f"❌ 성능 최적화 시스템 시작 실패: {e}")
            self.running = False
            raise
    
    def stop(self):
        """성능 최적화 시스템 중지 (완전 구현)"""
        try:
            if not self.running:
                print("⚠️ 성능 최적화 시스템이 이미 중지되어 있습니다")
                return
            
            print("🛑 성능 최적화 시스템 중지 중...")
            self.running = False
            
            # 실행 시간 계산
            if hasattr(self, 'start_time'):
                runtime = time.time() - self.start_time
                print(f"⏱️ 총 실행 시간: {runtime:.1f}초")
            
            # 큐 정리
            print("🧹 큐 정리 중...")
            try:
                while not self.ui_update_queue.empty():
                    self.ui_update_queue.get_nowait()
            except queue.Empty:
                pass
            
            try:
                while not self.background_task_queue.empty():
                    self.background_task_queue.get_nowait()
            except queue.Empty:
                pass
            
            # 스레드 풀 종료
            print("🔄 스레드 풀 종료 중...")
            self.thread_pool.shutdown(wait=True)
            print("✅ 스레드 풀 종료 완료")
            
            # 워커 스레드들 종료 대기
            print("⏹️ 워커 스레드들 종료 중...")
            for name, thread in self.worker_threads.items():
                if thread.is_alive():
                    print(f"⏳ {name} 워커 종료 대기 중...")
                    thread.join(timeout=3)
                    if thread.is_alive():
                        print(f"⚠️ {name} 워커 강제 종료 (타임아웃)")
                    else:
                        print(f"⏹️ {name} 워커 종료됨")
                else:
                    print(f"✅ {name} 워커 이미 종료됨")
            
            # 최종 시스템 상태 확인
            final_memory = psutil.virtual_memory().percent
            final_cpu = psutil.cpu_percent()
            print(f"📊 종료 시 시스템 상태 - 메모리: {final_memory:.1f}%, CPU: {final_cpu:.1f}%")
            
            # 캐시 정리
            cache_size = len(self.data_cache)
            if cache_size > 0:
                print(f"🧹 캐시 정리: {cache_size}개 항목")
                self.data_cache.clear()
                self.cache_timestamps.clear()
            
            print("🏁 성능 최적화 시스템 종료됨")
            
        except Exception as e:
            print(f"❌ 성능 최적화 시스템 종료 중 오류: {e}")
            # 강제 종료
            self.running = False
    
    def schedule_ui_update(self, callback: Callable, *args, **kwargs):
        """UI 업데이트 작업 스케줄링 (메인 스레드에서 실행)"""
        task = {
            'type': 'ui_update',
            'callback': callback,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time()
        }
        
        try:
            self.ui_update_queue.put_nowait(task)
        except queue.Full:
            print("⚠️ UI 업데이트 큐가 가득참")
    
    def schedule_background_task(self, callback: Callable, *args, **kwargs) -> threading.Thread:
        """백그라운드 작업 스케줄링"""
        task = {
            'type': 'background_task',
            'callback': callback,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time()
        }
        
        try:
            self.background_task_queue.put_nowait(task)
        except queue.Full:
            print("⚠️ 백그라운드 작업 큐가 가득참")
        
        # 즉시 실행을 위한 스레드 반환
        thread = threading.Thread(target=callback, args=args, kwargs=kwargs, daemon=True)
        return thread
    
    def schedule_log_processing(self, log_file_path: str, callback: Callable, chunk_size: Optional[int] = None):
        """로그 처리 작업 스케줄링"""
        task = {
            'type': 'log_processing',
            'file_path': log_file_path,
            'callback': callback,
            'chunk_size': chunk_size or self.log_chunk_size,
            'timestamp': time.time()
        }
        
        try:
            self.log_processing_queue.put_nowait(task)
        except queue.Full:
            print("⚠️ 로그 처리 큐가 가득참")
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """캐시된 데이터 조회 (완전 구현)"""
        try:
            if key not in self.data_cache:
                print(f"🔍 캐시 미스: {key}")
                return None
            
            # 캐시 만료 확인
            if key in self.cache_timestamps:
                age = time.time() - self.cache_timestamps[key]
                if age > self.cache_max_age:
                    print(f"⏰ 캐시 만료: {key} (나이: {age:.1f}초)")
                    self._remove_from_cache(key)
                    return None
            
            print(f"✅ 캐시 히트: {key}")
            return self.data_cache[key]
            
        except Exception as e:
            print(f"❌ 캐시 조회 오류: {key} - {e}")
            return None
    
    def set_cached_data(self, key: str, data: Any):
        """데이터 캐시 저장 (완전 구현)"""
        try:
            # 캐시 크기 제한 확인
            if len(self.data_cache) >= self.cache_max_size:
                print(f"🧹 캐시 크기 제한 도달, 정리 실행 (현재: {len(self.data_cache)})")
                self._cleanup_old_cache_entries()
            
            # 데이터 크기 확인 (메모리 효율성)
            data_size = sys.getsizeof(data)
            if data_size > 10 * 1024 * 1024:  # 10MB 초과
                print(f"⚠️ 대용량 데이터 캐시: {key} ({data_size / 1024 / 1024:.1f}MB)")
            
            self.data_cache[key] = data
            self.cache_timestamps[key] = time.time()
            print(f"💾 캐시 저장: {key}")
            
        except Exception as e:
            print(f"❌ 캐시 저장 오류: {key} - {e}")
    
    def process_large_log_file(self, file_path: str, callback: Callable, 
                              start_line: int = 0, max_lines: int = 10000) -> List[str]:
        """대용량 로그 파일 청크 단위 처리"""
        if not os.path.exists(file_path):
            return []
        
        # 캐시 키 생성
        cache_key = f"log_{file_path}_{start_line}_{max_lines}"
        
        # 캐시된 데이터 확인
        cached_result = self.get_cached_data(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            lines = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 시작 위치로 이동
                for _ in range(start_line):
                    f.readline()
                
                # 청크 단위로 읽기
                for i in range(max_lines):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line.rstrip('\n\r'))
            
            # 결과 캐시 저장
            self.set_cached_data(cache_key, lines)
            
            return lines
            
        except Exception as e:
            print(f"❌ 로그 파일 처리 오류: {e}")
            return []
    
    def get_log_file_tail(self, file_path: str, num_lines: int = 100) -> List[str]:
        """로그 파일 끝부분 효율적 읽기"""
        if not os.path.exists(file_path):
            return []
        
        cache_key = f"log_tail_{file_path}_{num_lines}"
        
        # 파일 수정 시간 확인
        try:
            file_mtime = os.path.getmtime(file_path)
            if cache_key in self.cache_timestamps:
                if file_mtime <= self.cache_timestamps[cache_key]:
                    cached_result = self.get_cached_data(cache_key)
                    if cached_result is not None:
                        return cached_result
        except OSError:
            pass
        
        try:
            lines = []
            with open(file_path, 'rb') as f:
                # 파일 끝에서부터 읽기
                f.seek(0, 2)  # 파일 끝으로 이동
                file_size = f.tell()
                
                if file_size == 0:
                    return []
                
                # 청크 단위로 역방향 읽기
                chunk_size = min(8192, file_size)
                lines_found = 0
                pos = file_size
                
                while pos > 0 and lines_found < num_lines:
                    # 읽을 위치 계산
                    read_size = min(chunk_size, pos)
                    pos -= read_size
                    
                    f.seek(pos)
                    chunk = f.read(read_size).decode('utf-8', errors='ignore')
                    
                    # 라인 분할
                    chunk_lines = chunk.split('\n')
                    
                    # 첫 번째 청크가 아니면 첫 라인은 불완전할 수 있음
                    if pos > 0 and chunk_lines:
                        chunk_lines = chunk_lines[1:]
                    
                    # 라인들을 역순으로 추가
                    for line in reversed(chunk_lines):
                        if line.strip():  # 빈 라인 제외
                            lines.insert(0, line)
                            lines_found += 1
                            if lines_found >= num_lines:
                                break
                
                # 결과 캐시 저장
                self.set_cached_data(cache_key, lines)
                self.cache_timestamps[cache_key] = file_mtime
                
                return lines
                
        except Exception as e:
            print(f"❌ 로그 tail 읽기 오류: {e}")
            return []
    
    def optimize_json_loading(self, file_path: str) -> Optional[Dict]:
        """JSON 파일 최적화 로딩"""
        if not os.path.exists(file_path):
            return None
        
        cache_key = f"json_{file_path}"
        
        # 파일 수정 시간 확인
        try:
            file_mtime = os.path.getmtime(file_path)
            if cache_key in self.cache_timestamps:
                if file_mtime <= self.cache_timestamps[cache_key]:
                    cached_result = self.get_cached_data(cache_key)
                    if cached_result is not None:
                        return cached_result
        except OSError:
            pass
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 결과 캐시 저장
            self.set_cached_data(cache_key, data)
            self.cache_timestamps[cache_key] = file_mtime
            
            return data
            
        except Exception as e:
            print(f"❌ JSON 로딩 오류: {e}")
            return None
    
    def batch_ui_updates(self, updates: List[Callable], delay: float = 0.1):
        """UI 업데이트 배치 처리"""
        def batch_executor():
            time.sleep(delay)  # 짧은 지연으로 업데이트 배치화
            for update_func in updates:
                try:
                    update_func()
                except Exception as e:
                    print(f"❌ 배치 UI 업데이트 오류: {e}")
        
        self.schedule_background_task(batch_executor)
    
    def debounce_function(self, func: Callable, delay: float = 0.5) -> Callable:
        """함수 디바운싱 (연속 호출 방지)"""
        last_call_time = [0]
        
        def debounced_func(*args, **kwargs):
            current_time = time.time()
            if current_time - last_call_time[0] >= delay:
                last_call_time[0] = current_time
                return func(*args, **kwargs)
        
        return debounced_func
    
    def throttle_function(self, func: Callable, interval: float = 1.0) -> Callable:
        """함수 스로틀링 (호출 빈도 제한)"""
        last_call_time = [0]
        
        def throttled_func(*args, **kwargs):
            current_time = time.time()
            if current_time - last_call_time[0] >= interval:
                last_call_time[0] = current_time
                return func(*args, **kwargs)
        
        return throttled_func
    
    def trigger_memory_cleanup(self):
        """메모리 정리 트리거 (외부 호출용)"""
        try:
            import gc
            collected = gc.collect()
            print(f"🧹 메모리 정리: {collected}개 객체 해제됨")
            
            # 캐시 정리
            self._cleanup_old_cache_entries()
            
            # 정리 후 메모리 사용량 재확인
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"📊 정리 후 메모리 사용량: {memory_mb:.1f}MB")
            
            return True
            
        except Exception as e:
            print(f"❌ 메모리 정리 오류: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        # 메모리 사용량 업데이트
        import psutil
        process = psutil.Process()
        self.performance_metrics['memory_usage_mb'] = process.memory_info().rss / 1024 / 1024
        self.performance_metrics['thread_count'] = threading.active_count()
        
        return self.performance_metrics.copy()
    
    def _ui_update_worker(self):
        """UI 업데이트 워커 스레드"""
        updates_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                # 큐에서 작업 가져오기 (타임아웃 설정)
                task = self.ui_update_queue.get(timeout=1.0)
                
                # UI 업데이트 실행
                callback = task['callback']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                
                callback(*args, **kwargs)
                updates_count += 1
                
                # 성능 메트릭 업데이트
                elapsed = time.time() - start_time
                if elapsed >= 1.0:
                    self.performance_metrics['ui_updates_per_second'] = updates_count / elapsed
                    updates_count = 0
                    start_time = time.time()
                
                self.ui_update_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ UI 업데이트 워커 오류: {e}")
    
    def _background_task_worker(self):
        """백그라운드 작업 워커 스레드"""
        while self.running:
            try:
                # 큐에서 작업 가져오기
                task = self.background_task_queue.get(timeout=1.0)
                
                # 백그라운드 작업 실행
                callback = task['callback']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                
                callback(*args, **kwargs)
                self.performance_metrics['background_tasks_completed'] += 1
                
                self.background_task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 백그라운드 작업 워커 오류: {e}")
    
    def _log_processing_worker(self):
        """로그 처리 워커 스레드"""
        while self.running:
            try:
                # 큐에서 작업 가져오기
                task = self.log_processing_queue.get(timeout=1.0)
                
                start_time = time.time()
                
                # 로그 처리 실행
                file_path = task['file_path']
                callback = task['callback']
                chunk_size = task['chunk_size']
                
                # 청크 단위로 로그 처리
                lines = self.process_large_log_file(file_path, callback, max_lines=chunk_size)
                callback(lines)
                
                # 처리 시간 기록
                processing_time = time.time() - start_time
                self.performance_metrics['log_processing_time'] = processing_time
                
                self.log_processing_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 로그 처리 워커 오류: {e}")
    
    def _performance_monitor_worker(self):
        """성능 모니터링 워커 스레드"""
        while self.running:
            try:
                # 5초마다 성능 메트릭 업데이트
                time.sleep(5)
                
                # 메트릭 수집
                metrics = self.get_performance_metrics()
                
                # 성능 경고 확인
                if metrics['memory_usage_mb'] > 500:  # 500MB 초과
                    print(f"⚠️ 높은 메모리 사용량: {metrics['memory_usage_mb']:.1f}MB")
                
                if metrics['thread_count'] > 20:  # 스레드 20개 초과
                    print(f"⚠️ 높은 스레드 수: {metrics['thread_count']}")
                
            except Exception as e:
                print(f"❌ 성능 모니터링 오류: {e}")
    
    def _memory_cleanup_worker(self):
        """메모리 정리 워커 스레드"""
        while self.running:
            try:
                # 30초마다 메모리 정리
                time.sleep(30)
                
                # 캐시 정리
                self._cleanup_old_cache_entries()
                
                # 가비지 컬렉션 실행
                collected = gc.collect()
                if collected > 0:
                    print(f"🧹 가비지 컬렉션: {collected}개 객체 정리됨")
                
            except Exception as e:
                print(f"❌ 메모리 정리 오류: {e}")
    
    def _cleanup_old_cache_entries(self):
        """오래된 캐시 항목 정리"""
        current_time = time.time()
        keys_to_remove = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.cache_max_age:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._remove_from_cache(key)
        
        # 캐시 크기 제한
        if len(self.data_cache) > self.cache_max_size:
            # 가장 오래된 항목들 제거
            sorted_items = sorted(self.cache_timestamps.items(), key=lambda x: x[1])
            remove_count = len(self.data_cache) - self.cache_max_size + 100  # 여유분 확보
            
            for key, _ in sorted_items[:remove_count]:
                self._remove_from_cache(key)
    
    def _remove_from_cache(self, key: str):
        """캐시에서 항목 제거"""
        if key in self.data_cache:
            del self.data_cache[key]
        if key in self.cache_timestamps:
            del self.cache_timestamps[key]


# 전역 성능 최적화 인스턴스
_performance_optimizer = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """전역 성능 최적화 인스턴스 반환"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
        _performance_optimizer.start()
    return _performance_optimizer


def create_performance_optimizer(max_workers: int = 4) -> PerformanceOptimizer:
    """성능 최적화 시스템 생성"""
    optimizer = PerformanceOptimizer(max_workers=max_workers)
    optimizer.start()
    return optimizer


if __name__ == "__main__":
    # 테스트 코드
    optimizer = create_performance_optimizer()
    
    def test_callback(message):
        print(f"테스트 콜백: {message}")
    
    # 테스트 작업들
    optimizer.schedule_ui_update(test_callback, "UI 업데이트 테스트")
    optimizer.schedule_background_task(test_callback, "백그라운드 작업 테스트")
    
    # 성능 메트릭 출력
    time.sleep(2)
    metrics = optimizer.get_performance_metrics()
    print("성능 메트릭:", metrics)
    
    optimizer.stop()