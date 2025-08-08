# 🛠️ POSCO 워치햄스터 v2.0 개발자 가이드

## 📖 목차
1. [개발 환경 설정](#개발-환경-설정)
2. [아키텍처 이해](#아키텍처-이해)
3. [새로운 모듈 개발](#새로운-모듈-개발)
4. [ModuleRegistry 설정](#moduleregistry-설정)
5. [워치햄스터 확장](#워치햄스터-확장)

---

## 🏗️ 개발 환경 설정

### 필수 요구사항
- Python 3.8+
- Git
- 필수 패키지: `requests`, `psutil`, `json`

### 개발 디렉토리 구조
```
📁 POSCO 워치햄스터 v2.0
├── Monitoring/Posco_News_mini/          # 기존 시스템
│   ├── monitor_WatchHamster.py          # 메인 워치햄스터
│   ├── posco_main_notifier.py           # 기존 모듈들
│   └── config.py                        # 설정 파일
├── Monitoring/Posco_News_mini_v2/       # 새로운 아키텍처
│   ├── core/                            # 핵심 컴포넌트
│   │   ├── enhanced_process_manager.py  # 프로세스 관리
│   │   ├── module_registry.py           # 모듈 레지스트리
│   │   └── notification_manager.py      # 알림 관리
│   └── modules.json                     # 모듈 설정
└── posco_control_center.sh              # 제어센터
```

### 개발 환경 초기화
```bash
# 저장소 클론
git clone <repository-url>
cd posco-watchhamster

# Python 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

---

## 🏛️ 아키텍처 이해

### 핵심 컴포넌트

#### 1. Enhanced ProcessManager
- **역할**: 하위 프로세스 생명주기 관리
- **기능**: 시작/중지/재시작, 헬스체크, 자동 복구
- **파일**: `Monitoring/Posco_News_mini_v2/core/enhanced_process_manager.py`

#### 2. ModuleRegistry  
- **역할**: 모듈 설정 및 메타데이터 관리
- **기능**: JSON 기반 설정, 의존성 관리, 동적 등록/해제
- **파일**: `Monitoring/Posco_News_mini_v2/core/module_registry.py`

#### 3. NotificationManager
- **역할**: 통합 알림 시스템
- **기능**: 다양한 알림 타입, 템플릿 시스템, 통계 추적
- **파일**: `Monitoring/Posco_News_mini_v2/core/notification_manager.py`

### 데이터 흐름
```
🔄 워치햄스터 v2.0 데이터 흐름

1. 워치햄스터 시작
   ↓
2. ModuleRegistry에서 설정 로드
   ↓  
3. ProcessManager가 모듈들 시작
   ↓
4. 헬스체크 수행 (5분 간격)
   ↓
5. 문제 발견 시 자동 복구 시도
   ↓
6. NotificationManager로 알림 전송
```-
--

## 🆕 새로운 모듈 개발

### 1. 모듈 개발 가이드라인

#### 기본 구조
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 POSCO 모듈 템플릿

모듈 설명을 여기에 작성하세요.
"""

import os
import sys
import time
import logging
from datetime import datetime

class YourNewModule:
    """새로운 모듈 클래스"""
    
    def __init__(self):
        """모듈 초기화"""
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # 설정 로드
        self.load_config()
        
        # 초기화 로그
        self.logger.info("🚀 새로운 모듈 초기화 완료")
    
    def load_config(self):
        """설정 파일 로드"""
        # config.py에서 설정 로드
        pass
    
    def start(self):
        """모듈 시작"""
        self.running = True
        self.logger.info("▶️ 모듈 시작")
        
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.logger.info("🛑 모듈 중단 요청")
        except Exception as e:
            self.logger.error(f"❌ 모듈 오류: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """모듈 중지"""
        self.running = False
        self.logger.info("⏹️ 모듈 중지")
    
    def main_loop(self):
        """메인 실행 루프"""
        while self.running:
            try:
                # 여기에 모듈의 주요 로직 구현
                self.process_data()
                
                # 대기
                time.sleep(30)  # 30초 간격
                
            except Exception as e:
                self.logger.error(f"❌ 처리 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def process_data(self):
        """데이터 처리 로직"""
        # 실제 작업 수행
        pass
    
    def health_check(self):
        """헬스체크 메서드 (워치햄스터에서 호출)"""
        try:
            # 모듈 상태 확인 로직
            return True  # 정상
        except:
            return False  # 비정상

if __name__ == "__main__":
    module = YourNewModule()
    module.start()
```

#### 필수 구현 사항
1. **생명주기 메서드**: `start()`, `stop()`, `main_loop()`
2. **헬스체크**: `health_check()` 메서드
3. **로깅**: 표준 logging 모듈 사용
4. **예외 처리**: 모든 예외 상황 처리
5. **설정 관리**: config.py 또는 별도 설정 파일 사용

### 2. 모듈 개발 예시

#### 예시: 시스템 리소스 모니터링 모듈
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시스템 리소스 모니터링 모듈

CPU, 메모리, 디스크 사용률을 모니터링하고 임계값 초과 시 알림을 전송합니다.
"""

import psutil
import time
import logging
from datetime import datetime

class SystemResourceMonitor:
    """시스템 리소스 모니터링 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # 임계값 설정
        self.cpu_threshold = 80.0      # CPU 80%
        self.memory_threshold = 85.0   # 메모리 85%
        self.disk_threshold = 90.0     # 디스크 90%
        
        # 체크 간격 (초)
        self.check_interval = 300      # 5분
        
        self.logger.info("🖥️ 시스템 리소스 모니터 초기화 완료")
    
    def start(self):
        """모니터링 시작"""
        self.running = True
        self.logger.info("▶️ 시스템 리소스 모니터링 시작")
        
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.logger.info("🛑 모니터링 중단 요청")
        finally:
            self.stop()
    
    def stop(self):
        """모니터링 중지"""
        self.running = False
        self.logger.info("⏹️ 시스템 리소스 모니터링 중지")
    
    def main_loop(self):
        """메인 모니터링 루프"""
        while self.running:
            try:
                # 시스템 리소스 체크
                self.check_system_resources()
                
                # 대기
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"❌ 리소스 체크 오류: {e}")
                time.sleep(60)
    
    def check_system_resources(self):
        """시스템 리소스 체크"""
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # 로그 기록
        self.logger.info(f"📊 리소스 상태 - CPU: {cpu_percent:.1f}%, 메모리: {memory_percent:.1f}%, 디스크: {disk_percent:.1f}%")
        
        # 임계값 체크
        alerts = []
        if cpu_percent > self.cpu_threshold:
            alerts.append(f"CPU 사용률 높음: {cpu_percent:.1f}%")
        
        if memory_percent > self.memory_threshold:
            alerts.append(f"메모리 사용률 높음: {memory_percent:.1f}%")
        
        if disk_percent > self.disk_threshold:
            alerts.append(f"디스크 사용률 높음: {disk_percent:.1f}%")
        
        # 알림 전송
        if alerts:
            self.send_alert(alerts)
    
    def send_alert(self, alerts):
        """알림 전송"""
        alert_message = "🚨 시스템 리소스 임계값 초과\n\n"
        alert_message += f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        alert_message += "⚠️ 감지된 문제:\n"
        
        for alert in alerts:
            alert_message += f"  • {alert}\n"
        
        # 여기서 실제 알림 전송 (Dooray 등)
        self.logger.warning(f"🚨 알림 전송: {alert_message}")
    
    def health_check(self):
        """헬스체크"""
        try:
            # psutil 모듈이 정상 작동하는지 확인
            psutil.cpu_percent()
            return True
        except:
            return False

if __name__ == "__main__":
    monitor = SystemResourceMonitor()
    monitor.start()
```---

#
# 📋 ModuleRegistry 설정

### 1. modules.json 구조

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2025-08-07T14:30:00",
    "description": "POSCO WatchHamster Module Registry Configuration"
  },
  "modules": {
    "your_new_module": {
      "script_path": "your_new_module.py",
      "description": "새로운 모듈 설명",
      "auto_start": true,
      "restart_on_failure": true,
      "max_restart_attempts": 3,
      "health_check_interval": 300,
      "dependencies": [],
      "environment_vars": {
        "PYTHONUNBUFFERED": "1"
      },
      "working_directory": "../Posco_News_mini",
      "timeout": 30,
      "priority": 5
    }
  }
}
```

### 2. 설정 항목 설명

#### 필수 설정
- **script_path**: 모듈 스크립트 파일 경로
- **description**: 모듈 설명
- **auto_start**: 자동 시작 여부 (true/false)

#### 프로세스 관리 설정
- **restart_on_failure**: 실패 시 재시작 여부
- **max_restart_attempts**: 최대 재시작 횟수 (기본: 3)
- **health_check_interval**: 헬스체크 간격 (초, 기본: 300)
- **timeout**: 프로세스 시작/중지 타임아웃 (초, 기본: 30)

#### 의존성 및 환경 설정
- **dependencies**: 의존하는 다른 모듈 목록
- **environment_vars**: 환경 변수 설정
- **working_directory**: 작업 디렉토리 (상대 경로)
- **priority**: 시작 우선순위 (낮을수록 먼저 시작)

### 3. 새 모듈 등록 과정

#### 단계 1: 모듈 개발 완료
```bash
# 모듈 파일 생성
touch Monitoring/Posco_News_mini/your_new_module.py

# 실행 권한 부여
chmod +x Monitoring/Posco_News_mini/your_new_module.py
```

#### 단계 2: modules.json 업데이트
```json
{
  "modules": {
    "system_resource_monitor": {
      "script_path": "system_resource_monitor.py",
      "description": "시스템 리소스 모니터링 모듈",
      "auto_start": true,
      "restart_on_failure": true,
      "max_restart_attempts": 3,
      "health_check_interval": 300,
      "dependencies": [],
      "environment_vars": {
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      },
      "working_directory": "../Posco_News_mini",
      "timeout": 30,
      "priority": 5
    }
  }
}
```

#### 단계 3: 설정 검증
```python
# 설정 검증 스크립트
import json
import os

def validate_module_config(config_path):
    """모듈 설정 검증"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for name, module in config['modules'].items():
            # 필수 필드 확인
            required_fields = ['script_path', 'description']
            for field in required_fields:
                if field not in module:
                    print(f"❌ {name}: 필수 필드 누락 - {field}")
                    return False
            
            # 스크립트 파일 존재 확인
            script_path = os.path.join('../Posco_News_mini', module['script_path'])
            if not os.path.exists(script_path):
                print(f"❌ {name}: 스크립트 파일 없음 - {script_path}")
                return False
            
            print(f"✅ {name}: 설정 검증 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 검증 실패: {e}")
        return False

# 검증 실행
if validate_module_config('Monitoring/Posco_News_mini_v2/modules.json'):
    print("🎉 모든 모듈 설정이 유효합니다!")
```

#### 단계 4: 워치햄스터 재시작
```bash
# 제어센터에서 재시작
./posco_control_center.sh
→ 메뉴 3번 (워치햄스터 재시작)
```

### 4. 의존성 관리

#### 의존성 설정 예시
```json
{
  "modules": {
    "data_collector": {
      "script_path": "data_collector.py",
      "dependencies": [],
      "priority": 1
    },
    "data_processor": {
      "script_path": "data_processor.py", 
      "dependencies": ["data_collector"],
      "priority": 2
    },
    "report_generator": {
      "script_path": "report_generator.py",
      "dependencies": ["data_collector", "data_processor"],
      "priority": 3
    }
  }
}
```

#### 시작 순서 결정
1. **의존성 없는 모듈**: 우선순위 순으로 시작
2. **의존성 있는 모듈**: 의존 모듈 시작 후 시작
3. **순환 의존성**: 감지 시 오류 발생

### 5. 동적 모듈 관리

#### 런타임 모듈 등록
```python
# 새 모듈을 런타임에 등록
from core.module_registry import ModuleRegistry, ModuleConfig

registry = ModuleRegistry('modules.json')

new_module = ModuleConfig(
    name='dynamic_module',
    script_path='dynamic_module.py',
    description='동적으로 추가된 모듈',
    auto_start=True,
    restart_on_failure=True,
    max_restart_attempts=3,
    health_check_interval=300,
    dependencies=[],
    priority=10
)

if registry.register_module('dynamic_module', new_module):
    print("✅ 모듈 등록 성공")
else:
    print("❌ 모듈 등록 실패")
```

#### 모듈 해제
```python
# 모듈 등록 해제
if registry.unregister_module('dynamic_module'):
    print("✅ 모듈 해제 성공")
else:
    print("❌ 모듈 해제 실패")
```---

##
 🔧 워치햄스터 확장

### 1. 새로운 알림 타입 추가

#### NotificationManager 확장
```python
# core/notification_manager.py에 새 메서드 추가

def send_custom_alert(self, alert_type: str, message: str, details: Dict[str, Any] = None) -> bool:
    """
    커스텀 알림 전송
    
    Args:
        alert_type (str): 알림 타입 (예: 'SECURITY', 'PERFORMANCE')
        message (str): 알림 메시지
        details (Dict[str, Any]): 추가 상세 정보
        
    Returns:
        bool: 전송 성공 여부
    """
    try:
        current_time = datetime.now()
        
        # 알림 타입별 색상 및 아이콘 설정
        type_config = {
            'SECURITY': {'color': '#dc3545', 'icon': '🔒', 'bot_name': 'POSCO 보안 알림'},
            'PERFORMANCE': {'color': '#ffc107', 'icon': '⚡', 'bot_name': 'POSCO 성능 알림'},
            'MAINTENANCE': {'color': '#6c757d', 'icon': '🔧', 'bot_name': 'POSCO 유지보수 알림'}
        }
        
        config = type_config.get(alert_type, {
            'color': '#17a2b8', 
            'icon': '📢', 
            'bot_name': 'POSCO 커스텀 알림'
        })
        
        # 메시지 구성
        alert_message = f"{config['icon']} POSCO 워치햄스터 {alert_type} 알림\n\n"
        alert_message += f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        alert_message += f"📢 메시지: {message}\n"
        
        if details:
            alert_message += f"\n📋 상세 정보:\n"
            for key, value in details.items():
                alert_message += f"  • {key}: {value}\n"
        
        return self._send_with_template(
            message=alert_message,
            bot_name=config['bot_name'],
            color=config['color'],
            notification_type=NotificationType.CUSTOM
        )
        
    except Exception as e:
        self.logger.error(f"❌ 커스텀 알림 전송 오류: {e}")
        return False
```

#### 사용 예시
```python
# 새로운 알림 타입 사용
if watchhamster.notification_manager:
    watchhamster.notification_manager.send_custom_alert(
        alert_type='SECURITY',
        message='비정상적인 로그인 시도 감지',
        details={
            'IP 주소': '192.168.1.100',
            '시도 횟수': '5회',
            '차단 상태': '자동 차단됨'
        }
    )
```

### 2. 새로운 헬스체크 로직 추가

#### ProcessManager 확장
```python
# core/enhanced_process_manager.py에 새 메서드 추가

def perform_advanced_health_check(self) -> Dict[str, Dict[str, Any]]:
    """
    고급 헬스체크 수행
    
    Returns:
        Dict[str, Dict[str, Any]]: 프로세스별 상세 헬스체크 결과
    """
    results = {}
    current_time = datetime.now()
    
    for name in self.process_info.keys():
        health_result = {
            'is_healthy': False,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_time': None,
            'error_rate': 0.0,
            'last_activity': None
        }
        
        try:
            # 기본 프로세스 상태 확인
            is_running = self.is_process_running(name)
            
            if is_running:
                # 리소스 사용률 확인
                process_info = self.get_process_info(name)
                if process_info:
                    health_result['cpu_usage'] = process_info.cpu_usage
                    health_result['memory_usage'] = process_info.memory_usage
                
                # 응답 시간 측정 (모듈별 커스텀 헬스체크)
                response_time = self._measure_response_time(name)
                health_result['response_time'] = response_time
                
                # 오류율 계산
                error_rate = self._calculate_error_rate(name)
                health_result['error_rate'] = error_rate
                
                # 종합 판단
                health_result['is_healthy'] = (
                    is_running and
                    health_result['cpu_usage'] < 80.0 and
                    health_result['memory_usage'] < 1000.0 and  # 1GB
                    (response_time is None or response_time < 5.0) and
                    error_rate < 0.1  # 10% 미만
                )
            
            results[name] = health_result
            
        except Exception as e:
            self.logger.error(f"❌ {name} 고급 헬스체크 오류: {e}")
            results[name] = health_result
    
    return results

def _measure_response_time(self, process_name: str) -> Optional[float]:
    """프로세스 응답 시간 측정"""
    try:
        # 프로세스별 커스텀 응답 시간 측정 로직
        # 예: HTTP 엔드포인트 호출, 파일 생성 시간 측정 등
        start_time = time.time()
        
        # 실제 측정 로직은 모듈별로 다르게 구현
        # 여기서는 예시로 간단한 파일 체크
        log_file = f"{process_name}.log"
        if os.path.exists(log_file):
            os.path.getmtime(log_file)
        
        return time.time() - start_time
        
    except Exception:
        return None

def _calculate_error_rate(self, process_name: str) -> float:
    """프로세스 오류율 계산"""
    try:
        # 최근 1시간 동안의 로그에서 오류율 계산
        log_file = f"{process_name}.log"
        if not os.path.exists(log_file):
            return 0.0
        
        # 간단한 오류율 계산 (실제로는 더 정교한 로직 필요)
        with open(log_file, 'r') as f:
            recent_logs = f.readlines()[-1000:]  # 최근 1000줄
        
        total_logs = len(recent_logs)
        error_logs = sum(1 for log in recent_logs if 'ERROR' in log or '❌' in log)
        
        return error_logs / total_logs if total_logs > 0 else 0.0
        
    except Exception:
        return 0.0
```

### 3. 커스텀 복구 전략 구현

#### 복구 전략 인터페이스
```python
# core/recovery_strategies.py (새 파일)

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class RecoveryStrategy(ABC):
    """복구 전략 인터페이스"""
    
    @abstractmethod
    def can_handle(self, process_name: str, error_info: Dict[str, Any]) -> bool:
        """이 전략이 해당 오류를 처리할 수 있는지 확인"""
        pass
    
    @abstractmethod
    def recover(self, process_name: str, error_info: Dict[str, Any]) -> bool:
        """복구 실행"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """전략 이름 반환"""
        pass

class MemoryLeakRecoveryStrategy(RecoveryStrategy):
    """메모리 누수 복구 전략"""
    
    def can_handle(self, process_name: str, error_info: Dict[str, Any]) -> bool:
        """메모리 사용량이 임계값을 초과했는지 확인"""
        memory_usage = error_info.get('memory_usage', 0)
        return memory_usage > 1000.0  # 1GB 초과
    
    def recover(self, process_name: str, error_info: Dict[str, Any]) -> bool:
        """메모리 정리 후 재시작"""
        try:
            # 1. 프로세스 강제 종료
            import psutil
            pid = error_info.get('pid')
            if pid:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=10)
            
            # 2. 메모리 정리
            import gc
            gc.collect()
            
            # 3. 잠시 대기 후 재시작
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ 메모리 누수 복구 실패: {e}")
            return False
    
    def get_strategy_name(self) -> str:
        return "메모리 누수 복구"

class NetworkErrorRecoveryStrategy(RecoveryStrategy):
    """네트워크 오류 복구 전략"""
    
    def can_handle(self, process_name: str, error_info: Dict[str, Any]) -> bool:
        """네트워크 관련 오류인지 확인"""
        error_message = error_info.get('error_message', '').lower()
        network_errors = ['connection refused', 'timeout', 'network unreachable']
        return any(err in error_message for err in network_errors)
    
    def recover(self, process_name: str, error_info: Dict[str, Any]) -> bool:
        """네트워크 연결 복구 시도"""
        try:
            # 1. 네트워크 연결 테스트
            import requests
            response = requests.get('https://www.google.com', timeout=5)
            
            if response.status_code != 200:
                # 네트워크 문제가 지속되면 더 긴 대기
                time.sleep(60)
            
            # 2. DNS 캐시 정리 (가능한 경우)
            # 3. 재시작
            return True
            
        except Exception as e:
            logging.error(f"❌ 네트워크 오류 복구 실패: {e}")
            return False
    
    def get_strategy_name(self) -> str:
        return "네트워크 오류 복구"
```

### 4. 모니터링 대시보드 확장

#### 웹 기반 대시보드 추가
```python
# dashboard/web_dashboard.py (새 파일)

from flask import Flask, render_template, jsonify
import json
from datetime import datetime

app = Flask(__name__)

class WatchHamsterDashboard:
    """워치햄스터 웹 대시보드"""
    
    def __init__(self, watchhamster_instance):
        self.watchhamster = watchhamster_instance
    
    @app.route('/')
    def index():
        """메인 대시보드 페이지"""
        return render_template('dashboard.html')
    
    @app.route('/api/status')
    def get_status():
        """시스템 상태 API"""
        try:
            if hasattr(self.watchhamster, 'get_all_process_status'):
                status = self.watchhamster.get_all_process_status()
            else:
                status = {'error': '상태 정보를 가져올 수 없습니다'}
            
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'status': status
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/processes')
    def get_processes():
        """프로세스 목록 API"""
        try:
            processes = []
            if hasattr(self.watchhamster, 'managed_processes'):
                for process_name in self.watchhamster.managed_processes:
                    process_status = self.watchhamster.get_process_status(process_name)
                    processes.append({
                        'name': process_name,
                        'status': process_status
                    })
            
            return jsonify({'processes': processes})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """대시보드 서버 실행"""
        app.run(host=host, port=port, debug=debug)

# 사용 예시
if __name__ == "__main__":
    from monitor_WatchHamster import PoscoMonitorWatchHamster
    
    watchhamster = PoscoMonitorWatchHamster()
    dashboard = WatchHamsterDashboard(watchhamster)
    dashboard.run(debug=True)
```

---

## 🧪 테스트 및 디버깅

### 1. 단위 테스트 작성

```python
# tests/test_new_module.py

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 테스트 대상 모듈 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Monitoring', 'Posco_News_mini'))
from your_new_module import YourNewModule

class TestYourNewModule(unittest.TestCase):
    """새 모듈 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.module = YourNewModule()
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertIsNotNone(self.module)
        self.assertFalse(self.module.running)
    
    def test_health_check(self):
        """헬스체크 테스트"""
        result = self.module.health_check()
        self.assertIsInstance(result, bool)
    
    @patch('your_new_module.time.sleep')
    def test_main_loop(self, mock_sleep):
        """메인 루프 테스트"""
        # 짧은 실행을 위해 running을 False로 설정
        self.module.running = True
        
        # 한 번만 실행되도록 설정
        def stop_after_one():
            self.module.running = False
        
        mock_sleep.side_effect = stop_after_one
        
        # 예외 없이 실행되는지 확인
        try:
            self.module.main_loop()
        except Exception as e:
            self.fail(f"main_loop raised {e} unexpectedly!")

if __name__ == '__main__':
    unittest.main()
```

### 2. 통합 테스트

```python
# tests/test_integration.py

import unittest
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Monitoring', 'Posco_News_mini'))
from monitor_WatchHamster import PoscoMonitorWatchHamster

class TestWatchHamsterIntegration(unittest.TestCase):
    """워치햄스터 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.watchhamster = PoscoMonitorWatchHamster()
    
    def test_new_architecture_initialization(self):
        """새 아키텍처 초기화 테스트"""
        # 새 아키텍처 컴포넌트들이 초기화되었는지 확인
        self.assertTrue(hasattr(self.watchhamster, 'process_manager'))
        self.assertTrue(hasattr(self.watchhamster, 'module_registry'))
        self.assertTrue(hasattr(self.watchhamster, 'notification_manager'))
    
    def test_module_registration(self):
        """모듈 등록 테스트"""
        if hasattr(self.watchhamster, 'module_registry') and self.watchhamster.module_registry:
            modules = self.watchhamster.module_registry.list_modules()
            self.assertIsInstance(modules, dict)
            self.assertGreater(len(modules), 0)
    
    def test_process_management(self):
        """프로세스 관리 테스트"""
        if hasattr(self.watchhamster, 'process_manager') and self.watchhamster.process_manager:
            # 헬스체크 테스트
            health_results = self.watchhamster.process_manager.perform_health_check()
            self.assertIsInstance(health_results, dict)

if __name__ == '__main__':
    unittest.main()
```

---

*🛠️ 이 개발자 가이드는 POSCO 워치햄스터 v2.0 (2025-08-07) 기준으로 작성되었습니다.*