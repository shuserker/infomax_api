#!/usr/bin/env python3
"""
POSCO 시스템 파일 분류 및 분석 시스템
File Classification and Analysis System

2000+ 파일들을 논리적으로 분류하고 분석하여 체계적인 정리를 위한 기반을 제공합니다.
기존 시스템의 내용과 로직은 절대 변경하지 않습니다.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

# 한글 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_classification.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileCategory(Enum):
    """파일 카테고리"""
    CORE = "핵심_시스템"
    TOOLS = "개발_도구"
    DOCS = "문서"
    TEMP = "임시_파일"
    CONFIG = "설정_파일"
    ARCHIVE = "보관_파일"
    UNKNOWN = "미분류"

@dataclass
class FileInfo:
    """파일 정보 데이터 클래스"""
    path: str
    size: int
    modified_time: datetime
    category: FileCategory
    importance: str  # 'critical', 'important', 'normal', 'low'
    dependencies: List[str]
    description: str
    
class FileClassifier:
    """파일 분류 시스템"""
    
    def __init__(self):
        # 핵심 시스템 파일 패턴 (절대 보존)
        self.core_patterns = {
            'POSCO_News_250808.py': '메인 뉴스 모니터링 시스템',
            '🐹POSCO_워치햄스터_v3_제어센터.bat': 'Windows 제어센터',
            '🐹POSCO_워치햄스터_v3_제어센터.command': 'macOS 제어센터',
            'Monitoring/POSCO_News_250808/*.py': '모니터링 시스템 모듈',
            'Monitoring/Posco_News_mini_v2/**/*.py': 'v2 모니터링 시스템'
        }
        
        # 개발 도구 파일 패턴
        self.tool_patterns = {
            '*_repair*.py': '수리 도구',
            '*_fixer*.py': '수정 도구',
            '*_repairer*.py': '복구 도구',
            'test_*.py': '테스트 파일',
            '*_test*.py': '테스트 파일',
            '*_testing*.py': '테스트 도구',
            '*_verification*.py': '검증 도구',
            '*_validator*.py': '검증 도구',
            'automated_*.py': '자동화 도구',
            'enhanced_*.py': '향상된 도구',
            'comprehensive_*.py': '종합 도구',
            '*_cli.py': '명령행 도구',
            '*_system.py': '시스템 도구'
        }
        
        # 문서 파일 패턴
        self.doc_patterns = {
            '*.md': '마크다운 문서',
            '*.txt': '텍스트 문서',
            '*_guide*.md': '가이드 문서',
            '*_manual*.md': '매뉴얼 문서',
            '*_documentation*.md': '기술 문서',
            'README*': 'README 파일',
            '*_summary*.md': '요약 보고서',
            '*_report*.md': '보고서',
            '*_index*.md': '인덱스 문서'
        }
        
        # 임시 파일 패턴
        self.temp_patterns = {
            'task*_completion_summary.md': '작업 완료 보고서',
            'task*_*.md': '작업 관련 임시 파일',
            '*.backup': '백업 파일',
            '*.bak': '백업 파일',
            '*_temp*': '임시 파일',
            '*.log': '로그 파일',
            '*_logs*': '로그 파일',
            '*.tmp': '임시 파일'
        }
        
        # 설정 파일 패턴
        self.config_patterns = {
            '*.json': 'JSON 설정 파일',
            '*.yaml': 'YAML 설정 파일',
            '*.yml': 'YAML 설정 파일',
            '*.ini': 'INI 설정 파일',
            '*.conf': '설정 파일',
            '*_config*': '설정 파일',
            '*_settings*': '설정 파일'
        }
        
        # 보관 파일 패턴 (이미 완료된 작업들)
        self.archive_patterns = {
            'Task*_*.md': '완료된 작업 문서',
            '*_Implementation_Summary.md': '구현 요약',
            '*_completion_*.md': '완료 보고서',
            'ModuleRegistry_*.md': '모듈 레지스트리',
            'migration_*.py': '마이그레이션 스크립트',
            'post_migration_*.py': '마이그레이션 후 처리'
        }
        
        self.classification_results = {}
        self.duplicate_files = []
        self.large_files = []
        
    def classify_all_files(self) -> Dict[FileCategory, List[FileInfo]]:
        """모든 파일 분류"""
        logger.info("📂 전체 파일 분류 시작")
        
        classified_files = {category: [] for category in FileCategory}
        total_files = 0
        total_size = 0
        
        # 제외할 디렉토리
        exclude_dirs = {
            '__pycache__',
            '.git',
            '.kiro',
            'node_modules',
            '.vscode',
            '.idea'
        }
        
        for root, dirs, files in os.walk('.'):
            # 제외 디렉토리 필터링
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                try:
                    # 파일 정보 수집
                    stat_info = file_path.stat()
                    file_info = FileInfo(
                        path=str(file_path),
                        size=stat_info.st_size,
                        modified_time=datetime.fromtimestamp(stat_info.st_mtime),
                        category=self._classify_file(file_path),
                        importance=self._determine_importance(file_path),
                        dependencies=self._analyze_dependencies(file_path),
                        description=self._get_file_description(file_path)
                    )
                    
                    classified_files[file_info.category].append(file_info)
                    total_files += 1
                    total_size += file_info.size
                    
                    # 대용량 파일 식별 (10MB 이상)
                    if file_info.size > 10 * 1024 * 1024:
                        self.large_files.append(file_info)
                    
                    if total_files % 500 == 0:
                        logger.info(f"진행 상황: {total_files}개 파일 분류 완료")
                        
                except Exception as e:
                    logger.warning(f"파일 분류 실패 {file_path}: {e}")
        
        # 중복 파일 검사
        self._find_duplicate_files(classified_files)
        
        # 분류 결과 저장
        self.classification_results = classified_files
        
        logger.info(f"✅ 파일 분류 완료")
        logger.info(f"   총 파일 수: {total_files:,}개")
        logger.info(f"   총 크기: {total_size / 1024 / 1024:.1f}MB")
        logger.info(f"   대용량 파일: {len(self.large_files)}개")
        logger.info(f"   중복 파일: {len(self.duplicate_files)}개")
        
        return classified_files
    
    def _classify_file(self, file_path: Path) -> FileCategory:
        """개별 파일 분류"""
        file_str = str(file_path)
        file_name = file_path.name
        
        # 핵심 시스템 파일 확인
        for pattern, desc in self.core_patterns.items():
            if self._match_pattern(file_str, pattern):
                return FileCategory.CORE
        
        # 보관 파일 확인 (임시 파일보다 우선)
        for pattern, desc in self.archive_patterns.items():
            if self._match_pattern(file_name, pattern):
                return FileCategory.ARCHIVE
        
        # 임시 파일 확인
        for pattern, desc in self.temp_patterns.items():
            if self._match_pattern(file_name, pattern):
                return FileCategory.TEMP
        
        # 개발 도구 확인
        for pattern, desc in self.tool_patterns.items():
            if self._match_pattern(file_name, pattern):
                return FileCategory.TOOLS
        
        # 설정 파일 확인
        for pattern, desc in self.config_patterns.items():
            if self._match_pattern(file_name, pattern):
                return FileCategory.CONFIG
        
        # 문서 파일 확인
        for pattern, desc in self.doc_patterns.items():
            if self._match_pattern(file_name, pattern):
                return FileCategory.DOCS
        
        return FileCategory.UNKNOWN
    
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """패턴 매칭"""
        import fnmatch
        
        # 경로 패턴 처리
        if '/' in pattern:
            return fnmatch.fnmatch(file_path, pattern)
        else:
            # 파일명만 매칭
            file_name = Path(file_path).name
            return fnmatch.fnmatch(file_name, pattern)
    
    def _determine_importance(self, file_path: Path) -> str:
        """파일 중요도 결정"""
        file_str = str(file_path)
        file_name = file_path.name
        
        # 핵심 파일
        critical_patterns = [
            'POSCO_News_250808.py',
            '🐹POSCO_워치햄스터_v3_제어센터.*',
            'Monitoring/POSCO_News_250808/*.py'
        ]
        
        for pattern in critical_patterns:
            if self._match_pattern(file_str, pattern):
                return 'critical'
        
        # 중요 파일
        important_patterns = [
            '*_system.py',
            '*_manager.py',
            '*_verification.py',
            'final_*.py'
        ]
        
        for pattern in important_patterns:
            if self._match_pattern(file_name, pattern):
                return 'important'
        
        # 임시 파일은 낮은 중요도
        if file_name.startswith('task') or 'temp' in file_name.lower():
            return 'low'
        
        return 'normal'
    
    def _analyze_dependencies(self, file_path: Path) -> List[str]:
        """파일 의존성 분석"""
        dependencies = []
        
        if file_path.suffix == '.py':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # import 구문 찾기
                import re
                import_patterns = [
                    r'from\s+([^\s]+)\s+import',
                    r'import\s+([^\s,]+)'
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if not match.startswith('.') and match not in ['os', 'sys', 'json', 'time']:
                            dependencies.append(match)
                
            except Exception:
                pass
        
        return list(set(dependencies))  # 중복 제거
    
    def _get_file_description(self, file_path: Path) -> str:
        """파일 설명 생성"""
        file_str = str(file_path)
        file_name = file_path.name
        
        # 핵심 파일 설명
        for pattern, desc in self.core_patterns.items():
            if self._match_pattern(file_str, pattern):
                return desc
        
        # 도구 파일 설명
        for pattern, desc in self.tool_patterns.items():
            if self._match_pattern(file_name, pattern):
                return desc
        
        # 문서 파일 설명
        for pattern, desc in self.doc_patterns.items():
            if self._match_pattern(file_name, pattern):
                return desc
        
        # 임시 파일 설명
        for pattern, desc in self.temp_patterns.items():
            if self._match_pattern(file_name, pattern):
                return desc
        
        # 설정 파일 설명
        for pattern, desc in self.config_patterns.items():
            if self._match_pattern(file_name, pattern):
                return desc
        
        # 보관 파일 설명
        for pattern, desc in self.archive_patterns.items():
            if self._match_pattern(file_name, pattern):
                return desc
        
        return f"{file_path.suffix} 파일"
    
    def _find_duplicate_files(self, classified_files: Dict[FileCategory, List[FileInfo]]):
        """중복 파일 찾기"""
        logger.info("🔍 중복 파일 검사 중...")
        
        file_hashes = {}
        
        for category, files in classified_files.items():
            for file_info in files:
                try:
                    # 작은 파일만 해시 계산 (성능상 이유)
                    if file_info.size < 1024 * 1024:  # 1MB 미만
                        with open(file_info.path, 'rb') as f:
                            content = f.read()
                            file_hash = hashlib.md5(content).hexdigest()
                            
                            if file_hash in file_hashes:
                                self.duplicate_files.append({
                                    'original': file_hashes[file_hash],
                                    'duplicate': file_info.path,
                                    'size': file_info.size
                                })
                            else:
                                file_hashes[file_hash] = file_info.path
                                
                except Exception:
                    continue
        
        logger.info(f"중복 파일 {len(self.duplicate_files)}개 발견")
    
    def generate_classification_report(self) -> str:
        """분류 보고서 생성"""
        if not self.classification_results:
            return "분류 결과가 없습니다. 먼저 classify_all_files()를 실행하세요."
        
        report_time = datetime.now()
        
        report = f"""
# POSCO 시스템 파일 분류 보고서

**생성 시간**: {report_time.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 분류 결과 요약

"""
        
        total_files = sum(len(files) for files in self.classification_results.values())
        total_size = sum(sum(f.size for f in files) for files in self.classification_results.values())
        
        report += f"- **총 파일 수**: {total_files:,}개\n"
        report += f"- **총 크기**: {total_size / 1024 / 1024:.1f}MB\n"
        report += f"- **대용량 파일**: {len(self.large_files)}개\n"
        report += f"- **중복 파일**: {len(self.duplicate_files)}개\n\n"
        
        # 카테고리별 통계
        report += "## 📂 카테고리별 분류 결과\n\n"
        
        for category, files in self.classification_results.items():
            if not files:
                continue
                
            category_size = sum(f.size for f in files)
            report += f"### {category.value}\n\n"
            report += f"- **파일 수**: {len(files):,}개\n"
            report += f"- **총 크기**: {category_size / 1024 / 1024:.1f}MB\n"
            report += f"- **평균 크기**: {category_size / len(files) / 1024:.1f}KB\n"
            
            # 중요도별 분류
            importance_count = {}
            for file_info in files:
                importance_count[file_info.importance] = importance_count.get(file_info.importance, 0) + 1
            
            if importance_count:
                report += "- **중요도별**:\n"
                for importance, count in sorted(importance_count.items()):
                    report += f"  - {importance}: {count}개\n"
            
            # 상위 5개 파일 (크기순)
            top_files = sorted(files, key=lambda x: x.size, reverse=True)[:5]
            if top_files:
                report += "- **주요 파일** (크기순):\n"
                for file_info in top_files:
                    size_mb = file_info.size / 1024 / 1024
                    report += f"  - `{file_info.path}` ({size_mb:.1f}MB) - {file_info.description}\n"
            
            report += "\n"
        
        # 중복 파일 정보
        if self.duplicate_files:
            report += "## 🔄 중복 파일 목록\n\n"
            for dup in self.duplicate_files[:10]:  # 상위 10개만
                size_kb = dup['size'] / 1024
                report += f"- `{dup['original']}` ↔ `{dup['duplicate']}` ({size_kb:.1f}KB)\n"
            
            if len(self.duplicate_files) > 10:
                report += f"- ... 및 {len(self.duplicate_files) - 10}개 추가\n"
            report += "\n"
        
        # 대용량 파일 정보
        if self.large_files:
            report += "## 📦 대용량 파일 목록\n\n"
            for file_info in sorted(self.large_files, key=lambda x: x.size, reverse=True):
                size_mb = file_info.size / 1024 / 1024
                report += f"- `{file_info.path}` ({size_mb:.1f}MB) - {file_info.description}\n"
            report += "\n"
        
        # 정리 권장사항
        report += "## 💡 정리 권장사항\n\n"
        
        temp_files = self.classification_results.get(FileCategory.TEMP, [])
        archive_files = self.classification_results.get(FileCategory.ARCHIVE, [])
        
        if temp_files:
            temp_size = sum(f.size for f in temp_files) / 1024 / 1024
            report += f"1. **임시 파일 정리**: {len(temp_files)}개 파일 ({temp_size:.1f}MB) → `archive/temp/` 이동\n"
        
        if archive_files:
            archive_size = sum(f.size for f in archive_files) / 1024 / 1024
            report += f"2. **완료 작업 보관**: {len(archive_files)}개 파일 ({archive_size:.1f}MB) → `archive/completed/` 이동\n"
        
        if self.duplicate_files:
            dup_size = sum(dup['size'] for dup in self.duplicate_files) / 1024 / 1024
            report += f"3. **중복 파일 제거**: {len(self.duplicate_files)}개 파일 ({dup_size:.1f}MB) 절약 가능\n"
        
        if self.large_files:
            report += f"4. **대용량 파일 압축**: {len(self.large_files)}개 파일 압축 검토\n"
        
        # 예상 절약 효과
        potential_savings = 0
        if temp_files:
            potential_savings += sum(f.size for f in temp_files)
        if self.duplicate_files:
            potential_savings += sum(dup['size'] for dup in self.duplicate_files)
        
        if potential_savings > 0:
            savings_mb = potential_savings / 1024 / 1024
            savings_percent = (potential_savings / total_size) * 100
            report += f"\n**예상 절약 효과**: {savings_mb:.1f}MB ({savings_percent:.1f}%)\n"
        
        report += f"""
---
*이 보고서는 자동으로 생성되었습니다.*
"""
        
        return report
    
    def save_classification_data(self, output_file: str = "file_classification_data.json"):
        """분류 데이터 JSON으로 저장"""
        if not self.classification_results:
            logger.warning("저장할 분류 데이터가 없습니다.")
            return
        
        # JSON 직렬화 가능한 형태로 변환
        serializable_data = {}
        
        for category, files in self.classification_results.items():
            serializable_data[category.value] = []
            for file_info in files:
                serializable_data[category.value].append({
                    'path': file_info.path,
                    'size': file_info.size,
                    'modified_time': file_info.modified_time.isoformat(),
                    'importance': file_info.importance,
                    'dependencies': file_info.dependencies,
                    'description': file_info.description
                })
        
        # 추가 정보
        serializable_data['_metadata'] = {
            'classification_time': datetime.now().isoformat(),
            'total_files': sum(len(files) for files in self.classification_results.values()),
            'duplicate_files': self.duplicate_files,
            'large_files': [
                {
                    'path': f.path,
                    'size': f.size,
                    'description': f.description
                } for f in self.large_files
            ]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📄 분류 데이터 저장: {output_file}")
            
        except Exception as e:
            logger.error(f"분류 데이터 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='POSCO 시스템 파일 분류')
    parser.add_argument('--classify', action='store_true', help='전체 파일 분류 실행')
    parser.add_argument('--report', action='store_true', help='분류 보고서 생성')
    parser.add_argument('--save-data', action='store_true', help='분류 데이터 JSON 저장')
    parser.add_argument('--category', type=str, help='특정 카테고리 파일 목록 출력')
    
    args = parser.parse_args()
    
    classifier = FileClassifier()
    
    try:
        if args.classify:
            logger.info("🚀 파일 분류 시작")
            classified_files = classifier.classify_all_files()
            
            # 분류 결과 요약 출력
            logger.info("\n📊 분류 결과 요약:")
            for category, files in classified_files.items():
                if files:
                    size_mb = sum(f.size for f in files) / 1024 / 1024
                    logger.info(f"  {category.value}: {len(files):,}개 ({size_mb:.1f}MB)")
        
        if args.report:
            logger.info("📋 분류 보고서 생성 중...")
            report = classifier.generate_classification_report()
            
            report_file = f"file_classification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"✅ 분류 보고서 생성: {report_file}")
        
        if args.save_data:
            classifier.save_classification_data()
        
        if args.category:
            try:
                category = FileCategory(args.category)
                files = classifier.classification_results.get(category, [])
                
                logger.info(f"\n📂 {category.value} 카테고리 파일 목록:")
                for file_info in files:
                    size_kb = file_info.size / 1024
                    logger.info(f"  - {file_info.path} ({size_kb:.1f}KB) - {file_info.description}")
                    
            except ValueError:
                logger.error(f"잘못된 카테고리: {args.category}")
                logger.info("사용 가능한 카테고리: " + ", ".join([c.value for c in FileCategory]))
        
        if not any([args.classify, args.report, args.save_data, args.category]):
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ 실행 중 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()