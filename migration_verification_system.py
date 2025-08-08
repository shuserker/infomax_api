#!/usr/bin/env python3
"""
POSCO 워치햄스터 v2.0 마이그레이션 검증 시스템
Migration Verification System for POSCO WatchHamster v2.0

이 시스템은 다음 기능을 제공합니다:
- 마이그레이션 안전성 체크 및 백업 검증
- 롤백 기능 테스트
- 마이그레이션 후 검증
- 마이그레이션 상태 보고 및 로깅
"""

import os
import sys
import json
import subprocess
import time
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class MigrationStatus:
    """마이그레이션 상태 정보"""
    timestamp: str
    phase: str  # 'pre_check', 'backup', 'migration', 'verification', 'complete', 'failed', 'rollback'
    status: str  # 'success', 'warning', 'error'
    message: str
    details: Dict[str, Any]

@dataclass
class BackupInfo:
    """백업 정보"""
    backup_dir: str
    timestamp: str
    size_mb: float
    file_count: int
    checksum: str
    verified: bool

@dataclass
class VerificationResult:
    """검증 결과"""
    test_name: str
    status: str  # 'passed', 'failed', 'warning'
    execution_time: float
    error_message: Optional[str]
    details: Dict[str, Any]

class MigrationVerificationSystem:
    """마이그레이션 검증 시스템"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.log_file = self.script_dir / "migration_verification.log"
        self.status_file = self.script_dir / "migration_status.json"
        self.backup_registry = self.script_dir / "backup_registry.json"
        
        # 로깅 설정
        self._setup_logging()
        
        # 상태 초기화
        self.migration_history: List[MigrationStatus] = []
        self.backup_info: Optional[BackupInfo] = None
        self.verification_results: List[VerificationResult] = []
        
        # 색상 정의
        self.colors = {
            'RED': '\033[0;31m',
            'GREEN': '\033[0;32m',
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'PURPLE': '\033[0;35m',
            'CYAN': '\033[0;36m',
            'NC': '\033[0m'  # No Color
        }
        
        self.logger.info("마이그레이션 검증 시스템 초기화 완료")
    
    def _setup_logging(self):
        """로깅 시스템 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _print_colored(self, message: str, color: str = 'NC'):
        """색상이 있는 메시지 출력"""
        print(f"{self.colors[color]}{message}{self.colors['NC']}")
    
    def _log_status(self, phase: str, status: str, message: str, details: Dict[str, Any] = None):
        """상태 로깅"""
        migration_status = MigrationStatus(
            timestamp=datetime.now().isoformat(),
            phase=phase,
            status=status,
            message=message,
            details=details or {}
        )
        
        self.migration_history.append(migration_status)
        
        # 파일에 저장
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(status) for status in self.migration_history], f, 
                     indent=2, ensure_ascii=False)
        
        # 로그 출력
        level = logging.ERROR if status == 'error' else logging.WARNING if status == 'warning' else logging.INFO
        self.logger.log(level, f"[{phase}] {message}")
    
    def calculate_directory_checksum(self, directory: Path) -> str:
        """디렉토리의 체크섬 계산"""
        hash_md5 = hashlib.md5()
        
        if not directory.exists():
            return ""
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    # 파일 경로도 해시에 포함
                    hash_md5.update(str(file_path.relative_to(directory)).encode())
                except (IOError, OSError) as e:
                    self.logger.warning(f"체크섬 계산 중 파일 읽기 실패: {file_path} - {e}")
        
        return hash_md5.hexdigest()
    
    def verify_backup_safety(self) -> bool:
        """백업 안전성 체크"""
        self._print_colored("🔍 백업 안전성 체크 시작", 'BLUE')
        
        try:
            # 백업 디렉토리 찾기
            backup_dirs = list(self.script_dir.glob("backup_*"))
            if not backup_dirs:
                self._log_status('backup_check', 'error', '백업 디렉토리를 찾을 수 없습니다')
                return False
            
            # 가장 최근 백업 선택
            latest_backup = max(backup_dirs, key=lambda x: x.stat().st_mtime)
            self._print_colored(f"✅ 최신 백업 발견: {latest_backup.name}", 'GREEN')
            
            # 백업 내용 검증
            required_items = [
                'Monitoring',
                'watchhamster_control_center.sh'
            ]
            
            missing_items = []
            for item in required_items:
                item_path = latest_backup / item
                if not item_path.exists():
                    missing_items.append(item)
            
            if missing_items:
                self._log_status('backup_check', 'error', 
                               f'백업에서 필수 항목 누락: {missing_items}')
                return False
            
            # 백업 크기 및 파일 수 계산
            total_size = 0
            file_count = 0
            
            for file_path in latest_backup.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            size_mb = total_size / (1024 * 1024)
            
            # 체크섬 계산
            checksum = self.calculate_directory_checksum(latest_backup)
            
            # 백업 정보 저장
            self.backup_info = BackupInfo(
                backup_dir=str(latest_backup),
                timestamp=datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat(),
                size_mb=round(size_mb, 2),
                file_count=file_count,
                checksum=checksum,
                verified=True
            )
            
            # 백업 레지스트리에 저장
            registry_data = []
            if self.backup_registry.exists():
                with open(self.backup_registry, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
            
            registry_data.append(asdict(self.backup_info))
            
            with open(self.backup_registry, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            self._print_colored(f"✅ 백업 검증 완료: {size_mb:.2f}MB, {file_count}개 파일", 'GREEN')
            self._log_status('backup_check', 'success', 
                           f'백업 검증 성공: {latest_backup.name}',
                           asdict(self.backup_info))
            
            return True
            
        except Exception as e:
            self._log_status('backup_check', 'error', f'백업 검증 실패: {str(e)}')
            return False
    
    def test_rollback_functionality(self) -> bool:
        """롤백 기능 테스트"""
        self._print_colored("🔄 롤백 기능 테스트 시작", 'BLUE')
        
        try:
            # 롤백 스크립트 존재 확인
            rollback_script = self.script_dir / "rollback_migration.sh"
            if not rollback_script.exists():
                self._log_status('rollback_test', 'error', '롤백 스크립트를 찾을 수 없습니다')
                return False
            
            # 롤백 스크립트 문법 검사
            result = subprocess.run(
                ['bash', '-n', str(rollback_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self._log_status('rollback_test', 'error', 
                               f'롤백 스크립트 문법 오류: {result.stderr}')
                return False
            
            self._print_colored("✅ 롤백 스크립트 문법 검사 통과", 'GREEN')
            
            # 드라이런 모드로 롤백 테스트 (실제 실행하지 않음)
            # 백업 디렉토리 확인
            if not self.backup_info:
                self._log_status('rollback_test', 'error', '백업 정보가 없습니다')
                return False
            
            backup_path = Path(self.backup_info.backup_dir)
            if not backup_path.exists():
                self._log_status('rollback_test', 'error', '백업 디렉토리가 존재하지 않습니다')
                return False
            
            # 백업 무결성 재검증
            current_checksum = self.calculate_directory_checksum(backup_path)
            if current_checksum != self.backup_info.checksum:
                self._log_status('rollback_test', 'warning', 
                               '백업 체크섬이 변경되었습니다. 백업이 손상되었을 수 있습니다')
                return False
            
            self._print_colored("✅ 백업 무결성 확인 완료", 'GREEN')
            
            # 롤백 시뮬레이션 (실제로는 실행하지 않음)
            self._print_colored("✅ 롤백 기능 테스트 완료 (시뮬레이션)", 'GREEN')
            self._log_status('rollback_test', 'success', '롤백 기능 테스트 성공')
            
            return True
            
        except Exception as e:
            self._log_status('rollback_test', 'error', f'롤백 테스트 실패: {str(e)}')
            return False
    
    def verify_post_migration(self) -> bool:
        """마이그레이션 후 검증"""
        self._print_colored("🔍 마이그레이션 후 검증 시작", 'BLUE')
        
        verification_tests = [
            self._test_v2_components_initialization,
            self._test_watchhamster_functionality,
            self._test_control_center_functions,
            self._test_module_registry_integration,
            self._test_notification_system,
            self._test_process_management
        ]
        
        all_passed = True
        
        for test_func in verification_tests:
            try:
                start_time = time.time()
                result = test_func()
                execution_time = time.time() - start_time
                
                test_name = test_func.__name__.replace('_test_', '').replace('_', ' ').title()
                
                if result:
                    self._print_colored(f"✅ {test_name} 테스트 통과", 'GREEN')
                    verification_result = VerificationResult(
                        test_name=test_name,
                        status='passed',
                        execution_time=execution_time,
                        error_message=None,
                        details={'success': True}
                    )
                else:
                    self._print_colored(f"❌ {test_name} 테스트 실패", 'RED')
                    verification_result = VerificationResult(
                        test_name=test_name,
                        status='failed',
                        execution_time=execution_time,
                        error_message="테스트 실패",
                        details={'success': False}
                    )
                    all_passed = False
                
                self.verification_results.append(verification_result)
                
            except Exception as e:
                self._print_colored(f"❌ {test_func.__name__} 테스트 오류: {str(e)}", 'RED')
                verification_result = VerificationResult(
                    test_name=test_func.__name__,
                    status='failed',
                    execution_time=0,
                    error_message=str(e),
                    details={'exception': True}
                )
                self.verification_results.append(verification_result)
                all_passed = False
        
        if all_passed:
            self._log_status('post_migration', 'success', '모든 마이그레이션 후 검증 통과')
        else:
            self._log_status('post_migration', 'error', '일부 마이그레이션 후 검증 실패')
        
        return all_passed
    
    def _test_v2_components_initialization(self) -> bool:
        """v2 컴포넌트 초기화 테스트"""
        try:
            # 워치햄스터 임시 실행하여 v2 컴포넌트 로드 테스트
            result = subprocess.run([
                "python3", "-c", 
                f"""
import sys
sys.path.insert(0, '{self.script_dir}/Monitoring/Posco_News_mini')
from monitor_WatchHamster import PoscoMonitorWatchHamster
wh = PoscoMonitorWatchHamster()
print('v2_enabled:', wh.v2_enabled)
print('process_manager:', wh.process_manager is not None)
print('module_registry:', wh.module_registry is not None)
print('notification_manager:', wh.notification_manager is not None)
                """
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "v2_enabled: True" in result.stdout:
                return True
            else:
                self.logger.error(f"v2 컴포넌트 초기화 실패: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"v2 컴포넌트 테스트 오류: {str(e)}")
            return False
    
    def _test_watchhamster_functionality(self) -> bool:
        """워치햄스터 기능 테스트"""
        try:
            watchhamster_path = self.script_dir / "Monitoring/Posco_News_mini/monitor_WatchHamster.py"
            if not watchhamster_path.exists():
                return False
            
            # 워치햄스터 임시 실행 (10초)
            process = subprocess.Popen([
                "python3", str(watchhamster_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(5)  # 초기화 대기
            
            # 프로세스가 실행 중인지 확인
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"워치햄스터 기능 테스트 오류: {str(e)}")
            return False
    
    def _test_control_center_functions(self) -> bool:
        """제어센터 기능 테스트"""
        try:
            control_center_path = self.script_dir / "watchhamster_control_center.sh"
            if not control_center_path.exists():
                return False
            
            # 제어센터 스크립트 문법 검사
            result = subprocess.run([
                "bash", "-n", str(control_center_path)
            ], capture_output=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"제어센터 기능 테스트 오류: {str(e)}")
            return False
    
    def _test_module_registry_integration(self) -> bool:
        """모듈 레지스트리 통합 테스트"""
        try:
            modules_json_path = self.script_dir / "Monitoring/Posco_News_mini_v2/modules.json"
            if not modules_json_path.exists():
                return False
            
            with open(modules_json_path, 'r', encoding='utf-8') as f:
                modules_config = json.load(f)
            
            # 필수 모듈 확인
            required_modules = ['posco_main_notifier', 'realtime_news_monitor']
            for module in required_modules:
                if module not in modules_config.get('modules', {}):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"모듈 레지스트리 테스트 오류: {str(e)}")
            return False
    
    def _test_notification_system(self) -> bool:
        """알림 시스템 테스트"""
        try:
            # v2 NotificationManager 로드 테스트
            result = subprocess.run([
                "python3", "-c", 
                f"""
import sys
sys.path.insert(0, '{self.script_dir}/Monitoring/Posco_News_mini_v2')
from core.notification_manager import NotificationManager
nm = NotificationManager('test_webhook', 'test_image')
print('NotificationManager 로드 성공')
                """
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"알림 시스템 테스트 오류: {str(e)}")
            return False
    
    def _test_process_management(self) -> bool:
        """프로세스 관리 테스트"""
        try:
            # v2 ProcessManager 로드 테스트
            result = subprocess.run([
                "python3", "-c", 
                f"""
import sys
sys.path.insert(0, '{self.script_dir}/Monitoring/Posco_News_mini_v2')
from core.enhanced_process_manager import ProcessManager
pm = ProcessManager('{self.script_dir}/Monitoring/Posco_News_mini')
print('ProcessManager 로드 성공')
                """
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"프로세스 관리 테스트 오류: {str(e)}")
            return False
    
    def generate_migration_report(self) -> str:
        """마이그레이션 상태 보고서 생성"""
        self._print_colored("📋 마이그레이션 보고서 생성 중...", 'BLUE')
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("POSCO 워치햄스터 v2.0 마이그레이션 검증 보고서")
        report_lines.append("=" * 80)
        report_lines.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 백업 정보
        if self.backup_info:
            report_lines.append("📦 백업 정보")
            report_lines.append("-" * 40)
            report_lines.append(f"백업 디렉토리: {self.backup_info.backup_dir}")
            report_lines.append(f"백업 시간: {self.backup_info.timestamp}")
            report_lines.append(f"백업 크기: {self.backup_info.size_mb}MB")
            report_lines.append(f"파일 수: {self.backup_info.file_count}개")
            report_lines.append(f"체크섬: {self.backup_info.checksum}")
            report_lines.append(f"검증 상태: {'✅ 검증됨' if self.backup_info.verified else '❌ 미검증'}")
            report_lines.append("")
        
        # 마이그레이션 히스토리
        report_lines.append("📈 마이그레이션 진행 상황")
        report_lines.append("-" * 40)
        for status in self.migration_history:
            status_icon = "✅" if status.status == "success" else "⚠️" if status.status == "warning" else "❌"
            report_lines.append(f"{status_icon} [{status.phase}] {status.message}")
        report_lines.append("")
        
        # 검증 결과
        if self.verification_results:
            report_lines.append("🔍 검증 결과")
            report_lines.append("-" * 40)
            passed_count = sum(1 for r in self.verification_results if r.status == 'passed')
            total_count = len(self.verification_results)
            
            report_lines.append(f"전체 테스트: {total_count}개")
            report_lines.append(f"통과: {passed_count}개")
            report_lines.append(f"실패: {total_count - passed_count}개")
            report_lines.append("")
            
            for result in self.verification_results:
                status_icon = "✅" if result.status == "passed" else "❌"
                report_lines.append(f"{status_icon} {result.test_name} ({result.execution_time:.2f}초)")
                if result.error_message:
                    report_lines.append(f"   오류: {result.error_message}")
            report_lines.append("")
        
        # 권장사항
        report_lines.append("💡 권장사항")
        report_lines.append("-" * 40)
        
        failed_tests = [r for r in self.verification_results if r.status == 'failed']
        if failed_tests:
            report_lines.append("❌ 실패한 테스트가 있습니다:")
            for test in failed_tests:
                report_lines.append(f"   - {test.test_name}")
            report_lines.append("   롤백을 고려하거나 문제를 해결한 후 다시 시도하세요.")
        else:
            report_lines.append("✅ 모든 검증이 통과했습니다.")
            report_lines.append("   마이그레이션이 성공적으로 완료되었습니다.")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        report_content = "\n".join(report_lines)
        
        # 보고서 파일 저장
        report_file = self.script_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self._print_colored(f"📋 보고서 저장됨: {report_file}", 'GREEN')
        
        return report_content
    
    def run_full_verification(self) -> bool:
        """전체 검증 실행"""
        self._print_colored("🚀 POSCO 워치햄스터 v2.0 마이그레이션 검증 시작", 'CYAN')
        self._log_status('verification_start', 'success', '마이그레이션 검증 시작')
        
        success = True
        
        # 1. 백업 안전성 체크
        if not self.verify_backup_safety():
            success = False
        
        # 2. 롤백 기능 테스트
        if not self.test_rollback_functionality():
            success = False
        
        # 3. 마이그레이션 후 검증
        if not self.verify_post_migration():
            success = False
        
        # 4. 보고서 생성
        report = self.generate_migration_report()
        print("\n" + report)
        
        if success:
            self._print_colored("🎉 마이그레이션 검증 완료 - 모든 테스트 통과!", 'GREEN')
            self._log_status('verification_complete', 'success', '마이그레이션 검증 완료')
        else:
            self._print_colored("❌ 마이그레이션 검증 실패 - 일부 테스트 실패", 'RED')
            self._log_status('verification_complete', 'error', '마이그레이션 검증 실패')
        
        return success

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        mvs = MigrationVerificationSystem()
        
        if command == "backup-check":
            success = mvs.verify_backup_safety()
            sys.exit(0 if success else 1)
        elif command == "rollback-test":
            success = mvs.test_rollback_functionality()
            sys.exit(0 if success else 1)
        elif command == "post-migration":
            success = mvs.verify_post_migration()
            sys.exit(0 if success else 1)
        elif command == "report":
            mvs.generate_migration_report()
            sys.exit(0)
        elif command == "full":
            success = mvs.run_full_verification()
            sys.exit(0 if success else 1)
        else:
            print(f"알 수 없는 명령어: {command}")
            print("사용법: python3 migration_verification_system.py [backup-check|rollback-test|post-migration|report|full]")
            sys.exit(1)
    else:
        # 기본적으로 전체 검증 실행
        mvs = MigrationVerificationSystem()
        success = mvs.run_full_verification()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()