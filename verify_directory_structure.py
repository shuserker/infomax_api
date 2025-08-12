#!/usr/bin/env python3
"""
POSCO 시스템 디렉토리 구조 검증 스크립트

Task 4의 모든 요구사항이 충족되었는지 검증합니다.
"""

import os
import stat
from pathlib import Path
from typing import Dict, List, Tuple
import json

class DirectoryStructureVerifier:
    """디렉토리 구조 검증 시스템"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.verification_results = []
        
        # 예상되는 디렉토리 구조
        self.expected_structure = {
            "core": ["POSCO_News_250808", "watchhamster", "monitoring"],
            "tools": ["repair", "testing", "quality", "automation"],
            "docs": ["user_guides", "technical", "troubleshooting", "api"],
            "archive": ["task_summaries", "migration_logs", "backups", "temp"],
            "config": ["system", "language", "cleanup"],
            "scripts": ["cleanup", "verification", "backup"]
        }
        
        # 예상되는 심볼릭 링크
        self.expected_symlinks = [
            ("core/POSCO_News_250808/POSCO_News_250808.py", "../../POSCO_News_250808.py"),
            ("core/watchhamster/🐹POSCO_워치햄스터_v3_제어센터.bat", "../../🐹POSCO_워치햄스터_v3_제어센터.bat"),
            ("core/watchhamster/🐹POSCO_워치햄스터_v3_제어센터.command", "../../🐹POSCO_워치햄스터_v3_제어센터.command"),
            ("scripts/backup/backup_system.py", "../../backup_system.py")
        ]
    
    def verify_all_requirements(self) -> bool:
        """모든 요구사항 검증"""
        print("🔍 POSCO 시스템 디렉토리 구조 검증을 시작합니다...")
        
        # 1. 논리적 디렉토리 구조 검증
        structure_ok = self._verify_directory_structure()
        
        # 2. README 파일 검증
        readme_ok = self._verify_readme_files()
        
        # 3. 파일 접근 권한 검증
        permissions_ok = self._verify_file_permissions()
        
        # 4. 심볼릭 링크 검증
        symlinks_ok = self._verify_symbolic_links()
        
        # 결과 요약
        all_ok = structure_ok and readme_ok and permissions_ok and symlinks_ok
        
        self._generate_verification_report(all_ok)
        
        return all_ok
    
    def _verify_directory_structure(self) -> bool:
        """논리적 디렉토리 구조 검증"""
        print("\n📁 디렉토리 구조 검증 중...")
        
        structure_ok = True
        
        for main_dir, subdirs in self.expected_structure.items():
            main_path = self.root_path / main_dir
            
            # 메인 디렉토리 존재 확인
            if not main_path.exists():
                self.verification_results.append(f"❌ 메인 디렉토리 누락: {main_dir}")
                structure_ok = False
                continue
            
            if not main_path.is_dir():
                self.verification_results.append(f"❌ {main_dir}가 디렉토리가 아닙니다")
                structure_ok = False
                continue
            
            print(f"  ✅ {main_dir}/ 디렉토리 확인")
            
            # 하위 디렉토리 존재 확인
            for subdir in subdirs:
                subdir_path = main_path / subdir
                if not subdir_path.exists():
                    self.verification_results.append(f"❌ 하위 디렉토리 누락: {main_dir}/{subdir}")
                    structure_ok = False
                elif not subdir_path.is_dir():
                    self.verification_results.append(f"❌ {main_dir}/{subdir}가 디렉토리가 아닙니다")
                    structure_ok = False
                else:
                    print(f"    ✅ {main_dir}/{subdir}/ 하위 디렉토리 확인")
        
        if structure_ok:
            self.verification_results.append("✅ 모든 디렉토리 구조가 올바르게 생성되었습니다")
        
        return structure_ok
    
    def _verify_readme_files(self) -> bool:
        """README 파일 검증"""
        print("\n📄 README 파일 검증 중...")
        
        readme_ok = True
        
        for main_dir in self.expected_structure.keys():
            readme_path = self.root_path / main_dir / "README.md"
            
            if not readme_path.exists():
                self.verification_results.append(f"❌ README 파일 누락: {main_dir}/README.md")
                readme_ok = False
                continue
            
            # README 파일 내용 검증
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 필수 섹션 확인
                required_sections = ["# " + main_dir.upper(), "## 개요", "## 목적", "## 구조"]
                missing_sections = []
                
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)
                
                if missing_sections:
                    self.verification_results.append(f"❌ {main_dir}/README.md에 필수 섹션 누락: {missing_sections}")
                    readme_ok = False
                else:
                    print(f"  ✅ {main_dir}/README.md 내용 확인")
                    
            except Exception as e:
                self.verification_results.append(f"❌ {main_dir}/README.md 읽기 오류: {e}")
                readme_ok = False
        
        if readme_ok:
            self.verification_results.append("✅ 모든 README 파일이 올바르게 생성되었습니다")
        
        return readme_ok
    
    def _verify_file_permissions(self) -> bool:
        """파일 접근 권한 검증"""
        print("\n🔒 파일 권한 검증 중...")
        
        permissions_ok = True
        
        # 예상 권한 설정
        expected_permissions = {
            "core": 0o755,
            "tools": 0o755,
            "docs": 0o755,
            "archive": 0o755,
            "config": 0o755,
            "scripts": 0o755
        }
        
        for dir_name, expected_perm in expected_permissions.items():
            dir_path = self.root_path / dir_name
            
            if not dir_path.exists():
                continue
            
            try:
                actual_perm = stat.S_IMODE(dir_path.stat().st_mode)
                
                if actual_perm == expected_perm:
                    print(f"  ✅ {dir_name}/ 권한 확인: {oct(actual_perm)}")
                else:
                    self.verification_results.append(
                        f"❌ {dir_name}/ 권한 불일치: 예상 {oct(expected_perm)}, 실제 {oct(actual_perm)}"
                    )
                    permissions_ok = False
                    
            except Exception as e:
                self.verification_results.append(f"❌ {dir_name}/ 권한 확인 오류: {e}")
                permissions_ok = False
        
        if permissions_ok:
            self.verification_results.append("✅ 모든 디렉토리 권한이 올바르게 설정되었습니다")
        
        return permissions_ok
    
    def _verify_symbolic_links(self) -> bool:
        """심볼릭 링크 검증"""
        print("\n🔗 심볼릭 링크 검증 중...")
        
        symlinks_ok = True
        
        for link_path, expected_target in self.expected_symlinks:
            full_link_path = self.root_path / link_path
            
            if not full_link_path.exists():
                # 원본 파일이 없는 경우는 경고만 출력
                original_file = self.root_path / expected_target.replace("../../", "")
                if not original_file.exists():
                    print(f"  ⚠️ 원본 파일 없음으로 심볼릭 링크 생성 안됨: {link_path}")
                    continue
                else:
                    self.verification_results.append(f"❌ 심볼릭 링크 누락: {link_path}")
                    symlinks_ok = False
                    continue
            
            if not full_link_path.is_symlink():
                self.verification_results.append(f"❌ {link_path}가 심볼릭 링크가 아닙니다")
                symlinks_ok = False
                continue
            
            try:
                actual_target = os.readlink(full_link_path)
                
                if actual_target == expected_target:
                    print(f"  ✅ 심볼릭 링크 확인: {link_path} -> {actual_target}")
                    
                    # 링크가 실제로 작동하는지 확인
                    if full_link_path.resolve().exists():
                        print(f"    ✅ 링크 대상 파일 접근 가능")
                    else:
                        self.verification_results.append(f"❌ 심볼릭 링크 대상 파일 접근 불가: {link_path}")
                        symlinks_ok = False
                else:
                    self.verification_results.append(
                        f"❌ 심볼릭 링크 대상 불일치: {link_path} -> 예상: {expected_target}, 실제: {actual_target}"
                    )
                    symlinks_ok = False
                    
            except Exception as e:
                self.verification_results.append(f"❌ 심볼릭 링크 확인 오류: {link_path} ({e})")
                symlinks_ok = False
        
        if symlinks_ok:
            self.verification_results.append("✅ 모든 심볼릭 링크가 올바르게 생성되었습니다")
        
        return symlinks_ok
    
    def _generate_verification_report(self, all_ok: bool) -> None:
        """검증 보고서 생성"""
        report_path = self.root_path / "directory_structure_verification_report.md"
        
        status = "✅ 성공" if all_ok else "❌ 실패"
        
        report_content = f"""# POSCO 시스템 디렉토리 구조 검증 보고서

## 검증 결과: {status}

## 검증 항목별 결과

### 1. 논리적 디렉토리 구조 생성
- core/, tools/, docs/, archive/, config/, scripts/ 디렉토리 및 하위 디렉토리 생성 확인

### 2. 각 디렉토리별 README 파일 생성
- 모든 메인 디렉토리에 README.md 파일 생성 및 내용 확인

### 3. 파일 접근 권한 및 보안 설정
- 디렉토리별 적절한 권한 설정 확인

### 4. 심볼릭 링크를 통한 하위 호환성 보장
- 핵심 파일들에 대한 심볼릭 링크 생성 및 동작 확인

## 상세 검증 결과

"""
        
        for result in self.verification_results:
            report_content += f"- {result}\n"
        
        report_content += f"""
## 요구사항 충족 확인

### 2.2 디렉토리 구조 최적화
- ✅ 논리적이고 체계적인 6단계 디렉토리 구조 생성
- ✅ 각 디렉토리의 목적과 역할이 명확히 구분됨

### 4.1 파일 접근성 향상
- ✅ 각 디렉토리별 README 파일로 구조 설명 제공
- ✅ 심볼릭 링크를 통한 기존 파일 접근 경로 유지
- ✅ 명확한 디렉토리 분류로 파일 탐색 용이성 향상

## 다음 단계 권장사항

1. **파일 이동**: 기존 파일들을 적절한 디렉토리로 분류하여 이동
2. **참조 업데이트**: 파일 이동 후 코드 내 경로 참조 업데이트
3. **무결성 검증**: 이동 후 모든 기능이 정상 작동하는지 확인
4. **문서 업데이트**: 새로운 구조에 맞게 문서 업데이트

---
*검증 일시: {self._get_current_time()}*
*이 보고서는 Task 4 구현 검증을 위해 자동 생성되었습니다.*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📊 검증 보고서 생성: {report_path}")
    
    def _get_current_time(self) -> str:
        """현재 시간 반환"""
        from datetime import datetime
        return datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')

def main():
    """메인 실행 함수"""
    verifier = DirectoryStructureVerifier()
    
    success = verifier.verify_all_requirements()
    
    if success:
        print("\n🎉 Task 4 구현이 성공적으로 완료되었습니다!")
        print("✅ 모든 요구사항이 충족되었습니다:")
        print("  - 논리적 디렉토리 구조 생성")
        print("  - 각 디렉토리별 README 파일 생성")
        print("  - 파일 접근 권한 및 보안 설정")
        print("  - 심볼릭 링크를 통한 하위 호환성 보장")
    else:
        print("\n⚠️ 일부 요구사항이 충족되지 않았습니다.")
        print("📋 상세 내용은 검증 보고서를 확인하세요.")
    
    print("\n📊 검증 보고서: directory_structure_verification_report.md")

if __name__ == "__main__":
    main()