#!/usr/bin/env python3
"""
POSCO 시스템 최적화된 디렉토리 구조 생성 시스템

이 모듈은 POSCO 시스템의 논리적 디렉토리 구조를 생성하고,
각 디렉토리별 README 파일을 생성하며, 적절한 권한을 설정합니다.
"""

import os
import stat
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('directory_structure_creation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DirectoryStructureCreator:
    """최적화된 디렉토리 구조 생성 시스템"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.created_directories = []
        self.created_files = []
        self.symlinks_created = []
        
        # 디렉토리 구조 정의
        self.directory_structure = {
            "core": {
                "description": "핵심 시스템 파일들",
                "purpose": "POSCO 뉴스 모니터링 및 워치햄스터 제어센터 등 핵심 실행 파일들",
                "subdirs": {
                    "POSCO_News_250808": "메인 뉴스 모니터링 시스템",
                    "watchhamster": "워치햄스터 제어센터 관련 파일들",
                    "monitoring": "모니터링 시스템 파일들"
                }
            },
            "tools": {
                "description": "개발 및 유지보수 도구들",
                "purpose": "시스템 수리, 테스트, 품질 관리 등에 사용되는 도구들",
                "subdirs": {
                    "repair": "시스템 수리 도구들",
                    "testing": "테스트 도구들",
                    "quality": "품질 관리 도구들",
                    "automation": "자동화 도구들"
                }
            },
            "docs": {
                "description": "문서화 파일들",
                "purpose": "사용자 가이드, 기술 문서, 트러블슈팅 가이드 등",
                "subdirs": {
                    "user_guides": "사용자 가이드",
                    "technical": "기술 문서",
                    "troubleshooting": "문제 해결 가이드",
                    "api": "API 문서"
                }
            },
            "archive": {
                "description": "완료된 작업 및 백업 파일들",
                "purpose": "작업 완료 보고서, 마이그레이션 로그, 백업 파일 보관",
                "subdirs": {
                    "task_summaries": "작업 완료 보고서들",
                    "migration_logs": "마이그레이션 로그",
                    "backups": "백업 파일들",
                    "temp": "임시 파일들"
                }
            },
            "config": {
                "description": "설정 파일들",
                "purpose": "시스템 설정, 언어 설정, 정리 규칙 등",
                "subdirs": {
                    "system": "시스템 설정",
                    "language": "언어 설정",
                    "cleanup": "정리 규칙"
                }
            },
            "scripts": {
                "description": "실행 스크립트들",
                "purpose": "정리, 검증, 롤백 등 자동화 스크립트들",
                "subdirs": {
                    "cleanup": "정리 스크립트",
                    "verification": "검증 스크립트",
                    "backup": "백업 스크립트"
                }
            }
        }
    
    def create_directory_structure(self) -> bool:
        """전체 디렉토리 구조 생성"""
        try:
            logger.info("🏗️ POSCO 시스템 디렉토리 구조 생성을 시작합니다")
            
            # 메인 디렉토리들 생성
            for dir_name, dir_info in self.directory_structure.items():
                self._create_main_directory(dir_name, dir_info)
            
            # 권한 설정
            self._set_directory_permissions()
            
            # 하위 호환성을 위한 심볼릭 링크 생성
            self._create_compatibility_symlinks()
            
            # 생성 보고서 작성
            self._generate_creation_report()
            
            logger.info("✅ 디렉토리 구조 생성이 완료되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"❌ 디렉토리 구조 생성 중 오류 발생: {e}")
            return False
    
    def _create_main_directory(self, dir_name: str, dir_info: Dict) -> None:
        """메인 디렉토리 및 하위 디렉토리 생성"""
        main_dir = self.root_path / dir_name
        
        # 메인 디렉토리 생성
        main_dir.mkdir(exist_ok=True)
        self.created_directories.append(str(main_dir))
        logger.info(f"📁 디렉토리 생성: {main_dir}")
        
        # 하위 디렉토리 생성
        if "subdirs" in dir_info:
            for subdir_name, subdir_desc in dir_info["subdirs"].items():
                subdir = main_dir / subdir_name
                subdir.mkdir(exist_ok=True)
                self.created_directories.append(str(subdir))
                logger.info(f"  📂 하위 디렉토리 생성: {subdir}")
        
        # README 파일 생성
        self._create_readme_file(main_dir, dir_name, dir_info)
    
    def _create_readme_file(self, dir_path: Path, dir_name: str, dir_info: Dict) -> None:
        """각 디렉토리별 README 파일 생성"""
        readme_path = dir_path / "README.md"
        
        readme_content = f"""# {dir_name.upper()} 디렉토리

## 개요
{dir_info['description']}

## 목적
{dir_info['purpose']}

## 구조
"""
        
        if "subdirs" in dir_info:
            readme_content += "\n### 하위 디렉토리\n\n"
            for subdir_name, subdir_desc in dir_info["subdirs"].items():
                readme_content += f"- **{subdir_name}/**: {subdir_desc}\n"
        
        readme_content += f"""
## 사용 가이드

### 파일 추가 시 주의사항
- 이 디렉토리의 목적에 맞는 파일만 추가하세요
- 파일명은 명확하고 일관된 네이밍 규칙을 따르세요
- 중요한 파일은 백업을 생성하세요

### 권한 관리
- 실행 파일: 755 권한
- 설정 파일: 644 권한
- 민감한 정보: 600 권한

## 마지막 업데이트
{datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}

---
*이 파일은 POSCO 시스템 정리 작업의 일환으로 자동 생성되었습니다.*
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.created_files.append(str(readme_path))
        logger.info(f"📄 README 파일 생성: {readme_path}")
    
    def _set_directory_permissions(self) -> None:
        """디렉토리 및 파일 권한 설정"""
        logger.info("🔒 파일 및 디렉토리 권한을 설정합니다")
        
        permission_rules = {
            "core": {
                "dirs": 0o755,  # rwxr-xr-x
                "files": 0o755  # 실행 파일들
            },
            "tools": {
                "dirs": 0o755,
                "files": 0o755  # 도구들은 실행 가능해야 함
            },
            "docs": {
                "dirs": 0o755,
                "files": 0o644  # rw-r--r--
            },
            "archive": {
                "dirs": 0o755,
                "files": 0o644
            },
            "config": {
                "dirs": 0o755,
                "files": 0o600  # rw------- (민감한 설정)
            },
            "scripts": {
                "dirs": 0o755,
                "files": 0o755  # 스크립트는 실행 가능
            }
        }
        
        for dir_name, permissions in permission_rules.items():
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                # 디렉토리 권한 설정
                os.chmod(dir_path, permissions["dirs"])
                
                # 하위 디렉토리 권한 설정
                for subdir in dir_path.iterdir():
                    if subdir.is_dir():
                        os.chmod(subdir, permissions["dirs"])
                    elif subdir.is_file():
                        os.chmod(subdir, permissions["files"])
                
                logger.info(f"🔐 권한 설정 완료: {dir_name}")
    
    def _create_compatibility_symlinks(self) -> None:
        """하위 호환성을 위한 심볼릭 링크 생성"""
        logger.info("🔗 하위 호환성을 위한 심볼릭 링크를 생성합니다")
        
        # 중요한 파일들에 대한 심볼릭 링크 생성
        symlink_mappings = {
            # 핵심 파일들
            "POSCO_News_250808.py": "core/POSCO_News_250808/POSCO_News_250808.py",
            "🐹POSCO_워치햄스터_v3_제어센터.bat": "core/watchhamster/🐹POSCO_워치햄스터_v3_제어센터.bat",
            "🐹POSCO_워치햄스터_v3_제어센터.command": "core/watchhamster/🐹POSCO_워치햄스터_v3_제어센터.command",
            
            # 자주 사용되는 도구들
            "cleanup_system.py": "scripts/cleanup/cleanup_system.py",
            "verify_integrity.py": "scripts/verification/verify_integrity.py",
            "backup_system.py": "scripts/backup/backup_system.py",
            
            # 설정 파일들
            "language_settings.json": "config/language/language_settings.json",
            "cleanup_rules.json": "config/cleanup/cleanup_rules.json"
        }
        
        for original_name, target_path in symlink_mappings.items():
            original_path = self.root_path / original_name
            target_full_path = self.root_path / target_path
            
            # 원본 파일이 존재하고 타겟 경로의 디렉토리가 존재하는 경우에만 링크 생성
            if original_path.exists() and target_full_path.parent.exists():
                try:
                    # 기존 심볼릭 링크가 있으면 제거
                    if target_full_path.is_symlink():
                        target_full_path.unlink()
                    
                    # 상대 경로로 심볼릭 링크 생성
                    relative_path = os.path.relpath(original_path, target_full_path.parent)
                    target_full_path.symlink_to(relative_path)
                    
                    self.symlinks_created.append(f"{original_name} -> {target_path}")
                    logger.info(f"🔗 심볼릭 링크 생성: {original_name} -> {target_path}")
                    
                except OSError as e:
                    logger.warning(f"⚠️ 심볼릭 링크 생성 실패: {original_name} -> {target_path} ({e})")
    
    def _generate_creation_report(self) -> None:
        """디렉토리 구조 생성 보고서 작성"""
        report_path = self.root_path / "directory_structure_creation_report.json"
        
        report_data = {
            "creation_timestamp": datetime.now().isoformat(),
            "created_directories": self.created_directories,
            "created_files": self.created_files,
            "symlinks_created": self.symlinks_created,
            "directory_structure": self.directory_structure,
            "summary": {
                "total_directories": len(self.created_directories),
                "total_files": len(self.created_files),
                "total_symlinks": len(self.symlinks_created)
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 생성 보고서 작성: {report_path}")
        
        # 마크다운 보고서도 생성
        self._generate_markdown_report(report_data)
    
    def _generate_markdown_report(self, report_data: Dict) -> None:
        """마크다운 형식의 생성 보고서 작성"""
        report_path = self.root_path / "directory_structure_creation_report.md"
        
        markdown_content = f"""# POSCO 시스템 디렉토리 구조 생성 보고서

## 생성 정보
- **생성 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
- **생성된 디렉토리 수**: {len(self.created_directories)}개
- **생성된 파일 수**: {len(self.created_files)}개
- **생성된 심볼릭 링크 수**: {len(self.symlinks_created)}개

## 디렉토리 구조

```
POSCO_System_Root/
├── core/                          # 핵심 시스템 파일
│   ├── POSCO_News_250808/        # 메인 뉴스 모니터링 시스템
│   ├── watchhamster/             # 워치햄스터 제어센터 관련 파일들
│   └── monitoring/               # 모니터링 시스템 파일들
├── tools/                         # 개발 및 유지보수 도구들
│   ├── repair/                   # 시스템 수리 도구들
│   ├── testing/                  # 테스트 도구들
│   ├── quality/                  # 품질 관리 도구들
│   └── automation/               # 자동화 도구들
├── docs/                          # 문서화 파일들
│   ├── user_guides/              # 사용자 가이드
│   ├── technical/                # 기술 문서
│   ├── troubleshooting/          # 문제 해결 가이드
│   └── api/                      # API 문서
├── archive/                       # 완료된 작업 및 백업 파일들
│   ├── task_summaries/           # 작업 완료 보고서들
│   ├── migration_logs/           # 마이그레이션 로그
│   ├── backups/                  # 백업 파일들
│   └── temp/                     # 임시 파일들
├── config/                        # 설정 파일들
│   ├── system/                   # 시스템 설정
│   ├── language/                 # 언어 설정
│   └── cleanup/                  # 정리 규칙
└── scripts/                       # 실행 스크립트들
    ├── cleanup/                  # 정리 스크립트
    ├── verification/             # 검증 스크립트
    └── backup/                   # 백업 스크립트
```

## 생성된 디렉토리 목록
"""
        
        for directory in self.created_directories:
            markdown_content += f"- {directory}\n"
        
        markdown_content += f"""
## 생성된 README 파일 목록
"""
        
        for file_path in self.created_files:
            if file_path.endswith('README.md'):
                markdown_content += f"- {file_path}\n"
        
        if self.symlinks_created:
            markdown_content += f"""
## 생성된 심볼릭 링크 목록
"""
            for symlink in self.symlinks_created:
                markdown_content += f"- {symlink}\n"
        
        markdown_content += f"""
## 권한 설정
- **core/**: 755 (실행 파일들)
- **tools/**: 755 (도구들은 실행 가능)
- **docs/**: 644 (문서 파일들)
- **archive/**: 644 (보관 파일들)
- **config/**: 600 (민감한 설정 파일들)
- **scripts/**: 755 (실행 스크립트들)

## 다음 단계
1. 기존 파일들을 적절한 디렉토리로 이동
2. 파일 참조 경로 업데이트
3. 무결성 검증 수행
4. 심볼릭 링크 동작 확인

---
*이 보고서는 POSCO 시스템 정리 작업의 일환으로 자동 생성되었습니다.*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"📋 마크다운 보고서 작성: {report_path}")

def main():
    """메인 실행 함수"""
    creator = DirectoryStructureCreator()
    
    print("🏗️ POSCO 시스템 최적화된 디렉토리 구조 생성을 시작합니다...")
    
    success = creator.create_directory_structure()
    
    if success:
        print("✅ 디렉토리 구조 생성이 성공적으로 완료되었습니다!")
        print("📊 생성 보고서를 확인하세요:")
        print("  - directory_structure_creation_report.json")
        print("  - directory_structure_creation_report.md")
    else:
        print("❌ 디렉토리 구조 생성 중 오류가 발생했습니다.")
        print("📋 로그 파일을 확인하세요: directory_structure_creation.log")

if __name__ == "__main__":
    main()