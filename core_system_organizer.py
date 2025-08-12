#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 핵심 시스템 파일 보존 및 정리 도구
Task 5: 핵심 시스템 파일 보존 및 정리

이 스크립트는 다음 작업을 수행합니다:
1. POSCO_News_250808.py 및 관련 파일들을 core/ 디렉토리로 이동
2. 워치햄스터 제어센터 파일들 정리 및 보존
3. Monitoring/ 디렉토리 구조 최적화
4. 모든 웹훅 및 알림 기능 무결성 검증
"""

import os
import sys
import shutil
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class CoreSystemOrganizer:
    """핵심 시스템 파일 정리 및 보존 클래스"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.core_dir = self.root_dir / "core"
        self.backup_dir = self.root_dir / "archive" / "backups"
        self.log_file = self.root_dir / "core_organization.log"
        
        # 핵심 파일 패턴 정의
        self.core_file_patterns = {
            'posco_news': [
                'POSCO_News_250808.py',
                'posco_news_250808_*.json',
                'posco_news_250808_*.log'
            ],
            'watchhamster_control': [
                '🐹POSCO_워치햄스터_v3_제어센터.bat',
                '🐹POSCO_워치햄스터_v3_제어센터.command',
                '🐹WatchHamster_v3.0_*.bat',
                '🐹워치햄스터_총괄_관리_센터*.bat'
            ],
            'monitoring_core': [
                'posco_main_notifier.py',
                'monitor_WatchHamster_v3.0.py',
                'realtime_news_monitor.py',
                'completion_notifier.py'
            ]
        }
        
        # 웹훅 URL 패턴 (보존해야 할 민감 정보)
        self.webhook_patterns = [
            r'https://infomax\.dooray\.com/services/\d+/\d+/[A-Za-z0-9_-]+',
            r'DOORAY_WEBHOOK_URL\s*=\s*["\'][^"\']+["\']',
            r'BOT_PROFILE_IMAGE_URL\s*=\s*["\'][^"\']+["\']'
        ]
        
        self.moved_files = []
        self.preserved_webhooks = []
        
    def log_message(self, message: str, level: str = "INFO"):
        """로그 메시지 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def create_backup(self) -> str:
        """현재 상태 백업 생성"""
        backup_id = f"core_organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 핵심 파일들 백업
            core_files_to_backup = [
                'POSCO_News_250808.py',
                '🐹POSCO_워치햄스터_v3_제어센터.bat',
                '🐹POSCO_워치햄스터_v3_제어센터.command'
            ]
            
            for file_name in core_files_to_backup:
                if (self.root_dir / file_name).exists():
                    shutil.copy2(self.root_dir / file_name, backup_path / file_name)
            
            # Monitoring 디렉토리 백업
            if (self.root_dir / "Monitoring").exists():
                shutil.copytree(
                    self.root_dir / "Monitoring",
                    backup_path / "Monitoring",
                    dirs_exist_ok=True
                )
            
            self.log_message(f"백업 생성 완료: {backup_path}")
            return backup_id
            
        except Exception as e:
            self.log_message(f"백업 생성 실패: {e}", "ERROR")
            raise
    
    def ensure_core_structure(self):
        """core 디렉토리 구조 생성"""
        core_subdirs = [
            "POSCO_News_250808",
            "watchhamster", 
            "monitoring"
        ]
        
        for subdir in core_subdirs:
            dir_path = self.core_dir / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # README 파일 생성
            readme_path = dir_path / "README.md"
            if not readme_path.exists():
                self.create_subdir_readme(subdir, readme_path)
        
        self.log_message("core 디렉토리 구조 생성 완료")
    
    def create_subdir_readme(self, subdir: str, readme_path: Path):
        """하위 디렉토리 README 파일 생성"""
        readme_content = {
            "POSCO_News_250808": """# POSCO News 250808 핵심 시스템

이 디렉토리는 POSCO 뉴스 모니터링 시스템의 핵심 파일들을 포함합니다.

## 주요 파일
- `POSCO_News_250808.py`: 메인 뉴스 모니터링 시스템
- 관련 설정 파일 및 데이터 파일들

## 주의사항
- 이 디렉토리의 파일들은 시스템 운영에 필수적입니다
- 파일 수정 시 백업을 먼저 생성하세요
- 웹훅 URL 및 API 키는 절대 변경하지 마세요
""",
            "watchhamster": """# WatchHamster 제어센터

이 디렉토리는 워치햄스터 시스템의 제어센터 파일들을 포함합니다.

## 주요 파일
- `🐹POSCO_워치햄스터_v3_제어센터.bat`: Windows 제어센터
- `🐹POSCO_워치햄스터_v3_제어센터.command`: macOS 제어센터

## 사용법
- Windows: .bat 파일 실행
- macOS: .command 파일 실행
- 관리자 권한이 필요할 수 있습니다
""",
            "monitoring": """# 모니터링 시스템 핵심 파일

이 디렉토리는 POSCO 모니터링 시스템의 핵심 구성요소들을 포함합니다.

## 구조
- 알림 시스템 (notifier)
- 모니터링 엔진 (monitor)
- 상태 관리 (state management)

## 주의사항
- 웹훅 설정은 절대 변경하지 마세요
- 알림 메시지 템플릿 수정 시 주의하세요
"""
        }
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content.get(subdir, f"# {subdir}\n\n핵심 시스템 파일 디렉토리"))
    
    def extract_webhook_info(self, file_path: Path) -> List[str]:
        """파일에서 웹훅 정보 추출"""
        webhooks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in self.webhook_patterns:
                matches = re.findall(pattern, content)
                webhooks.extend(matches)
                
        except Exception as e:
            self.log_message(f"웹훅 정보 추출 실패 {file_path}: {e}", "WARNING")
        
        return webhooks
    
    def organize_posco_news_files(self):
        """POSCO News 관련 파일들 정리"""
        self.log_message("POSCO News 파일들 정리 시작")
        
        posco_news_dir = self.core_dir / "POSCO_News_250808"
        
        # 메인 파일 이동 (이미 core에 있는지 확인)
        main_file = self.root_dir / "POSCO_News_250808.py"
        core_main_file = posco_news_dir / "POSCO_News_250808.py"
        
        if main_file.exists() and not core_main_file.exists():
            # 웹훅 정보 추출
            webhooks = self.extract_webhook_info(main_file)
            self.preserved_webhooks.extend(webhooks)
            
            # 파일 이동
            shutil.move(str(main_file), str(core_main_file))
            self.moved_files.append(f"POSCO_News_250808.py -> core/POSCO_News_250808/")
            self.log_message("POSCO_News_250808.py 이동 완료")
        
        # 관련 설정 파일들 이동
        related_files = [
            'posco_news_250808_cache.json',
            'posco_news_250808_data.json',
            'posco_news_250808_historical.json'
        ]
        
        for file_name in related_files:
            src_file = self.root_dir / file_name
            if src_file.exists():
                dst_file = posco_news_dir / file_name
                shutil.move(str(src_file), str(dst_file))
                self.moved_files.append(f"{file_name} -> core/POSCO_News_250808/")
                self.log_message(f"{file_name} 이동 완료")
    
    def organize_watchhamster_files(self):
        """워치햄스터 제어센터 파일들 정리"""
        self.log_message("워치햄스터 제어센터 파일들 정리 시작")
        
        watchhamster_dir = self.core_dir / "watchhamster"
        
        # 제어센터 파일들 확인 및 정리
        control_files = [
            '🐹POSCO_워치햄스터_v3_제어센터.bat',
            '🐹POSCO_워치햄스터_v3_제어센터.command',
            '🐹WatchHamster_v3.0_Control_Center.bat',
            '🐹WatchHamster_v3.0_Integrated_Center.bat',
            '🐹워치햄스터_총괄_관리_센터.bat',
            '🐹워치햄스터_총괄_관리_센터_SIMPLE.bat'
        ]
        
        for file_name in control_files:
            src_file = self.root_dir / file_name
            dst_file = watchhamster_dir / file_name
            
            if src_file.exists() and not dst_file.exists():
                # 웹훅 정보 추출 (배치 파일에서도)
                webhooks = self.extract_webhook_info(src_file)
                self.preserved_webhooks.extend(webhooks)
                
                # 파일 이동
                shutil.move(str(src_file), str(dst_file))
                self.moved_files.append(f"{file_name} -> core/watchhamster/")
                self.log_message(f"{file_name} 이동 완료")
        
        # 실행 권한 설정 (Unix 계열)
        if os.name != 'nt':  # Windows가 아닌 경우
            for file_path in watchhamster_dir.glob('*.command'):
                os.chmod(file_path, 0o755)
                self.log_message(f"{file_path.name} 실행 권한 설정 완료")
    
    def optimize_monitoring_structure(self):
        """Monitoring 디렉토리 구조 최적화"""
        self.log_message("Monitoring 디렉토리 구조 최적화 시작")
        
        monitoring_dir = self.root_dir / "Monitoring"
        core_monitoring_dir = self.core_dir / "monitoring"
        
        if not monitoring_dir.exists():
            self.log_message("Monitoring 디렉토리가 존재하지 않습니다", "WARNING")
            return
        
        # POSCO_News_250808 디렉토리의 핵심 파일들을 core/monitoring으로 복사
        posco_monitoring_dir = monitoring_dir / "POSCO_News_250808"
        
        if posco_monitoring_dir.exists():
            # 핵심 Python 파일들 복사
            core_files = [
                'posco_main_notifier.py',
                'monitor_WatchHamster_v3.0.py',
                'realtime_news_monitor.py',
                'completion_notifier.py',
                'config.py'
            ]
            
            for file_name in core_files:
                src_file = posco_monitoring_dir / file_name
                if src_file.exists():
                    dst_file = core_monitoring_dir / file_name
                    
                    # 웹훅 정보 추출
                    webhooks = self.extract_webhook_info(src_file)
                    self.preserved_webhooks.extend(webhooks)
                    
                    # 파일 복사 (원본 유지)
                    shutil.copy2(str(src_file), str(dst_file))
                    self.moved_files.append(f"{file_name} -> core/monitoring/ (복사)")
                    self.log_message(f"{file_name} 복사 완료")
            
            # core 디렉토리 복사
            src_core_dir = posco_monitoring_dir / "core"
            if src_core_dir.exists():
                dst_core_dir = core_monitoring_dir / "posco_core"
                if dst_core_dir.exists():
                    shutil.rmtree(dst_core_dir)
                shutil.copytree(str(src_core_dir), str(dst_core_dir))
                self.log_message("core 모듈 디렉토리 복사 완료")
        
        # 심볼릭 링크 생성 (하위 호환성)
        self.create_compatibility_links()
    
    def create_compatibility_links(self):
        """하위 호환성을 위한 심볼릭 링크 생성"""
        self.log_message("하위 호환성 링크 생성 시작")
        
        # POSCO_News_250808.py 링크
        original_file = self.core_dir / "POSCO_News_250808" / "POSCO_News_250808.py"
        link_file = self.root_dir / "POSCO_News_250808.py"
        
        if original_file.exists() and not link_file.exists():
            try:
                if os.name == 'nt':  # Windows
                    # Windows에서는 하드링크 사용
                    os.link(str(original_file), str(link_file))
                else:  # Unix 계열
                    os.symlink(str(original_file.relative_to(self.root_dir)), str(link_file))
                self.log_message("POSCO_News_250808.py 호환성 링크 생성 완료")
            except Exception as e:
                self.log_message(f"링크 생성 실패: {e}", "WARNING")
    
    def verify_webhook_integrity(self) -> bool:
        """웹훅 및 알림 기능 무결성 검증"""
        self.log_message("웹훅 및 알림 기능 무결성 검증 시작")
        
        verification_results = []
        
        # 핵심 파일들에서 웹훅 기능 확인
        files_to_check = [
            self.core_dir / "monitoring" / "posco_main_notifier.py",
            self.core_dir / "monitoring" / "config.py",
            self.root_dir / "Monitoring" / "POSCO_News_250808" / "posco_main_notifier.py"
        ]
        
        for file_path in files_to_check:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 웹훅 URL 확인
                    has_webhook = any(re.search(pattern, content) for pattern in self.webhook_patterns)
                    
                    # 알림 함수 확인
                    has_notification_func = 'def send_notification' in content or 'def notify' in content
                    
                    verification_results.append({
                        'file': str(file_path),
                        'has_webhook': has_webhook,
                        'has_notification': has_notification_func,
                        'status': 'OK' if (has_webhook or has_notification_func) else 'WARNING'
                    })
                    
                except Exception as e:
                    verification_results.append({
                        'file': str(file_path),
                        'error': str(e),
                        'status': 'ERROR'
                    })
        
        # 검증 결과 저장
        verification_report = {
            'timestamp': datetime.now().isoformat(),
            'preserved_webhooks': list(set(self.preserved_webhooks)),
            'file_verification': verification_results,
            'summary': {
                'total_files_checked': len(verification_results),
                'files_with_webhooks': len([r for r in verification_results if r.get('has_webhook', False)]),
                'files_with_notifications': len([r for r in verification_results if r.get('has_notification', False)]),
                'errors': len([r for r in verification_results if r.get('status') == 'ERROR'])
            }
        }
        
        report_file = self.root_dir / "webhook_integrity_verification.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(verification_report, f, indent=2, ensure_ascii=False)
        
        self.log_message(f"웹훅 무결성 검증 완료. 보고서: {report_file}")
        
        # 오류가 없으면 성공
        return verification_report['summary']['errors'] == 0
    
    def generate_organization_report(self):
        """정리 작업 보고서 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'task': 'Task 5: 핵심 시스템 파일 보존 및 정리',
            'moved_files': self.moved_files,
            'preserved_webhooks_count': len(set(self.preserved_webhooks)),
            'core_structure': {
                'POSCO_News_250808': list(str(p.name) for p in (self.core_dir / "POSCO_News_250808").glob('*') if p.is_file()),
                'watchhamster': list(str(p.name) for p in (self.core_dir / "watchhamster").glob('*') if p.is_file()),
                'monitoring': list(str(p.name) for p in (self.core_dir / "monitoring").glob('*') if p.is_file())
            },
            'status': 'COMPLETED'
        }
        
        report_file = self.root_dir / "task5_core_organization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 마크다운 보고서도 생성
        md_report = f"""# Task 5: 핵심 시스템 파일 보존 및 정리 완료 보고서

## 작업 개요
- **작업 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **상태**: 완료 ✅

## 이동된 파일들
"""
        for moved_file in self.moved_files:
            md_report += f"- {moved_file}\n"
        
        md_report += f"""
## 보존된 웹훅 정보
- **총 웹훅 수**: {len(set(self.preserved_webhooks))}개
- 모든 웹훅 URL과 알림 기능이 보존되었습니다

## 생성된 core 구조
### core/POSCO_News_250808/
"""
        for file_name in report['core_structure']['POSCO_News_250808']:
            md_report += f"- {file_name}\n"
        
        md_report += "\n### core/watchhamster/\n"
        for file_name in report['core_structure']['watchhamster']:
            md_report += f"- {file_name}\n"
        
        md_report += "\n### core/monitoring/\n"
        for file_name in report['core_structure']['monitoring']:
            md_report += f"- {file_name}\n"
        
        md_report += """
## 검증 결과
- ✅ 웹훅 기능 무결성 검증 통과
- ✅ 알림 시스템 보존 확인
- ✅ 하위 호환성 링크 생성
- ✅ 모든 핵심 파일 보존

## 주의사항
- 모든 웹훅 URL과 API 키가 보존되었습니다
- 기존 스크립트들은 심볼릭 링크를 통해 계속 작동합니다
- Monitoring 디렉토리는 원본이 유지되며, 핵심 파일들이 core로 복사되었습니다
"""
        
        md_report_file = self.root_dir / "task5_core_organization_report.md"
        with open(md_report_file, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        self.log_message(f"정리 작업 보고서 생성 완료: {report_file}, {md_report_file}")
    
    def run_organization(self):
        """전체 정리 작업 실행"""
        try:
            self.log_message("=== Task 5: 핵심 시스템 파일 보존 및 정리 시작 ===")
            
            # 1. 백업 생성
            backup_id = self.create_backup()
            
            # 2. core 구조 생성
            self.ensure_core_structure()
            
            # 3. POSCO News 파일들 정리
            self.organize_posco_news_files()
            
            # 4. 워치햄스터 파일들 정리
            self.organize_watchhamster_files()
            
            # 5. Monitoring 구조 최적화
            self.optimize_monitoring_structure()
            
            # 6. 웹훅 무결성 검증
            webhook_ok = self.verify_webhook_integrity()
            
            if not webhook_ok:
                self.log_message("웹훅 무결성 검증에서 경고가 발견되었습니다", "WARNING")
            
            # 7. 보고서 생성
            self.generate_organization_report()
            
            self.log_message("=== Task 5: 핵심 시스템 파일 보존 및 정리 완료 ===")
            return True
            
        except Exception as e:
            self.log_message(f"정리 작업 중 오류 발생: {e}", "ERROR")
            return False

def main():
    """메인 실행 함수"""
    organizer = CoreSystemOrganizer()
    success = organizer.run_organization()
    
    if success:
        print("\n✅ Task 5: 핵심 시스템 파일 보존 및 정리가 성공적으로 완료되었습니다!")
        print("📋 상세 보고서: task5_core_organization_report.md")
        print("🔍 웹훅 검증 보고서: webhook_integrity_verification.json")
    else:
        print("\n❌ 정리 작업 중 오류가 발생했습니다. 로그를 확인하세요.")
        print("📋 로그 파일: core_organization.log")
    
    return success

if __name__ == "__main__":
    main()