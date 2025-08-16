#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 파일 구조 정리 및 최적화 도구
현재 4,602개 파일을 1,743개로 최적화
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import hashlib

class FileStructureOptimizer:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.backup_folders = [
            ".aggressive_syntax_repair_backup",
            ".comprehensive_repair_backup", 
            ".enhanced_repair_backups",
            ".file_reference_backup",
            ".file_renaming_backup",
            ".filename_standardization_backup",
            ".final_file_reference_cleanup_backup",
            ".final_reference_cleanup_backup",
            ".final_syntax_repair_backup",
            ".focused_file_reference_backup",
            ".indentation_backup",
            ".naming_backup",
            ".refined_file_reference_backup",
            ".repair_backups",
            ".syntax_repair_backup"
        ]
        
        self.temp_folders = [
            "__pycache__",
            "cache",
            "logs",
            "migration_logs",
            "migration_reports",
            "analysis_reports",
            "reports",
            "webhook_backup",
            "deployment_backup_20250810_185935"
        ]
        
        self.duplicate_patterns = [
            r".*\.backup.*",
            r".*\.old$",
            r".*_old\.py$",
            r".*\.backup_emergency$",
            r".*_backup_\d+.*"
        ]
        
        self.optimization_report = {
            "start_time": datetime.now().isoformat(),
            "initial_file_count": 0,
            "final_file_count": 0,
            "removed_folders": [],
            "removed_files": [],
            "renamed_files": [],
            "duplicate_files": [],
            "optimization_summary": {}
        }
    
    def analyze_current_structure(self) -> Dict:
        """현재 파일 구조 분석"""
        print("📊 현재 파일 구조를 분석하고 있습니다...")
        
        analysis = {
            "total_files": 0,
            "total_folders": 0,
            "backup_folders": [],
            "temp_folders": [],
            "duplicate_files": [],
            "large_files": [],
            "file_types": {},
            "folder_sizes": {}
        }
        
        for root, dirs, files in os.walk(self.workspace_root):
            root_path = Path(root)
            relative_root = root_path.relative_to(self.workspace_root)
            
            # 폴더 분석
            analysis["total_folders"] += len(dirs)
            
            # 백업 폴더 식별
            for folder in dirs:
                if folder in self.backup_folders:
                    analysis["backup_folders"].append(str(relative_root / folder))
                elif folder in self.temp_folders:
                    analysis["temp_folders"].append(str(relative_root / folder))
            
            # 파일 분석
            for file in files:
                file_path = root_path / file
                relative_path = file_path.relative_to(self.workspace_root)
                
                analysis["total_files"] += 1
                
                # 파일 확장자별 분류
                ext = file_path.suffix.lower()
                analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                
                # 큰 파일 식별 (10MB 이상)
                try:
                    size = file_path.stat().st_size
                    if size > 10 * 1024 * 1024:  # 10MB
                        analysis["large_files"].append({
                            "path": str(relative_path),
                            "size_mb": round(size / (1024 * 1024), 2)
                        })
                except:
                    pass
                
                # 중복 파일 패턴 확인
                for pattern in self.duplicate_patterns:
                    if re.match(pattern, file):
                        analysis["duplicate_files"].append(str(relative_path))
                        break
        
        self.optimization_report["initial_file_count"] = analysis["total_files"]
        
        print(f"✅ 분석 완료:")
        print(f"   - 총 파일 수: {analysis['total_files']:,}개")
        print(f"   - 총 폴더 수: {analysis['total_folders']:,}개")
        print(f"   - 백업 폴더: {len(analysis['backup_folders'])}개")
        print(f"   - 임시 폴더: {len(analysis['temp_folders'])}개")
        print(f"   - 중복 파일: {len(analysis['duplicate_files'])}개")
        
        return analysis
    
    def remove_backup_folders(self) -> List[str]:
        """백업 폴더들 제거"""
        print("🗂️ 불필요한 백업 폴더들을 제거하고 있습니다...")
        
        removed_folders = []
        
        for folder_name in self.backup_folders:
            folder_path = self.workspace_root / folder_name
            if folder_path.exists() and folder_path.is_dir():
                try:
                    # 폴더 크기 계산
                    total_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
                    size_mb = round(total_size / (1024 * 1024), 2)
                    
                    shutil.rmtree(folder_path)
                    removed_folders.append(f"{folder_name} ({size_mb}MB)")
                    print(f"   ✅ 제거됨: {folder_name} ({size_mb}MB)")
                except Exception as e:
                    print(f"   ❌ 제거 실패: {folder_name} - {e}")
        
        self.optimization_report["removed_folders"] = removed_folders
        return removed_folders
    
    def remove_temp_folders(self) -> List[str]:
        """임시 폴더들 제거"""
        print("📁 임시 폴더들을 정리하고 있습니다...")
        
        removed_temp = []
        
        for folder_name in self.temp_folders:
            for folder_path in self.workspace_root.rglob(folder_name):
                if folder_path.is_dir():
                    try:
                        # 중요한 파일이 있는지 확인
                        important_files = []
                        for file_path in folder_path.rglob('*'):
                            if file_path.is_file() and file_path.suffix in ['.py', '.md', '.json', '.yaml', '.yml']:
                                # 최근 수정된 파일인지 확인
                                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                                if (datetime.now() - mtime).days < 7:
                                    important_files.append(str(file_path))
                        
                        if not important_files:
                            total_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
                            size_mb = round(total_size / (1024 * 1024), 2)
                            
                            shutil.rmtree(folder_path)
                            removed_temp.append(f"{folder_path.relative_to(self.workspace_root)} ({size_mb}MB)")
                            print(f"   ✅ 제거됨: {folder_path.relative_to(self.workspace_root)} ({size_mb}MB)")
                        else:
                            print(f"   ⚠️ 보존됨: {folder_path.relative_to(self.workspace_root)} (중요 파일 {len(important_files)}개)")
                    except Exception as e:
                        print(f"   ❌ 제거 실패: {folder_path} - {e}")
        
        return removed_temp
    
    def identify_duplicate_files(self) -> List[Dict]:
        """중복 파일 식별"""
        print("🔍 중복 파일을 식별하고 있습니다...")
        
        file_hashes = {}
        duplicates = []
        
        for file_path in self.workspace_root.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts[1:]):
                try:
                    # 파일 해시 계산
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    relative_path = file_path.relative_to(self.workspace_root)
                    
                    if file_hash in file_hashes:
                        duplicates.append({
                            "original": file_hashes[file_hash],
                            "duplicate": str(relative_path),
                            "hash": file_hash
                        })
                    else:
                        file_hashes[file_hash] = str(relative_path)
                        
                except Exception as e:
                    continue
        
        print(f"   📋 중복 파일 {len(duplicates)}개 발견")
        self.optimization_report["duplicate_files"] = duplicates
        return duplicates
    
    def remove_duplicate_files(self, duplicates: List[Dict]) -> List[str]:
        """중복 파일 제거"""
        print("🗑️ 중복 파일을 제거하고 있습니다...")
        
        removed_files = []
        
        for dup in duplicates:
            duplicate_path = self.workspace_root / dup["duplicate"]
            
            # 백업 파일이나 임시 파일 우선 제거
            if any(pattern in dup["duplicate"] for pattern in [".backup", "_old", ".emergency"]):
                try:
                    duplicate_path.unlink()
                    removed_files.append(dup["duplicate"])
                    print(f"   ✅ 제거됨: {dup['duplicate']}")
                except Exception as e:
                    print(f"   ❌ 제거 실패: {dup['duplicate']} - {e}")
        
        self.optimization_report["removed_files"] = removed_files
        return removed_files
    
    def standardize_filenames(self) -> List[Dict]:
        """파일명 표준화"""
        print("📝 파일명을 표준화하고 있습니다...")
        
        renamed_files = []
        
        # 한국어/영어 파일명 규칙
        korean_patterns = {
            r"워치햄스터": "watchhamster",
            r"제어센터": "control_center", 
            r"알림": "notification",
            r"모니터링": "monitoring",
            r"시스템": "system",
            r"테스트": "test",
            r"설정": "config",
            r"보고서": "report"
        }
        
        for file_path in self.workspace_root.rglob('*'):
            if file_path.is_file():
                original_name = file_path.name
                new_name = original_name
                
                # 한국어 → 영어 변환
                for korean, english in korean_patterns.items():
                    if korean in new_name:
                        new_name = re.sub(korean, english, new_name)
                
                # 특수문자 정리
                new_name = re.sub(r'[🎛️🐹🚀🔄🔍🔔🔧🗂️🛠️📋🎨]', '', new_name)
                new_name = re.sub(r'[^\w\-_.]', '_', new_name)
                new_name = re.sub(r'_+', '_', new_name)
                new_name = new_name.strip('_')
                
                if new_name != original_name and new_name:
                    new_path = file_path.parent / new_name
                    if not new_path.exists():
                        try:
                            file_path.rename(new_path)
                            renamed_files.append({
                                "original": original_name,
                                "new": new_name,
                                "path": str(file_path.parent.relative_to(self.workspace_root))
                            })
                            print(f"   ✅ 이름 변경: {original_name} → {new_name}")
                        except Exception as e:
                            print(f"   ❌ 이름 변경 실패: {original_name} - {e}")
        
        self.optimization_report["renamed_files"] = renamed_files
        return renamed_files
    
    def optimize_folder_structure(self) -> Dict:
        """폴더 구조 최적화"""
        print("📂 폴더 구조를 최적화하고 있습니다...")
        
        # 핵심 폴더 구조 정의
        core_structure = {
            "core": "핵심 시스템 모듈",
            "config": "설정 파일",
            "scripts": "실행 스크립트",
            "tools": "유틸리티 도구",
            "docs": "문서",
            "recovery_config": "복구 설정",
            ".kiro": "Kiro 설정"
        }
        
        optimization_summary = {
            "preserved_folders": list(core_structure.keys()),
            "created_folders": [],
            "moved_files": []
        }
        
        # 필요한 폴더 생성
        for folder_name in core_structure.keys():
            folder_path = self.workspace_root / folder_name
            if not folder_path.exists():
                folder_path.mkdir(exist_ok=True)
                optimization_summary["created_folders"].append(folder_name)
                print(f"   ✅ 폴더 생성: {folder_name}")
        
        return optimization_summary
    
    def generate_optimization_report(self) -> str:
        """최적화 보고서 생성"""
        print("📊 최적화 보고서를 생성하고 있습니다...")
        
        # 최종 파일 수 계산
        final_count = sum(1 for _ in self.workspace_root.rglob('*') if _.is_file())
        self.optimization_report["final_file_count"] = final_count
        self.optimization_report["end_time"] = datetime.now().isoformat()
        
        # 최적화 요약
        removed_count = len(self.optimization_report["removed_files"])
        renamed_count = len(self.optimization_report["renamed_files"])
        folder_count = len(self.optimization_report["removed_folders"])
        
        self.optimization_report["optimization_summary"] = {
            "files_removed": removed_count,
            "files_renamed": renamed_count,
            "folders_removed": folder_count,
            "size_reduction": self.optimization_report["initial_file_count"] - final_count,
            "optimization_percentage": round((self.optimization_report["initial_file_count"] - final_count) / self.optimization_report["initial_file_count"] * 100, 2)
        }
        
        # 보고서 파일 저장
        report_path = self.workspace_root / "file_structure_optimization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_report, f, ensure_ascii=False, indent=2)
        
        # 요약 보고서 생성
        summary = f"""
# 파일 구조 최적화 완료 보고서

## 최적화 결과
- **시작 파일 수**: {self.optimization_report['initial_file_count']:,}개
- **최종 파일 수**: {final_count:,}개
- **제거된 파일**: {removed_count:,}개
- **최적화율**: {self.optimization_report['optimization_summary']['optimization_percentage']}%

## 제거된 백업 폴더
{chr(10).join(f"- {folder}" for folder in self.optimization_report['removed_folders'])}

## 파일명 표준화
- 이름 변경된 파일: {renamed_count}개
- 한국어 → 영어 변환 적용
- 특수문자 정리 완료

## 목표 달성도
- 목표: 1,743개 파일
- 현재: {final_count:,}개 파일
- 목표 대비: {'✅ 달성' if final_count <= 1743 else f'❌ 초과 ({final_count - 1743}개)'}

최적화 작업이 성공적으로 완료되었습니다!
"""
        
        summary_path = self.workspace_root / "optimization_summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("✅ 최적화 보고서가 생성되었습니다:")
        print(f"   - 상세 보고서: {report_path}")
        print(f"   - 요약 보고서: {summary_path}")
        
        return summary

def main():
    """메인 실행 함수"""
    print("🚀 POSCO 시스템 파일 구조 최적화를 시작합니다...")
    print("=" * 60)
    
    optimizer = FileStructureOptimizer()
    
    try:
        # 1. 현재 구조 분석
        analysis = optimizer.analyze_current_structure()
        
        # 2. 백업 폴더 제거
        removed_backups = optimizer.remove_backup_folders()
        
        # 3. 임시 폴더 정리
        removed_temps = optimizer.remove_temp_folders()
        
        # 4. 중복 파일 식별 및 제거
        duplicates = optimizer.identify_duplicate_files()
        removed_duplicates = optimizer.remove_duplicate_files(duplicates)
        
        # 5. 파일명 표준화
        renamed_files = optimizer.standardize_filenames()
        
        # 6. 폴더 구조 최적화
        structure_optimization = optimizer.optimize_folder_structure()
        
        # 7. 최적화 보고서 생성
        summary = optimizer.generate_optimization_report()
        
        print("=" * 60)
        print("🎉 파일 구조 최적화가 완료되었습니다!")
        print(summary)
        
    except Exception as e:
        print(f"❌ 최적화 중 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()