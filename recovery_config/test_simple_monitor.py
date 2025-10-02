#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 워치햄스터 모니터링 시스템 테스트
"""

import subprocess
import time
import os
import sys
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class SimpleWatchHamsterMonitor:
    """간단한 워치햄스터 모니터링 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        """초기화"""
        self.config = config
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.managed_processes = config.get('managed_processes', [])
        self.process_status = {}
        self.system_start_time = datetime.now()
        
        print(f"🐹 워치햄스터 모니터링 시스템 초기화 완료")
        print(f"📋 관리 프로세스: {len(self.managed_processes)}개")
    
    def monitor_processes(self) -> Dict[str, Any]:
        """프로세스 감시"""
        results = {
            'timestamp': datetime.now(),
            'total_processes': len(self.managed_processes),
            'healthy_processes': 0,
            'failed_processes': [],
            'process_details': {}
        }
        
        print("🔍 프로세스 감시 시작")
        
        for process_name in self.managed_processes:
            # 프로세스 찾기
            found = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if process_name in cmdline or process_name in proc.info['name']:
                        results['process_details'][process_name] = {
                            'status': 'running',
                            'pid': proc.info['pid']
                        }
                        results['healthy_processes'] += 1
                        found = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not found:
                results['process_details'][process_name] = {
                    'status': 'stopped',
                    'pid': None
                }
                results['failed_processes'].append(process_name)
        
        print(f"📊 프로세스 감시 완료: {results['healthy_processes']}/{results['total_processes']} 정상")
        return results
    
    def check_git_status(self) -> Dict[str, Any]:
        """Git 상태 확인"""
        git_status = {
            'timestamp': datetime.now(),
            'status': 'unknown',
            'current_branch': None,
            'current_commit': None,
            'errors': []
        }
        
        print("📋 Git 상태 확인 시작")
        
        try:
            # 현재 브랜치 확인
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, timeout=30,
                cwd=self.script_dir
            )
            if result.returncode == 0:
                git_status['current_branch'] = result.stdout.strip()
                git_status['status'] = 'clean'
            else:
                git_status['errors'].append("브랜치 확인 실패")
                
        except Exception as e:
            git_status['errors'].append(f"Git 상태 확인 오류: {e}")
        
        print(f"📋 Git 상태: {git_status['status']}")
        return git_status
    
    def monitor_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 모니터링"""
        resource_status = {
            'timestamp': datetime.now(),
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0,
            'overall_level': 'normal'
        }
        
        print("📊 시스템 리소스 모니터링 시작")
        
        try:
            # CPU 사용률
            resource_status['cpu_percent'] = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            resource_status['memory_percent'] = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            resource_status['disk_percent'] = (disk.used / disk.total) * 100
            
            # 전체 레벨 결정
            max_usage = max(
                resource_status['cpu_percent'],
                resource_status['memory_percent'],
                resource_status['disk_percent']
            )
            
            if max_usage >= 90:
                resource_status['overall_level'] = 'critical'
            elif max_usage >= 70:
                resource_status['overall_level'] = 'warning'
            else:
                resource_status['overall_level'] = 'normal'
                
        except Exception as e:
            print(f"❌ 시스템 리소스 모니터링 오류: {e}")
            resource_status['overall_level'] = 'error'
        
        print(f"📊 시스템 리소스: CPU {resource_status['cpu_percent']:.1f}%, "
              f"메모리 {resource_status['memory_percent']:.1f}%, "
              f"디스크 {resource_status['disk_percent']:.1f}%")
        
        return resource_status
    
    def generate_status_message(self, process_results, git_status, resource_status) -> str:
        """상태 메시지 생성"""
        current_time = datetime.now()
        uptime = current_time - self.system_start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        
        message_parts = [
            "🐹 POSCO 워치햄스터 상태 보고\n",
            f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"⏱️ 가동 시간: {hours}시간 {minutes}분\n"
        ]
        
        # 프로세스 상태
        if process_results:
            healthy = process_results['healthy_processes']
            total = process_results['total_processes']
            failed = process_results['failed_processes']
            
            if failed:
                message_parts.append(f"\n🔴 프로세스 상태: {healthy}/{total} 정상\n")
                message_parts.append("❌ 문제 프로세스:\n")
                for process in failed:
                    message_parts.append(f"  • {process}\n")
            else:
                message_parts.append(f"\n🟢 프로세스 상태: {healthy}/{total} 모두 정상\n")
        
        # Git 상태
        if git_status and git_status['current_branch']:
            message_parts.append(f"\n📋 Git 브랜치: {git_status['current_branch']}\n")
        
        # 시스템 리소스
        if resource_status:
            cpu = resource_status['cpu_percent']
            memory = resource_status['memory_percent']
            disk = resource_status['disk_percent']
            level = resource_status['overall_level']
            
            level_emoji = {
                'normal': '🟢',
                'warning': '🟡',
                'critical': '🔴',
                'error': '❌'
            }.get(level, '⚪')
            
            message_parts.append(f"\n{level_emoji} 시스템 리소스: CPU {cpu:.1f}% | 메모리 {memory:.1f}% | 디스크 {disk:.1f}%\n")
        
        message_parts.append("\n🛡️ 자동 모니터링 활성화")
        
        return "".join(message_parts)

def test_simple_monitor():
    """간단한 모니터링 테스트"""
    print("🚀 간단한 워치햄스터 모니터링 테스트 시작")
    print("=" * 50)
    
    # 테스트 설정
    config = {
        'managed_processes': ['python', 'bash', 'zsh'],  # 실제 존재할 가능성이 높은 프로세스들
        'process_check_interval': 60
    }
    
    # 모니터 생성
    monitor = SimpleWatchHamsterMonitor(config)
    
    # 프로세스 모니터링 테스트
    print("\n1. 프로세스 모니터링 테스트")
    process_results = monitor.monitor_processes()
    
    # Git 상태 확인 테스트
    print("\n2. Git 상태 확인 테스트")
    git_status = monitor.check_git_status()
    
    # 시스템 리소스 모니터링 테스트
    print("\n3. 시스템 리소스 모니터링 테스트")
    resource_status = monitor.monitor_system_resources()
    
    # 상태 메시지 생성 테스트
    print("\n4. 상태 메시지 생성 테스트")
    status_message = monitor.generate_status_message(process_results, git_status, resource_status)
    
    print("\n📝 생성된 상태 메시지:")
    print("-" * 50)
    print(status_message)
    print("-" * 50)
    
    print("\n✅ 간단한 워치햄스터 모니터링 테스트 완료")
    
    # 결과 요약
    print(f"\n📊 테스트 결과 요약:")
    print(f"  • 관리 프로세스: {len(config['managed_processes'])}개")
    print(f"  • 정상 프로세스: {process_results['healthy_processes']}개")
    print(f"  • Git 상태: {git_status['status']}")
    print(f"  • 시스템 리소스 레벨: {resource_status['overall_level']}")
    print(f"  • 메시지 길이: {len(status_message)} 문자")

if __name__ == "__main__":
    test_simple_monitor()