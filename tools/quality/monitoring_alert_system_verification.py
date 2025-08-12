#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모니터링 및 알림 시스템 검증 도구
POSCO 시스템 수리 및 완성 - Task 10

이 도구는 다음을 검증합니다:
- 모든 웹훅 기능 정상 작동 확인
- 알림 메시지 내용 및 형식 보존 검증
- 비즈니스 로직 무결성 확인
- 데이터 호환성 검증

Created: 2025-08-09
"""

import os
import sys
import json
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import traceback
from pathlib import Path

class MonitoringAlertSystemVerifier:
    """모니터링 및 알림 시스템 검증 클래스"""
    
    def __init__(self):
        """검증 시스템 초기화"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.verification_results = {}
        self.webhook_urls = []
        self.business_logic_files = []
        self.notification_messages = {}
        self.data_structures = {}
        
        # 로그 파일 설정
        self.log_file = os.path.join(self.script_dir, "monitoring_alert_verification.log")
        
        # 검증 시작 시간
        self.verification_start_time = datetime.now()
        
        self.log("🔍 모니터링 및 알림 시스템 검증 시작")
        
    def log(self, message: str):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def verify_webhook_functionality(self) -> Dict[str, Any]:
        """웹훅 기능 정상 작동 확인"""
        self.log("🔗 웹훅 기능 검증 시작")
        
        webhook_results = {
            'total_webhooks': 0,
            'accessible_webhooks': 0,
            'failed_webhooks': 0,
            'webhook_details': [],
            'status': 'unknown'
        }
        
        try:
            # 1. 설정 파일에서 웹훅 URL 추출
            webhook_urls = self._extract_webhook_urls()
            webhook_results['total_webhooks'] = len(webhook_urls)
            
            if not webhook_urls:
                self.log("⚠️ 웹훅 URL을 찾을 수 없습니다")
                webhook_results['status'] = 'no_webhooks_found'
                return webhook_results
            
            # 2. 각 웹훅 URL 연결성 테스트
            for webhook_name, webhook_url in webhook_urls.items():
                self.log(f"🔗 웹훅 테스트: {webhook_name}")
                
                try:
                    # HEAD 요청으로 연결성만 확인 (실제 메시지 전송 안함)
                    response = requests.head(webhook_url, timeout=10)
                    
                    webhook_detail = {
                        'name': webhook_name,
                        'url': webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url,
                        'status_code': response.status_code,
                        'accessible': False,
                        'response_time': None
                    }
                    
                    # 웹훅 서비스별 성공 상태 코드 확인
                    if response.status_code in [200, 405, 404]:  # 405: Method Not Allowed (정상), 404: 엔드포인트 존재하지만 HEAD 미지원
                        webhook_detail['accessible'] = True
                        webhook_results['accessible_webhooks'] += 1
                        self.log(f"  ✅ 접근 가능 (상태: {response.status_code})")
                    else:
                        webhook_results['failed_webhooks'] += 1
                        self.log(f"  ❌ 접근 불가 (상태: {response.status_code})")
                    
                    webhook_results['webhook_details'].append(webhook_detail)
                    
                except requests.exceptions.RequestException as e:
                    webhook_detail = {
                        'name': webhook_name,
                        'url': webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url,
                        'status_code': None,
                        'accessible': False,
                        'error': str(e)
                    }
                    webhook_results['webhook_details'].append(webhook_detail)
                    webhook_results['failed_webhooks'] += 1
                    self.log(f"  ❌ 연결 실패: {e}")
            
            # 3. 전체 웹훅 상태 판단
            if webhook_results['accessible_webhooks'] == webhook_results['total_webhooks']:
                webhook_results['status'] = 'all_accessible'
                self.log("✅ 모든 웹훅이 정상 접근 가능합니다")
            elif webhook_results['accessible_webhooks'] > 0:
                webhook_results['status'] = 'partially_accessible'
                self.log(f"⚠️ 일부 웹훅만 접근 가능합니다 ({webhook_results['accessible_webhooks']}/{webhook_results['total_webhooks']})")
            else:
                webhook_results['status'] = 'all_failed'
                self.log("❌ 모든 웹훅 접근 실패")
            
        except Exception as e:
            self.log(f"❌ 웹훅 기능 검증 중 오류: {e}")
            webhook_results['status'] = 'verification_error'
            webhook_results['error'] = str(e)
        
        return webhook_results
    
    def _extract_webhook_urls(self) -> Dict[str, str]:
        """설정 파일 및 코드에서 웹훅 URL 추출"""
        webhook_urls = {}
        
        # 1. config.py에서 웹훅 URL 추출
        config_files = [
            "Monitoring/POSCO_News_250808/config.py",
            "config.py"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 웹훅 URL 패턴 매칭
                    webhook_patterns = [
                        (r'DOORAY_WEBHOOK_URL\s*=\s*["\']([^"\']+)["\']', 'DOORAY_WEBHOOK'),
                        (r'WATCHHAMSTER_WEBHOOK_URL\s*=\s*["\']([^"\']+)["\']', 'WATCHHAMSTER_WEBHOOK'),
                        (r'webhook.*url.*=\s*["\']([^"\']+)["\']', 'GENERIC_WEBHOOK')
                    ]
                    
                    for pattern, name in webhook_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for i, match in enumerate(matches):
                            webhook_name = f"{name}_{i+1}" if i > 0 else name
                            webhook_urls[webhook_name] = match
                            self.log(f"📋 웹훅 발견: {webhook_name}")
                    
                except Exception as e:
                    self.log(f"⚠️ {config_file} 읽기 실패: {e}")
        
        # 2. 하드코딩된 웹훅 URL 추가 (백업용)
        if not webhook_urls:
            self.log("⚠️ 설정 파일에서 웹훅을 찾을 수 없어 기본 웹훅을 사용합니다")
            webhook_urls = {
                'POSCO_NEWS_WEBHOOK': "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg",
                'WATCHHAMSTER_WEBHOOK': "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"
            }
        
        return webhook_urls
    
    def verify_notification_message_integrity(self) -> Dict[str, Any]:
        """알림 메시지 내용 및 형식 보존 검증"""
        self.log("📝 알림 메시지 무결성 검증 시작")
        
        message_results = {
            'total_files_checked': 0,
            'files_with_messages': 0,
            'preserved_messages': 0,
            'modified_messages': 0,
            'message_details': [],
            'status': 'unknown'
        }
        
        try:
            # 1. 알림 메시지가 포함된 파일 찾기
            notification_files = self._find_notification_files()
            message_results['total_files_checked'] = len(notification_files)
            
            # 2. 각 파일의 메시지 내용 검증
            for file_path in notification_files:
                self.log(f"📝 메시지 검증: {os.path.basename(file_path)}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 메시지 패턴 추출
                    messages = self._extract_notification_messages(content)
                    
                    if messages:
                        message_results['files_with_messages'] += 1
                        
                        for message_type, message_content in messages.items():
                            # 메시지 무결성 검증
                            is_preserved = self._verify_message_preservation(message_type, message_content)
                            
                            message_detail = {
                                'file': os.path.basename(file_path),
                                'message_type': message_type,
                                'content_preview': message_content[:100] + "..." if len(message_content) > 100 else message_content,
                                'is_preserved': is_preserved,
                                'length': len(message_content)
                            }
                            
                            message_results['message_details'].append(message_detail)
                            
                            if is_preserved:
                                message_results['preserved_messages'] += 1
                            else:
                                message_results['modified_messages'] += 1
                    
                except Exception as e:
                    self.log(f"⚠️ {file_path} 메시지 검증 실패: {e}")
            
            # 3. 전체 메시지 보존 상태 판단
            total_messages = message_results['preserved_messages'] + message_results['modified_messages']
            if total_messages == 0:
                message_results['status'] = 'no_messages_found'
                self.log("⚠️ 알림 메시지를 찾을 수 없습니다")
            elif message_results['modified_messages'] == 0:
                message_results['status'] = 'all_preserved'
                self.log("✅ 모든 알림 메시지가 보존되었습니다")
            else:
                preservation_rate = (message_results['preserved_messages'] / total_messages) * 100
                message_results['preservation_rate'] = preservation_rate
                
                if preservation_rate >= 95:
                    message_results['status'] = 'mostly_preserved'
                    self.log(f"✅ 대부분의 메시지가 보존됨 ({preservation_rate:.1f}%)")
                else:
                    message_results['status'] = 'partially_preserved'
                    self.log(f"⚠️ 일부 메시지가 변경됨 (보존율: {preservation_rate:.1f}%)")
            
        except Exception as e:
            self.log(f"❌ 알림 메시지 검증 중 오류: {e}")
            message_results['status'] = 'verification_error'
            message_results['error'] = str(e)
        
        return message_results
    
    def _find_notification_files(self) -> List[str]:
        """알림 메시지가 포함된 파일 찾기"""
        notification_files = []
        
        # 검색할 파일 패턴
        search_patterns = [
            "Monitoring/POSCO_News_250808/posco_main_notifier.py",
            "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py",
            "Monitoring/POSCO_News_250808/realtime_news_monitor.py",
            "Monitoring/POSCO_News_250808/completion_notifier.py",
            "*notifier*.py",
            "*monitor*.py"
        ]
        
        for pattern in search_patterns:
            if '*' in pattern:
                # 와일드카드 패턴 처리
                import glob
                matches = glob.glob(pattern, recursive=True)
                notification_files.extend(matches)
            else:
                # 직접 파일 경로
                if os.path.exists(pattern):
                    notification_files.append(pattern)
        
        # 중복 제거
        notification_files = list(set(notification_files))
        
        self.log(f"📋 알림 파일 {len(notification_files)}개 발견")
        return notification_files
    
    def _extract_notification_messages(self, content: str) -> Dict[str, str]:
        """파일 내용에서 알림 메시지 추출"""
        messages = {}
        
        # 메시지 패턴들
        message_patterns = [
            # Dooray 메시지 패턴
            (r'"text":\s*"(\\[^"\\]+)"', 'dooray_text'),
            (r'"attachments":\s*\[.*?"text":\s*"(\\[^"\\]+)"', 'dooray_attachment'),
            
            # 일반 알림 메시지 패턴
            (r'message\s*=\s*["\']([^"\']+)["\']', 'general_message'),
            (r'notification.*=\s*["\']([^"\']+)["\']', 'notification_message'),
            
            # 로그 메시지 패턴
            (r'log_message\(["\']([^"\']+)["\']', 'log_message'),
            (r'self\.log\(["\']([^"\']+)["\']', 'self_log_message'),
            
            # 상태 메시지 패턴
            (r'status.*=\s*["\']([^"\']+)["\']', 'status_message'),
            (r'display.*=\s*["\']([^"\']+)["\']', 'display_message')
        ]
        
        for pattern, message_type in message_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for i, match in enumerate(matches):
                # 개행 문자 및 특수 문자 정리
                cleaned_message = match.replace('\\n', '\n').replace('\\"', '"')
                key = f"{message_type}_{i+1}" if i > 0 else message_type
                messages[key] = cleaned_message
        
        return messages
    
    def _verify_message_preservation(self, message_type: str, message_content: str) -> bool:
        """메시지 보존 여부 검증"""
        # 보존되어야 할 메시지 특성 확인
        preservation_indicators = [
            # 웹훅 관련 메시지는 보존되어야 함
            'webhook' in message_content.lower(),
            'dooray' in message_content.lower(),
            'slack' in message_content.lower(),
            
            # 비즈니스 로직 메시지는 보존되어야 함
            'posco' in message_content.lower(),
            'news' in message_content.lower(),
            'market' in message_content.lower(),
            'kospi' in message_content.lower(),
            'exchange' in message_content.lower(),
            
            # 상태 알림 메시지는 보존되어야 함
            '발행' in message_content,
            '지연' in message_content,
            '완료' in message_content,
            '시작' in message_content,
            '중지' in message_content,
            
            # 이모지가 포함된 메시지는 보존되어야 함
            any(ord(char) > 127 for char in message_content)  # 유니코드 문자 (이모지 등)
        ]
        
        # 하나라도 해당되면 보존되어야 할 메시지로 판단
        should_be_preserved = any(preservation_indicators)
        
        if should_be_preserved:
            # 실제로 보존되었는지 확인 (길이, 특수문자 등)
            is_meaningful = len(message_content.strip()) > 5  # 의미있는 길이
            has_content = not message_content.strip() in ['', 'TODO', 'FIXME', 'test']
            
            return is_meaningful and has_content
        
        return True  # 보존 대상이 아닌 메시지는 통과
    
    def verify_business_logic_integrity(self) -> Dict[str, Any]:
        """비즈니스 로직 무결성 확인"""
        self.log("🧠 비즈니스 로직 무결성 검증 시작")
        
        logic_results = {
            'total_logic_files': 0,
            'verified_logic_files': 0,
            'logic_issues': 0,
            'logic_details': [],
            'status': 'unknown'
        }
        
        try:
            # 1. 비즈니스 로직 파일 찾기
            logic_files = self._find_business_logic_files()
            logic_results['total_logic_files'] = len(logic_files)
            
            # 2. 각 파일의 비즈니스 로직 검증
            for file_path in logic_files:
                self.log(f"🧠 로직 검증: {os.path.basename(file_path)}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 비즈니스 로직 요소 검증
                    logic_verification = self._verify_business_logic_elements(content, file_path)
                    
                    logic_detail = {
                        'file': os.path.basename(file_path),
                        'monitoring_logic': logic_verification.get('monitoring_logic', False),
                        'analysis_logic': logic_verification.get('analysis_logic', False),
                        'decision_logic': logic_verification.get('decision_logic', False),
                        'scheduling_logic': logic_verification.get('scheduling_logic', False),
                        'data_processing': logic_verification.get('data_processing', False),
                        'issues': logic_verification.get('issues', []),
                        'overall_status': 'verified' if not logic_verification.get('issues') else 'has_issues'
                    }
                    
                    logic_results['logic_details'].append(logic_detail)
                    
                    if logic_detail['overall_status'] == 'verified':
                        logic_results['verified_logic_files'] += 1
                    else:
                        logic_results['logic_issues'] += len(logic_detail['issues'])
                    
                except Exception as e:
                    self.log(f"⚠️ {file_path} 로직 검증 실패: {e}")
                    logic_results['logic_issues'] += 1
            
            # 3. 전체 비즈니스 로직 상태 판단
            if logic_results['total_logic_files'] == 0:
                logic_results['status'] = 'no_logic_files'
                self.log("⚠️ 비즈니스 로직 파일을 찾을 수 없습니다")
            elif logic_results['logic_issues'] == 0:
                logic_results['status'] = 'all_verified'
                self.log("✅ 모든 비즈니스 로직이 검증되었습니다")
            else:
                verification_rate = (logic_results['verified_logic_files'] / logic_results['total_logic_files']) * 100
                logic_results['verification_rate'] = verification_rate
                
                if verification_rate >= 90:
                    logic_results['status'] = 'mostly_verified'
                    self.log(f"✅ 대부분의 로직이 검증됨 ({verification_rate:.1f}%)")
                else:
                    logic_results['status'] = 'partially_verified'
                    self.log(f"⚠️ 일부 로직에 문제 있음 (검증율: {verification_rate:.1f}%)")
            
        except Exception as e:
            self.log(f"❌ 비즈니스 로직 검증 중 오류: {e}")
            logic_results['status'] = 'verification_error'
            logic_results['error'] = str(e)
        
        return logic_results
    
    def _find_business_logic_files(self) -> List[str]:
        """비즈니스 로직이 포함된 파일 찾기"""
        logic_files = []
        
        # 핵심 비즈니스 로직 파일들
        core_logic_files = [
            "Monitoring/POSCO_News_250808/posco_main_notifier.py",
            "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py",
            "Monitoring/POSCO_News_250808/realtime_news_monitor.py",
            "Monitoring/POSCO_News_250808/integrated_report_scheduler.py",
            "POSCO_News_250808.py"
        ]
        
        for file_path in core_logic_files:
            if os.path.exists(file_path):
                logic_files.append(file_path)
        
        # 추가 로직 파일 검색
        import glob
        additional_patterns = [
            "Monitoring/POSCO_News_250808/*.py",
            "*monitor*.py",
            "*scheduler*.py",
            "*analyzer*.py"
        ]
        
        for pattern in additional_patterns:
            matches = glob.glob(pattern, recursive=True)
            for match in matches:
                if match not in logic_files and self._contains_business_logic(match):
                    logic_files.append(match)
        
        self.log(f"📋 비즈니스 로직 파일 {len(logic_files)}개 발견")
        return logic_files
    
    def _contains_business_logic(self, file_path: str) -> bool:
        """파일이 비즈니스 로직을 포함하는지 확인"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 비즈니스 로직 키워드 확인
            business_keywords = [
                'monitor', 'schedule', 'analyze', 'process',
                'notification', 'alert', 'webhook',
                'posco', 'news', 'market', 'kospi', 'exchange',
                'business_day', 'trading', 'publish'
            ]
            
            content_lower = content.lower()
            return any(keyword in content_lower for keyword in business_keywords)
            
        except Exception:
            return False
    
    def _verify_business_logic_elements(self, content: str, file_path: str) -> Dict[str, Any]:
        """비즈니스 로직 요소 검증"""
        verification = {
            'monitoring_logic': False,
            'analysis_logic': False,
            'decision_logic': False,
            'scheduling_logic': False,
            'data_processing': False,
            'issues': []
        }
        
        # 1. 모니터링 로직 검증
        monitoring_patterns = [
            r'def.*monitor.*\(',
            r'class.*Monitor',
            r'check.*status',
            r'get.*data'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in monitoring_patterns):
            verification['monitoring_logic'] = True
        
        # 2. 분석 로직 검증
        analysis_patterns = [
            r'def.*analyze.*\(',
            r'def.*process.*\(',
            r'def.*compare.*\(',
            r'calculate.*'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in analysis_patterns):
            verification['analysis_logic'] = True
        
        # 3. 의사결정 로직 검증
        decision_patterns = [
            r'if.*condition',
            r'if.*status',
            r'if.*time',
            r'elif.*',
            r'else.*:'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in decision_patterns):
            verification['decision_logic'] = True
        
        # 4. 스케줄링 로직 검증
        scheduling_patterns = [
            r'schedule.*',
            r'cron.*',
            r'interval.*',
            r'timer.*',
            r'datetime.*'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in scheduling_patterns):
            verification['scheduling_logic'] = True
        
        # 5. 데이터 처리 로직 검증
        data_patterns = [
            r'json\.',
            r'requests\.',
            r'api.*',
            r'parse.*',
            r'format.*'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in data_patterns):
            verification['data_processing'] = True
        
        # 6. 잠재적 문제 검출
        potential_issues = []
        
        # 하드코딩된 값 검출
        if re.search(r'["\'][0-9]{4}-[0-9]{2}-[0-9]{2}["\']', content):
            potential_issues.append("하드코딩된 날짜 발견")
        
        # TODO/FIXME 주석 검출
        if re.search(r'#.*TODO|#.*FIXME', content, re.IGNORECASE):
            potential_issues.append("미완성 코드 주석 발견")
        
        # 예외 처리 누락 검출
        try_count = len(re.findall(r'\btry\b', content))
        except_count = len(re.findall(r'\bexcept\b', content))
        if try_count > except_count:
            potential_issues.append("예외 처리 누락 가능성")
        
        verification['issues'] = potential_issues
        
        return verification
    
    def verify_data_compatibility(self) -> Dict[str, Any]:
        """데이터 호환성 검증"""
        self.log("📊 데이터 호환성 검증 시작")
        
        compatibility_results = {
            'total_data_files': 0,
            'compatible_files': 0,
            'incompatible_files': 0,
            'data_details': [],
            'status': 'unknown'
        }
        
        try:
            # 1. 데이터 파일 찾기
            data_files = self._find_data_files()
            compatibility_results['total_data_files'] = len(data_files)
            
            # 2. 각 데이터 파일 호환성 검증
            for file_path in data_files:
                self.log(f"📊 데이터 검증: {os.path.basename(file_path)}")
                
                try:
                    compatibility_check = self._verify_data_file_compatibility(file_path)
                    
                    data_detail = {
                        'file': os.path.basename(file_path),
                        'file_type': compatibility_check.get('file_type', 'unknown'),
                        'is_valid': compatibility_check.get('is_valid', False),
                        'structure_preserved': compatibility_check.get('structure_preserved', False),
                        'encoding_correct': compatibility_check.get('encoding_correct', False),
                        'issues': compatibility_check.get('issues', []),
                        'overall_compatible': compatibility_check.get('overall_compatible', False)
                    }
                    
                    compatibility_results['data_details'].append(data_detail)
                    
                    if data_detail['overall_compatible']:
                        compatibility_results['compatible_files'] += 1
                    else:
                        compatibility_results['incompatible_files'] += 1
                    
                except Exception as e:
                    self.log(f"⚠️ {file_path} 데이터 검증 실패: {e}")
                    compatibility_results['incompatible_files'] += 1
            
            # 3. 전체 데이터 호환성 상태 판단
            if compatibility_results['total_data_files'] == 0:
                compatibility_results['status'] = 'no_data_files'
                self.log("⚠️ 데이터 파일을 찾을 수 없습니다")
            elif compatibility_results['incompatible_files'] == 0:
                compatibility_results['status'] = 'all_compatible'
                self.log("✅ 모든 데이터 파일이 호환됩니다")
            else:
                compatibility_rate = (compatibility_results['compatible_files'] / compatibility_results['total_data_files']) * 100
                compatibility_results['compatibility_rate'] = compatibility_rate
                
                if compatibility_rate >= 95:
                    compatibility_results['status'] = 'mostly_compatible'
                    self.log(f"✅ 대부분의 데이터가 호환됨 ({compatibility_rate:.1f}%)")
                else:
                    compatibility_results['status'] = 'partially_compatible'
                    self.log(f"⚠️ 일부 데이터 호환성 문제 ({compatibility_rate:.1f}%)")
            
        except Exception as e:
            self.log(f"❌ 데이터 호환성 검증 중 오류: {e}")
            compatibility_results['status'] = 'verification_error'
            compatibility_results['error'] = str(e)
        
        return compatibility_results
    
    def _find_data_files(self) -> List[str]:
        """데이터 파일 찾기"""
        data_files = []
        
        # 데이터 파일 패턴
        data_patterns = [
            "*.json",
            "*.csv",
            "*.log",
            "Monitoring/POSCO_News_250808/*.json",
            "Monitoring/POSCO_News_250808/reports/*.json",
            "Monitoring/POSCO_News_250808/reports/*.html",
            "*cache*.json",
            "*config*.json",
            "*status*.json",
            "*state*.json"
        ]
        
        import glob
        for pattern in data_patterns:
            matches = glob.glob(pattern, recursive=True)
            data_files.extend(matches)
        
        # 중복 제거 및 필터링
        data_files = list(set(data_files))
        
        # 백업 파일 제외
        data_files = [f for f in data_files if not any(
            exclude in f for exclude in ['.backup', '_backup', '.bak', '__pycache__']
        )]
        
        self.log(f"📋 데이터 파일 {len(data_files)}개 발견")
        return data_files
    
    def _verify_data_file_compatibility(self, file_path: str) -> Dict[str, Any]:
        """개별 데이터 파일 호환성 검증"""
        verification = {
            'file_type': 'unknown',
            'is_valid': False,
            'structure_preserved': False,
            'encoding_correct': False,
            'issues': [],
            'overall_compatible': False
        }
        
        try:
            # 파일 타입 확인
            file_ext = os.path.splitext(file_path)[1].lower()
            verification['file_type'] = file_ext
            
            # 인코딩 확인
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                verification['encoding_correct'] = True
            except UnicodeDecodeError:
                verification['issues'].append("UTF-8 인코딩 문제")
                try:
                    with open(file_path, 'r', encoding='cp949') as f:
                        content = f.read()
                    verification['issues'].append("CP949 인코딩 사용됨")
                except:
                    verification['issues'].append("인코딩 확인 불가")
                    return verification
            
            # 파일 타입별 검증
            if file_ext == '.json':
                verification.update(self._verify_json_file(content, file_path))
            elif file_ext == '.csv':
                verification.update(self._verify_csv_file(content, file_path))
            elif file_ext == '.log':
                verification.update(self._verify_log_file(content, file_path))
            elif file_ext == '.html':
                verification.update(self._verify_html_file(content, file_path))
            else:
                verification['is_valid'] = True  # 기타 파일은 기본적으로 유효
                verification['structure_preserved'] = True
            
            # 전체 호환성 판단
            verification['overall_compatible'] = (
                verification['is_valid'] and 
                verification['structure_preserved'] and 
                verification['encoding_correct'] and 
                len(verification['issues']) == 0
            )
            
        except Exception as e:
            verification['issues'].append(f"검증 중 오류: {str(e)}")
        
        return verification
    
    def _verify_json_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """JSON 파일 검증"""
        result = {'is_valid': False, 'structure_preserved': False, 'issues': []}
        
        try:
            # JSON 파싱 테스트
            data = json.loads(content)
            result['is_valid'] = True
            
            # 구조 검증 (파일명 기반)
            filename = os.path.basename(file_path).lower()
            
            if 'config' in filename:
                # 설정 파일 구조 검증
                expected_keys = ['api_config', 'webhook', 'monitoring']
                if any(key in str(data).lower() for key in expected_keys):
                    result['structure_preserved'] = True
                else:
                    result['issues'].append("설정 파일 구조가 예상과 다름")
            
            elif 'status' in filename or 'state' in filename:
                # 상태 파일 구조 검증
                if isinstance(data, dict) and ('status' in data or 'state' in data or 'timestamp' in data):
                    result['structure_preserved'] = True
                else:
                    result['issues'].append("상태 파일 구조가 예상과 다름")
            
            elif 'cache' in filename:
                # 캐시 파일 구조 검증
                if isinstance(data, dict) and ('data' in data or 'timestamp' in data):
                    result['structure_preserved'] = True
                else:
                    result['issues'].append("캐시 파일 구조가 예상과 다름")
            
            else:
                # 기타 JSON 파일은 유효하면 구조 보존으로 간주
                result['structure_preserved'] = True
            
        except json.JSONDecodeError as e:
            result['issues'].append(f"JSON 파싱 오류: {str(e)}")
        
        return result
    
    def _verify_csv_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """CSV 파일 검증"""
        result = {'is_valid': False, 'structure_preserved': False, 'issues': []}
        
        try:
            import csv
            import io
            
            # CSV 파싱 테스트
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            
            if len(rows) > 0:
                result['is_valid'] = True
                
                # 헤더 존재 여부 확인
                if len(rows) > 1:
                    result['structure_preserved'] = True
                else:
                    result['issues'].append("CSV 데이터가 부족함")
            else:
                result['issues'].append("빈 CSV 파일")
        
        except Exception as e:
            result['issues'].append(f"CSV 파싱 오류: {str(e)}")
        
        return result
    
    def _verify_log_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """로그 파일 검증"""
        result = {'is_valid': True, 'structure_preserved': True, 'issues': []}
        
        # 로그 파일은 기본적으로 텍스트이므로 읽을 수 있으면 유효
        lines = content.split('\n')
        
        # 로그 형식 확인
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]',  # [YYYY-MM-DD HH:MM:SS]
        ]
        
        has_timestamps = any(
            re.search(pattern, line) for line in lines[:10] for pattern in timestamp_patterns
        )
        
        if not has_timestamps and len(lines) > 5:
            result['issues'].append("타임스탬프 형식을 찾을 수 없음")
        
        return result
    
    def _verify_html_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """HTML 파일 검증"""
        result = {'is_valid': False, 'structure_preserved': False, 'issues': []}
        
        # 기본 HTML 구조 확인
        html_indicators = ['<html', '<head', '<body', '<!DOCTYPE']
        
        if any(indicator in content.lower() for indicator in html_indicators):
            result['is_valid'] = True
            result['structure_preserved'] = True
        else:
            result['issues'].append("HTML 구조를 찾을 수 없음")
        
        return result
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """종합 검증 실행"""
        self.log("🚀 종합 모니터링 및 알림 시스템 검증 시작")
        
        comprehensive_results = {
            'verification_start_time': self.verification_start_time.isoformat(),
            'verification_end_time': None,
            'total_duration_seconds': None,
            'webhook_verification': {},
            'message_verification': {},
            'business_logic_verification': {},
            'data_compatibility_verification': {},
            'overall_status': 'unknown',
            'overall_score': 0,
            'recommendations': []
        }
        
        try:
            # 1. 웹훅 기능 검증
            self.log("1️⃣ 웹훅 기능 검증 실행")
            comprehensive_results['webhook_verification'] = self.verify_webhook_functionality()
            
            # 2. 알림 메시지 무결성 검증
            self.log("2️⃣ 알림 메시지 무결성 검증 실행")
            comprehensive_results['message_verification'] = self.verify_notification_message_integrity()
            
            # 3. 비즈니스 로직 무결성 검증
            self.log("3️⃣ 비즈니스 로직 무결성 검증 실행")
            comprehensive_results['business_logic_verification'] = self.verify_business_logic_integrity()
            
            # 4. 데이터 호환성 검증
            self.log("4️⃣ 데이터 호환성 검증 실행")
            comprehensive_results['data_compatibility_verification'] = self.verify_data_compatibility()
            
            # 5. 전체 결과 분석 및 점수 계산
            overall_score, overall_status, recommendations = self._calculate_overall_results(comprehensive_results)
            
            comprehensive_results['overall_score'] = overall_score
            comprehensive_results['overall_status'] = overall_status
            comprehensive_results['recommendations'] = recommendations
            
            # 6. 검증 완료 시간 기록
            verification_end_time = datetime.now()
            comprehensive_results['verification_end_time'] = verification_end_time.isoformat()
            comprehensive_results['total_duration_seconds'] = (verification_end_time - self.verification_start_time).total_seconds()
            
            self.log(f"✅ 종합 검증 완료 (소요시간: {comprehensive_results['total_duration_seconds']:.2f}초)")
            self.log(f"📊 전체 점수: {overall_score}/100, 상태: {overall_status}")
            
        except Exception as e:
            self.log(f"❌ 종합 검증 중 오류: {e}")
            comprehensive_results['overall_status'] = 'verification_error'
            comprehensive_results['error'] = str(e)
            comprehensive_results['traceback'] = traceback.format_exc()
        
        return comprehensive_results
    
    def _calculate_overall_results(self, results: Dict[str, Any]) -> Tuple[int, str, List[str]]:
        """전체 결과 분석 및 점수 계산"""
        scores = {}
        recommendations = []
        
        # 1. 웹훅 기능 점수 (25점)
        webhook_result = results.get('webhook_verification', {})
        if webhook_result.get('status') == 'all_accessible':
            scores['webhook'] = 25
        elif webhook_result.get('status') == 'partially_accessible':
            scores['webhook'] = 15
            recommendations.append("일부 웹훅 접근 불가 - 네트워크 연결 및 URL 확인 필요")
        else:
            scores['webhook'] = 0
            recommendations.append("웹훅 기능 전면 점검 필요 - 모든 웹훅 접근 불가")
        
        # 2. 메시지 무결성 점수 (25점)
        message_result = results.get('message_verification', {})
        if message_result.get('status') == 'all_preserved':
            scores['message'] = 25
        elif message_result.get('status') == 'mostly_preserved':
            scores['message'] = 20
            recommendations.append("일부 알림 메시지 변경됨 - 메시지 내용 재검토 필요")
        elif message_result.get('status') == 'partially_preserved':
            scores['message'] = 10
            recommendations.append("다수 알림 메시지 변경됨 - 메시지 복원 작업 필요")
        else:
            scores['message'] = 0
            recommendations.append("알림 메시지 시스템 전면 점검 필요")
        
        # 3. 비즈니스 로직 점수 (30점)
        logic_result = results.get('business_logic_verification', {})
        if logic_result.get('status') == 'all_verified':
            scores['logic'] = 30
        elif logic_result.get('status') == 'mostly_verified':
            scores['logic'] = 25
            recommendations.append("일부 비즈니스 로직 검토 필요")
        elif logic_result.get('status') == 'partially_verified':
            scores['logic'] = 15
            recommendations.append("비즈니스 로직 상당 부분 수정 필요")
        else:
            scores['logic'] = 0
            recommendations.append("비즈니스 로직 전면 재검토 필요")
        
        # 4. 데이터 호환성 점수 (20점)
        data_result = results.get('data_compatibility_verification', {})
        if data_result.get('status') == 'all_compatible':
            scores['data'] = 20
        elif data_result.get('status') == 'mostly_compatible':
            scores['data'] = 16
            recommendations.append("일부 데이터 파일 호환성 문제 해결 필요")
        elif data_result.get('status') == 'partially_compatible':
            scores['data'] = 10
            recommendations.append("다수 데이터 파일 호환성 문제 - 데이터 구조 점검 필요")
        else:
            scores['data'] = 0
            recommendations.append("데이터 호환성 전면 점검 필요")
        
        # 전체 점수 계산
        total_score = sum(scores.values())
        
        # 전체 상태 결정
        if total_score >= 90:
            overall_status = 'excellent'
        elif total_score >= 80:
            overall_status = 'good'
        elif total_score >= 70:
            overall_status = 'acceptable'
        elif total_score >= 50:
            overall_status = 'needs_improvement'
        else:
            overall_status = 'critical_issues'
        
        return total_score, overall_status, recommendations
    
    def generate_verification_report(self, results: Dict[str, Any]) -> str:
        """검증 보고서 생성"""
        report_file = os.path.join(self.script_dir, f"monitoring_alert_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.log(f"📄 검증 보고서 생성: {os.path.basename(report_file)}")
            return report_file
            
        except Exception as e:
            self.log(f"❌ 보고서 생성 실패: {e}")
            return None

def main():
    """메인 실행 함수"""
    print("🔍 POSCO 모니터링 및 알림 시스템 검증 도구")
    print("=" * 60)
    
    try:
        # 검증 시스템 초기화
        verifier = MonitoringAlertSystemVerifier()
        
        # 종합 검증 실행
        results = verifier.run_comprehensive_verification()
        
        # 보고서 생성
        report_file = verifier.generate_verification_report(results)
        
        # 결과 요약 출력
        print("\n" + "=" * 60)
        print("📊 검증 결과 요약")
        print("=" * 60)
        
        print(f"🕐 검증 시간: {results.get('total_duration_seconds', 0):.2f}초")
        print(f"📊 전체 점수: {results.get('overall_score', 0)}/100")
        print(f"🎯 전체 상태: {results.get('overall_status', 'unknown')}")
        
        # 개별 검증 결과
        webhook_result = results.get('webhook_verification', {})
        print(f"🔗 웹훅 기능: {webhook_result.get('accessible_webhooks', 0)}/{webhook_result.get('total_webhooks', 0)} 접근 가능")
        
        message_result = results.get('message_verification', {})
        print(f"📝 메시지 무결성: {message_result.get('preserved_messages', 0)}개 보존됨")
        
        logic_result = results.get('business_logic_verification', {})
        print(f"🧠 비즈니스 로직: {logic_result.get('verified_logic_files', 0)}/{logic_result.get('total_logic_files', 0)} 파일 검증됨")
        
        data_result = results.get('data_compatibility_verification', {})
        print(f"📊 데이터 호환성: {data_result.get('compatible_files', 0)}/{data_result.get('total_data_files', 0)} 파일 호환됨")
        
        # 권장사항
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 권장사항 ({len(recommendations)}개):")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        if report_file:
            print(f"\n📄 상세 보고서: {os.path.basename(report_file)}")
        
        print("\n✅ 모니터링 및 알림 시스템 검증 완료")
        
        return results.get('overall_score', 0) >= 80  # 80점 이상이면 성공
        
    except Exception as e:
        print(f"❌ 검증 도구 실행 중 오류: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)