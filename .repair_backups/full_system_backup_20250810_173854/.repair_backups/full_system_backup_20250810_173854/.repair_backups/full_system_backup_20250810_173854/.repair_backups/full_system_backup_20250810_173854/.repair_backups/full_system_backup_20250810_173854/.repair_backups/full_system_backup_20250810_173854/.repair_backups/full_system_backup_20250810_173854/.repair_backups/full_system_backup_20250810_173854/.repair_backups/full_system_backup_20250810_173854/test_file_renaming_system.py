#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test File Renaming System
POSCO 시스템 테스트

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import tempfile
import shutil
from pathlib import Path
import unittest
# REMOVED: from file_renaming_system.py import FileRenamingSystem, ComponentType, MappingEntry
# REMOVED: from naming_convention_manager.py import NamingConventionManager


class TestFileRenamingSystem(unittest.TestCase):
    """파일 리네이밍 시스템 테스트 클래스"""
    
    def setUp(self):
        """테스트 환경 설정"""
        # 임시 디렉토리 생성
        self.test_dir = Path(tempfile.mkdtemp())
        self.renaming_system = FileRenamingSystem(str(self.test_dir))
        
        # 테스트용 파일 및 폴더 생성
        self.create_test_files()
    
    def tearDown(self):
        """테스트 환경 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """테스트용 파일 및 폴더 생성"""
        # 워치햄스터 관련 파일들
        watchhamster_files = [
            ".naming_backup/config_data_backup/watchhamster.log",
# REMOVED:             "verify_folder_reorganization.py",
# REMOVED:             "final_integration_test_system.py",
            ".naming_backup/config_data_backup/watchhamster.log"
        ]
        
        # POSCO News 250808 관련 파일들
POSCO_News_250808_files =  [
# REMOVED:             "POSCO News 250808_mini.py",
            "Monitoring/POSCO_News_250808/posco_main_notifier.py",
            "posco_continuous_monitor.py",
# REMOVED:             "POSCO News 250808_data.json"
        ]
        
        # 워치햄스터 관련 폴더들
        watchhamster_folders = [
            "WatchHamster_v3.0",
            "watchhamster-v3.0-integration"
        ]
        
        # POSCO News 250808 관련 폴더들
POSCO_News_250808_folders =  [
            "POSCO News 250808_mini"
        ]
        
        # 파일 생성
        for filename in watchhamster_files + POSCO News 250808_files:
            file_path = self.test_dir / filename
            file_path.write_text(f"# Test content for {filename}/n", encoding='utf-8')
        
        # 폴더 생성
        for foldername in watchhamster_folders + POSCO News 250808_folders:
            folder_path = self.test_dir / foldername
            folder_path.mkdir(exist_ok=True)
            # 폴더 안에 테스트 파일 생성
# REMOVED: (folder_path_/_"test_file.txt").write_text("test_content",_encoding = 'utf-8')
    
    def test_analyze_existing_files(self):
        """기존 파일 분석 테스트"""
        mapping_by_component = self.renaming_system.analyze_existing_files()
        
        # 워치햄스터 관련 매핑이 있는지 확인
        self.assertGreater(len(mapping_by_component[ComponentType.WATCHHAMSTER]), 0)
        
        # POSCO News 250808 관련 매핑이 있는지 확인
        self.assertGreater(len(mapping_by_component[ComponentType.POSCO News 250808]), 0)
        
        # 매핑 테이블이 생성되었는지 확인
        self.assertGreater(len(self.renaming_system.mapping_table), 0)
        
        print(f"분석된 매핑 수: {len(self.renaming_system.mapping_table)}")
        for entry in self.renaming_system.mapping_table[:5]:  # 처음 5개만 출력
            print(f"  {entry.original_path} → {entry.new_path} ({entry.component.value})")
    
    def test_rename_watchhamster_files_dry_run(self):
        """워치햄스터 파일 이름 변경 드라이 런 테스트"""
        # 먼저 파일 분석
        self.renaming_system.analyze_existing_files()
        
        # 드라이 런 실행
        operations = self.renaming_system.rename_watchhamster_files(dry_run=True)
        
        # 작업이 수행되었는지 확인
        self.assertGreater(len(operations), 0)
        
        # 모든 작업이 성공으로 표시되었는지 확인 (드라이 런이므로)
        for operation in operations:
            self.assertTrue(operation.success)
        
        print(f"워치햄스터 드라이 런 작업 수: {len(operations)}")
        for operation in operations[:3]:  # 처음 3개만 출력
            print(f"  {operation.source_path} → {operation.target_path}")
    
    def test_rename_POSCO News 250808_files_dry_run(self):
        """POSCO News 250808 파일 이름 변경 드라이 런 테스트"""
        # 먼저 파일 분석
        self.renaming_system.analyze_existing_files()
        
        # 드라이 런 실행
        operations = self.renaming_system.rename_POSCO News 250808_files(dry_run=True)
        
        # 작업이 수행되었는지 확인
        self.assertGreater(len(operations), 0)
        
        # 모든 작업이 성공으로 표시되었는지 확인 (드라이 런이므로)
        for operation in operations:
            self.assertTrue(operation.success)
        
        print(f"POSCO News 250808 드라이 런 작업 수: {len(operations)}")
        for operation in operations[:3]:  # 처음 3개만 출력
            print(f"  {operation.source_path} → {operation.target_path}")
    
    def test_actual_file_renaming(self):
        """실제 파일 이름 변경 테스트"""
        # 먼저 파일 분석
        self.renaming_system.analyze_existing_files()
        
        # 변경 전 파일 목록 저장
        original_files = list(self.test_dir.glob("*"))
        
        # 워치햄스터 파일 이름 변경
        wh_operations = self.renaming_system.rename_watchhamster_files(dry_run=False)
        
        # POSCO News 250808 파일 이름 변경
        pn_operations = self.renaming_system.rename_POSCO News 250808_files(dry_run=False)
        
        # 변경 후 파일 목록
        new_files = list(self.test_dir.glob("*"))
        
        print(f"실제 변경 작업 수: {len(wh_operations + pn_operations)}")
        print(f"변경 전 파일 수: {len(original_files)}")
        print(f"변경 후 파일 수: {len(new_files)}")
        
        # 성공한 작업이 있는지 확인
        successful_operations = [op for op in wh_operations + pn_operations if op.success]
        self.assertGreater(len(successful_operations), 0)
        
        print(f"성공한 작업 수: {len(successful_operations)}")
    
    def test_rollback_functionality(self):
        """롤백 기능 테스트"""
        # 먼저 파일 분석 및 변경
        self.renaming_system.analyze_existing_files()
        operations = self.renaming_system.rename_watchhamster_files(dry_run=False)
        
        # 성공한 작업이 있는 경우에만 롤백 테스트
        successful_operations = [op for op in operations if op.success]
        if successful_operations:
            # 롤백 실행
            rollback_success = self.renaming_system.rollback_operations()
            self.assertTrue(rollback_success)
            
            print(f"롤백 완료: {len(successful_operations)}개 작업")
    
    def test_mapping_table_persistence(self):
        """매핑 테이블 저장/로드 테스트"""
        # 파일 분석
        self.renaming_system.analyze_existing_files()
        original_mapping_count = len(self.renaming_system.mapping_table)
        
        # 매핑 테이블 파일이 생성되었는지 확인
        self.assertTrue(self.renaming_system.mapping_table_file.exists())
        
        # 새로운 시스템 인스턴스로 로드 테스트
        new_system = FileRenamingSystem(str(self.test_dir))
        # 매핑 테이블은 analyze_existing_files에서 생성되므로 다시 분석
        new_system.analyze_existing_files()
        
        print(f"원본 매핑 수: {original_mapping_count}")
        print(f"새로 로드된 매핑 수: {len(new_system.mapping_table)}")
    
    def test_operations_log_persistence(self):
        """작업 로그 저장/로드 테스트"""
        # 파일 분석 및 작업 수행
        self.renaming_system.analyze_existing_files()
        operations = self.renaming_system.rename_watchhamster_files(dry_run=True)
        
        # 작업 로그 저장
        self.renaming_system._save_operations_log()
        
        # 작업 로그 파일이 생성되었는지 확인
        self.assertTrue(self.renaming_system.operations_log_file.exists())
        
        # 새로운 시스템 인스턴스로 로드 테스트
        new_system = FileRenamingSystem(str(self.test_dir))
        load_success = new_system.load_previous_operations()
        
        if load_success:
            self.assertEqual(len(new_system.operations_log), len(operations))
            print(f"로드된 작업 로그 수: {len(new_system.operations_log)}")
    
    def test_generate_reports(self):
        """보고서 생성 테스트"""
        # 파일 분석 및 작업 수행
        self.renaming_system.analyze_existing_files()
        self.renaming_system.rename_watchhamster_files(dry_run=True)
        
        # 작업 보고서 생성
        operations_report = self.renaming_system.generate_operations_report()
        self.assertIsInstance(operations_report, str)
        self.assertGreater(len(operations_report), 0)
        
        # 매핑 요약 생성
        mapping_summary = self.renaming_system.get_mapping_summary()
        self.assertIsInstance(mapping_summary, dict)
        self.assertIn("total_mappings", mapping_summary)
        
        print("작업 보고서 생성 완료")
        print(f"매핑 요약: {mapping_summary}")


def run_integration_test():
    """통합 테스트 실행"""
    print("POSCO 파일 리네이밍 시스템 통합 테스트")
    print("=" * 50)
    
    # 실제 워크스페이스에서 테스트 (드라이 런만)
    real_system = FileRenamingSystem(".")
    
    print("/n1. 실제 파일 분석 중...")
    mapping_by_component = real_system.analyze_existing_files()
    
    summary = real_system.get_mapping_summary()
    print(f"/n실제 워크스페이스 분석 결과:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print(f"/n2. 워치햄스터 파일 변경 시뮬레이션...")
    wh_operations = real_system.rename_watchhamster_files(dry_run=True)
    print(f"워치햄스터 변경 예정: {len(wh_operations)}개")
    
    print(f"/n3. POSCO News 250808 파일 변경 시뮬레이션...")
    pn_operations = real_system.rename_POSCO News 250808_files(dry_run=True)
    print(f"POSCO News 250808 변경 예정: {len(pn_operations)}개")
    
    # 변경 예정 파일들 출력 (처음 10개만)
    all_operations = wh_operations + pn_operations
    successful_ops = [op for op in all_operations if op.success]
    
    print(f"/n4. 변경 예정 파일들 (처음 10개):")
    for i, operation in enumerate(successful_ops[:10]):
        source_name = Path(operation.source_path).name
        target_name = Path(operation.target_path).name
        print(f"  {i+1}. {source_name} → {target_name}")
    
    if len(successful_ops) > 10:
        print(f"  ... 외 {len(successful_ops) - 10}개 더")
    
    # 보고서 생성
    report = real_system.generate_operations_report()
    report_file = Path("file_renaming_simulation_report.txt")
with_open(report_file,_'w',_encoding = 'utf-8') as f:
        f.write(report)
    
    print(f"/n5. 시뮬레이션 보고서 저장: {report_file}")
    print("/n통합 테스트 완료!")


if __name__ == "__main__":
    # 단위 테스트 실행
    print("단위 테스트 실행 중...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
print("/n"_+_" = "*50)
    
    # 통합 테스트 실행
    run_integration_test()