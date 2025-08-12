#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 웹훅 설정 및 상수 복원 시스템
WebhookConfigRestorer 클래스 구현

Requirements: 2.2, 2.3
Created: 2025-01-11
"""

import os
import re
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class WebhookConfigRestorer:
    """
    웹훅 설정 및 상수 복원 전담 클래스
    
    원본 커밋의 웹훅 URL, 메시지 템플릿 상수, 알림 관련 설정을 복원합니다.
    """
    
    def __init__(self, target_file_path: str, config_file_path: str):
        """
        WebhookConfigRestorer 초기화
        
        Args:
            target_file_path (str): 복원 대상 파일 경로
            config_file_path (str): 설정 파일 경로
        """
        self.target_file = target_file_path
        self.config_file = config_file_path
        self.backup_dir = os.path.join(os.path.dirname(target_file_path), '.webhook_config_backup')
        self.backup_created = False
        
        # 복원할 웹훅 설정 목록
        self.webhook_settings = [
            "DOORAY_WEBHOOK_URL",
            "WATCHHAMSTER_WEBHOOK_URL", 
            "BOT_PROFILE_IMAGE_URL",
            "API_CONFIG"
        ]
        
        # 복원할 메시지 템플릿 상수들
        self.message_constants = [
            "NEWS_MONITOR_CONFIG",
            "MASTER_MONITORING_STRATEGY",
            "MONITORING_CONFIG",
            "STATUS_CONFIG",
            "NEWS_TYPES"
        ]
        
        # 줄바꿈 문자 복원 패턴 (Requirements 1.1, 1.2)
        self.line_break_patterns = [
            (r'\\n', '\n'),  # \\n을 \n으로 복원
            (r'/n', '\n'),   # /n을 \n으로 복원 (잘못된 형태)
        ]
        
        self.log_messages = []
    
    def log(self, message: str):
        """로그 메시지 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
    
    def create_backup(self) -> bool:
        """
        복원 작업 전 현재 파일들 백업
        
        Returns:
            bool: 백업 성공 여부
        """
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 대상 파일 백업
            if os.path.exists(self.target_file):
                backup_target = os.path.join(
                    self.backup_dir, 
                    f"{os.path.basename(self.target_file)}.backup_{timestamp}"
                )
                shutil.copy2(self.target_file, backup_target)
                self.log(f"✅ 대상 파일 백업 완료: {backup_target}")
            
            # 설정 파일 백업
            if os.path.exists(self.config_file):
                backup_config = os.path.join(
                    self.backup_dir,
                    f"{os.path.basename(self.config_file)}.backup_{timestamp}"
                )
                shutil.copy2(self.config_file, backup_config)
                self.log(f"✅ 설정 파일 백업 완료: {backup_config}")
            
            self.backup_created = True
            return True
            
        except Exception as e:
            self.log(f"❌ 백업 생성 실패: {e}")
            return False
    
    def extract_original_webhook_settings(self) -> Dict[str, str]:
        """
        백업된 원본 설정에서 웹훅 관련 설정 추출
        
        Returns:
            Dict[str, str]: 원본 웹훅 설정들
        """
        original_settings = {}
        
        try:
            # 백업된 원본 config 파일 읽기
            backup_config_path = "core/monitoring/.webhook_config_backup/config.py.backup_20250811_112227"
            
            if os.path.exists(backup_config_path):
                with open(backup_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 웹훅 URL 추출
                dooray_match = re.search(r'DOORAY_WEBHOOK_URL\s*=\s*["\']([^"\']+)["\']', content)
                if dooray_match:
                    original_settings['DOORAY_WEBHOOK_URL'] = dooray_match.group(1)
                
                watchhamster_match = re.search(r'WATCHHAMSTER_WEBHOOK_URL\s*=\s*["\']([^"\']+)["\']', content)
                if watchhamster_match:
                    original_settings['WATCHHAMSTER_WEBHOOK_URL'] = watchhamster_match.group(1)
                
                # 봇 프로필 이미지 URL 추출
                bot_image_match = re.search(r'BOT_PROFILE_IMAGE_URL\s*=\s*["\']([^"\']+)["\']', content)
                if bot_image_match:
                    original_settings['BOT_PROFILE_IMAGE_URL'] = bot_image_match.group(1)
                
                # API_CONFIG 추출
                api_config_match = re.search(r'API_CONFIG\s*=\s*({[^}]+})', content, re.DOTALL)
                if api_config_match:
                    original_settings['API_CONFIG'] = api_config_match.group(1)
                
                self.log(f"✅ 원본 웹훅 설정 {len(original_settings)}개 추출 완료")
                
            else:
                self.log(f"⚠️ 백업된 원본 설정 파일을 찾을 수 없음: {backup_config_path}")
                
        except Exception as e:
            self.log(f"❌ 원본 웹훅 설정 추출 실패: {e}")
        
        return original_settings
    
    def extract_original_message_constants(self) -> Dict[str, str]:
        """
        백업된 원본 설정에서 메시지 템플릿 상수들 추출
        
        Returns:
            Dict[str, str]: 원본 메시지 상수들
        """
        original_constants = {}
        
        try:
            backup_config_path = "core/monitoring/.webhook_config_backup/config.py.backup_20250811_112227"
            
            if os.path.exists(backup_config_path):
                with open(backup_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # NEWS_MONITOR_CONFIG에서 줄바꿈 문자 패턴 확인
                news_config_match = re.search(r'NEWS_MONITOR_CONFIG\s*=\s*({.*?})\s*#', content, re.DOTALL)
                if news_config_match:
                    config_text = news_config_match.group(1)
                    # /n 패턴이 있는지 확인 (원본에서 손상된 부분)
                    if '/n' in config_text:
                        self.log("🔍 원본에서 /n 패턴 발견 - 이를 \\n으로 복원해야 함")
                        original_constants['NEWS_MONITOR_CONFIG'] = config_text
                
                # 다른 설정들도 추출
                for constant_name in self.message_constants:
                    if constant_name != 'NEWS_MONITOR_CONFIG':  # 이미 처리됨
                        pattern = rf'{constant_name}\s*=\s*({{.*?}})\s*(?:#|$|\n\n)'
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            original_constants[constant_name] = match.group(1)
                
                self.log(f"✅ 원본 메시지 상수 {len(original_constants)}개 추출 완료")
                
        except Exception as e:
            self.log(f"❌ 원본 메시지 상수 추출 실패: {e}")
        
        return original_constants
    
    def restore_line_break_characters(self, content: str) -> str:
        """
        줄바꿈 문자 복원 (Requirements 1.1, 1.2)
        
        Args:
            content (str): 복원할 내용
            
        Returns:
            str: 줄바꿈 문자가 복원된 내용
        """
        restored_content = content
        
        for pattern, replacement in self.line_break_patterns:
            if pattern in restored_content:
                count = restored_content.count(pattern)
                restored_content = restored_content.replace(pattern, replacement)
                self.log(f"🔧 줄바꿈 문자 복원: {pattern} → {replacement} ({count}개)")
        
        return restored_content
    
    def restore_webhook_settings_in_config(self, original_settings: Dict[str, str]) -> bool:
        """
        config.py 파일의 웹훅 설정 복원
        
        Args:
            original_settings (Dict[str, str]): 원본 웹훅 설정들
            
        Returns:
            bool: 복원 성공 여부
        """
        try:
            if not os.path.exists(self.config_file):
                self.log(f"❌ 설정 파일을 찾을 수 없음: {self.config_file}")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            restored_count = 0
            
            # 각 웹훅 설정 복원
            for setting_name, original_value in original_settings.items():
                if setting_name == 'API_CONFIG':
                    # API_CONFIG는 딕셔너리 형태로 처리
                    pattern = rf'{setting_name}\s*=\s*{{[^}}]*}}'
                    if re.search(pattern, content, re.DOTALL):
                        content = re.sub(pattern, f'{setting_name} = {original_value}', content, flags=re.DOTALL)
                        restored_count += 1
                        self.log(f"✅ {setting_name} 복원 완료")
                else:
                    # URL 설정들
                    pattern = rf'{setting_name}\s*=\s*["\'][^"\']*["\']'
                    if re.search(pattern, content):
                        content = re.sub(pattern, f'{setting_name} = "{original_value}"', content)
                        restored_count += 1
                        self.log(f"✅ {setting_name} 복원 완료")
            
            # 줄바꿈 문자 복원
            content = self.restore_line_break_characters(content)
            
            # 파일 저장
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"✅ config.py 웹훅 설정 {restored_count}개 복원 완료")
            return True
            
        except Exception as e:
            self.log(f"❌ config.py 웹훅 설정 복원 실패: {e}")
            return False
    
    def restore_webhook_constants_in_target(self, original_constants: Dict[str, str]) -> bool:
        """
        대상 파일의 웹훅 관련 상수들 복원
        
        Args:
            original_constants (Dict[str, str]): 원본 메시지 상수들
            
        Returns:
            bool: 복원 성공 여부
        """
        try:
            if not os.path.exists(self.target_file):
                self.log(f"❌ 대상 파일을 찾을 수 없음: {self.target_file}")
                return False
            
            with open(self.target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 웹훅 URL import 문 복원
            import_pattern = r'from config import.*'
            original_import = 'from config import WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, API_CONFIG'
            
            if re.search(import_pattern, content):
                content = re.sub(import_pattern, original_import, content)
                self.log("✅ 웹훅 설정 import 문 복원 완료")
            
            # 줄바꿈 문자 복원
            content = self.restore_line_break_characters(content)
            
            # 파일 저장
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("✅ 대상 파일의 웹훅 상수 복원 완료")
            return True
            
        except Exception as e:
            self.log(f"❌ 대상 파일 웹훅 상수 복원 실패: {e}")
            return False
    
    def verify_restoration(self) -> Dict[str, bool]:
        """
        복원 작업 검증
        
        Returns:
            Dict[str, bool]: 검증 결과
        """
        verification_results = {}
        
        try:
            # config.py 검증
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                verification_results['dooray_webhook'] = 'DOORAY_WEBHOOK_URL' in config_content
                verification_results['watchhamster_webhook'] = 'WATCHHAMSTER_WEBHOOK_URL' in config_content
                verification_results['bot_profile_image'] = 'BOT_PROFILE_IMAGE_URL' in config_content
                verification_results['api_config'] = 'API_CONFIG' in config_content
                verification_results['line_breaks_fixed'] = '/n' not in config_content
            
            # 대상 파일 검증
            if os.path.exists(self.target_file):
                with open(self.target_file, 'r', encoding='utf-8') as f:
                    target_content = f.read()
                
                verification_results['import_statement'] = 'WATCHHAMSTER_WEBHOOK_URL' in target_content
                verification_results['target_line_breaks_fixed'] = '/n' not in target_content
            
            # 검증 결과 로그
            passed_checks = sum(1 for result in verification_results.values() if result)
            total_checks = len(verification_results)
            
            self.log(f"🔍 복원 검증 완료: {passed_checks}/{total_checks} 통과")
            
            for check_name, result in verification_results.items():
                status = "✅" if result else "❌"
                self.log(f"  {status} {check_name}: {'통과' if result else '실패'}")
            
        except Exception as e:
            self.log(f"❌ 복원 검증 중 오류: {e}")
        
        return verification_results
    
    def restore_all_webhook_settings(self) -> bool:
        """
        모든 웹훅 설정 및 상수 복원 실행
        
        Returns:
            bool: 전체 복원 성공 여부
        """
        self.log("🚀 웹훅 설정 및 상수 복원 작업 시작")
        
        # 1. 백업 생성
        if not self.create_backup():
            self.log("❌ 백업 생성 실패로 복원 작업 중단")
            return False
        
        # 2. 원본 설정 추출
        original_settings = self.extract_original_webhook_settings()
        original_constants = self.extract_original_message_constants()
        
        if not original_settings:
            self.log("❌ 원본 웹훅 설정을 찾을 수 없어 복원 작업 중단")
            return False
        
        # 3. config.py 웹훅 설정 복원
        config_restored = self.restore_webhook_settings_in_config(original_settings)
        
        # 4. 대상 파일 웹훅 상수 복원
        target_restored = self.restore_webhook_constants_in_target(original_constants)
        
        # 5. 복원 검증
        verification_results = self.verify_restoration()
        
        # 6. 결과 요약
        success = config_restored and target_restored
        if success:
            self.log("🎉 웹훅 설정 및 상수 복원 작업 완료!")
        else:
            self.log("❌ 웹훅 설정 및 상수 복원 작업 실패")
        
        return success
    
    def generate_restoration_report(self) -> str:
        """
        복원 작업 보고서 생성
        
        Returns:
            str: 보고서 파일 경로
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"webhook_config_restoration_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("POSCO 워치햄스터 웹훅 설정 및 상수 복원 보고서\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"복원 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"대상 파일: {self.target_file}\n")
                f.write(f"설정 파일: {self.config_file}\n\n")
                
                f.write("복원 로그:\n")
                f.write("-" * 40 + "\n")
                for log_message in self.log_messages:
                    f.write(f"{log_message}\n")
            
            self.log(f"📋 복원 보고서 생성 완료: {report_file}")
            return report_file
            
        except Exception as e:
            self.log(f"❌ 복원 보고서 생성 실패: {e}")
            return ""


def main():
    """메인 실행 함수"""
    print("POSCO 워치햄스터 웹훅 설정 및 상수 복원 시스템")
    print("=" * 60)
    
    # 파일 경로 설정
    target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
    config_file = "core/monitoring/config.py"
    
    # 복원 시스템 초기화
    restorer = WebhookConfigRestorer(target_file, config_file)
    
    # 복원 실행
    success = restorer.restore_all_webhook_settings()
    
    # 보고서 생성
    report_file = restorer.generate_restoration_report()
    
    if success:
        print("\n🎉 웹훅 설정 및 상수 복원이 성공적으로 완료되었습니다!")
        print(f"📋 상세 보고서: {report_file}")
        return True
    else:
        print("\n❌ 웹훅 설정 및 상수 복원에 실패했습니다.")
        print(f"📋 오류 보고서: {report_file}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)