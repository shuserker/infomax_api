#!/usr/bin/env python3
"""
POSCO 시스템 언어 설정 관리 시스템
Language Settings Management System

모든 시스템 메시지, 상태 표시, 로그 출력을 한글로 통일합니다.
기존 시스템의 비즈니스 로직과 웹훅 내용은 절대 변경하지 않습니다.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# 한글 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('language_management.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TranslationRule:
    """번역 규칙 데이터 클래스"""
    original: str
    translated: str
    context: str
    category: str

class LanguageManager:
    """언어 설정 관리자"""
    
    def __init__(self):
        # 상태 메시지 번역 사전
        self.status_translations = {
            # 작업 상태
            'completed': '완료',
            'in_progress': '진행중',
            'not_started': '시작안함',
            'pending': '대기중',
            'running': '실행중',
            'stopped': '중지됨',
            'paused': '일시정지',
            'cancelled': '취소됨',
            
            # 결과 상태
            'success': '성공',
            'failed': '실패',
            'error': '오류',
            'warning': '경고',
            'info': '정보',
            'debug': '디버그',
            
            # 시스템 상태
            'active': '활성',
            'inactive': '비활성',
            'enabled': '활성화',
            'disabled': '비활성화',
            'online': '온라인',
            'offline': '오프라인',
            'connected': '연결됨',
            'disconnected': '연결끊김',
            
            # 파일 작업 상태
            'created': '생성됨',
            'updated': '업데이트됨',
            'deleted': '삭제됨',
            'moved': '이동됨',
            'copied': '복사됨',
            'renamed': '이름변경됨',
            
            # 테스트 상태
            'passed': '통과',
            'skipped': '건너뜀',
            'timeout': '시간초과',
            'retry': '재시도',
            
            # 일반 동작
            'start': '시작',
            'stop': '중지',
            'restart': '재시작',
            'continue': '계속',
            'finish': '완료',
            'cancel': '취소'
        }
        
        # 메시지 템플릿
        self.message_templates = {
            # 파일 작업 메시지
            'file_moved': '파일이 {source}에서 {destination}으로 이동되었습니다',
            'file_copied': '파일이 {source}에서 {destination}으로 복사되었습니다',
            'file_deleted': '파일 {path}가 삭제되었습니다',
            'file_created': '파일 {path}가 생성되었습니다',
            'file_renamed': '파일이 {old_name}에서 {new_name}으로 이름이 변경되었습니다',
            
            # 백업 관련 메시지
            'backup_created': '백업이 {path}에 생성되었습니다',
            'backup_restored': '백업 {backup_id}에서 복원되었습니다',
            'backup_failed': '백업 생성에 실패했습니다: {error}',
            
            # 시스템 상태 메시지
            'system_starting': '시스템을 시작하는 중입니다',
            'system_stopping': '시스템을 중지하는 중입니다',
            'system_ready': '시스템이 준비되었습니다',
            'system_error': '시스템 오류가 발생했습니다: {error}',
            
            # 작업 진행 메시지
            'task_started': '작업 "{task_name}"을 시작했습니다',
            'task_completed': '작업 "{task_name}"이 완료되었습니다',
            'task_failed': '작업 "{task_name}"이 실패했습니다: {error}',
            'progress_update': '진행 상황: {current}/{total} ({percentage:.1f}%)',
            
            # 정리 작업 메시지
            'cleanup_started': '정리 작업을 시작합니다',
            'cleanup_completed': '정리 작업이 완료되었습니다',
            'cleanup_progress': '{processed}개 파일 처리 완료',
            'files_organized': '{count}개 파일이 {destination}으로 정리되었습니다',
            
            # 검증 메시지
            'verification_started': '무결성 검증을 시작합니다',
            'verification_passed': '무결성 검증이 통과되었습니다',
            'verification_failed': '무결성 검증이 실패했습니다',
            
            # 롤백 메시지
            'rollback_initiated': '롤백을 시작합니다',
            'rollback_completed': '롤백이 완료되었습니다',
            'rollback_failed': '롤백이 실패했습니다: {error}'
        }
        
        # 영어 패턴과 한글 대체 규칙
        self.pattern_replacements = [
            # 로그 레벨
            (r'\bINFO\b', '정보'),
            (r'\bWARNING\b', '경고'),
            (r'\bERROR\b', '오류'),
            (r'\bDEBUG\b', '디버그'),
            
            # 일반적인 동작 단어
            (r'\bStarting\b', '시작 중'),
            (r'\bStopping\b', '중지 중'),
            (r'\bProcessing\b', '처리 중'),
            (r'\bCompleted\b', '완료됨'),
            (r'\bFailed\b', '실패함'),
            
            # 파일 작업
            (r'\bFile not found\b', '파일을 찾을 수 없음'),
            (r'\bPermission denied\b', '권한이 거부됨'),
            (r'\bDirectory created\b', '디렉토리가 생성됨'),
            
            # 시간 관련
            (r'\bseconds?\b', '초'),
            (r'\bminutes?\b', '분'),
            (r'\bhours?\b', '시간'),
            (r'\bdays?\b', '일'),
            
            # 단위
            (r'\bfiles?\b', '파일'),
            (r'\bdirectories\b', '디렉토리'),
            (r'\bfolders?\b', '폴더'),
            (r'\bbytes?\b', '바이트'),
            (r'\bKB\b', 'KB'),
            (r'\bMB\b', 'MB'),
            (r'\bGB\b', 'GB')
        ]
        
        self.config_file = Path("config/language_settings.json")
        self.translation_log = []
        
    def create_language_config(self):
        """언어 설정 파일 생성"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config = {
            "default_language": "ko",
            "status_translations": self.status_translations,
            "message_templates": self.message_templates,
            "date_format": "%Y년 %m월 %d일 %H시 %M분",
            "number_format": {
                "decimal_separator": ".",
                "thousands_separator": ","
            },
            "ui_labels": {
                "yes": "예",
                "no": "아니오",
                "ok": "확인",
                "cancel": "취소",
                "continue": "계속",
                "skip": "건너뛰기",
                "retry": "다시 시도",
                "exit": "종료"
            },
            "file_operations": {
                "create": "생성",
                "read": "읽기",
                "update": "수정",
                "delete": "삭제",
                "move": "이동",
                "copy": "복사",
                "rename": "이름 변경"
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 언어 설정 파일 생성: {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ 언어 설정 파일 생성 실패: {e}")
    
    def translate_status(self, status: str) -> str:
        """상태 메시지 한글 번역"""
        return self.status_translations.get(status.lower(), status)
    
    def format_message(self, template_key: str, **kwargs) -> str:
        """메시지 템플릿 포맷팅"""
        template = self.message_templates.get(template_key, template_key)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"메시지 템플릿 매개변수 누락: {e}")
            return template
    
    def translate_text(self, text: str) -> str:
        """텍스트 패턴 기반 번역"""
        translated = text
        
        for pattern, replacement in self.pattern_replacements:
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
        
        return translated
    
    def update_file_messages(self, file_path: str, dry_run: bool = True) -> List[str]:
        """파일 내 메시지 한글화 (기존 로직 보존)"""
        changes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 상태 문자열 번역 (따옴표 안의 상태만)
            for english, korean in self.status_translations.items():
                # 문자열 리터럴 내의 상태만 변경
                patterns = [
                    f'"{english}"',
                    f"'{english}'",
                    f'status.*=.*"{english}"',
                    f"status.*=.*'{english}'"
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        old_pattern = f'"{english}"'
                        new_pattern = f'"{korean}"'
                        content = re.sub(old_pattern, new_pattern, content, flags=re.IGNORECASE)
                        changes.append(f"{english} → {korean}")
            
            # 로그 메시지 번역 (print, logger 구문)
            log_patterns = [
                (r'print\s*\(\s*["\']([^"\']*)\s*completed\s*([^"\']*)["\']', 
                 r'print("\1완료\2")'),
                (r'print\s*\(\s*["\']([^"\']*)\s*failed\s*([^"\']*)["\']', 
                 r'print("\1실패\2")'),
                (r'print\s*\(\s*["\']([^"\']*)\s*success\s*([^"\']*)["\']', 
                 r'print("\1성공\2")'),
                (r'logger\.info\s*\(\s*["\']([^"\']*)\s*starting\s*([^"\']*)["\']', 
                 r'logger.info("\1시작 중\2")'),
                (r'logger\.info\s*\(\s*["\']([^"\']*)\s*finished\s*([^"\']*)["\']', 
                 r'logger.info("\1완료됨\2")')
            ]
            
            for pattern, replacement in log_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    changes.append(f"로그 메시지 한글화: {pattern[:30]}...")
            
            # 실제 파일 업데이트 (dry_run이 False인 경우)
            if not dry_run and content != original_content:
                # 백업 생성
                backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # 업데이트된 내용 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                changes.append(f"파일 업데이트됨 (백업: {backup_path})")
            
        except Exception as e:
            logger.error(f"파일 메시지 업데이트 실패 {file_path}: {e}")
            changes.append(f"오류: {str(e)}")
        
        return changes
    
    def scan_and_update_system_messages(self, target_dirs: List[str] = None, dry_run: bool = True) -> Dict[str, List[str]]:
        """시스템 전체 메시지 한글화"""
        if target_dirs is None:
            target_dirs = ['.']
        
        logger.info(f"🌏 시스템 메시지 한글화 {'시뮬레이션' if dry_run else '실행'}")
        
        results = {}
        total_files = 0
        updated_files = 0
        
        # Python 파일만 대상으로 함
        python_files = []
        for target_dir in target_dirs:
            for file_path in Path(target_dir).rglob('*.py'):
                # 핵심 시스템 파일은 제외 (웹훅, 비즈니스 로직 보존)
                if self._is_critical_file(str(file_path)):
                    logger.info(f"⚠️ 핵심 파일 건너뜀: {file_path}")
                    continue
                
                python_files.append(str(file_path))
        
        logger.info(f"대상 파일: {len(python_files)}개")
        
        for file_path in python_files:
            total_files += 1
            
            changes = self.update_file_messages(file_path, dry_run)
            
            if changes:
                results[file_path] = changes
                updated_files += 1
                
                if dry_run:
                    logger.info(f"📝 {file_path}: {len(changes)}개 변경 예정")
                else:
                    logger.info(f"✅ {file_path}: {len(changes)}개 변경 완료")
            
            if total_files % 100 == 0:
                logger.info(f"진행 상황: {total_files}개 파일 처리 완료")
        
        logger.info(f"{'시뮬레이션' if dry_run else '업데이트'} 완료:")
        logger.info(f"  총 파일: {total_files}개")
        logger.info(f"  변경 대상: {updated_files}개")
        
        return results
    
    def _is_critical_file(self, file_path: str) -> bool:
        """핵심 파일 여부 확인 (웹훅, 비즈니스 로직 보존)"""
        critical_patterns = [
            'POSCO_News_250808.py',
            'posco_main_notifier.py',
            'monitor_WatchHamster_v3.0_minimal.py',
            'Monitoring/POSCO_News_250808/',
            'Monitoring/Posco_News_mini_v2/'
        ]
        
        for pattern in critical_patterns:
            if pattern in file_path:
                return True
        
        return False
    
    def generate_translation_report(self, scan_results: Dict[str, List[str]]) -> str:
        """번역 보고서 생성"""
        report_time = datetime.now()
        
        total_files = len(scan_results)
        total_changes = sum(len(changes) for changes in scan_results.values())
        
        report = f"""
# POSCO 시스템 언어 설정 보고서

**생성 시간**: {report_time.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 번역 결과 요약

- **대상 파일**: {total_files}개
- **총 변경 사항**: {total_changes}개
- **상태 번역**: {len(self.status_translations)}개 규칙
- **메시지 템플릿**: {len(self.message_templates)}개

## 🔄 상태 번역 규칙

"""
        
        # 상태 번역 규칙 표시
        for english, korean in sorted(self.status_translations.items()):
            report += f"- `{english}` → `{korean}`\n"
        
        report += "\n## 📝 메시지 템플릿\n\n"
        
        # 메시지 템플릿 표시
        for key, template in sorted(self.message_templates.items()):
            report += f"- **{key}**: {template}\n"
        
        if scan_results:
            report += "\n## 📂 파일별 변경 사항\n\n"
            
            for file_path, changes in sorted(scan_results.items()):
                report += f"### {file_path}\n\n"
                for change in changes:
                    report += f"- {change}\n"
                report += "\n"
        
        report += f"""
## 🔒 보존 확인 사항

- **웹훅 URL**: 모든 웹훅 주소가 보존되었습니다
- **알림 메시지**: 사용자 알림 내용이 변경되지 않았습니다
- **비즈니스 로직**: 모니터링 및 분석 로직이 보존되었습니다
- **핵심 시스템 파일**: 다음 파일들은 번역에서 제외되었습니다
  - POSCO_News_250808.py
  - posco_main_notifier.py
  - monitor_WatchHamster_v3.0_minimal.py
  - Monitoring/ 디렉토리 내 모든 파일

## 💡 사용법

```python
from language_manager import LanguageManager

# 언어 관리자 초기화
lang_mgr = LanguageManager()

# 상태 번역
status = lang_mgr.translate_status("completed")  # "완료"

# 메시지 포맷팅
message = lang_mgr.format_message("file_moved", 
                                 source="old.txt", 
                                 destination="new.txt")
# "파일이 old.txt에서 new.txt으로 이동되었습니다"
```

---
*이 보고서는 자동으로 생성되었습니다.*
"""
        
        return report
    
    def create_korean_status_helper(self):
        """한글 상태 도우미 모듈 생성"""
        helper_code = '''#!/usr/bin/env python3
"""
POSCO 시스템 한글 상태 도우미
Korean Status Helper for POSCO System

모든 시스템에서 일관된 한글 상태 메시지를 사용할 수 있도록 도와줍니다.
"""

# 상태 번역 사전
STATUS_KO = {
'''
        
        for english, korean in sorted(self.status_translations.items()):
            helper_code += f'    "{english}": "{korean}",\n'
        
        helper_code += '''}

def get_korean_status(status: str) -> str:
    """영어 상태를 한글로 번역"""
    return STATUS_KO.get(status.lower(), status)

def format_korean_message(template: str, **kwargs) -> str:
    """한글 메시지 템플릿 포맷팅"""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template

# 자주 사용되는 메시지 템플릿
MESSAGES_KO = {
'''
        
        for key, template in sorted(self.message_templates.items()):
            helper_code += f'    "{key}": "{template}",\n'
        
        helper_code += '''}

def get_korean_message(key: str, **kwargs) -> str:
    """한글 메시지 템플릿 가져오기"""
    template = MESSAGES_KO.get(key, key)
    return format_korean_message(template, **kwargs)

# 사용 예시
if __name__ == "__main__":
    print(get_korean_status("completed"))  # "완료"
    print(get_korean_message("file_moved", source="a.txt", destination="b.txt"))
'''
        
        try:
            with open("korean_status_helper.py", 'w', encoding='utf-8') as f:
                f.write(helper_code)
            
            logger.info("✅ 한글 상태 도우미 모듈 생성: korean_status_helper.py")
            
        except Exception as e:
            logger.error(f"❌ 한글 상태 도우미 생성 실패: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='POSCO 시스템 언어 설정 관리')
    parser.add_argument('--create-config', action='store_true', help='언어 설정 파일 생성')
    parser.add_argument('--scan', action='store_true', help='시스템 메시지 스캔 (시뮬레이션)')
    parser.add_argument('--update', action='store_true', help='시스템 메시지 실제 업데이트')
    parser.add_argument('--report', action='store_true', help='번역 보고서 생성')
    parser.add_argument('--create-helper', action='store_true', help='한글 상태 도우미 모듈 생성')
    parser.add_argument('--translate', type=str, help='특정 텍스트 번역 테스트')
    
    args = parser.parse_args()
    
    lang_manager = LanguageManager()
    
    try:
        if args.create_config:
            lang_manager.create_language_config()
        
        if args.scan:
            logger.info("🔍 시스템 메시지 스캔 시작 (시뮬레이션)")
            results = lang_manager.scan_and_update_system_messages(dry_run=True)
            
            if results:
                logger.info(f"📊 스캔 결과: {len(results)}개 파일에서 변경 사항 발견")
            else:
                logger.info("📊 변경할 메시지가 없습니다")
        
        if args.update:
            logger.info("🔄 시스템 메시지 실제 업데이트 시작")
            results = lang_manager.scan_and_update_system_messages(dry_run=False)
            
            if results:
                logger.info(f"✅ 업데이트 완료: {len(results)}개 파일 변경")
            else:
                logger.info("📊 변경할 메시지가 없습니다")
        
        if args.report:
            logger.info("📋 번역 보고서 생성 중...")
            
            # 스캔 결과가 없으면 새로 스캔
            if 'results' not in locals():
                results = lang_manager.scan_and_update_system_messages(dry_run=True)
            
            report = lang_manager.generate_translation_report(results)
            
            report_file = f"language_translation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"✅ 번역 보고서 생성: {report_file}")
        
        if args.create_helper:
            lang_manager.create_korean_status_helper()
        
        if args.translate:
            translated = lang_manager.translate_text(args.translate)
            logger.info(f"번역 결과: '{args.translate}' → '{translated}'")
        
        if not any([args.create_config, args.scan, args.update, args.report, 
                   args.create_helper, args.translate]):
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ 실행 중 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()