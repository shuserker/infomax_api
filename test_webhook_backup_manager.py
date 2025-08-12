#!/usr/bin/env python3
"""
웹훅 백업 관리자 테스트 시스템
Webhook Backup Manager Test System

WebhookBackupManager의 모든 기능을 테스트하고 검증합니다.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import logging

# 테스트용 로깅 설정
logging.basicConfig(level=logging.DEBUG)

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, '.')

try:
    from webhook_backup_manager import WebhookBackupManager
except ImportError as e:
    print(f"❌ webhook_backup_manager 모듈을 가져올 수 없습니다: {e}")
    sys.exit(1)

class TestWebhookBackupManager(unittest.TestCase):
    """웹훅 백업 관리자 테스트 클래스"""
    
    def setUp(self):
        """테스트 환경 설정"""
        # 임시 테스트 디렉토리 생성
        self.test_dir = Path(tempfile.mkdtemp(prefix="webhook_backup_test_"))
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 테스트용 웹훅 파일들 생성
        self.create_test_webhook_files()
        
        # 백업 관리자 인스턴스 생성
        self.backup_manager = WebhookBackupManager()
        
        print(f"🧪 테스트 환경 설정 완료: {self.test_dir}")
    
    def tearDown(self):
        """테스트 환경 정리"""
        os.chdir(self.original_cwd)
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        print("🧹 테스트 환경 정리 완료")
    
    def create_test_webhook_files(self):
        """테스트용 웹훅 파일들 생성"""
        # core/monitoring 디렉토리 생성
        core_monitoring_dir = Path("core/monitoring")
        core_monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # 테스트용 monitor_WatchHamster_v3.0.py 파일 생성
        monitor_file = core_monitoring_dir / "monitor_WatchHamster_v3.0.py"
        monitor_content = '''#!/usr/bin/env python3
"""
테스트용 POSCO 워치햄스터 모니터링 시스템
"""

def send_status_notification(message):
    """상태 알림 전송"""
    print(f"알림 전송: {message}")
    return True

def send_notification(title, content):
    """일반 알림 전송"""
    print(f"제목: {title}, 내용: {content}")
    return True

if __name__ == "__main__":
    print("POSCO 워치햄스터 v3.0 모니터링 시스템")
'''
        
        with open(monitor_file, 'w', encoding='utf-8') as f:
            f.write(monitor_content)
        
        # 기타 테스트용 파일들 생성
        test_files = [
            "webhook_message_restorer.py",
            "webhook_config_restorer.py", 
            "compatibility_checker.py"
        ]
        
        for file_name in test_files:
            test_content = f'''#!/usr/bin/env python3
"""
테스트용 {file_name}
"""

class TestClass:
    def __init__(self):
        self.name = "{file_name}"
    
    def test_method(self):
        return f"테스트 메서드 실행: {{self.name}}"

if __name__ == "__main__":
    test_obj = TestClass()
    print(test_obj.test_method())
'''
            
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(test_content)
        
        print("✅ 테스트용 웹훅 파일들 생성 완료")
    
    def test_backup_creation(self):
        """백업 생성 테스트"""
        print("\n🧪 백업 생성 테스트 시작")
        
        backup_name = "test_backup"
        description = "테스트용 백업"
        
        # 백업 생성
        backup_id = self.backup_manager.create_backup(backup_name, description)
        
        # 백업 ID가 올바르게 생성되었는지 확인
        self.assertIsNotNone(backup_id)
        self.assertIn("webhook_backup_test_backup", backup_id)
        
        # 메타데이터에 백업 정보가 저장되었는지 확인
        self.assertIn(backup_id, self.backup_manager.metadata)
        
        backup_info = self.backup_manager.metadata[backup_id]
        self.assertEqual(backup_info['backup_name'], backup_name)
        self.assertEqual(backup_info['description'], description)
        self.assertEqual(backup_info['status'], 'completed')
        self.assertGreater(backup_info['file_count'], 0)
        
        # 백업 디렉토리가 생성되었는지 확인
        backup_path = Path(backup_info['backup_path'])
        self.assertTrue(backup_path.exists())
        
        print(f"✅ 백업 생성 테스트 통과: {backup_id}")
    
    def test_backup_listing(self):
        """백업 목록 조회 테스트"""
        print("\n🧪 백업 목록 조회 테스트 시작")
        
        # 여러 개의 백업 생성
        backup_ids = []
        for i in range(3):
            backup_id = self.backup_manager.create_backup(
                f"test_backup_{i}",
                f"테스트 백업 {i+1}"
            )
            backup_ids.append(backup_id)
        
        # 백업 목록 조회
        backups = self.backup_manager.list_backups()
        
        # 생성한 백업 수와 일치하는지 확인
        self.assertEqual(len(backups), 3)
        
        # 각 백업 정보가 올바른지 확인
        for i, backup in enumerate(backups):
            self.assertIn('backup_id', backup)
            self.assertIn('backup_name', backup)
            self.assertIn('created_at', backup)
            self.assertEqual(backup['status'], 'completed')
        
        print(f"✅ 백업 목록 조회 테스트 통과: {len(backups)}개 백업 확인")
    
    def test_backup_integrity_verification(self):
        """백업 무결성 검증 테스트"""
        print("\n🧪 백업 무결성 검증 테스트 시작")
        
        # 백업 생성
        backup_id = self.backup_manager.create_backup("integrity_test", "무결성 테스트용 백업")
        
        # 무결성 검증
        is_valid = self.backup_manager.verify_backup_integrity(backup_id)
        self.assertTrue(is_valid)
        
        # 존재하지 않는 백업 검증
        is_valid_fake = self.backup_manager.verify_backup_integrity("fake_backup_id")
        self.assertFalse(is_valid_fake)
        
        print("✅ 백업 무결성 검증 테스트 통과")
    
    def test_rollback_functionality(self):
        """롤백 기능 테스트"""
        print("\n🧪 롤백 기능 테스트 시작")
        
        # 원본 파일 내용 저장
        monitor_file = Path("core/monitoring/monitor_WatchHamster_v3.0.py")
        original_content = monitor_file.read_text(encoding='utf-8')
        
        # 백업 생성
        backup_id = self.backup_manager.create_backup("rollback_test", "롤백 테스트용 백업")
        
        # 파일 내용 변경
        modified_content = original_content + "\n# 테스트용 수정 내용\nprint('파일이 수정되었습니다')\n"
        monitor_file.write_text(modified_content, encoding='utf-8')
        
        # 파일이 실제로 변경되었는지 확인
        current_content = monitor_file.read_text(encoding='utf-8')
        self.assertNotEqual(original_content, current_content)
        self.assertIn("테스트용 수정 내용", current_content)
        
        # 롤백 실행
        rollback_success = self.backup_manager.rollback_to_backup(backup_id)
        self.assertTrue(rollback_success)
        
        # 파일이 원본으로 복원되었는지 확인
        restored_content = monitor_file.read_text(encoding='utf-8')
        self.assertEqual(original_content, restored_content)
        self.assertNotIn("테스트용 수정 내용", restored_content)
        
        print("✅ 롤백 기능 테스트 통과")
    
    def test_auto_rollback_functionality(self):
        """자동 롤백 기능 테스트"""
        print("\n🧪 자동 롤백 기능 테스트 시작")
        
        # 백업 생성
        backup_id = self.backup_manager.create_backup("auto_rollback_test", "자동 롤백 테스트용 백업")
        
        # 자동 롤백 활성화 확인
        self.assertTrue(self.backup_manager.auto_rollback_enabled)
        
        # 자동 롤백 실행
        error_context = "테스트 오류 상황"
        auto_rollback_success = self.backup_manager.auto_rollback_on_error(error_context)
        self.assertTrue(auto_rollback_success)
        
        # 자동 롤백 히스토리 확인
        auto_rollback_history = self.backup_manager.metadata.get('auto_rollback_history', [])
        self.assertGreater(len(auto_rollback_history), 0)
        
        last_auto_rollback = auto_rollback_history[-1]
        self.assertEqual(last_auto_rollback['error_context'], error_context)
        self.assertTrue(last_auto_rollback['success'])
        
        print("✅ 자동 롤백 기능 테스트 통과")
    
    def test_backup_status_reporting(self):
        """백업 상태 보고 테스트"""
        print("\n🧪 백업 상태 보고 테스트 시작")
        
        # 여러 백업 생성
        for i in range(2):
            self.backup_manager.create_backup(f"status_test_{i}", f"상태 테스트 {i+1}")
        
        # 상태 조회
        status = self.backup_manager.get_backup_status()
        
        # 상태 정보 검증
        self.assertIn('total_backups', status)
        self.assertIn('successful_backups', status)
        self.assertIn('failed_backups', status)
        self.assertIn('auto_rollback_enabled', status)
        self.assertIn('most_recent_backup', status)
        
        self.assertEqual(status['total_backups'], 2)
        self.assertEqual(status['successful_backups'], 2)
        self.assertEqual(status['failed_backups'], 0)
        self.assertTrue(status['auto_rollback_enabled'])
        self.assertIsNotNone(status['most_recent_backup'])
        
        print("✅ 백업 상태 보고 테스트 통과")
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        print("\n🧪 오류 처리 테스트 시작")
        
        # 존재하지 않는 백업으로 롤백 시도
        rollback_result = self.backup_manager.rollback_to_backup("nonexistent_backup")
        self.assertFalse(rollback_result)
        
        # 존재하지 않는 백업 무결성 검증
        integrity_result = self.backup_manager.verify_backup_integrity("nonexistent_backup")
        self.assertFalse(integrity_result)
        
        print("✅ 오류 처리 테스트 통과")
    
    def test_metadata_persistence(self):
        """메타데이터 지속성 테스트"""
        print("\n🧪 메타데이터 지속성 테스트 시작")
        
        # 백업 생성
        backup_id = self.backup_manager.create_backup("persistence_test", "지속성 테스트")
        
        # 새로운 백업 관리자 인스턴스 생성 (메타데이터 재로드)
        new_backup_manager = WebhookBackupManager()
        
        # 메타데이터가 올바르게 로드되었는지 확인
        self.assertIn(backup_id, new_backup_manager.metadata)
        
        backup_info = new_backup_manager.metadata[backup_id]
        self.assertEqual(backup_info['backup_name'], "persistence_test")
        self.assertEqual(backup_info['description'], "지속성 테스트")
        
        print("✅ 메타데이터 지속성 테스트 통과")

class WebhookBackupIntegrationTest:
    """웹훅 백업 관리자 통합 테스트"""
    
    def __init__(self):
        self.backup_manager = WebhookBackupManager()
        self.test_results = []
    
    def run_integration_tests(self):
        """통합 테스트 실행"""
        print("\n🔧 웹훅 백업 관리자 통합 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("실제 파일 백업 테스트", self.test_real_file_backup),
            ("백업 시스템 상태 테스트", self.test_backup_system_status),
            ("백업 정리 기능 테스트", self.test_backup_cleanup),
            ("실제 롤백 시나리오 테스트", self.test_real_rollback_scenario),
            ("오류 복구 시나리오 테스트", self.test_error_recovery_scenario)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 {test_name} 실행 중...")
                result = test_func()
                self.test_results.append({
                    'test_name': test_name,
                    'status': 'PASS' if result else 'FAIL',
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✅ {test_name} {'통과' if result else '실패'}")
            except Exception as e:
                self.test_results.append({
                    'test_name': test_name,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ {test_name} 오류: {e}")
        
        self.generate_test_report()
    
    def test_real_file_backup(self):
        """실제 파일 백업 테스트"""
        try:
            # 현재 존재하는 웹훅 관련 파일들 확인
            webhook_files = []
            for file_path in self.backup_manager.webhook_files:
                if Path(file_path).exists():
                    webhook_files.append(file_path)
            
            if not webhook_files:
                print("⚠️ 백업할 웹훅 파일이 없습니다")
                return True
            
            # 백업 생성
            backup_id = self.backup_manager.create_backup(
                "integration_test_real_files",
                "통합 테스트용 실제 파일 백업"
            )
            
            # 백업 검증
            is_valid = self.backup_manager.verify_backup_integrity(backup_id)
            
            print(f"   백업 ID: {backup_id}")
            print(f"   백업된 파일 수: {len(webhook_files)}개")
            print(f"   무결성 검증: {'통과' if is_valid else '실패'}")
            
            return is_valid
            
        except Exception as e:
            print(f"   실제 파일 백업 테스트 오류: {e}")
            return False
    
    def test_backup_system_status(self):
        """백업 시스템 상태 테스트"""
        try:
            status = self.backup_manager.get_backup_status()
            
            required_fields = [
                'total_backups', 'successful_backups', 'failed_backups',
                'auto_rollback_enabled', 'backup_root'
            ]
            
            for field in required_fields:
                if field not in status:
                    print(f"   필수 상태 필드 누락: {field}")
                    return False
            
            print(f"   총 백업 수: {status['total_backups']}개")
            print(f"   성공한 백업: {status['successful_backups']}개")
            print(f"   자동 롤백: {'활성화' if status['auto_rollback_enabled'] else '비활성화'}")
            
            return True
            
        except Exception as e:
            print(f"   백업 시스템 상태 테스트 오류: {e}")
            return False
    
    def test_backup_cleanup(self):
        """백업 정리 기능 테스트"""
        try:
            # 현재 백업 수 확인
            initial_backups = len(self.backup_manager.list_backups())
            
            # 최대 백업 수를 낮게 설정
            original_max = self.backup_manager.max_backup_count
            self.backup_manager.max_backup_count = 3
            
            # 여러 백업 생성 (최대 수 초과)
            for i in range(5):
                self.backup_manager.create_backup(
                    f"cleanup_test_{i}",
                    f"정리 테스트 백업 {i+1}"
                )
            
            # 백업 수가 최대 수를 초과하지 않는지 확인
            final_backups = self.backup_manager.list_backups()
            regular_backups = [b for b in final_backups if 'emergency' not in b['backup_name']]
            
            # 원래 설정 복원
            self.backup_manager.max_backup_count = original_max
            
            print(f"   초기 백업 수: {initial_backups}개")
            print(f"   최종 일반 백업 수: {len(regular_backups)}개")
            print(f"   정리 기능: {'정상 작동' if len(regular_backups) <= 3 else '오작동'}")
            
            return len(regular_backups) <= 3
            
        except Exception as e:
            print(f"   백업 정리 기능 테스트 오류: {e}")
            return False
    
    def test_real_rollback_scenario(self):
        """실제 롤백 시나리오 테스트"""
        try:
            # 테스트할 파일 선택 (존재하는 경우)
            test_file = None
            for file_path in self.backup_manager.webhook_files:
                if Path(file_path).exists():
                    test_file = Path(file_path)
                    break
            
            if not test_file:
                print("   롤백 테스트할 파일이 없습니다")
                return True
            
            # 원본 내용 저장
            original_content = test_file.read_text(encoding='utf-8')
            
            # 백업 생성
            backup_id = self.backup_manager.create_backup(
                "rollback_scenario_test",
                "롤백 시나리오 테스트용 백업"
            )
            
            # 파일 수정
            modified_content = original_content + "\n# 통합 테스트용 수정\n"
            test_file.write_text(modified_content, encoding='utf-8')
            
            # 롤백 실행
            rollback_success = self.backup_manager.rollback_to_backup(backup_id)
            
            # 복원 확인
            restored_content = test_file.read_text(encoding='utf-8')
            content_restored = (restored_content == original_content)
            
            print(f"   테스트 파일: {test_file}")
            print(f"   롤백 실행: {'성공' if rollback_success else '실패'}")
            print(f"   내용 복원: {'성공' if content_restored else '실패'}")
            
            return rollback_success and content_restored
            
        except Exception as e:
            print(f"   실제 롤백 시나리오 테스트 오류: {e}")
            return False
    
    def test_error_recovery_scenario(self):
        """오류 복구 시나리오 테스트"""
        try:
            # 백업이 있는지 확인
            recent_backup = self.backup_manager.get_most_recent_backup()
            
            if not recent_backup:
                # 테스트용 백업 생성
                recent_backup = self.backup_manager.create_backup(
                    "error_recovery_test",
                    "오류 복구 테스트용 백업"
                )
            
            # 자동 롤백 테스트
            error_context = "통합 테스트 오류 시뮬레이션"
            auto_rollback_success = self.backup_manager.auto_rollback_on_error(error_context)
            
            # 자동 롤백 히스토리 확인
            auto_rollback_history = self.backup_manager.metadata.get('auto_rollback_history', [])
            has_history = len(auto_rollback_history) > 0
            
            print(f"   최근 백업: {recent_backup}")
            print(f"   자동 롤백: {'성공' if auto_rollback_success else '실패'}")
            print(f"   히스토리 기록: {'있음' if has_history else '없음'}")
            
            return auto_rollback_success and has_history
            
        except Exception as e:
            print(f"   오류 복구 시나리오 테스트 오류: {e}")
            return False
    
    def generate_test_report(self):
        """테스트 보고서 생성"""
        print("\n" + "=" * 60)
        print("📊 웹훅 백업 관리자 통합 테스트 결과")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        print(f"총 테스트 수: {total_tests}개")
        print(f"통과: {passed_tests}개")
        print(f"실패: {failed_tests}개")
        print(f"오류: {error_tests}개")
        print(f"성공률: {(passed_tests / total_tests * 100):.1f}%")
        
        print("\n📋 상세 결과:")
        for result in self.test_results:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌', 
                'ERROR': '💥'
            }.get(result['status'], '❓')
            
            print(f"{status_icon} {result['test_name']}: {result['status']}")
            if 'error' in result:
                print(f"   오류: {result['error']}")
        
        # 결과를 JSON 파일로 저장
        report_file = f"webhook_backup_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'success_rate': passed_tests / total_tests * 100
            },
            'test_results': self.test_results,
            'generated_at': datetime.now().isoformat()
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"\n📄 상세 테스트 보고서 저장: {report_file}")
        except Exception as e:
            print(f"⚠️ 테스트 보고서 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='웹훅 백업 관리자 테스트 시스템')
    parser.add_argument('--unit', action='store_true', help='단위 테스트 실행')
    parser.add_argument('--integration', action='store_true', help='통합 테스트 실행')
    parser.add_argument('--all', action='store_true', help='모든 테스트 실행')
    
    args = parser.parse_args()
    
    if args.unit or args.all:
        print("🧪 단위 테스트 실행")
        print("=" * 50)
        
        # 단위 테스트 실행
        unittest.main(argv=[''], exit=False, verbosity=2)
    
    if args.integration or args.all:
        print("\n🔧 통합 테스트 실행")
        print("=" * 50)
        
        # 통합 테스트 실행
        integration_test = WebhookBackupIntegrationTest()
        integration_test.run_integration_tests()
    
    if not any([args.unit, args.integration, args.all]):
        parser.print_help()

if __name__ == "__main__":
    main()